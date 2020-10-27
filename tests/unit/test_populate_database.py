from sqlalchemy import select, inspect
from movie_app.adapters.orm import metadata


def test_database_populate_inspect_table_names(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['actors', 'directors', 'genres', 'movie_actors', 'movie_genres', 'movies',
                                           'reviews', 'user_watched_movies', 'users']


def test_database_populate_select_all_directors(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_directors_table = inspector.get_table_names()[1]

    with database_engine.connect() as connection:
        # query for records in table directors
        select_statement = select([metadata.tables[name_of_directors_table]])
        result = connection.execute(select_statement)

        all_directors = []
        for row in result:
            all_directors.append(row['director_full_name'])

        assert 'James Gunn' in all_directors
        assert 'Barry Sonnenfeld' in all_directors
        assert len(all_directors) == 644


def test_database_populate_select_all_genres(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_genres_table = inspector.get_table_names()[2]

    with database_engine.connect() as connection:
        # query for records in table genres
        select_statement = select([metadata.tables[name_of_genres_table]])
        result = connection.execute(select_statement)

        all_genre_names = []
        for row in result:
            all_genre_names.append(row['genre_name'])

        assert len(all_genre_names) == 20
        assert all_genre_names == ['Action', 'Adventure', 'Sci-Fi', 'Mystery', 'Horror', 'Thriller', 'Animation',
                                   'Comedy', 'Family', 'Fantasy', 'Drama', 'Music', 'Biography', 'Romance', 'History',
                                   'Crime', 'Western', 'War', 'Musical', 'Sport']


def test_database_populate_select_all_actors(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_actors_table = inspector.get_table_names()[0]

    with database_engine.connect() as connection:
        # query for records in table actors
        select_statement = select([metadata.tables[name_of_actors_table]])
        result = connection.execute(select_statement)

        all_actors = []
        for row in result:
            all_actors.append(row['actor_full_name'])

        assert 'Chris Pratt' in all_actors
        assert 'Vin Diesel' in all_actors
        assert 'Bradley Cooper' in all_actors
        assert len(all_actors) == 1985


def test_database_populate_select_all_movies(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_table = inspector.get_table_names()[5]

    with database_engine.connect() as connection:
        # query for records in table movies
        select_statement = select([metadata.tables[name_of_movies_table]])
        result = connection.execute(select_statement)

        all_movies = []
        for row in result:
            all_movies.append((row['id'], row['title'], row['release_year']))

        assert all_movies[0] == (1, 'Guardians of the Galaxy', 2014)
        assert all_movies[499] == (500, 'Up', 2009)
        assert all_movies[999] == (1000, 'Nine Lives', 2016)
        assert len(all_movies) == 1000


def test_database_populate_select_all_reviews(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_reviews_table = inspector.get_table_names()[6]

    with database_engine.connect() as connection:
        # query for records in table reviews
        select_statement = select([metadata.tables[name_of_reviews_table]])
        result = connection.execute(select_statement)

        all_reviews = []
        for row in result:
            all_reviews.append((row['id'], row['movie_id'], row['review_text'], row['rating'], row['user_id']))

        assert all_reviews == [(1, 1, 'GOTG is my new favourite movie of all time!', 10, 1)]


def test_database_populate_select_all_users(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[8]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['username'])

        assert all_users == ['nton939']
