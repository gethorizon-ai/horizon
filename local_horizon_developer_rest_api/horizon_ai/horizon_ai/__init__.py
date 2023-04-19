# horizon_ai/__init__.py

import requests
from urllib.parse import urljoin


class APIClient:
    def __init__(self, base_url):
        self.base_url = base_url

    def _get(self, endpoint, headers=None):
        response = requests.get(urljoin(self.base_url, endpoint), headers=headers)
        return self._handle_response(response)

    def _post(self, endpoint, json=None, headers=None):  # Add this method here
        response = requests.post(
            urljoin(self.base_url, endpoint), json=json, headers=headers
        )
        return self._handle_response(response)

    def _get_auth_headers(self, api_key):  # Add this method here
        return {"Authorization": f"Bearer {api_key}"}

    def _handle_response(self, response):
        if response.status_code not in [200, 201]:
            raise Exception(
                f"Request failed with status code {response.status_code}: {response.text}"
            )
        if not response.text:
            return {"message": "Empty response"}
        return response.json()

    # User-related methods
    def register_user(self, username, email, password):
        data = {"username": username, "email": email, "password": password}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                f"{self.base_url}/api/users/register", json=data, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def authenticate_user(self, username, password):
        data = {"username": username, "password": password}
        headers = {"Content-Type": "application/json"}
        try:
            response = requests.post(
                f"{self.base_url}/api/users/authenticate", json=data, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def get_user(self, api_key):
        headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
        try:
            response = requests.get(f"{self.base_url}/api/users/", headers=headers)
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def delete_user(self, api_key):
        headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
        try:
            response = requests.delete(f"{self.base_url}/api/users/", headers=headers)
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Project-related methods
    def list_projects(self, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(f"{self.base_url}/api/projects", headers=headers)
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def create_project(self, name, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        data = {"name": name}
        try:
            response = requests.post(
                f"{self.base_url}/api/projects/create", json=data, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def get_project(self, project_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(
                f"{self.base_url}/api/projects/{project_id}", headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def update_project(
        self,
        project_id,
        api_key,
        description=None,
        status=None,
        delete_evaluation_dataset=False,
    ):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        data = {
            "description": description,
            "status": status,
            "delete_evaluation_dataset": delete_evaluation_dataset,
        }
        try:
            response = requests.put(
                f"{self.base_url}/api/projects/{project_id}", json=data, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def delete_project(self, project_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.delete(
                f"{self.base_url}/api/projects/{project_id}", headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Task-related methods
    # List tasks
    def list_tasks(self, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(f"{self.base_url}/api/tasks", headers=headers)
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Create a new task
    def create_task(self, name, task_type, project_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {"name": name, "task_type": task_type, "project_id": project_id}
        try:
            response = requests.post(
                f"{self.base_url}/api/tasks/create", json=payload, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Get task information
    def get_task(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/{task_id}", headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Update a task
    def update_task(
        self,
        task_id,
        api_key,
        description=None,
        task_type=None,
        evaluation_dataset=None,
        status=None,
    ):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {
            "description": description,
            "task_type": task_type,
            "evaluation_dataset": evaluation_dataset,
            "status": status,
        }
        try:
            response = requests.put(
                f"{self.base_url}/api/tasks/{task_id}", json=payload, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Delete a task
    def delete_task(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.delete(
                f"{self.base_url}/api/tasks/{task_id}", headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Get the current prompt of a task
    def get_task_curr_prompt(self, task_id, api_key):
        headers = {"task_id": task_id, "X-Api-Key": api_key}
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/get_curr_prompt", headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Set the current prompt of a task
    def set_task_curr_prompt(self, task_id, prompt_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {"task_id": task_id, "prompt_id": prompt_id}
        try:
            response = requests.put(
                f"{self.base_url}/api/tasks/set_curr_prompt",
                json=payload,
                headers=headers,
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Generate a task
    def generate_task(self, task_id, objective, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {"task_id": task_id, "objective": objective}
        try:
            response = requests.post(
                f"{self.base_url}/api/tasks/generate", json=payload, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Deploy a task using the current prompt
    def deploy_task(self, task_id, inputs, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {"task_id": task_id, "inputs": inputs}
        try:
            response = requests.post(
                f"{self.base_url}/api/tasks/deploy", json=payload, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def upload_evaluation_dataset(self, task_id, file_path, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            with open(file_path, "rb") as f:
                response = requests.post(
                    f"{self.base_url}/api/tasks/{task_id}/upload_evaluation_dataset",
                    files={"evaluation_dataset": f},
                    headers=headers,
                )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def view_evaluation_dataset(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/{task_id}/view_evaluation_dataset",
                headers=headers,
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def get_evaluation_dataset(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/{task_id}/evaluation_dataset",
                headers=headers,
            )
            return response
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    def delete_evaluation_dataset(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.delete(
                f"{self.base_url}/api/tasks/{task_id}/delete_evaluation_dataset",
                headers=headers,
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # def create_task(self, name, project_id, task_type, objective, file_path, api_key):
    #     headers = {"X-Api-Key": api_key}
    #     # Create a new task
    #     payload = {"name": name, "task_type": task_type, "project_id": project_id}
    #     task_response = requests.post(
    #         f"{self.base_url}/api/tasks/create", json=payload, headers=headers
    #     )
    #     data = task_response.json()
    #     print(data)
    #     task_id = data["task"]["id"]

    #     # Upload evaluation dataset
    #     with open(file_path, "rb") as f:
    #         eval_response = requests.post(
    #             f"{self.base_url}/api/tasks/{task_id}/upload_evaluation_dataset",
    #             files={"evaluation_dataset": f},
    #             headers=headers,
    #         )

    #     # Generate a task
    #     payload = {"task_id": task_id, "objective": objective}
    #     generate_response = requests.post(
    #         f"{self.base_url}/api/tasks/generate", json=payload, headers=headers
    #     )

    #     # Add the task_id to the returned JSON object
    #     response_data = generate_response.json()
    #     response_data["task_id"] = task_id

    #     return response_data

    # Get information to confirm with user (e.g., estimated cost) before proceeding with task creation
    def get_task_confirmation_details(self, task_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(
                f"{self.base_url}/api/tasks/{task_id}/get_task_confirmation_details",
                headers=headers,
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Prompt-related methods
    # List prompts
    def list_prompts(self, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(f"{self.base_url}/api/prompts", headers=headers)
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Create a new prompt
    def create_prompt(self, name, task_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {"name": name, "task_id": task_id}
        try:
            response = requests.post(
                f"{self.base_url}/api/prompts/new", json=payload, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Get prompt information
    def get_prompt(self, prompt_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.get(
                f"{self.base_url}/api/prompts/{prompt_id}", headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Update a prompt
    def update_prompt(self, prompt_id, api_key, **kwargs):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {k: v for k, v in kwargs.items() if v is not None}
        try:
            response = requests.put(
                f"{self.base_url}/api/prompts/{prompt_id}",
                json=payload,
                headers=headers,
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Delete a prompt
    def delete_prompt(self, prompt_id, api_key):
        headers = {"X-Api-Key": api_key}
        try:
            response = requests.delete(
                f"{self.base_url}/api/prompts/{prompt_id}", headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Generate a prompt
    def generate_prompt(self, objective, prompt_id, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {"objective": objective, "prompt_id": prompt_id}
        try:
            response = requests.post(
                f"{self.base_url}/api/prompts/generate", json=payload, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None

    # Deploy a prompt
    def deploy_prompt(self, prompt_id, inputs, api_key):
        headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
        payload = {"prompt_id": prompt_id, "inputs": inputs}
        try:
            response = requests.post(
                f"{self.base_url}/api/prompts/deploy", json=payload, headers=headers
            )
            return response.json()
        except Exception as e:
            print(f"Failed with exception: {str(e)}")
            return None
