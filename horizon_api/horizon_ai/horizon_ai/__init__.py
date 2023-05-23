# horizon_ai/__init__.py

import requests
import os
import json
from urllib.parse import urljoin

# Base url for API calls
base_url = "http://127.0.0.1:5000"

# API keys for user to set
api_key = None
openai_api_key = None
anthropic_api_key = None


def _get(endpoint, headers=None):
    global base_url
    response = requests.get(urljoin(base_url, endpoint), headers=headers)
    return _handle_response(response)


def _post(endpoint, json=None, headers=None, files=None):
    global base_url
    response = requests.post(
        urljoin(base_url, endpoint),
        json=json,
        headers=headers,
        files=files,
    )
    return _handle_response(response)


def _delete(endpoint, headers=None):
    global base_url
    response = requests.delete(urljoin(base_url, endpoint), headers=headers)
    return _handle_response(response)


def _put(endpoint, json=None, headers=None):
    global base_url
    response = requests.put(urljoin(base_url, endpoint), json=json, headers=headers)
    return _handle_response(response)


def _get_auth_headers():
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    return {"Authorization": f"Bearer {api_key}"}


def _handle_response(response):
    if response.status_code not in [200, 201]:
        raise Exception(
            f"Request failed with status code {response.status_code}: {response.text}"
        )
    if not response.text:
        return {"message": "Empty response"}
    return response.json()


# User-related methods
# def register_user(name, email, password):
#     data = {"name": name, "email": email, "password": password}
#     headers = {"Content-Type": "application/json"}
#     response = _post(endpoint="/api/users/register", json=data, headers=headers)
#     return response


def generate_new_api_key(email, password):
    data = {"email": email, "password": password}
    headers = {"Content-Type": "application/json"}
    response = _post(
        endpoint="/api/users/generate_new_api_key",
        json=data,
        headers=headers,
    )
    return response


# def get_user():
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
#     response = _get(endpoint="/api/users/", headers=headers)
#     return response


# def delete_user():
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key, "Content-Type": "application/json"}
#     response = _delete(endpoint="/api/users/", headers=headers)
#     return response


# Project-related methods
def list_projects():
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _get(endpoint="/api/projects", headers=headers)
    return response


def create_project(name):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
    data = {"name": name}
    response = _post(
        endpoint="/api/projects/create",
        json=data,
        headers=headers,
    )
    return response


def get_project(project_id):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _get(endpoint=f"/api/projects/{project_id}", headers=headers)
    return response


# def update_project(
#     project_id,
#     description=None,
#     status=None,
# ):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
#     data = {
#         "description": description,
#         "status": status,
#     }
#     response = _put(endpoint=f"/api/projects/{project_id}", json=data, headers=headers)
#     return response


def delete_project(project_id):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _delete(endpoint=f"/api/projects/{project_id}", headers=headers)
    return response


# Task-related methods
# List tasks
def list_tasks():
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _get(endpoint="/api/tasks", headers=headers)
    return response


# Create a new task
def create_task(
    name: str,
    project_id: int,
    allowed_models: list,
    task_type: str = "text_generation",
):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    if type(allowed_models) != list or len(allowed_models) == 0:
        raise Exception("Must provide list with at least one allowed model.")
    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
    payload = {
        "name": name,
        "task_type": task_type,
        "project_id": project_id,
        "allowed_models": allowed_models,
    }
    response = _post(endpoint="/api/tasks/create", json=payload, headers=headers)
    return response


# Get task information
def get_task(task_id):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _get(endpoint=f"/api/tasks/{task_id}", headers=headers)
    return response


# # Update a task
# def update_task(
#     self,
#     task_id,
#     api_key,
#     description=None,
#     task_type=None,
#     evaluation_dataset=None,
#     status=None,
# ):
#     headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
#     payload = {
#         "description": description,
#         "task_type": task_type,
#         "evaluation_dataset": evaluation_dataset,
#         "status": status,
#     }
#     try:
#         response = requests.put(
#             f"{self.base_url}/api/tasks/{task_id}", json=payload, headers=headers
#         )
#         return response.json()
#     except Exception as e:
#         print(f"Failed with exception: {str(e)}")
#         return None


# Delete a task
def delete_task(task_id):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _delete(endpoint=f"/api/tasks/{task_id}", headers=headers)
    return response


# # Get the current prompt of a task
# def get_task_curr_prompt(task_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"task_id": task_id, "X-Api-Key": api_key}
#     response = _get(endpoint="/api/tasks/get_curr_prompt", headers=headers)
#     return response


# # Set the current prompt of a task
# def set_task_curr_prompt(task_id, prompt_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
#     payload = {"task_id": task_id, "prompt_id": prompt_id}
#     response = _put(
#         endpoint="/api/tasks/set_curr_prompt",
#         json=payload,
#         headers=headers,
#     )
#     return response


