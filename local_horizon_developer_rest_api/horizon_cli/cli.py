import click
from horizon_ai import APIClient
import json


@click.group()
def cli():
    pass


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--username', prompt='Username', help='The username for the new user.')
@click.option('--email', prompt='Email', help='The email for the new user.')
@click.option('--password', prompt='Password', help='The password for the new user.')
def register_user(base_url, username, email, password):
    client = APIClient(base_url)
    result = client.register_user(username, email, password)
    click.echo(result)


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--username', prompt='Username', help='The username for the user.')
@click.option('--password', prompt='Password', help='The password for the user.')
def authenticate_user(base_url, username, password):
    client = APIClient(base_url)
    result = client.authenticate_user(username, password)
    click.echo(result)


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--user_id', prompt='User ID', help='The ID of the user.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def get_user(base_url, user_id, api_key):
    client = APIClient(base_url)
    result = client.get_user(user_id, api_key)
    click.echo(result)


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--user_id', prompt='User ID', help='The ID of the user to delete.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def delete_user(base_url, user_id, api_key):
    client = APIClient(base_url)
    result = client.delete_user(user_id, api_key)
    click.echo(result)


# List Projects
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def list_projects(base_url, api_key):
    client = APIClient(base_url)
    result = client.list_projects(api_key)
    click.echo(result)


