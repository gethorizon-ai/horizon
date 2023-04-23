"""Test API methods related to Task object."""

import pytest
import json
from app.models.component import Task, User, Project
from app import create_app, db
import tempfile
import csv
import os


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


def test_task_creation(test_client):
    """Test API method for task creation."""
    with test_client.application.app_context():
        # Create sample user
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        # Create sample project
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Create new task
        t = Task(name="Sample Task", task_type="testing", project_id=p.id)
        db.session.add(t)
        db.session.commit()

        # Check if the task is in the database
        task = Task.query.filter_by(name="Sample Task").first()
        assert task is not None

        # Clean up
        db.session.delete(t)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_get_tasks(test_client):
    """Test API method to get tasks."""
    with test_client.application.app_context():
        # Create sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Create sample project
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Create sample task
        t = Task(name="Sample Task", task_type="testing", project_id=p.id)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks endpoint (GET)
        response = test_client.get("/api/tasks", headers={"X-Api-Key": api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["name"] == "Sample Task"

        # Clean up
        db.session.delete(t)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_create_task(test_client):
    """Test API method to create task."""
    with test_client.application.app_context():
        # Create sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Create sample project for user
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Test the /api/tasks/create endpoint (POST)
        task_data = {"name": "New Task", "task_type": "development", "project_id": p.id}

        response = test_client.post(
            "/api/tasks/create", json=task_data, headers={"X-Api-Key": api_key}
        )
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data["message"] == "Task created successfully"
        assert data["task"]["name"] == "New Task"

        # Clean up
        task = Task.query.filter_by(name="New Task").first()
        db.session.delete(task)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_get_task(test_client):
    """Test API method to get task."""
    with test_client.application.app_context():
        # Create sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Create sample project
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Create sample task
        t = Task(name="Sample Task", task_type="testing", project_id=p.id)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks/1 endpoint (GET)
        response = test_client.get("/api/tasks/1", headers={"X-Api-Key": api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["task"]["name"] == "Sample Task"

        # Clean up
        db.session.delete(t)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_update_task(test_client):
    """Test API method to update task."""
    with test_client.application.app_context():
        # Create a sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Create sample project
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        t = Task(name="Sample Task", task_type="testing", project_id=p.id)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks/1 endpoint (PUT)
        update_data = {
            "objective": "Updated objective",
            "task_type": "development",
            "status": "completed",
        }

        response = test_client.put(
            "/api/tasks/1", json=update_data, headers={"X-Api-Key": api_key}
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["message"] == "Task updated successfully"
        assert data["task"]["objective"] == "Updated objective"

        # Clean up
        db.session.delete(t)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_delete_task(test_client):
    """Test API method to delete task."""
    with test_client.application.app_context():
        # Create sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Create sample project
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Create sample task
        t = Task(name="Sample Task", task_type="testing", project_id=p.id)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks/1 endpoint (DELETE)
        response = test_client.delete("/api/tasks/1", headers={"X-Api-Key": api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["message"] == "Task deleted successfully"

        # Check if the task is removed from the database
        task = Task.query.get(1)
        assert task is None

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_upload_evaluation_datasets(test_client):
    """Test API method to upload evaluation dataset."""
    with test_client.application.app_context():
        # Create sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Create sample project
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Create sample task
        t = Task(name="Sample Task", task_type="testing", project_id=p.id)
        db.session.add(t)
        db.session.commit()

        # Test the /api/projects/1/upload_evaluation_datasets endpoint (POST)
        evaluation_dataset = [
            {"field1": "value1", "field2": "value2"} for i in range(15)
        ]
        temp_file_name = create_csv_temp_file(evaluation_dataset)
        with open(temp_file_name, "rb") as f:
            response = test_client.post(
                f"/api/tasks/{t.id}/upload_evaluation_dataset",
                data={"evaluation_dataset": f},
                headers={"X-Api-Key": api_key},
            )

        os.remove(temp_file_name)
        assert response.status_code == 200

        # Clean up
        db.session.delete(t)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_view_evaluation_datasets(test_client):
    """Test API method to view evaluation datasets."""
    with test_client.application.app_context():
        # Create sample user
        u = User(username="john", email="john@example.com", password="cat")
        api_key = u.generate_new_api_key()
        db.session.add(u)
        db.session.commit()

        # Create sample project
        p = Project(name="Sample Project", user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Create sample task
        t = Task(name="Sample Task", task_type="testing", project_id=p.id)
        db.session.add(t)
        db.session.commit()

        # Add evaluation datasets
        evaluation_dataset = [
            {"field1": "value1", "field2": "value2"} for i in range(15)
        ]
        temp_file_name = create_csv_temp_file(evaluation_dataset)
        t.evaluation_dataset = temp_file_name
        db.session.commit()

        # Test the /api/projects/1/view_evaluation_datasets endpoint (GET)
        response = test_client.get(
            f"/api/tasks/{t.id}/view_evaluation_dataset",
            headers={"X-Api-Key": api_key},
        )
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data["evaluation_dataset"] == evaluation_dataset

        # Clean up
        os.remove(temp_file_name)
        db.session.delete(t)
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def create_csv_temp_file(rows):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    with open(temp_file.name, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return temp_file.name
