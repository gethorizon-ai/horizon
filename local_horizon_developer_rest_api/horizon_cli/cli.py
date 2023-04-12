from horizon_ai import APIClient
import os
import json
import click
import configparser


config = configparser.ConfigParser()
config.read(os.path.expanduser('~/.horizonai.cfg'))


@click.group()
def cli():
    pass


@click.group()
def user():
    pass


@click.group()
def project():
    pass


@click.group()
def task():
    pass


@click.group()
def evaluation_dataset():
    pass


@click.group()
def prompt():
    pass


@click.command(name='register')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--username', prompt='Username', help='The username for the new user.')
@click.option('--email', prompt='Email', help='The email for the new user.')
@click.option('--password', prompt='Password', help='The password for the new user.')
def register_user(base_url, username, email, password):
    client = APIClient(base_url)
    result = client.register_user(username, email, password)
    click.echo(result)


@click.command(name='authenticate')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--username', prompt='Username', help='The username for the user.')
@click.option('--password', prompt='Password', help='The password for the user.')
def authenticate_user(base_url, username, password):
    client = APIClient(base_url)
    result = client.authenticate_user(username, password)
    click.echo(result)


@click.command(name='get')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--user_id', prompt='User ID', help='The ID of the user.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
def get_user(base_url, user_id, api_key):
    client = APIClient(base_url)
    result = client.get_user(user_id, api_key)
    click.echo(result)


@click.command(name='delete')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--user_id', prompt='User ID', help='The ID of the user to delete.')
def delete_user(base_url, user_id, api_key):
    client = APIClient(base_url)
    result = client.delete_user(user_id, api_key)
    click.echo(result)


@click.command(name='list')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
def list_projects(base_url, api_key):
    client = APIClient(base_url)
    result = client.list_projects(api_key)
    click.echo(result)


@click.command(name='create')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--name', prompt='Project name', help='The name of the project to create.')
def create_project(base_url, name, api_key):
    client = APIClient(base_url)
    result = client.create_project(name, api_key)
    # Extract the desired elements from the result
    message = result['message']
    project_id = result['project']['id']
    project_name = result['project']['name']

    # Create a new dictionary with only the desired elements
    output = {
        'message': message,
        'project': {
            'id': project_id,
            'name': project_name
        }
    }

    # Format the output dictionary as a JSON string with indentation
    formatted_output = json.dumps(output, indent=4)

    # Print the formatted output
    click.echo(formatted_output)


# Get Project
@click.command(name='get')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to retrieve.')
def get_project(base_url, project_id, api_key):
    client = APIClient(base_url)
    result = client.get_project(project_id, api_key)
    click.echo(result)


# Update Project
@click.command(name='update')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to update.')
@click.option('--description', help='The new description for the project.')
@click.option('--status', help='The new status for the project.')
def update_project(base_url, project_id, api_key, description=None, status=None):
    client = APIClient(base_url)
    result = client.update_project(
        project_id, api_key, description, status)
    click.echo(result)


cli.add_command(update_project)


# Delete Project
@click.command(name='delete')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project to delete.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
def delete_project(base_url, project_id, api_key):
    client = APIClient(base_url)
    result = client.delete_project(project_id, api_key)
    click.echo(result)


# List Tasks
@click.command(name='list')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
def list_tasks(base_url, api_key):
    client = APIClient(base_url)
    result = client.list_tasks(api_key)
    click.echo(result)