# Create Project
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--name', prompt='Project name', help='The name of the project to create.')
@click.option('--user_id', prompt='User ID', help='The ID of the user who will own the project.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def create_project(base_url, name, user_id, api_key):
    client = APIClient(base_url)
    result = client.create_project(name, user_id, api_key)
    click.echo(result)


# Get Project
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to retrieve.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def get_project(base_url, project_id, api_key):
    client = APIClient(base_url)
    result = client.get_project(project_id, api_key)
    click.echo(result)


# Update Project
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to update.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
@click.option('--description', help='The new description for the project.')
@click.option('--status', help='The new status for the project.')
@click.option('--evaluation_datasets', help='The new evaluation datasets for the project.')
@click.option('--delete_evaluation_datasets', default=False, is_flag=True, help='Whether to delete the evaluation datasets for the project.')
def update_project(base_url, project_id, api_key, description, status, evaluation_datasets, delete_evaluation_datasets):
    client = APIClient(base_url)
    result = client.update_project(
        project_id, api_key, description, status, evaluation_datasets, delete_evaluation_datasets)
    click.echo(result)


cli.add_command(update_project)

# Delete Project


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to delete.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def delete_project(base_url, project_id, api_key):
    client = APIClient(base_url)
    result = client.delete_project(project_id, api_key)
    click.echo(result)


# Upload Evaluation Datasets
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to upload evaluation datasets for.')
@click.option('--file_path', prompt='File Path', help='The path to the file containing the evaluation datasets to upload.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def upload_evaluation_dataset(base_url, project_id, file_path, api_key):
    client = APIClient(base_url)
    result = client.upload_evaluation_datasets(project_id, file_path, api_key)
    click.echo(result)


# View Evaluation Datasets
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to view evaluation datasets for.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def view_evaluation_datasets(base_url, project_id, api_key):
    client = APIClient(base_url)
    result = client.view_evaluation_datasets(project_id, api_key)
    click.echo(result)

# Get Evaluation Datasets


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to get evaluation datasets for.')
@click.option('--api_key', prompt='API Key', help='The API key to use for authentication.')
def get_evaluation_datasets(project_id, api_key):
    client = APIClient()
    result = client.get_evaluation_datasets(project_id, api_key)
    click.echo(result)

# Delete Evaluation Datasets


@click.command()
@click.option('--api_key', prompt='API Key', help='Your Horizon API key.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to delete evaluation datasets for.')
def delete_evaluation_datasets(base_url, api_key, project_id):
    client = APIClient(base_url)
    result = client.delete_evaluation_datasets(project_id, api_key)
    click.echo(result)


# List Tasks
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def list_tasks(base_url, api_key):
    client = APIClient(base_url)
    result = client.list_tasks(api_key)
    click.echo(result)


# Create Task
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--name', prompt='Task name', help='The name of the task to create.')
@click.option('--task_type', prompt='Task type', help='The type of the task to create.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project that the task belongs to.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def create_task(base_url, name, task_type, project_id, api_key):
    client = APIClient(base_url)
    result = client.create_task(name, task_type, project_id, api_key)
    click.echo(result)


# Get Task
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to retrieve.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def get_task(base_url, task_id, api_key):
    client = APIClient(base_url)
    result = client.get_task(task_id, api_key)
    click.echo(result)


# Update Task
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to update.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
@click.option('--description', help='The new description for the task.')
@click.option('--task_type', help='The new task type for the task.')
@click.option('--status', help='The new status for the task.')
def update_task(base_url, task_id, api_key, description=None, task_type=None, status=None):
    client = APIClient(base_url)
    result = client.update_task(
        task_id, api_key, description, task_type, status)
    click.echo(result)


# Delete Task
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to delete.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def delete_task(base_url, task_id, api_key):
    client = APIClient(base_url)
    result = client.delete_task(task_id, api_key)
    click.echo(result)


# List prompts
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def list_prompts(base_url, api_key):
    client = APIClient(base_url)
    result = client.list_prompts(api_key)
    click.echo(result)


# Create prompt
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--name', prompt='Prompt name', help='The name of the prompt to create.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task associated with the prompt.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def create_prompt(base_url, name, task_id, api_key):
    client = APIClient(base_url)
    result = client.create_prompt(name, task_id, api_key)
    click.echo(result)


# Get prompt information
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to retrieve.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def get_prompt(base_url, prompt_id, api_key):
    client = APIClient(base_url)
    result = client.get_prompt(prompt_id, api_key)
    click.echo(result)


# Update prompt
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to update.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
@click.option('--name', help='The new name for the prompt.')
@click.option('--task_id', help='The new task ID for the prompt.')
def update_prompt(base_url, prompt_id, api_key, name, task_id):
    client = APIClient(base_url)
    result = client.update_prompt(
        prompt_id, api_key, name=name, task_id=task_id)
    click.echo(result)


# Delete prompt
@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to delete.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def delete_prompt(base_url, prompt_id, api_key):
    client = APIClient(base_url)
    result = client.delete_prompt(prompt_id, api_key)
    click.echo(result)

# Generate prompt


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--objective', prompt='Objective', help='The objective to generate prompts for.')
@click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to generate prompts for.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def generate_prompt(base_url, objective, prompt_id, api_key):
    client = APIClient(base_url)
    result = client.generate_prompt(objective, prompt_id, api_key)
    click.echo(result)

# deploy prompt


@click.command()
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to deploy.')
@click.option('--inputs', prompt='Inputs', help='The inputs to use when generating prompts.')
@click.option('--api_key', prompt='API Key', help='The API key for the user.')
def deploy_prompt(base_url, prompt_id, inputs, api_key):
    client = APIClient(base_url)
    inputs = json.loads(inputs)
    result = client.deploy_prompt(prompt_id, inputs, api_key)
    click.echo(result)


cli.add_command(register_user)
cli.add_command(authenticate_user)
cli.add_command(get_user)
cli.add_command(delete_user)
cli.add_command(create_project)
cli.add_command(get_project)
cli.add_command(update_project)
cli.add_command(delete_project)
cli.add_command(upload_evaluation_dataset)
cli.add_command(view_evaluation_datasets)
cli.add_command(get_evaluation_datasets)
cli.add_command(delete_evaluation_datasets)
cli.add_command(list_tasks)
cli.add_command(create_task)
cli.add_command(get_task)
cli.add_command(update_task)
cli.add_command(delete_task)
cli.add_command(list_prompts)
cli.add_command(create_prompt)
cli.add_command(get_prompt)
cli.add_command(update_prompt)
cli.add_command(delete_prompt)
cli.add_command(generate_prompt)
cli.add_command(deploy_prompt)

if __name__ == '__main__':
    cli()
