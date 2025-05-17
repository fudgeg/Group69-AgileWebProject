
from app.models import Movie

# This test function checks if the Movie model is created correctly.
def test_movie_repr():
    movie = Movie(title="Inception", genre="Sci-Fi")
    assert "Inception" in repr(movie)
    assert "Sci-Fi" in repr(movie)
