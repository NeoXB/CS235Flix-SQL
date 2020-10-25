import csv
import os
from datetime import datetime
from typing import List
from sqlalchemy import desc, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import scoped_session
from flask import _app_ctx_stack
from movie_app.domain.model import Director, Genre, Actor, Movie, Review, User, WatchList
from movie_app.adapters.repository import AbstractRepository

directors = None
genres = None
actors = None


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


def csv_processor(filename: str):
    with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
        movie_file_reader = csv.DictReader(csvfile)
        for row in movie_file_reader:
            # Reading from csv.
            movie_rank = int(row['Rank'].strip())
            movie_genres = row['Genre'].split(',')
            movie_director = row['Director'].strip()
            movie_actors = row['Actors'].split(',')

            # Add any new director; associate the current movie with director.
            if movie_director not in directors.keys():
                directors[movie_director] = list()
            directors[movie_director].append(movie_rank)

            # Add any new genres; associate the current movie with genres.
            for genre in movie_genres:
                if genre not in genres.keys():
                    genres[genre] = list()
                genres[genre].append(movie_rank)

            # Add any new actors; associate the current movie with actors.
            for actor in movie_actors:
                if actor not in actors.keys():
                    actors[actor] = list()
                actors[actor].append(movie_rank)


def director_generator():
    director_records = list()
    director_key = 0

    for director in directors.keys():
        director_key += 1
        director_records.append((director_key, director))
    return director_records


def genre_generator():
    genre_records = list()
    genre_key = 0

    for genre in genres.keys():
        genre_key += 1
        genre_records.append((genre_key, genre))
    return genre_records


def actor_generator():
    actor_records = list()
    actor_key = 0

    for actor in actors.keys():
        actor_key += 1
        actor_records.append((actor_key, actor))
    return actor_records


def movie_generator(filename: str):
    with open(filename, mode='r', encoding='utf-8-sig') as csvfile:
        movie_file_reader = csv.DictReader(csvfile)
        for row in movie_file_reader:
            # Reading from csv.
            movie_rank = int(row['Rank'].strip())
            movie_title = row['Title']
            movie_description = row['Description'].strip()
            movie_director = row['Director'].strip()
            movie_year = int(row['Year'].strip())
            movie_runtime = int(row['Runtime (Minutes)'].strip())
            movie_rating = float(row['Rating'].strip()) if row['Rating'].strip() != 'N/A' else row['Rating'].strip()
            movie_votes = int(row['Votes'].strip()) if row['Votes'].strip() != 'N/A' else row['Votes'].strip()
            movie_revenue = float(row['Revenue (Millions)'].strip()) \
                if row['Revenue (Millions)'].strip() != 'N/A' else row['Revenue (Millions)'].strip()
            movie_metascore = int(row['Metascore'].strip()) \
                if row['Metascore'].strip() != 'N/A' else row['Metascore'].strip()

            # Get director id for movie.
            director_records = list()
            director_key = 0

            for director in directors.keys():
                director_key += 1
                director_records.append((director_key, director))

            director_id = 0
            for record in director_records:
                if record[1] == movie_director:
                    director_id = record[0]

            yield movie_rank, movie_title, movie_year, movie_description, director_id, movie_runtime, movie_rating, \
                movie_votes, movie_revenue, movie_metascore


def movie_actors_generator():
    movie_actors_key = 0
    actor_key = 0

    for actor in actors.keys():
        actor_key += 1
        for movie_key in actors[actor]:
            movie_actors_key += 1
            yield movie_actors_key, movie_key, actor_key


def movie_genres_generator():
    movie_genres_key = 0
    genre_key = 0

    for genre in genres.keys():
        genre_key += 1
        for movie_key in genres[genre]:
            movie_genres_key += 1
            yield movie_genres_key, movie_key, genre_key


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

    global directors, genres, actors
    directors = dict()
    genres = dict()
    actors = dict()

    csv_processor(os.path.join(data_path, 'Data1000Movies.csv'))

    insert_directors = """
        INSERT INTO directors (id, director_full_name)
        VALUES (?, ?)"""
    cursor.executemany(insert_directors, director_generator())

    insert_genres = """
        INSERT INTO genres (id, genre_name)
        VALUES (?, ?)"""
    cursor.executemany(insert_genres, genre_generator())

    insert_actors = """
        INSERT INTO actors (id, actor_full_name)
        VALUES (?, ?)"""
    cursor.executemany(insert_actors, actor_generator())

    insert_movies = """
        INSERT INTO movies (id, title, release_year, description, director_id, runtime_minutes, rating, votes, 
        revenue_in_millions, metascore)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_movies, movie_generator(os.path.join(data_path, 'Data1000Movies.csv')))

    insert_movie_actors = """
        INSERT INTO movie_actors (id, movie_id, actor_id)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_movie_actors, movie_actors_generator())

    insert_movie_genres = """
        INSERT INTO movie_genres (id, movie_id, genre_id)
        VALUES (?, ?, ?)"""
    cursor.executemany(insert_movie_genres, movie_genres_generator())

    default_review = [1, 1, 'GOTG is my new favourite movie of all time!', 10, datetime.now(), 1]
    insert_reviews = """
        INSERT INTO reviews (id, movie_id, review_text, rating, timestamp, user_id)
        VALUES (?, ?, ?, ?, ?, ?)"""
    cursor.executemany(insert_reviews, default_review)

    default_user = [1, 'nton939', generate_password_hash('nton939Password'), 121]
    insert_users = """
        INSERT INTO users (id, username, password, time_spent_watching_movies_minutes)
        VALUES (?, ?, ?, ?)"""
    cursor.executemany(insert_users, default_user)

    conn.commit()
    conn.close()
