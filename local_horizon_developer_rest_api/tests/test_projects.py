import json
import pytest
from app.models import Experiment, Project, Prompt, Task, User
from app import create_app, db
import os
from io import BytesIO
import tempfile
import csv
from werkzeug.datastructures import CombinedMultiDict, MultiDict
import requests
import base64


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


def test_list_projects(test_client):
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Project(name='Sample Project', user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects endpoint (GET)
        response = test_client.get(
            '/api/projects', headers={'X-Api-Key': u.api_key})

        # Check if the response is JSON before attempting to parse it
        if response.content_type == 'application/json':
            data = json.loads(response.data)
        else:
            raise ValueError(
                f"Unexpected content type: {response.content_type}, response: {response.data}")

        assert response.status_code == 200
        assert data['projects'][0]['name'] == 'Sample Project'

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_create_project(test_client):
    with test_client.application.app_context():
        # Create a sample user
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        # Test the /api/projects/create endpoint (POST)
        new_project = {
            'name': 'New Project',
            'user_id': u.id
        }

        response = test_client.post(
            '/api/projects/create', json=new_project, headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['message'] == 'Project created successfully'
        assert data['project']['name'] == 'New Project'

        # Clean up
        p = Project.query.get(u.id)
        db.session.delete(p)

        # # Test the /api/projects/create endpoint (POST) with file upload
        # new_project_with_file = {
        #     'name': 'New Project with File',
        #     'user_id': u.id
        # }
        # file_data = BytesIO(b'sample,evaluation,data\n1,2,3\n4,5,6\n')
        # file_data.seek(0)
        # base64_file_data = base64.b64encode(file_data.read()).decode()

        # new_project_with_file['evaluation_datasets'] = {
        #     'filename': 'evaluation_datasets.csv',
        #     'content_type': 'text/csv',
        #     'data': base64_file_data
        # }

        # response = test_client.post(
        #     '/api/projects/create',
        #     json=new_project_with_file,
        #     headers={'X-Api-Key': u.api_key}
        # )
        # data = json.loads(response.data)

        # assert response.status_code == 201
        # assert data['message'] == 'Project created successfully'

        # # Add tests for the get_evaluation_datasets() function
        # project_id = data['project']['id']
        # response = test_client.get(
        #     f'/api/projects/{project_id}/evaluation_datasets',
        #     headers={'X-Api-Key': u.api_key}
        # )

        # assert response.status_code == 200
        # assert response.mimetype == 'text/csv'
        # assert b'sample,evaluation,data\n1,2,3\n4,5,6\n' == response.data

        # # Clean up
        # p = Project.query.get(project_id)
        # db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_get_project(test_client):
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Project(name='Sample Project', user_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects/1 endpoint (GET)
        response = test_client.get(
            '/api/projects/1', headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['name'] == 'Sample Project'

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_update_project(test_client):
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Project(name='Sample Project', user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects/1 endpoint (PUT)
        update_data = {
            'description': 'Updated description',
            'status': 'completed',
        }

        response = test_client.put(
            f'/api/projects/{u.id}', json=update_data, headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['message'] == 'Project updated successfully'
        assert data['project']['description'] == 'Updated description'
        assert data['project']['status'] == 'completed'

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_delete_project(test_client):
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Project(name='Sample Project', user_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects/1 endpoint (DELETE)
        response = test_client.delete(
            '/api/projects/1', headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['message'] == 'Project deleted successfully'

        # Clean up
        db.session.delete(u)
        db.session.commit()


def create_csv_temp_file(rows):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    with open(temp_file.name, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return temp_file.name


def test_upload_evaluation_datasets(test_client):
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Project(name='Sample Project', user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Test the /api/projects/1/upload_evaluation_datasets endpoint (POST)
        evaluation_datasets = [
            {'field1': 'value1', 'field2': 'value2'},
            {'field1': 'value3', 'field2': 'value4'}
        ]
        temp_file_name = create_csv_temp_file(evaluation_datasets)
        with open(temp_file_name, 'rb') as f:
            response = test_client.post(
                f'/api/projects/{p.id}/upload_evaluation_datasets',
                data={'evaluation_datasets': f},
                headers={'X-Api-Key': u.api_key}
            )

        os.remove(temp_file_name)

        assert response.status_code == 200

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_view_evaluation_datasets(test_client):
    with test_client.application.app_context():
        # Create a sample user and project
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Project(name='Sample Project', user_id=u.id)
        db.session.add(p)
        db.session.commit()

        # Add evaluation datasets
        evaluation_datasets = [
            {'field1': 'value1', 'field2': 'value2'},
            {'field1': 'value3', 'field2': 'value4'}
        ]
        temp_file_name = create_csv_temp_file(evaluation_datasets)
        with open(temp_file_name, 'rb') as f:
            p.evaluation_datasets = f.read()

        db.session.commit()
        os.remove(temp_file_name)

        # Test the /api/projects/1/view_evaluation_datasets endpoint (GET)
        response = test_client.get(
            f'/api/projects/{p.id}/view_evaluation_datasets',
            headers={'X-Api-Key': u.api_key}
        )

        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['evaluation_datasets'] == evaluation_datasets

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()
