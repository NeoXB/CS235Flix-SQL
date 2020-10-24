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

    def add_genre(self, genre: Genre):
        with self._session_cm as scm:
            scm.session.add(genre)
            scm.commit()

    def get_genres(self) -> List[Genre]:
        genres = self._session_cm.session.query(Genre).all()
        return genres

    def add_actor(self, actor: Actor):
        with self._session_cm as scm:
            scm.session.add(actor)
            scm.commit()

    def get_actor(self, actor_name) -> Actor:
        actor = None
        try:
            actor = self._session_cm.session.query(Actor).filter_by(__actor_full_name=actor_name).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return actor

    def add_movie(self, movie: Movie):
        with self._session_cm as scm:
            scm.session.add(movie)
            scm.commit()

    def get_movie(self, rank: int) -> Movie:
        movie = None
        try:
            movie = self._session_cm.session.query(Movie).filter(Movie.__rank == rank).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return movie

    def get_number_of_movies(self):
        number_of_movies = self._session_cm.session.query(Movie).count()
        return number_of_movies

    def get_first_movie(self) -> Movie:
        movie = self._session_cm.session.query(Movie).first()
        return movie

    def get_last_movie(self) -> Movie:
        movie = self._session_cm.session.query(Movie).order_by(desc(Movie.__rank)).first()
        return movie

    def get_movies_by_rank(self, rank_list):
        movies = self._session_cm.session.query(Movie).filter(Movie.__rank.in_(rank_list)).all()
        return movies

    def get_movie_ranks_for_genre(self, genre_name: str):
        # Use native SQL to retrieve movie ranks, since there is no mapped class for the movie_genres table.
        row = self._session_cm.session.execute('SELECT id FROM genres WHERE genre_name = :genre_name',
                                               {'genre_name': genre_name}).fetchone()

        if row is None:
            # No genre with the name genre_name - create an empty list.
            movie_ranks = list()
        else:
            genre_id = row[0]

            # Retrieve article ids of articles associated with the tag.
            movie_ranks = self._session_cm.session.execute(
                'SELECT movie_id FROM movie_genres WHERE genre_id = :genre_id ORDER BY movie_id ASC',
                {'genre_id': genre_id}
            ).fetchall()
            movie_ranks = [rank[0] for rank in movie_ranks]

        return movie_ranks

    def add_review(self, review: Review):
        super().add_review(review)
        with self._session_cm as scm:
            scm.session.add(review)
            scm.commit()

    def get_reviews(self):
        reviews = self._session_cm.session.query(Review).all()
        return reviews

    def add_user(self, user: User):
        with self._session_cm as scm:
            scm.session.add(user)
            scm.commit()

    def get_user(self, username: str) -> User:
        user = None
        try:
            user = self._session_cm.session.query(User).filter_by(__user_name=username).one()
        except NoResultFound:
            # Ignore any exception and return None.
            pass

        return user

    def add_watchlist(self, watchlist: WatchList):
        pass

    def get_watchlist(self, user: User) -> List[WatchList]:
        pass

# CONTINUE HERE
def csv_processor(filename: str):
    with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
        movie_file_reader = csv.DictReader(csvfile)
        i = 0
        for row in movie_file_reader:
            # reading from csv
            movie_rank = int(row['Rank'].strip())
            title = row['Title']
            genres = row['Genre'].split(',')
            movie_description = row['Description'].strip()
            director = row['Director'].strip()
            actors = row['Actors'].split(',')
            year = int(row['Year'].strip())
            runtime = int(row['Runtime (Minutes)'].strip())
            movie_rating = float(row['Rating'].strip()) if row['Rating'].strip() != 'N/A' else row['Rating'].strip()
            movie_votes = int(row['Votes'].strip()) if row['Votes'].strip() != 'N/A' else row['Votes'].strip()
            movie_revenue = float(row['Revenue (Millions)'].strip()) \
                if row['Revenue (Millions)'].strip() != 'N/A' else row['Revenue (Millions)'].strip()
            movie_metascore = int(row['Metascore'].strip()) \
                if row['Metascore'].strip() != 'N/A' else row['Metascore'].strip()

            # assigning to respective objects
            movie_director = Director(director)
            movie_genres = list()
            for g in genres:
                genre = g.strip()
                movie_genres.append(Genre(genre))
            movie_actors = list()
            for a in actors:
                actor = a.strip()
                movie_actors.append(Actor(actor))

            # assigning to respective datasets
            self.__dataset_of_movies.append(Movie(title, year))
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].rank = movie_rank
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].genres = movie_genres
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].description = movie_description
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].director = movie_director
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].actors = movie_actors
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].runtime_minutes = runtime
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].rating = movie_rating
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].votes = movie_votes
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].revenue = movie_revenue
            self.__dataset_of_movies[len(self.__dataset_of_movies) - 1].metascore = movie_metascore
            for a in movie_actors:
                self.__dataset_of_actors.add(a)
            self.__dataset_of_directors.add(movie_director)
            for g in movie_genres:
                self.__dataset_of_genres.add(g)
            i += 1


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

