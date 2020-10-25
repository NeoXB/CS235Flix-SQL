from sqlalchemy import Table, MetaData, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import mapper, relationship
from movie_app.domain import model

metadata = MetaData()

directors = Table(
    'directors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('director_full_name', String(255), nullable=False)
)

genres = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('genre_name', String(255), nullable=False)
)

actors = Table(
    'actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('actor_full_name', String(255), nullable=False),
)

movies = Table(
    'movies', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('release_year', Integer, nullable=False),
    Column('description', String(1024), nullable=False),
    Column('director_id', ForeignKey('directors.id')),
    Column('runtime_minutes', Integer, nullable=False),
    Column('rating', Float),
    Column('votes', Integer),
    Column('revenue_in_millions', Float),
    Column('metascore', Integer)
)

movie_actors = Table(
    'movie_actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('actor_id', ForeignKey('actors.id'))
)

movie_genres = Table(
    'movie_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('genre_id', ForeignKey('genres.id'))
)

reviews = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('review_text', String(1024), nullable=False),
    Column('rating', Integer, nullable=False),
    Column('timestamp', DateTime, nullable=False),
    Column('user_id', ForeignKey('users.id'))
)

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False),
    Column('time_spent_watching_movies_minutes', Integer, nullable=False)
)


def map_model_to_tables():
    mapper(model.Director, directors, properties={
        '_Director__director_full_name': directors.c.director_full_name
    })

    genre_mapper = mapper(model.Genre, genres, properties={
        '_Genre__genre_name': genres.c.genre_name
    })

    actor_mapper = mapper(model.Actor, actors, properties={
        '_Actor__actor_full_name': actors.c.actor_full_name
    })

    mapper(model.Movie, movies, properties={
        '_Movie__rank': movies.c.id,
        '_Movie__title': movies.c.title,
        '_Movie__release_year': movies.c.release_year,
        '_Movie__description': movies.c.description,
        '_Movie__runtime_minutes': movies.c.runtime_minutes,
        '_Movie__rating': movies.c.rating,
        '_Movie__votes': movies.c.votes,
        '_Movie__revenue': movies.c.revenue_in_millions,
        '_Movie__metascore': movies.c.metascore,
        '_Movie__director': relationship(model.Director, backref='_movie'),
        '_Movie__actors': relationship(actor_mapper, secondary=movie_actors, backref='_movie'),
        '_Movie__genres': relationship(genre_mapper, secondary=movie_genres, backref='_movie'),
    })

    mapper(model.Review, reviews, properties={
        '_Review__review_text': reviews.c.review_text,
        '_Review__rating': reviews.c.rating,
        '_Review__timestamp': reviews.c.timestamp,
        '_Review__movie': relationship(model.Movie, backref='_review'),
    })

    mapper(model.User, users, properties={
        '_User__user_name': users.c.username,
        '_User__password': users.c.password,
        '_User__time_spent_watching_movies_minutes': users.c.time_spent_watching_movies_minutes,
        '_User__reviews': relationship(model.Review, backref='_user')
    })
