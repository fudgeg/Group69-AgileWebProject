
from app.models import User


# This test file checks if the User model is created correctly.


# This test functions checks if password hashing works as expected.
def test_password_hashing():
    user = User(name="TestUser", email="test@example.com")
    user.set_password("secure123")
    assert user.check_password("secure123")
    assert not user.check_password("wrongpass")
    
# This test functions checks if user creation works as expected.
def test_user_repr():
    user = User(name="TestUser", email="test@example.com")
    assert repr(user) == "<User test@example.com>"
