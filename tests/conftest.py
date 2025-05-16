# tests/conftest.py
import os
import sys
import pytest

# Ensure the project root is on sys.path so `import app` works
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from app.models import db

@pytest.fixture
def app():
    # Create your Flask app without any unexpected kwargs
    app = create_app()

    # Override config for testing
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        # If you use Flask-WTF CSRF, you might disable it for tests:
        "WTF_CSRF_ENABLED": False,
    })

    # Create & tear down the in-memory database around each test
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
