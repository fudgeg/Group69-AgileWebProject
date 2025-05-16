
from app.models import User

def test_password_hashing():
    user = User(name="TestUser", email="test@example.com")
    user.set_password("secure123")
    assert user.check_password("secure123")
    assert not user.check_password("wrongpass")

def test_user_repr():
    user = User(name="TestUser", email="test@example.com")
    assert repr(user) == "<User test@example.com>"
