
from app.models import Music

# Test the Music model
def test_music_repr():
    track = Music(title="Creep", artist="Radiohead")
    assert "Creep" in repr(track)
    assert "Radiohead" in repr(track)
