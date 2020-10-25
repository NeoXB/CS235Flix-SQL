import pytest
import datetime
from sqlalchemy.exc import IntegrityError
from movie_app.domain.model import Director, Genre, Actor, Movie, Review, User


def insert_directors(empty_session):
    empty_session.execute(
        'INSERT INTO directors (director_full_name) VALUES ("Barraza"), ("Orion")'
    )
    rows = list(empty_session.execute('SELECT id from directors'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_genres(empty_session):
    empty_session.execute(
        'INSERT INTO genres (genre_name) VALUES ("Anime"), ("Gaming")'
    )
    rows = list(empty_session.execute('SELECT id from genres'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_actors(empty_session):
    empty_session.execute(
        'INSERT INTO actors (actor_full_values) VALUES ("Scarlet"), ("Xull")'
    )
    rows = list(empty_session.execute('SELECT id from actors'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_movie(empty_session):
    empty_session.execute(
        'INSERT INTO movies (id, title, release_year, description, director_id, runtime_minutes, rating, votes, '
        'revenue_in_millions, metascore) VALUES '
        '(1001, "WOW", 2020, "This is the best movie in the world.", 1, 100, 100, 100, 100, 100)'
    )
    row = empty_session.execute('SELECT id from movies').fetchone()
    return row[0]


def insert_movie_actors(empty_session, movie_key, actor_keys):
    stmt = 'INSERT INTO movie_actors (movie_id, actor_id) VALUES (:movie_id, :actor_id)'
    for actor_key in actor_keys:
        empty_session.execute(stmt, {'movie_id': movie_key, 'actor_id': actor_key})


def insert_movie_genres(empty_session, movie_key, genre_keys):
    stmt = 'INSERT INTO movie_genres (movie_id, genre_id) VALUES (:movie_id, :genre_id)'
    for genre_key in genre_keys:
        empty_session.execute(stmt, {'movie_id': movie_key, 'genre_id': genre_key})


def insert_user(empty_session, values=None):
    new_name = "Bob"
    new_password = "Thisisbob1"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (username, password, time_spent_watching_movies_minutes) '
                          'VALUES (:username, :password, 0)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where username = :username', {'username': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password, time_spent_watching_movies_minutes) '
                              'VALUES (:username, :password, 0)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_reviewed_movie(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now()
    timestamp_2 = datetime.datetime.now()

    empty_session.execute(
        'INSERT INTO reviews (movie_id, review_text, rating, timestamp, user_id) VALUES '
        '(:movie_id, "Review 1", :timestamp_1, :user_id), '
        '(:movie_id, "Review 2", :timestamp_2, :user_id)',
        {'movie_id': movie_key, 'timestamp_1': timestamp_1, 'timestamp_2': timestamp_2, 'user_id': user_key}
    )

    row = empty_session.execute('SELECT id from movies').fetchone()
    return row[0]


def make_director():
    director = Director("Barraza")
    return director


def make_genre():
    genre = Genre("Anime")
    return genre


def make_actor():
    actor = Actor("Scarlet")
    return actor


def make_movie():
    movie = Movie("WOW", 2020)
    movie.rank = 1001
    movie.description = "This is the best movie in the world."
    movie.director = Director("Barraza")
    movie.runtime_minutes = 100
    movie.rating = 100
    movie.votes = 100
    movie.revenue = 100
    movie.metascore = 100
    return movie


def make_user():
    user = User("Bob", "123")
    return user


def test_loading_of_movie(empty_session):
    insert_directors(empty_session)
    movie_key = insert_movie(empty_session)
    expected_movie = make_movie()
    fetched_movie = empty_session.query(Movie).one()

    assert expected_movie == fetched_movie
    assert movie_key == fetched_movie.id


def test_saving_of_movie(empty_session):
    insert_directors(empty_session)
    movie = make_movie()
    empty_session.add(movie)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT id, title, release_year, description, director_id, runtime_minutes, '
                                      'rating, votes, revenue_in_millions, metascore FROM movies'))
    assert rows == [(1001, "WOW", 2020, "This is the best movie in the world.", 1, 100, 100, 100, 100, 100)]


def test_loading_of_movie_actors(empty_session):
    movie_key = insert_movie(empty_session)
    actor_keys = insert_actors(empty_session)
    insert_movie_actors(empty_session, movie_key, actor_keys)

    movie = empty_session.query(Movie).get(movie_key)
    actors = [empty_session.query(Actor).get(key) for key in actor_keys]

    assert movie.actors == actors


def test_loading_of_movie_genres(empty_session):
    movie_key = insert_movie(empty_session)
    genre_keys = insert_genres(empty_session)
    insert_movie_genres(empty_session, movie_key, genre_keys)

    movie = empty_session.query(Movie).get(movie_key)
    genres = [empty_session.query(Genre).get(key) for key in genre_keys]

    assert movie.genres == genres


def test_saving_movie_actors(empty_session):
    movie = make_movie()
    actor = make_actor()

    # Establish the relationship between the Movie and the Actor.
    movie.actors = [actor]

    # Persist the Movie and Genre.
    empty_session.add(movie)
    empty_session.add(actor)
    empty_session.commit()

    # Test test_saving_of_movie() checks for insertion into the movies table.
    rows = list(empty_session.execute('SELECT id FROM movies'))
    movie_key = rows[0][0]

    # Check that the actors table has a new record.
    rows = list(empty_session.execute('SELECT id, actor_full_name FROM actors'))
    actor_key = rows[0][0]
    assert rows[0][1] == "Scarlet"

    # Check that the movie_actors table has a new record.
    rows = list(empty_session.execute('SELECT movie_id, actor_id from movie_actors'))
    movie_foreign_key = rows[0][0]
    actor_foreign_key = rows[0][1]

    assert movie_key == movie_foreign_key
    assert actor_key == actor_foreign_key


def test_saving_movie_genres(empty_session):
    movie = make_movie()
    genre = make_genre()

    # Establish the relationship between the Movie and the Genre.
    movie.genres = [genre]

    # Persist the Movie and Genre.
    empty_session.add(movie)
    empty_session.add(genre)
    empty_session.commit()

    # Test test_saving_of_movie() checks for insertion into the movies table.
    rows = list(empty_session.execute('SELECT id FROM movies'))
    movie_key = rows[0][0]

    # Check that the genres table has a new record.
    rows = list(empty_session.execute('SELECT id, genre_name FROM genres'))
    genre_key = rows[0][0]
    assert rows[0][1] == "Anime"

    # Check that the movie_genres table has a new record.
    rows = list(empty_session.execute('SELECT movie_id, genre_id from movie_genres'))
    movie_foreign_key = rows[0][0]
    genre_foreign_key = rows[0][1]

    assert movie_key == movie_foreign_key
    assert genre_key == genre_foreign_key


def test_loading_of_users(empty_session):
    users = list()
    users.append(("Bob", "Thisisbob1"))
    users.append(("Not Bob", "1234"))
    insert_users(empty_session, users)

    expected = [
        User("Bob", "Thisisbob1"),
        User("Not Bob", "123456789")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM users'))
    assert rows == [("Bob", "Thisisbob1")]


def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("Bob", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("Bob", "Thisisbob1")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_reviewed_movie(empty_session):
    insert_reviewed_movie(empty_session)
    movie = make_movie()

    rows = empty_session.query(Review).all()
    review = rows[0]

    assert review.__movie == movie
    assert review.__review_text == "Review 1"


def test_save_reviewed_movie(empty_session):
    # Create Movie and User objects.
    movie = make_movie()

    # Create a new Review.
    comment_text = "Some comment text."
    review = Review(movie, comment_text, 5)

    # Save the new Movie and Review.
    empty_session.add(movie)
    empty_session.add(review)
    empty_session.commit()

    # Test test_saving_of_movie() checks for insertion into the movies table.
    rows = list(empty_session.execute('SELECT id FROM movies'))
    movie_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM users'))
    user_key = rows[0][0]

    # Check that the reviews table has a new record that links to the movies and users tables.
    rows = list(empty_session.execute('SELECT user_id, movie_id, review_text FROM reviews'))
    assert rows == [(user_key, movie_key, comment_text)]


def test_saving_of_review(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session, ("Bob", "123"))

    rows = empty_session.query(Movie).all()
    movie = rows[0]

    # Create a new Review.
    comment_text = "Some comment text."
    review = Review(movie, comment_text, 5)

    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, movie_id, review_text FROM reviews'))
    assert rows == [(user_key, movie_key, comment_text)]
