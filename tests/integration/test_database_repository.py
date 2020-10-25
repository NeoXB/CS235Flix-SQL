from datetime import date, datetime
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

# Continue here
def test_repo_can_get_first_movie(in_memory_repo):
    movie = in_memory_repo.get_first_movie()
    assert movie.title == 'Guardians of the Galaxy'


def test_repo_can_get_last_movie(in_memory_repo):
    movie = in_memory_repo.get_last_movie()
    assert movie.title == 'Nine Lives'


def test_repo_can_retrieve_movie_count(in_memory_repo):
    no_of_movies = in_memory_repo.get_number_of_movies()
    assert no_of_movies == 1000


def test_repo_can_get_movies_by_ranks(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([1, 2, 3])
    assert len(movies) == 3
    assert movies[0].title == 'Guardians of the Galaxy'
    assert movies[1].title == 'Prometheus'
    assert movies[2].title == 'Split'


def test_repo_does_not_retrieve_movie_for_non_existent_rank(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([1000, 1001])
    assert len(movies) == 1
    assert movies[0].title == 'Nine Lives'


def test_repo_returns_an_empty_list_for_non_existent_ranks(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([1111, 2222])
    assert len(movies) == 0


def test_repo_returns_movie_ranks_for_existing_genre(in_memory_repo):
    movie_ranks = in_memory_repo.get_movie_ranks_for_genre('Action')
    assert len(movie_ranks) == 303


def test_repo_returns_an_empty_list_for_non_existent_genre(in_memory_repo):
    movie_ranks = in_memory_repo.get_movie_ranks_for_genre('Anime')
    assert len(movie_ranks) == 0


def test_repo_can_add_review(in_memory_repo):
    movie = in_memory_repo.get_movie(10)
    review = Review(movie=movie, txt='It was average.', rating=5)
    in_memory_repo.add_review(review)
    assert review in in_memory_repo.get_reviews()


def test_repo_does_not_add_review_without_a_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(2000)
    review = Review(movie=movie, txt='Wow! Such a cool movie!', rating=10)
    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repo_can_retrieve_reviews(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 1


def test_repo_can_add_user(in_memory_repo):
    user = User('person', '123456789')
    in_memory_repo.add_user(user)
    assert in_memory_repo.get_user('person') == user


def test_repo_can_retrieve_user(in_memory_repo):
    user = in_memory_repo.get_user('nton939')
    assert user == User('nton939', 'nton939Password')


def test_repo_does_not_retrieve_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('bob')
    assert user is None


def test_repo_can_add_watchlist(in_memory_repo):
    movies = in_memory_repo.get_movies_by_rank([1, 500, 1000])
    user = in_memory_repo.get_user('nton939')
    watchlist = WatchList(user, 'want to watch')
    for movie in movies:
        watchlist.add_movie(movie)
    in_memory_repo.add_watchlist(watchlist)
    assert len(in_memory_repo.get_watchlist(user)) == 2


def test_repo_can_retrieve_watchlist(in_memory_repo):
    user = in_memory_repo.get_user('nton939')
    watchlist = in_memory_repo.get_watchlist(user)
    assert len(watchlist) == 1


def test_repo_does_not_retrieve_non_existent_watchlist(in_memory_repo):
    user = in_memory_repo.get_user('abc')
    watchlist = in_memory_repo.get_watchlist(user)
    assert len(watchlist) == 0



def make_article(new_article_date):
    article = Article(
        new_article_date,
        'Coronavirus travel restrictions: Self-isolation deadline pushed back to give airlines breathing room',
        'The self-isolation deadline has been pushed back',
        'https://www.nzherald.co.nz/business/news/article.cfm?c_id=3&objectid=12316800',
        'https://th.bing.com/th/id/OIP.0lCxLKfDnOyswQCF9rcv7AHaCz?w=344&h=132&c=7&o=5&pid=1.7'
    )
    return article

def test_can_retrieve_an_article_and_add_a_comment_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Article and User.
    article = repo.get_article(5)
    author = repo.get_user('thorke')

    # Create a new Comment, connecting it to the Article and User.
    comment = make_comment('First death in Australia', author, article)

    article_fetched = repo.get_article(5)
    author_fetched = repo.get_user('thorke')

    assert comment in article_fetched.comments
    assert comment in author_fetched.comments

