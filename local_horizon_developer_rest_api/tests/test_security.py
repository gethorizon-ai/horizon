"""Test security of different methods."""

import pytest
import json
from app.models.component import Task, User, Project
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


def test_login_with_wrong_password(test_client):
    """Test ability of user to authenticate with wrong password."""
    with test_client.application.app_context():
        # Create sample user
        u = User(email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        # Try generating an API key with the right password. Should succeed
        correct_response = test_client.post(
            "/api/users/generate_new_api_key",
            json={
                "email": u.email,
                "password": "cat",
            },
        )
        assert correct_response.status_code in [200, 201]

        # Try generating an API key with wrong password. Should fail
        incorrect_response = test_client.post(
            "/api/users/generate_new_api_key",
            json={
                "email": u.email,
                "password": "wrong_password",
            },
        )
        assert incorrect_response.status_code not in [200, 201]

        # Clean up
        db.session.delete(u)
        db.session.commit()


def test_get_data_with_different_api_key(test_client):
    """Test ability of user to access another user's data with their own Horizon API key.

    In other words, this checks that a user cannot provide a valid Horizon API key and access data that is associated with a
    different Horizon API key."""
    with test_client.application.app_context():
        # Create two sample users
        u_1 = User(email="john@example.com", password="cat")
        u_1_api_key = u_1.generate_new_api_key()
        db.session.add(u_1)
        db.session.commit()

        u_2 = User(email="tom@example.com", password="dog")
        u_2_api_key = u_2.generate_new_api_key()
        db.session.add(u_2)
        db.session.commit()

        # Create project for each user
        p_1 = Project(name="Sample Project", user_id=u_1.id)
        db.session.add(p_1)
        db.session.commit()

        p_2 = Project(name="Sample Project", user_id=u_2.id)
        db.session.add(p_2)
        db.session.commit()

        # Create task for each user
        task_data_1 = {
            "name": "New Task 1",
            "task_type": "development",
            "project_id": p_1.id,
        }
        create_task_response_1 = test_client.post(
            "/api/tasks/create", json=task_data_1, headers={"X-Api-Key": u_1_api_key}
        )
        task_data_2 = {
            "name": "New Task 2",
            "task_type": "development",
            "project_id": p_2.id,
        }
        create_task_response_2 = test_client.post(
            "/api/tasks/create", json=task_data_2, headers={"X-Api-Key": u_2_api_key}
        )
        assert create_task_response_1.status_code == 201
        assert create_task_response_2.status_code == 201
        data = json.loads(create_task_response_2.data)
        task_id_2 = data["task"]["id"]

        # Try to get task from user 2 using Horizon API key from user 1. Should fail
        get_task_response = test_client.get(
            f"/api/tasks/{task_id_2}", headers={"X-Api-Key": u_1_api_key}
        )
        assert get_task_response.status_code not in [200, 201]

        # Clean up
        task1 = Task.query.filter_by(name="New Task 1").first()
        task2 = Task.query.filter_by(name="New Task 2").first()
        db.session.delete(task1)
        db.session.delete(task2)
        db.session.delete(p_1)
        db.session.delete(p_2)
        db.session.delete(u_1)
        db.session.delete(u_2)
        db.session.commit()
