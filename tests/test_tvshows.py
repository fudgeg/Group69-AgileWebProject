
from app.models import TVShow

# This test function checks if the TVShow model is created correctly.
def test_tvshow_repr():
    show = TVShow(title="Dark", genre="Mystery")
    assert "Dark" in repr(show)
    assert "Mystery" in repr(show)
