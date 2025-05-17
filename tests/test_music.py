
from app.models import Music

# This test function checks if the Music model is created correctly.
def test_music_repr():
    track = Music(title="Creep", artist="Radiohead")
    assert "Creep" in repr(track)
    assert "Radiohead" in repr(track)
