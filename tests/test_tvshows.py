
from app.models import TVShow

def test_tvshow_repr():
    show = TVShow(title="Dark", genre="Mystery")
    assert "Dark" in repr(show)
    assert "Mystery" in repr(show)