# Get information to confirm with user (e.g., estimated cost) before proceeding with task creation
def get_task_confirmation_details(task_id):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _get(
        endpoint=f"/api/tasks/{task_id}/get_task_confirmation_details",
        headers=headers,
    )
    return response


# Generate a task
def generate_task(task_id, objective):
    global api_key, openai_api_key, anthropic_api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
    payload = {
        "task_id": task_id,
        "objective": objective,
        "openai_api_key": openai_api_key,
        "anthropic_api_key": anthropic_api_key,
    }
    response = _post(endpoint="/api/tasks/generate", json=payload, headers=headers)
    return response


# Deploy a task using the current prompt
def deploy_task(task_id, inputs, log_deployment=False):
    global api_key, openai_api_key, anthropic_api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
    payload = {
        "task_id": task_id,
        "inputs": inputs,
        "openai_api_key": openai_api_key,
        "anthropic_api_key": anthropic_api_key,
        "log_deployment": log_deployment,
    }
    response = _post(endpoint="/api/tasks/deploy", json=payload, headers=headers)
    return response


def upload_evaluation_dataset(task_id, file_path):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    with open(file_path, "rb") as f:
        response = _post(
            endpoint=f"/api/tasks/{task_id}/upload_evaluation_dataset",
            files={"evaluation_dataset": f},
            headers=headers,
        )
        return response


def upload_output_schema(task_id, file_path):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    with open(file_path, "rb") as f:
        response = _post(
            endpoint=f"/api/tasks/{task_id}/upload_output_schema",
            files={"output_schema": f},
            headers=headers,
        )
        return response


def view_deployment_logs(task_id):
    global api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    headers = {"X-Api-Key": api_key}
    response = _get(
        endpoint=f"/api/tasks/{task_id}/view_deployment_logs", headers=headers
    )
    return response


# def view_evaluation_dataset(task_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key}
#     response = _get(
#         endpoint=f"/api/tasks/{task_id}/view_evaluation_dataset", headers=headers
#     )
#     return response


# def get_evaluation_dataset(task_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key}
#     response = _get(
#         f"/api/tasks/{task_id}/evaluation_dataset",
#         headers=headers,
#     )
#     return response


# def delete_evaluation_dataset(task_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key}
#     response = _delete(
#         endpoint=f"/api/tasks/{task_id}/delete_evaluation_dataset",
#         headers=headers,
#     )
#     return response


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


# Prompt-related methods
# # List prompts
# def list_prompts():
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key}
#     response = _get(endpoint="/api/prompts", headers=headers)
#     return response


# # Create a new prompt
# def create_prompt(name, task_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
#     payload = {"name": name, "task_id": task_id}
#     response = _post(endpoint="/api/prompts/new", json=payload, headers=headers)
#     return response


# # Get prompt information
# def get_prompt(prompt_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key}
#     response = _get(f"/api/prompts/{prompt_id}", headers=headers)
#     return response


# # Update a prompt
# def update_prompt(prompt_id, **kwargs):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
#     payload = {k: v for k, v in kwargs.items() if v is not None}
#     response = _put(endpoint=f"/api/prompts/{prompt_id}", json=payload, headers=headers)
#     return response


# # Delete a prompt
# def delete_prompt(prompt_id):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"X-Api-Key": api_key}
#     response = _delete(endpoint=f"/api/prompts/{prompt_id}", headers=headers)
#     return response


# # Generate a prompt
# def generate_prompt(objective, prompt_id, openai_api_key):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
#     payload = {
#         "objective": objective,
#         "prompt_id": prompt_id,
#         "openai_api_key": openai_api_key,
#     }
#     response = _post(endpoint="/api/prompts/generate", json=payload, headers=headers)
#     return response


# # Deploy a prompt
# def deploy_prompt(prompt_id, inputs):
#     global api_key
#     if api_key == None:
#         raise Exception("Must set Horizon API key.")
#     headers = {"Content-Type": "application/json", "X-Api-Key": api_key}
#     payload = {"prompt_id": prompt_id, "inputs": inputs}
#     response = _post(endpoint="/api/prompts/deploy", json=payload, headers=headers)
#     return response


# Enabler-related methods
def generate_synthetic_data(objective, num_synthetic_data, file_path):
    global api_key, openai_api_key
    if api_key == None:
        raise Exception("Must set Horizon API key.")
    if openai_api_key == None:
        raise Exception("Must set OpenAI API key.")

    headers = {"X-Api-Key": api_key}
    payload = {
        "objective": objective,
        "num_synthetic_data": num_synthetic_data,
        "openai_api_key": openai_api_key,
    }
    with open(file_path, "rb") as f:
        # Create the multipart form data
        multipart_form_data = {
            "json_data": (None, json.dumps(payload), "application/json"),
            "original_dataset": ("original_dataset", f, "application/octet"),
        }
        response = _post(
            endpoint="/api/enablers/generate_synthetic_data",
            files=multipart_form_data,
            headers=headers,
        )
        return response