# Create Task
@click.command(name='create')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--name', prompt='Task name', help='The name of the task to create.')
@click.option('--project_id', prompt='Project ID', help='The ID of the project that the task belongs to.')
# @click.option('--task_type', prompt='Task type', help='The type of the task to create.')
@click.option('--task_type', default='text_generation', help='The type of the task to create.')
@ click.option('--objective', prompt='Objective', help='The objective of the task to generate.')
@click.option('--file_path', prompt='File Path', help='The path to the file containing the evaluation datasets to upload.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
def create_task(base_url, name, project_id, task_type, objective, file_path, api_key):
    client = APIClient(base_url)
    result = client.create_task(
        name, project_id, task_type, objective, file_path, api_key)
    # Extract the desired elements from the result
    task_id = result['task_id']  # Update this line
    prompt_template = result['generated_prompt']['template']

    # Replace '\n' with actual new lines in the string
    formatted_prompt_template = prompt_template.replace('\\n', '\n')

    output = {}

    # DEMO PURPOSES ONLY Before complete implementation
    # Add the new key-value pairs to the output dictionary
    output["task_id"] = task_id
    output["quality_score"] = 0.98
    output["evaluations_completed"] = 4739
    output["model_recommended"] = "gpt 3.5"
    output["few_shot"] = "no"
    output["few_shot_approach"] = "N/A"
    output["prompt_template"] = formatted_prompt_template
    # Create a new dictionary with only the desired elements
    # output = {
    #     'task_id': task_id,
    #     'prompt_template': formatted_prompt_template
    # }

    # # DEMO PURPOSES ONLY Before complete implementation
    # # Add the new key-value pairs to the output dictionary
    # output["quality_score"] = 0.98
    # output["evaluations_completed"] = 4739
    # output["model_recommended"] = "gpt 3.5"
    # output["prompt_technique"] = "role play"
    # output["few_shot"] = "no"
    # output["few_shot_approach"] = "N/A"

    # Format the output dictionary as a JSON string with indentation
    formatted_output = json.dumps(output, indent=4)

    # Print the formatted output
    click.echo(formatted_output)


# Get Task
@click.command(name='get')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to retrieve.')
def get_task(base_url, task_id, api_key):
    client = APIClient(base_url)
    result = client.get_task(task_id, api_key)
    click.echo(result)


# Update Task
@click.command(name='update')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to update.')
@click.option('--description', help='The new description for the task.')
@click.option('--task_type', help='The new task type for the task.')
@click.option('--evaluation_dataset', help='The new evaluation datasets for the task.')
@click.option('--delete_evaluation_dataset', default=False, is_flag=True, help='Whether to delete the evaluation datasets for the task.')
@click.option('--status', help='The new status for the task.')
def update_task(base_url, task_id, api_key, description=None, task_type=None, status=None, evaluation_dataset=None, delete_evaluation_dataset=None):
    client = APIClient(base_url)
    result = client.update_task(
        task_id, api_key, description, task_type, status, evaluation_dataset, delete_evaluation_dataset)
    click.echo(result)


# Delete Task
@click.command(name='delete')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to delete.')
def delete_task(base_url, task_id, api_key):
    client = APIClient(base_url)
    result = client.delete_task(task_id, api_key)
    click.echo(result)


# Get the current prompt of a task
@click.command(name='get-active-prompt')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task.')
def get_task_curr_prompt(base_url, task_id, api_key):
    client = APIClient(base_url)
    result = client.get_task_curr_prompt(task_id, api_key)
    click.echo(result)


# Set the current prompt of a task
@click.command(name='set-active-prompt')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task.')
@click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to set as the current prompt for the task.')
def set_task_curr_prompt(base_url, task_id, prompt_id, api_key):
    client = APIClient(base_url)
    result = client.set_task_curr_prompt(task_id, prompt_id, api_key)
    click.echo(result)


# Generate a task
@ click.command(name='generate')
@ click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@ click.option('--task_id', prompt='Task ID', help='The ID of the task to generate.')
@ click.option('--objective', prompt='Objective', help='The objective of the task to generate.')
def generate_task(base_url, task_id, objective, api_key):
    client = APIClient(base_url)
    result = client.generate_task(task_id, objective, api_key)
    click.echo(result)


# Deploy a task
@ click.command(name='deploy')
@ click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@ click.option('--task_id', prompt='Task ID', help='The ID of the task to deploy.')
@ click.option('--inputs', prompt='Inputs', help='The inputs to the task in JSON format.')
def deploy_task(base_url, task_id, inputs, api_key):
    inputs_dict = json.loads(inputs)
    client = APIClient(base_url)
    result = client.deploy_task(task_id, inputs_dict, api_key)
    click.echo(result)


# Upload Evaluation Dataset
@click.command(name='upload')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to upload evaluation datasets for.')
@click.option('--file_path', prompt='File Path', help='The path to the file containing the evaluation datasets to upload.')
def upload_evaluation_dataset(base_url, task_id, file_path, api_key):
    client = APIClient(base_url)
    result = client.upload_evaluation_dataset(task_id, file_path, api_key)
    click.echo(result)


# View Evaluation Dataset
@click.command(name='veiw')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to view evaluation datasets for.')
def view_evaluation_dataset(base_url, task_id, api_key):
    client = APIClient(base_url)
    result = client.view_evaluation_dataset(task_id, api_key)
    click.echo(result)


# Get Evaluation Dataset
@click.command(name='download')
@click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to get evaluation datasets for.')
def get_evaluation_dataset(task_id, api_key):
    client = APIClient()
    result = client.get_evaluation_dataset(task_id, api_key)
    click.echo(result)


# Delete Evaluation Dataset
@click.command(name='delete')
@click.option('--api_key', default=os.environ.get('HORIZONAI_API_KEY'), prompt='API Key' if not os.environ.get('HORIZONAI_API_KEY') else False, help='The API key for the user.')
@click.option('--task_id', prompt='Task ID', help='The ID of the task to delete evaluation datasets for.')
def delete_evaluation_dataset(base_url, api_key, task_id):
    client = APIClient(base_url)
    result = client.delete_evaluation_dataset(task_id, api_key)
    click.echo(result)


# # List prompts
# @click.command()
# @click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
# @click.option('--api_key', prompt='API Key', help='The API key for the user.')
# def list_prompts(base_url, api_key):
#     client = APIClient(base_url)
#     result = client.list_prompts(api_key)
#     click.echo(result)


# # Create prompt
# @click.command()
# @click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
# @click.option('--name', prompt='Prompt name', help='The name of the prompt to create.')
# @click.option('--task_id', prompt='Task ID', help='The ID of the task associated with the prompt.')
# @click.option('--api_key', prompt='API Key', help='The API key for the user.')
# def create_prompt(base_url, name, task_id, api_key):
#     client = APIClient(base_url)
#     result = client.create_prompt(name, task_id, api_key)
#     click.echo(result)


# # Get prompt information
# @click.command()
# @click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
# @click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to retrieve.')
# @click.option('--api_key', prompt='API Key', help='The API key for the user.')
# def get_prompt(base_url, prompt_id, api_key):
#     client = APIClient(base_url)
#     result = client.get_prompt(prompt_id, api_key)
#     click.echo(result)


# # Update prompt
# @click.command()
# @click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
# @click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to update.')
# @click.option('--api_key', prompt='API Key', help='The API key for the user.')
# @click.option('--name', help='The new name for the prompt.')
# @click.option('--task_id', help='The new task ID for the prompt.')
# def update_prompt(base_url, prompt_id, api_key, name, task_id):
#     client = APIClient(base_url)
#     result = client.update_prompt(
#         prompt_id, api_key, name=name, task_id=task_id)
#     click.echo(result)


# # Delete prompt
# @click.command()
# @click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
# @click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to delete.')
# @click.option('--api_key', prompt='API Key', help='The API key for the user.')
# def delete_prompt(base_url, prompt_id, api_key):
#     client = APIClient(base_url)
#     result = client.delete_prompt(prompt_id, api_key)
#     click.echo(result)

# # Generate prompt


# @click.command()
# @click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
# @click.option('--objective', prompt='Objective', help='The objective to generate prompts for.')
# @click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to generate prompts for.')
# @click.option('--api_key', prompt='API Key', help='The API key for the user.')
# def generate_prompt(base_url, objective, prompt_id, api_key):
#     client = APIClient(base_url)
#     result = client.generate_prompt(objective, prompt_id, api_key)
#     click.echo(result)

# # deploy prompt
# @click.command()
# @click.option('--base_url', default='http://127.0.0.1:5000', help='The base URL for the API.')
# @click.option('--prompt_id', prompt='Prompt ID', help='The ID of the prompt to deploy.')
# @click.option('--inputs', prompt='Inputs', help='The inputs to use when generating prompts.')
# @click.option('--api_key', prompt='API Key', help='The API key for the user.')
# def deploy_prompt(base_url, prompt_id, inputs, api_key):
#     client = APIClient(base_url)
#     inputs = json.loads(inputs)
#     result = client.deploy_prompt(prompt_id, inputs, api_key)
#     click.echo(result)

# Add CLI commands to their respective groups
cli.add_command(user)
cli.add_command(project)
cli.add_command(task)
cli.add_command(evaluation_dataset)
cli.add_command(prompt)

# User-related commands
user.add_command(register_user)
user.add_command(authenticate_user)
user.add_command(get_user)
user.add_command(delete_user)

# Project-related commands
project.add_command(create_project)
project.add_command(get_project)
project.add_command(update_project)
project.add_command(delete_project)

# Task-related commands
task.add_command(list_tasks)
task.add_command(create_task)
task.add_command(get_task)
task.add_command(get_task_curr_prompt)
task.add_command(set_task_curr_prompt)
task.add_command(generate_task)
task.add_command(deploy_task)

# Evaluation Dataset-related commands
evaluation_dataset.add_command(upload_evaluation_dataset)
evaluation_dataset.add_command(view_evaluation_dataset)
evaluation_dataset.add_command(get_evaluation_dataset)
evaluation_dataset.add_command(delete_evaluation_dataset)

# commented prompt-related commands
# prompt.add_command(list_prompts)
# prompt.add_command(create_prompt)
# prompt.add_command(get_prompt)
# prompt.add_command(update_prompt)
# prompt.add_command(delete_prompt)
# prompt.add_command(generate_prompt)
# prompt.add_command(deploy_prompt)

# Enable auto-completion
try:
    import click_completion
    click_completion.init()
except ImportError:
    pass

if __name__ == '__main__':
    cli()
