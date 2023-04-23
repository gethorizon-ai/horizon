"""Test API methods related to project object."""

import json
import pytest
from app.models.component import Project, User
from app import create_app, db
from werkzeug.datastructures import CombinedMultiDict, MultiDict


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


def test_list_projects(test_client):
    """Test API method to list projects."""
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects endpoint (GET)
        response = test_client.get("/api/projects", headers={"X-Api-Key": api_key})

        # Check if the response is JSON before attempting to parse it
        if response.content_type == "application/json":
            data = json.loads(response.data)
        else:
            raise ValueError(
                f"Unexpected content type: {response.content_type}, response: {response.data}"
            )

        assert response.status_code == 200
        assert data["projects"][0]["name"] == "Sample Project"

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_create_project(test_client):
    """Test API method to create project."""
    with test_client.application.app_context():
        # Create a sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Test the /api/projects/create endpoint (POST)
        new_project = {"name": "New Project", "user_id": u.id}

        response = test_client.post(
            "/api/projects/create", json=new_project, headers={"X-Api-Key": api_key}
        )
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data["message"] == "Project created successfully"
        assert data["project"]["name"] == "New Project"

        # Clean up
        p = Project.query.get(u.id)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_get_project(test_client):
    """Test API method to get project."""
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        p = Project(name="Sample Project", user_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects/1 endpoint (GET)
        response = test_client.get("/api/projects/1", headers={"X-Api-Key": api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["name"] == "Sample Project"

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_update_project(test_client):
    """Test API method to update project."""
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects/1 endpoint (PUT)
        update_data = {
            "description": "Updated description",
            "status": "completed",
        }

        response = test_client.put(
            f"/api/projects/{u.id}", json=update_data, headers={"X-Api-Key": api_key}
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["message"] == "Project updated successfully"
        assert data["project"]["description"] == "Updated description"
        assert data["project"]["status"] == "completed"

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_delete_project(test_client):
    """Test API method to delete project."""
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        p = Project(name="Sample Project", user_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects/1 endpoint (DELETE)
        response = test_client.delete("/api/projects/1", headers={"X-Api-Key": api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["message"] == "Project deleted successfully"

        # Clean up
        db.session.delete(u)
        db.session.commit()
