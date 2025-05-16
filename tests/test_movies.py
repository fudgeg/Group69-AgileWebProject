
from app.models import Movie

def test_movie_repr():
    movie = Movie(title="Inception", genre="Sci-Fi")
    assert "Inception" in repr(movie)
    assert "Sci-Fi" in repr(movie)
