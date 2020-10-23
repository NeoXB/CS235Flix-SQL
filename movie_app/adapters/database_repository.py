import csv
import os
from datetime import date
from typing import List
from sqlalchemy import desc, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack
from movie_app.domain.model import Director, Genre, Actor, Movie, MovieFileCSVReader, Review, User, WatchList
from movie_app.adapters.repository import AbstractRepository

genres = None


class SessionContextManager:
    def __init__(self, session_factory):
        self.__session_factory = session_factory
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    @property
    def session(self):
        return self.__session

    def commit(self):
        self.__session.commit()

    def rollback(self):
        self.__session.rollback()

    def reset_session(self):
        # this method can be used e.g. to allow Flask to start a new session for each http request,
        # via the 'before_request' callback
        self.close_current_session()
        self.__session = scoped_session(self.__session_factory, scopefunc=_app_ctx_stack.__ident_func__)

    def close_current_session(self):
        if not self.__session is None:
            self.__session.close()


class SqlAlchemyRepository(AbstractRepository):

    def __init__(self, session_factory):
        self._session_cm = SessionContextManager(session_factory)

    def close_session(self):
        self._session_cm.close_current_session()

    def reset_session(self):
        self._session_cm.reset_session()

    def add_director(self, director: Director):
        with self._session_cm as scm:
            scm.session.add(director)
            scm.commit()

    def get_director(self, director_name) -> Director:
        director = None
        try:
            director = self._session_cm.session.query(Director).filter_by(__director_full_name=director_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return director
    # Continue here
    def add_genre(self, genre: Genre):
        self._genres.append(genre)

    def get_genres(self) -> List[Genre]:
        return self._genres

    def add_actor(self, actor: Actor):
        self._actors.append(actor)

    def get_actor(self, actor_name) -> Actor:
        return next((actor for actor in self._actors if actor.actor_full_name == actor_name), None)

    def add_movie(self, movie: Movie):
        self._movies.append(movie)
        self._movies_index[movie.rank] = movie

    def get_movie(self, rank: int) -> Movie:
        movie = None
        try:
            movie = self._movies_index[rank]
        except KeyError:
            pass  # Ignore exception and return None.
        return movie

    def get_number_of_movies(self):
        return len(self._movies)

    def get_first_movie(self) -> Movie:
        movie = None
        if len(self._movies) > 0:
            movie = self._movies[0]
        return movie

    def get_last_movie(self) -> Movie:
        movie = None
        if len(self._movies) > 0:
            movie = self._movies[-1]
        return movie

    def get_movies_by_rank(self, rank_list):
        # Strip out any ranks in rank_list that don't represent Movie ranks in the repository.
        existing_ranks = [rank for rank in rank_list if rank in self._movies_index]

        # Fetch the Movies.
        movies = [self._movies_index[rank] for rank in existing_ranks]
        return movies

    def get_movie_ranks_for_genre(self, genre_name: str):
        # Linear search, to find the first occurrence of a Genre with the name genre_name.
        genre = next((genre for genre in self._genres if genre.genre_name == genre_name), None)

        # Retrieve the ranks of movies associated with the Genre.
        if genre is not None:
            movie_ranks = [movie.rank for movie in self._movies if genre in movie.genres]
        else:
            # No Genre with name genre_name. Return an empty list.
            movie_ranks = list()
        return movie_ranks

    def add_review(self, review: Review):
        super().add_review(review)
        self._reviews.append(review)

    def get_reviews(self):
        return self._reviews

    def add_user(self, user: User):
        self._users.append(user)

    def get_user(self, username: str) -> User:
        return next((user for user in self._users if user.user_name == username), None)

    def add_watchlist(self, watchlist: WatchList):
        self._all_watchlist.append(watchlist)

    def get_watchlist(self, user: User) -> List[WatchList]:
        all_watchlist = []
        for watchlist in self._all_watchlist:
            if watchlist.watchlist_owner == user:
                all_watchlist.append(watchlist)
        return all_watchlist


def article_record_generator(filename: str):
    with open(filename, mode='r', encoding='utf-8-sig') as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        headers = next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:

            article_data = row
            article_key = article_data[0]

            # Strip any leading/trailing white space from data read.
            article_data = [item.strip() for item in article_data]

            number_of_tags = len(article_data) - 6
            article_tags = article_data[-number_of_tags:]

            # Add any new tags; associate the current article with tags.
            for tag in article_tags:
                if tag not in tags.keys():
                    tags[tag] = list()
                tags[tag].append(article_key)

            del article_data[-number_of_tags:]

            yield article_data


def get_tag_records():
    tag_records = list()
    tag_key = 0

    for tag in tags.keys():
        tag_key = tag_key + 1
        tag_records.append((tag_key, tag))
    return tag_records


def article_tags_generator():
    article_tags_key = 0
    tag_key = 0

    for tag in tags.keys():
        tag_key = tag_key + 1
        for article_key in tags[tag]:
            article_tags_key = article_tags_key + 1
            yield article_tags_key, article_key, tag_key


def generic_generator(filename, post_process=None):
    with open(filename) as infile:
        reader = csv.reader(infile)

        # Read first line of the CSV file.
        next(reader)

        # Read remaining rows from the CSV file.
        for row in reader:
            # Strip any leading/trailing white space from data read.
            row = [item.strip() for item in row]

            if post_process is not None:
                row = post_process(row)
            yield row


def process_user(user_row):
    user_row[2] = generate_password_hash(user_row[2])
    return user_row


def populate(engine: Engine, data_path: str):
    conn = engine.raw_connection()
    cursor = conn.cursor()

    global tags
    tags = dict()

    insert_articles = """
        INSERT INTO articles (
        id, date, title, first_para, hyperlink, image_hyperlink)
        VALUES (?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_articles, article_record_generator(os.path.join(data_path, 'news_articles.csv')))

    insert_tags = """
        INSERT INTO tags (
        id, name)
        VALUES (?, ?)"""
    cursor.executemany(insert_tags, get_tag_records())

    insert_article_tags = """
        INSERT INTO article_tags (
        id, article_id, tag_id)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_article_tags, article_tags_generator())

    insert_users = """
        INSERT INTO users (
        id, username, password)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_users, generic_generator(os.path.join(data_path, 'users.csv'), process_user))

    insert_comments = """
        INSERT INTO comments (
        id, user_id, article_id, comment, timestamp)
        VALUES (?, ?, ?, ?, ?)"""
    cursor.executemany(insert_comments, generic_generator(os.path.join(data_path, 'comments.csv')))

    conn.commit()
    conn.close()

