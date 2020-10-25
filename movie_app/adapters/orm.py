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
        '__director_full_name': directors.c.director_full_name
    })

    genre_mapper = mapper(model.Genre, genres, properties={
        '__genre_name': genres.c.genre_name
    })

    actor_mapper = mapper(model.Actor, actors, properties={
        '__actor_full_name': actors.c.actor_full_name
    })

    mapper(model.Movie, movies, properties={
        '__rank': movies.c.id,
        '__title': movies.c.title,
        '__release_year': movies.c.release_year,
        '__description': movies.c.description,
        '__runtime_minutes': movies.c.runtime_minutes,
        '__rating': movies.c.rating,
        '__votes': movies.c.votes,
        '__revenue': movies.c.revenue_in_millions,
        '__metascore': movies.c.metascore,
        '__director': relationship(model.Director, backref='_movie'),
        '__actors': relationship(actor_mapper, secondary=movie_actors, backref='_movie'),
        '__genres': relationship(genre_mapper, secondary=movie_genres, backref='_movie'),
    })

    mapper(model.Review, reviews, properties={
        '__review_text': reviews.c.review_text,
        '__rating': reviews.c.rating,
        '__timestamp': reviews.c.timestamp,
        '__movie': relationship(model.Movie, backref='_review'),
    })

    mapper(model.User, users, properties={
        '__user_name': users.c.username,
        '__password': users.c.password,
        '__time_spent_watching_movies_minutes': users.c.time_spent_watching_movies_minutes,
        '__reviews': relationship(model.Review, backref='_user')
    })
