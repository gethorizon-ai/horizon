import pytest
from app.models.component import User
from werkzeug.security import check_password_hash
from app import create_app, db


@pytest.fixture
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as test_client:
        with app.app_context():
            db.create_all()
            yield test_client
            db.session.remove()
            db.drop_all()


def test_password_hashing(test_client):
    with test_client.application.app_context():
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        assert u.check_password('cat')
        assert not u.check_password('dog')
        db.session.delete(u)
        db.session.commit()


def test_password_verification():
    hashed_password = 'sha256$abcdefghijkl$1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef'
    user = User(username='testuser', email='test@example.com',
                hashed_password=hashed_password)
    assert user.check_password('password') == check_password_hash(
        hashed_password, 'password')
    assert not user.check_password('wrongpassword')


def test_user_registration(test_client):
    response = test_client.post(
        '/api/users/register',
        json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123#',
        }
    )
    assert response.status_code == 201
    assert response.json == {
        'message': 'User registered successfully', 'user_id': 1}


def test_user_authentication(test_client):
    user = User(username='testuser', email='test@example.com')
    user.set_password('TestPass123#')
    db.session.add(user)
    db.session.commit()

    response = test_client.post(
        '/api/users/authenticate',
        json={
            'username': 'testuser',
            'password': 'TestPass123#',
        }
    )
    assert response.status_code == 200
    assert 'api_key' in response.json
    assert response.json['message'] == 'User authenticated successfully'
