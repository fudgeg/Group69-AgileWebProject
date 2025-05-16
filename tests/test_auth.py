import pytest
from app.models import db, User

def test_duplicate_signup_fails(client):
    # 1) First signup — should succeed
    r1 = client.post(
        "/signup",
        data={
            "full_name": "Alice",
            "email": "alice@example.com",
            "password": "test123",
            "confirm_password": "test123",
        },
        follow_redirects=True,
    )
    # After successful signup your code flashes "...Please log in"
    assert b"Please log in" in r1.data

    # 2) Second signup with same email — should show caution
    r2 = client.post(
        "/signup",
        data={
            "full_name": "Alice 2",
            "email": "alice@example.com",  # duplicate
            "password": "anotherpass",
            "confirm_password": "anotherpass",
        },
        follow_redirects=True,
    )
    assert b"Email already registered" in r2.data

