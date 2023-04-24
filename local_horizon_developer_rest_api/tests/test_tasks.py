import pytest
import json
from app.models.component import Task, User
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


def test_task_creation(test_client):
    with test_client.application.app_context():
        # Create a sample user to associate the task with
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        # Create a new task
        file_path = "/Users/linatawfik/Documents/email_gen_demo.csv"
        t = Task(name='Sample Task', task_type='testing',
                 project_id=1, evaluation_dataset=file_path)
        db.session.add(t)
        db.session.commit()

        # Check if the task is in the database
        task = Task.query.filter_by(name='Sample Task').first()
        assert task is not None

        # Clean up
        db.session.delete(task)
        db.session.delete(u)
        db.session.commit()


def test_get_tasks(test_client):
    with test_client.application.app_context():
        # Create a sample user and task
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        t = Task(name='Sample Task', task_type='testing', project_id=1)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks endpoint (GET)
        response = test_client.get(
            '/api/tasks', headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert len(data['tasks']) == 1
        assert data['tasks'][0]['name'] == 'Sample Task'
        assert data['tasks'][0]['task_type'] == 'testing'

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_create_task(test_client):
    with test_client.application.app_context():
        # Create a sample user and task
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        # Test the /api/tasks/create endpoint (POST)
        task_data = {
            'name': 'New Task',
            'task_type': 'development',
            'project_id': 1
        }

        response = test_client.post(
            '/api/tasks/create', json=task_data, headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['message'] == 'Task created successfully'
        assert data['task']['name'] == 'New Task'
        assert data['task']['task_type'] == 'development'

        # Clean up
        task = Task.query.filter_by(name='New Task').first()
        db.session.delete(task)
        db.session.delete(u)
        db.session.commit()


def test_get_task(test_client):
    with test_client.application.app_context():
        # Create a sample user and task
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        t = Task(name='Sample Task', task_type='testing', project_id=1)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks/1 endpoint (GET)
        response = test_client.get(
            '/api/tasks/1', headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['name'] == 'Sample Task'
        assert data['task_type'] == 'testing'

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_update_task(test_client):
    with test_client.application.app_context():
        # Create a sample user and task
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        file_path = "/Users/linatawfik/Documents/email_gen_demo.csv"
        t = Task(name='Sample Task', task_type='testing',
                 project_id=1, evaluation_dataset=file_path)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks/1 endpoint (PUT)
        update_data = {
            'description': 'Updated description',
            'task_type': 'development',
            'status': 'completed'
        }

        response = test_client.put(
            '/api/tasks/1', json=update_data, headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['message'] == 'Task updated successfully'
        assert data['task']['description'] == 'Updated description'
        assert data['task']['task_type'] == 'development'
        assert data['task']['status'] == 'completed'

        # Clean up
        db.session.delete(t)
        db.session.delete(u)
        db.session.commit()


def test_delete_task(test_client):
    with test_client.application.app_context():
        # Create a sample user and task
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        t = Task(name='Sample Task', task_type='testing', project_id=1)
        db.session.add(t)
        db.session.commit()

        # Test the /api/tasks/1 endpoint (DELETE)
        response = test_client.delete(
            '/api/tasks/1', headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['message'] == 'Task deleted successfully'

        # Check if the task is removed from the database
        task = Task.query.get(1)
        assert task is None

        # Clean up
        db.session.delete(u)
        db.session.commit()

# def test_upload_evaluation_datasets(test_client):
#     with test_client.application.app_context():
#         # Create a sample user and project
#         u = User(username='john', email='john@example.com', password='cat')
#         db.session.add(u)
#         db.session.commit()

#         p = Project(name='Sample Project', user_id=u.id)
#         db.session.add(p)
#         db.session.commit()

#         # Test the /api/projects/1/upload_evaluation_datasets endpoint (POST)
#         evaluation_datasets = [
#             {'field1': 'value1', 'field2': 'value2'},
#             {'field1': 'value3', 'field2': 'value4'}
#         ]
#         temp_file_name = create_csv_temp_file(evaluation_datasets)
#         with open(temp_file_name, 'rb') as f:
#             response = test_client.post(
#                 f'/api/projects/{p.id}/upload_evaluation_datasets',
#                 data={'evaluation_datasets': f},
#                 headers={'X-Api-Key': u.api_key}
#             )

#         os.remove(temp_file_name)

#         assert response.status_code == 200

#         # Clean up
#         db.session.delete(p)
#         db.session.delete(u)
#         db.session.commit()


# def test_view_evaluation_datasets(test_client):
#     with test_client.application.app_context():
#         # Create a sample user and project
#         u = User(username='john', email='john@example.com', password='cat')
#         db.session.add(u)
#         db.session.commit()

#         p = Project(name='Sample Project', user_id=u.id)
#         db.session.add(p)
#         db.session.commit()

#         # Add evaluation datasets
#         evaluation_datasets = [
#             {'field1': 'value1', 'field2': 'value2'},
#             {'field1': 'value3', 'field2': 'value4'}
#         ]
#         temp_file_name = create_csv_temp_file(evaluation_datasets)
#         with open(temp_file_name, 'rb') as f:
#             p.evaluation_datasets = f.read()

#         db.session.commit()
#         os.remove(temp_file_name)

#         # Test the /api/projects/1/view_evaluation_datasets endpoint (GET)
#         response = test_client.get(
#             f'/api/projects/{p.id}/view_evaluation_datasets',
#             headers={'X-Api-Key': u.api_key}
#         )

#         data = json.loads(response.data)

#         assert response.status_code == 200
#         assert data['evaluation_datasets'] == evaluation_datasets

#         # Clean up
#         db.session.delete(p)
#         db.session.delete(u)
#         db.session.commit()
