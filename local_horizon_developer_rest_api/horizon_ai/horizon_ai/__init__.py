# horizon_ai/__init__.py

import requests
from urllib.parse import urljoin
from requests import Request, Session


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def _get(self, endpoint, headers=None):
        response = requests.get(
            urljoin(self.base_url, endpoint), headers=headers)
        return self._handle_response(response)

    def _post(self, endpoint, json=None, headers=None):  # Add this method here
        response = requests.post(
            urljoin(self.base_url, endpoint), json=json, headers=headers)
        return self._handle_response(response)

    def _get_auth_headers(self, api_key):  # Add this method here
        return {'Authorization': f'Bearer {api_key}'}

    def _handle_response(self, response):
        if response.status_code not in [200, 201]:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}")
        return response.json()

    # User-related methods

    def register_user(self, username, email, password):
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{self.base_url}/api/users/register", json=data, headers=headers)
        return response.json()

    def authenticate_user(self, username, password):
        data = {
            "username": username,
            "password": password
        }
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            f"{self.base_url}/api/users/authenticate", json=data, headers=headers)
        return response.json()

    def get_user(self, user_id, api_key):
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"{self.base_url}/api/users/{user_id}", headers=headers)
        return response.json()

    def delete_user(self, user_id, api_key):
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        response = requests.delete(
            f"{self.base_url}/api/users/{user_id}", headers=headers)
        return response.json()

    # Project-related methods
    def list_projects(self, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/projects", headers=headers)
        return response.json()

    def create_project(self, name, user_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        data = {"name": name, "user_id": user_id}
        response = requests.post(
            f"{self.base_url}/api/projects/create", json=data, headers=headers)
        return response.json()

    def get_project(self, project_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/projects/{project_id}", headers=headers)
        return response.json()

    def update_project(self, project_id, api_key, description=None, status=None, evaluation_datasets=None, delete_evaluation_datasets=False):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        data = {
            "description": description,
            "status": status,
            "evaluation_datasets": evaluation_datasets,
            "delete_evaluation_datasets": delete_evaluation_datasets
        }
        response = requests.put(
            f"{self.base_url}/api/projects/{project_id}", json=data, headers=headers)
        return response.json()

    def delete_project(self, project_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.delete(
            f"{self.base_url}/api/projects/{project_id}", headers=headers)
        return response.json()

    def upload_evaluation_datasets(self, project_id, file_path, api_key):
        headers = {"X-Api-Key": api_key}
        with open(file_path, 'rb') as f:
            response = requests.post(f"{self.base_url}/api/projects/{project_id}/upload_evaluation_datasets", files={
                                     "evaluation_datasets": f}, headers=headers)
        return response.json()

    def view_evaluation_datasets(self, project_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/projects/{project_id}/view_evaluation_datasets", headers=headers)
        return response.json()

    def get_evaluation_datasets(self, project_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/projects/{project_id}/evaluation_datasets", headers=headers)
        return response

    def delete_evaluation_datasets(self, project_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.delete(
            f"{self.base_url}/api/projects/{project_id}/delete_evaluation_datasets", headers=headers)
        return response.json()

    # Task-related methods
    # List tasks
    def list_tasks(self, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(f"{self.base_url}/api/tasks", headers=headers)
        return response.json()

    # Create a new task
    def create_task(self, name, task_type, project_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {
            "name": name,
            "task_type": task_type,
            "project_id": project_id
        }
        response = requests.post(
            f"{self.base_url}/api/tasks/create", json=payload, headers=headers)
        return response.json()

    # Get task information
    def get_task(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/tasks/{task_id}", headers=headers)
        return response.json()

    # Update a task
    def update_task(self, task_id, api_key, description=None, task_type=None, status=None):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {
            "description": description,
            "task_type": task_type,
            "status": status
        }
        response = requests.put(
            f"{self.base_url}/api/tasks/{task_id}", json=payload, headers=headers)
        return response.json()

    # Delete a task
    def delete_task(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.delete(
            f"{self.base_url}/api/tasks/{task_id}", headers=headers)
        return response.json()

    # Prompt-related methods

    # List prompts
    def list_prompts(self, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/prompts", headers=headers)
        return response.json()

    # Create a new prompt
    def create_prompt(self, name, task_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {
            "name": name,
            "task_id": task_id
        }
        response = requests.post(
            f"{self.base_url}/api/prompts/new", json=payload, headers=headers)
        return response.json()

    # Get prompt information
    def get_prompt(self, prompt_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.get(
            f"{self.base_url}/api/prompts/{prompt_id}", headers=headers)
        return response.json()

    # Update a prompt
    def update_prompt(self, prompt_id, api_key, **kwargs):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {k: v for k, v in kwargs.items() if v is not None}
        response = requests.put(
            f"{self.base_url}/api/prompts/{prompt_id}", json=payload, headers=headers)
        return response.json()

    # Delete a prompt
    def delete_prompt(self, prompt_id, api_key):
        headers = {"X-Api-Key": api_key}
        response = requests.delete(
            f"{self.base_url}/api/prompts/{prompt_id}", headers=headers)
        return response.json()

    # Generate a prompt
    def generate_prompt(self, objective, prompt_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {
            "objective": objective,
            "prompt_id": prompt_id
        }
        response = requests.post(
            f"{self.base_url}/api/prompts/generate", json=payload, headers=headers)
        return response.json()

    # Deploy a prompt
    def deploy_prompt(self, prompt_id, inputs, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {
            "prompt_id": prompt_id,
            "inputs": inputs
        }
        response = requests.post(
            f"{self.base_url}/api/prompts/deploy", json=payload, headers=headers)
        return response.json()
