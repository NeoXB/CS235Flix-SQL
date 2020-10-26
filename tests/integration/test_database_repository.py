import pytest
from movie_app.adapters.database_repository import SqlAlchemyRepository
from movie_app.domain.model import Director, Genre, Actor, Movie, Review, User
from movie_app.adapters.repository import RepositoryException


def test_repo_can_add_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    director = Director('Barazza')
    repo.add_director(director)

    assert director == repo.get_director('Barazza')


def test_repo_can_retrieve_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    director = repo.get_director('James Gunn')
    assert director == Director('James Gunn')


def test_repo_does_not_retrieve_non_existent_director(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    director = repo.get_director('Xull')
    assert director is None


def test_repo_can_add_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre('Anime')
    repo.add_genre(genre)

    assert genre in repo.get_genres()


def test_repo_can_retrieve_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genres = repo.get_genres()

    assert len(genres) == 20


def test_repo_can_add_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    actor = Actor('Scarlet')
    repo.add_actor(actor)

    assert actor == repo.get_actor('Scarlet')


def test_repo_can_retrieve_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    actor = repo.get_actor('Vin Diesel')
    assert actor == Director('Vin Diesel')


def test_repo_does_not_retrieve_non_existent_actor(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    actor = repo.get_actor('Orion')
    assert actor is None


def test_repo_can_add_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    new_movie_id = number_of_movies + 1

    movie = Movie("WOW", 2020)
    movie.rank = new_movie_id
    movie.description = "This is the best movie in the world."
    movie.director = Director("Barraza")
    movie.runtime_minutes = 100
    movie.rating = 100
    movie.votes = 100
    movie.revenue = 100
    movie.metascore = 100
    repo.add_movie(movie)

    assert repo.get_movie(new_movie_id) == movie


def test_repo_can_retrieve_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1)

    # Check that the Movie has the expected title.
    assert movie.title == 'Guardians of the Galaxy'

    # Check that the Movie is reviewed as expected.
    user = repo.get_user('nton939')
    assert user.reviews[0].review_text == 'GOTG is my new favourite movie of all time!'

    # Check that the Movie has the expected genres.
    assert movie.genres == [Genre('Action'), Genre('Adventure'), Genre('Sci-Fi')]


def test_repo_does_not_retrieve_non_existent_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1001)
    assert movie is None


def test_repo_can_get_first_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_first_movie()
    assert movie.title == 'Guardians of the Galaxy'


def test_repo_can_get_last_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_last_movie()
    assert movie.title == 'Nine Lives'


def test_repo_can_retrieve_movie_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    # Check that the query returned 1000 Movies.
    assert number_of_movies == 1000


def test_repo_can_get_movies_by_ranks(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_rank([1, 2, 3])

    assert len(movies) == 3
    assert movies[0].title == 'Guardians of the Galaxy'
    assert movies[1].title == 'Prometheus'
    assert movies[2].title == 'Split'


def test_repo_does_not_retrieve_movie_for_non_existent_rank(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_rank([1000, 1001])

    assert len(movies) == 1
    assert movies[0].title == 'Nine Lives'


def test_repo_returns_an_empty_list_for_non_existent_ranks(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_rank([0, 1001])

    assert len(movies) == 0


def test_repo_returns_movie_ranks_for_existing_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ranks = repo.get_movie_ranks_for_genre('Action')

    assert len(movie_ranks) == 303


def test_repo_returns_an_empty_list_for_non_existent_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ranks = repo.get_movie_ranks_for_genre('Anime')

    assert len(movie_ranks) == 0


def test_repo_can_add_review(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    #user = repo.get_user('nton939')
    movie = repo.get_movie(500)
    review = Review(movie, "wow!", 10)
    #user.add_review(review)

    repo.add_review(review)

    assert review in repo.get_reviews()


def test_repo_does_not_add_review_without_a_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(0)
    review = Review(movie, "good", 7)

    with pytest.raises(RepositoryException):
        repo.add_review(review)


def test_repo_can_retrieve_reviews(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_reviews()) == 1


def test_repo_can_add_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Artemis', '123456789')
    repo.add_user(user)

    repo.add_user(User('Jaeyun', '123456789'))

    user2 = repo.get_user('Artemis')

    assert user2 == user and user2 is user


def test_repo_can_retrieve_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('nton939')
    assert user == User('nton939', 'nton939Password')


def test_repo_does_not_retrieve_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('Cross')
    assert user is None


def test_can_retrieve_movie_and_add_review_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Movie and User.
    movie = repo.get_movie(1000)
    user = repo.get_user('nton939')

    # Create a new Review, connecting it to the Movie and User.
    review = Review(movie, "So good!", 9)
    user.add_review(review)
    repo.add_review(review)

    fetched_reviews = repo.get_reviews()
    fetched_user = repo.get_user('nton939')
    fetched_movie = repo.get_movie(1000)

    assert review in fetched_reviews
    assert review in fetched_user.reviews
    assert fetched_reviews[1].movie == fetched_movie
