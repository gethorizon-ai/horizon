"""Test API methods related to user object."""

import pytest
from app.models.component import User
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app, db


@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()
            yield test_client
            db.session.remove()
            db.drop_all()


def test_password_hashing(test_client):
    """Test hashing of user password."""
    with test_client.application.app_context():
        u = User(email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()
        assert u.check_password("cat")
        assert not u.check_password("dog")
        db.session.delete(u)
        db.session.commit()


def test_password_verification():
    """Test verification of user password."""
    password = "cat"
    hashed_password = generate_password_hash(password)
    user = User(email="test@example.com", password=password)
    assert user.check_password(password) == check_password_hash(
        hashed_password, password
    )
    assert not user.check_password("wrongpassword")


def test_user_registration(test_client):
    """Test user registration."""
    response = test_client.post(
        "/api/users/register",
        json={
            "email": "test@example.com",
            "password": "TestPass123#",
        },
    )
    assert response.status_code == 201
    assert response.json == {"message": "User registered successfully", "user_id": 1}


def test_generate_new_api_key(test_client):
    """Test generation of new API key."""
    user = User(email="test@example.com", password="TestPass123#")
    db.session.add(user)
    db.session.commit()

    response = test_client.post(
        "/api/users/generate_new_api_key",
        json={
            "email": user.email,
            "password": "TestPass123#",
        },
    )
    assert response.status_code == 200
    assert "api_key" in response.json
    assert (
        response.json["message"]
        == "API key generated successfully. Please store this securely as it cannot be retrieved. If lost, a new API key will need to be generated."
    )
