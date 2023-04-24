import json
import pytest
from app.models.component import User, Prompt
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


def test_list_prompts(test_client):
    with test_client.application.app_context():
        # Create a sample user and prompt
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Prompt(name='Sample Prompt', task_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/prompts endpoint (GET)
        response = test_client.get(
            '/api/prompts', headers={'X-Api-Key': u.api_key})

        # Check if the response is JSON before attempting to parse it
        if response.content_type == 'application/json':
            data = json.loads(response.data)
        else:
            raise ValueError(
                f"Unexpected content type: {response.content_type}, response: {response.data}")

        assert response.status_code == 200
        assert data['prompts'][0]['name'] == 'Sample Prompt'

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_create_prompt(test_client):
    with test_client.application.app_context():
        # Create a sample user
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        # Test the /api/prompts/new endpoint (POST)
        new_prompt = {
            'name': 'New Prompt',
            'task_id': 1
        }

        response = test_client.post(
            '/api/prompts/new', json=new_prompt, headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 201
        assert data['message'] == 'Prompt created successfully'
        assert data['prompt']['name'] == 'New Prompt'

        # Clean up
        created_prompt = Prompt.query.get(data['prompt']['id'])
        db.session.delete(created_prompt)
        db.session.delete(u)
        db.session.commit()


def test_get_prompt(test_client):
    with test_client.application.app_context():
        # Create a sample user and prompt
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Prompt(name='Sample Prompt', task_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/prompts/1 endpoint (GET)
        response = test_client.get(
            f'/api/prompts/{p.id}', headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['name'] == 'Sample Prompt'

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_update_prompt(test_client):
    with test_client.application.app_context():
        # Create a sample user and prompt
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Prompt(name='Sample Prompt', task_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/prompts/1 endpoint (PUT)
        update_data = {
            'version': 'v2.0',
            'status': 'completed',
            'source': 'new_source'
        }

        response = test_client.put(
            f'/api/prompts/{p.id}', json=update_data, headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['message'] == 'Prompt updated successfully'
        assert data['prompt']['version'] == 'v2.0'
        assert data['prompt']['status'] == 'completed'
        assert data['prompt']['source'] == 'new_source'

        # Clean up
        db.session.delete(p)
        db.session.delete(u)
        db.session.commit()


def test_delete_prompt(test_client):
    with test_client.application.app_context():
        # Create a sample user and prompt
        u = User(username='john', email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()

        p = Prompt(name='Sample Prompt', task_id=1)
        db.session.add(p)
        db.session.commit()

        # Test the /api/prompts/1 endpoint (DELETE)
        response = test_client.delete(
            f'/api/prompts/{p.id}', headers={'X-Api-Key': u.api_key})
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['message'] == 'Prompt deleted successfully'

        # Verify the prompt is deleted from the database
        deleted_prompt = Prompt.query.get(p.id)
        assert deleted_prompt is None

        # Clean up
        db.session.delete(u)
        db.session.commit()
