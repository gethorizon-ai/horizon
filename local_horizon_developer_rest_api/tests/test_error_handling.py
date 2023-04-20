"""Test security of different methods."""

import pytest
import json
from app.models.component import Task, User, Prompt, Project
from app import create_app, db
import shutil
import os
from pathlib import Path


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


def test_invalid_horizon_api_key(test_client):
    """Test error handling when user provides invalid Horizon API key."""
    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        # Use the create task API
        task_data = {"name": "New Task", "task_type": "development", "project_id": 1}
        create_task_response = test_client.post(
            "/api/tasks/create", json=task_data, headers={"X-Api-Key": u.api_key}
        )

        # Try to get the task using the wrong Horizon API key. Should fail
        get_task_response = test_client.get(
            "/api/tasks/1", headers={"X-Api-Key": "wrong_api_key"}
        )

        # Check that request failed
        assert get_task_response.status_code not in [200, 201]

        # Clean up
        task = Task.query.filter_by(name="New Task").first()
        db.session.delete(task)
        db.session.delete(u)
        db.session.commit()


def test_invalid_openai_api_key(test_client):
    """Test error handling when user provides invalid OpenAI API key."""
    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        t = Task(name="Sample Task", task_type="testing", project_id=1)
        db.session.add(t)
        db.session.commit()

        # Create example prompt to attach to task
        p = Prompt(name="Test", task_id=t.id)
        p.model_name = "gpt-3.5-turbo"
        model_params = {
            "model_name": "gpt-3.5-turbo",
            "temperature": 0.5,
            "max_tokens": 500,
        }
        p.model = json.dumps(model_params)
        p.template_type = "prompt"
        serialized_test_prompt_object = {
            "template": "This is a test prompt with one variable: {var_input}",
            "input_variables": ["var_input"],
        }
        p.template_data = json.dumps(serialized_test_prompt_object)
        db.session.add(p)
        db.session.commit()

        t.active_prompt_id = p.id
        db.session.add(t)
        db.session.commit()

        # Try to deploy task with wrong OpenAI API key. Should fail
        headers = {"Content-Type": "application/json", "X-Api-Key": u.api_key}
        payload = {
            "task_id": t.id,
            "inputs": {
                "input": "test"
            },  # Program prepends "var_" to input variable name
            "openai_api_key": "wrong_openai_api_key",
        }
        response = test_client.post("/api/tasks/deploy", json=payload, headers=headers)
        assert response.status_code not in [200, 201]

        # Clean up
        db.session.delete(p)
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_invalid_evaluation_dataset_file_type(test_client):
    """Test that error is raised when trying to upload evaluation dataset with invalid file type."""

    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        t = Task(name="Sample Task", task_type="testing", project_id=1)
        db.session.add(t)
        db.session.commit()

        # Try to upload a nonexistent evaluation dataset. Should fail
        with open("./test_data/samples.jsonl", "rb") as f:
            response = test_client.post(
                f"/api/tasks/{t.id}/upload_evaluation_dataset",
                data={"evaluation_dataset": f},
                headers={"X-Api-Key": u.api_key},
            )

        assert response.status_code not in [200, 201]

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_invalid_evaluation_dataset_file_type(test_client):
    """Test that error is raised when trying to upload evaluation dataset with invalid file type."""
    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        t = Task(name="Sample Task", task_type="testing", project_id=1)
        db.session.add(t)
        db.session.commit()

        # Try to upload a nonexistent evaluation dataset. Should fail
        path = str(Path(__file__).parent) + "/test_data/samples.jsonl"
        with open(path, "rb") as f:
            response = test_client.post(
                f"/api/tasks/{t.id}/upload_evaluation_dataset",
                data={"evaluation_dataset": f},
                headers={"X-Api-Key": u.api_key},
            )

        assert response.status_code not in [200, 201]

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_invalid_evaluation_dataset_num_rows(test_client):
    """Test that error is raised when trying to upload evaluation dataset with <15 rows."""
    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        t = Task(name="Sample Task", task_type="testing", project_id=1)
        db.session.add(t)
        db.session.commit()

        # Try to upload a nonexistent evaluation dataset. Should fail
        original_path = str(Path(__file__).parent) + "/test_data/data_too_few_rows.csv"
        copied_path = (
            str(Path(__file__).parent) + "/test_data/data_too_few_rows_copy.csv"
        )

        # First, copy the file since it will be deleted upon failure
        shutil.copyfile(src=original_path, dst=copied_path)

        with open(original_path, "rb") as f:
            response = test_client.post(
                f"/api/tasks/{t.id}/upload_evaluation_dataset",
                data={"evaluation_dataset": f},
                headers={"X-Api-Key": u.api_key},
            )
        assert response.status_code not in [200, 201]

        # Rename copied file to original file
        os.rename(src=copied_path, dst=original_path)

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_invalid_evaluation_dataset_header_names(test_client):
    """Test that error is raised when trying to upload evaluation dataset with invalid header names."""
    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        t = Task(name="Sample Task", task_type="testing", project_id=1)
        db.session.add(t)
        db.session.commit()

        # Try to upload a nonexistent evaluation dataset. Should fail
        original_path = (
            str(Path(__file__).parent) + "/test_data/data_invalid_header_names.csv"
        )
        copied_path = (
            str(Path(__file__).parent) + "/test_data/data_invalid_header_names_copy.csv"
        )

        # First, copy the file since it will be deleted upon failure
        shutil.copyfile(src=original_path, dst=copied_path)

        with open(original_path, "rb") as f:
            response = test_client.post(
                f"/api/tasks/{t.id}/upload_evaluation_dataset",
                data={"evaluation_dataset": f},
                headers={"X-Api-Key": u.api_key},
            )
        assert response.status_code not in [200, 201]

        # Rename copied file to original file
        os.rename(src=copied_path, dst=original_path)

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_invalid_evaluation_dataset_token_length(test_client):
    """Test that error is raised when trying to upload evaluation dataset with values that exceed llm token length"""
    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        t = Task(name="Sample Task", task_type="testing", project_id=1)
        db.session.add(t)
        db.session.commit()

        # Try to upload a nonexistent evaluation dataset. Should fail
        original_path = (
            str(Path(__file__).parent) + "/test_data/data_too_many_tokens.csv"
        )
        copied_path = (
            str(Path(__file__).parent) + "/test_data/data_too_many_tokens_copy.csv"
        )

        # First, copy the file since it will be deleted upon failure
        shutil.copyfile(src=original_path, dst=copied_path)

        with open(original_path, "rb") as f:
            response = test_client.post(
                f"/api/tasks/{t.id}/upload_evaluation_dataset",
                data={"evaluation_dataset": f},
                headers={"X-Api-Key": u.api_key},
            )
        assert response.status_code not in [200, 201]

        # Rename copied file to original file
        os.rename(src=copied_path, dst=original_path)

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_invalid_task_id(test_client):
    """Test that error is raised when trying to access task with invalid id."""
    with test_client.application.app_context():
        # Create sample user and task
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        # Use the create task API
        task_data = {"name": "New Task", "task_type": "development", "project_id": 1}
        create_task_response = test_client.post(
            "/api/tasks/create", json=task_data, headers={"X-Api-Key": u.api_key}
        )

        # Try to get the task using the wrong Horizon task id. Should fail
        get_task_response = test_client.get(
            "/api/tasks/0", headers={"X-Api-Key": u.api_key}
        )

        # Check that request failed
        assert get_task_response.status_code not in [200, 201]

        # Clean up
        task = Task.query.filter_by(name="New Task").first()
        db.session.delete(task)
        db.session.delete(u)
        db.session.commit()


def test_invalid_project_id(test_client):
    """Test that error is raised when trying to access project with invalid id."""
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username="john", email="john@example.com", password="cat")
        db.session.add(u)
        db.session.commit()

        p = Project(name="Sample Project", user_id=1)
        db.session.add(p)
        db.session.commit()

        # Try to get the project using the wrong id. Should fail
        response = test_client.get("/api/projects/0", headers={"X-Api-Key": u.api_key})

        # Check that request failed
        assert response.status_code not in [200, 201]

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()
