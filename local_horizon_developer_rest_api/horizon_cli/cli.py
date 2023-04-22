import horizon_ai
import os
import json
import click
import configparser


config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.horizonai.cfg"))


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


# User-related methods


# Register user
# TODO: remove after account creation triggered automatically from cognito sign-up
@click.command(name="register")
@click.option("--username", prompt="Username", help="The username for the new user.")
@click.option("--email", prompt="Email", help="The email for the new user.")
@click.option("--password", prompt="Password", help="The password for the new user.")
def register_user(username, email, password):
    try:
        result = horizon_ai.register_user(username, email, password)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Generate new Horizon API key for user
@click.command(name="api-key")
@click.option("--username", prompt="Username", help="The username for the user.")
@click.option("--password", prompt="Password", help="The password for the user.")
def authenticate_user(username, password):
    try:
        result = horizon_ai.generate_new_api_key(username, password)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Get user details
@click.command(name="get")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
def get_user(horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.get_user()
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Delete user
# @click.command(name="delete")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option("--user_id", prompt="User ID", help="The ID of the user to delete.")
# def delete_user(user_id, horizon_api_key):
#     horizon_ai.api_key = horizon_api_key
#     try:
#         result = horizon_ai.delete_user(user_id)
#         formatted_output = json.dumps(result, indent=4)
#         click.echo(formatted_output)
#     except Exception as e:
#         click.echo(str(e))


# Project-related methods


# List projects
@click.command(name="list")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
def list_projects(horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.list_projects()
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Create project
@click.command(name="create")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option(
    "--name", prompt="Project name", help="The name of the project to create."
)
def create_project(name, horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.create_project(name)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Get Project
@click.command(name="get")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option(
    "--project_id", prompt="Project ID", help="The ID of the project to retrieve."
)
def get_project(project_id, horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.get_project(project_id)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Update Project
@click.command(name="update")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option(
    "--project_id", prompt="Project ID", help="The ID of the project to update."
)
@click.option("--description", help="The new description for the project.")
@click.option("--status", help="The new status for the project.")
def update_project(project_id, horizon_api_key, description=None, status=None):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.update_project(project_id, description, status)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Delete Project
@click.command(name="delete")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option(
    "--project_id", prompt="Project ID", help="The ID of the project to delete."
)
def delete_project(project_id, horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.delete_project(project_id)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Task-related methods


# List Tasks
@click.command(name="list")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
def list_tasks(horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.list_tasks()
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Create Task record and generate prompt for it
@click.command(name="generate")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option("--name", prompt="Task name", help="The name of the task to create.")
@click.option(
    "--project_id",
    prompt="Project ID",
    help="The ID of the project that the task belongs to.",
)
# @click.option('--task_type', prompt='Task type', help='The type of the task to create.')
@click.option(
    "--task_type", default="text_generation", help="The type of the task to create."
)
@click.option(
    "--objective", prompt="Objective", help="The objective of the task to generate."
)
@click.option(
    "--file_path",
    prompt="File Path",
    help="The path to the file containing the evaluation datasets to upload.",
)
@click.option(
    "--openai_api_key",
    default=os.environ.get("OPENAI_API_KEY"),
    prompt="OpenAI API Key" if not os.environ.get("OPENAI_API_KEY") else False,
    help="The OpenAI API key for the user.",
)
def generate_task(
    name,
    project_id,
    task_type,
    objective,
    file_path,
    horizon_api_key,
    openai_api_key,
):
    horizon_ai.api_key = horizon_api_key
    horizon_ai.openai_api_key = openai_api_key

    # Create task record
    try:
        task_creation_response = horizon_ai.create_task(name, task_type, project_id)
        task_id = task_creation_response["task"]["id"]
    except Exception as e:
        click.echo("Failed in task creation")
        click.echo(str(e))
        return

    # Upload evaluation dataset
    try:
        upload_dataset_response = horizon_ai.upload_evaluation_dataset(
            task_id, file_path
        )
    except Exception as e:
        # If uploading evaluation dataset fails, then delete previously created task
        horizon_ai.delete_task(task_id)
        click.echo("Failed in dataset upload")
        click.echo(str(e))
        return

    # Confirm key details of task creation (e.g., estimated cost) with user before proceeding
    try:
        task_confirmation_details_response = horizon_ai.get_task_confirmation_details(
            task_id
        )
        task_confirmation_details = task_confirmation_details_response[
            "task_confirmation_details"
        ]
    except Exception as e:
        # If error with getting task confirmation details, then clean up task record and evaluation dataset before raising exception
        horizon_ai.delete_evaluation_dataset(task_id)
        horizon_ai.delete_task(task_id)
        click.echo("Failed in task confirmation details")
        click.echo(str(e))
        return

    click.echo("=====")
    click.echo(
        "Please confirm the following parameters for your task creation request:"
    )
    click.echo("")
    click.echo(f"1) Objective: {objective}")
    click.echo("")
    click.echo(f"2) Input variables: {task_confirmation_details['input_variables']}")
    click.echo(
        "* Inferred based on the headers of all but the right-most column in your evaluation dataset."
    )
    click.echo("")
    click.echo(
        f"3) Estimated LLM provider cost: ${task_confirmation_details['cost_estimate']['low']}-{task_confirmation_details['cost_estimate']['high']}"
    )
    click.echo(
        "* This is entirely the LLM provider cost and not a Horizon charge. Actual cost may vary."
    )
    click.echo("=====")

    # Cancel task creation if user does not give confirmation
    if not click.confirm("Do you want to proceed with task creation?"):
        # Delete task and evaluation dataset, and abort operation
        horizon_ai.delete_evaluation_dataset(task_id)
        horizon_ai.delete_task(task_id)
        click.echo("Cancelled task creation.")
        return

    # Given user's confirmation, continue with task creation
    try:
        click.echo("Proceeding with task creation...")
        generate_response = horizon_ai.generate_task(task_id, objective)
        click.echo(generate_response)
    except Exception as e:
        # If error with generating task, then clean up task record and evaluation dataset before raising exception
        horizon_ai.delete_evaluation_dataset(task_id)
        horizon_ai.delete_task(task_id)
        click.echo("Failed in task generation")
        click.echo(str(e))
        return

    # Print info about the newly created task object
    click.echo("=====")
    click.echo(
        "Task creation completed successfully. Here are details about your task:"
    )
    result = horizon_ai.get_task(task_id)
    formatted_output = json.dumps(result, indent=4)
    click.echo(formatted_output)


# Get Task
@click.command(name="get")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option("--task_id", prompt="Task ID", help="The ID of the task to retrieve.")
def get_task(task_id, horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.get_task(task_id)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# # Update Task
# @click.command(name="update")
# @click.option(
#     "--base_url", default="http://127.0.0.1:5000", help="The base URL for the API."
# )
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option("--task_id", prompt="Task ID", help="The ID of the task to update.")
# @click.option("--description", help="The new description for the task.")
# @click.option("--task_type", help="The new task type for the task.")
# @click.option("--evaluation_dataset", help="The new evaluation datasets for the task.")
# @click.option(
#     "--delete_evaluation_dataset",
#     default=False,
#     is_flag=True,
#     help="Whether to delete the evaluation datasets for the task.",
# )
# @click.option("--status", help="The new status for the task.")
# def update_task(
#     base_url,
#     task_id,
#     horizon_api_key,
#     description=None,
#     task_type=None,
#     status=None,
#     evaluation_dataset=None,
#     delete_evaluation_dataset=None,
# ):
#     client = APIClient(base_url)
#     result = client.update_task(
#         task_id,
#         horizon_api_key,
#         description,
#         task_type,
#         status,
#         evaluation_dataset,
#         delete_evaluation_dataset,
#     )
#     click.echo(result)


# Delete Task
@click.command(name="delete")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option("--task_id", prompt="Task ID", help="The ID of the task to delete.")
def delete_task(task_id, horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.delete_task(task_id)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Get the current prompt of a task
# @click.command(name="get-active-prompt")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option("--task_id", prompt="Task ID", help="The ID of the task.")
# def get_task_curr_prompt(task_id, horizon_api_key):
#     horizon_ai.api_key = horizon_api_key
#     try:
#         result = horizon_ai.get_task_curr_prompt(task_id)
#         click.echo(result)
#     except Exception as e:
#         click.echo(str(e))


# Set the current prompt of a task
# @click.command(name="set-active-prompt")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option("--task_id", prompt="Task ID", help="The ID of the task.")
# @click.option(
#     "--prompt_id",
#     prompt="Prompt ID",
#     help="The ID of the prompt to set as the current prompt for the task.",
# )
# def set_task_curr_prompt(task_id, prompt_id, horizon_api_key):
#     horizon_ai.api_key = horizon_api_key
#     try:
#         result = horizon_ai.set_task_curr_prompt(task_id, prompt_id)
#         click.echo(result)
#     except Exception as e:
#         click.echo(str(e))


# Generate a task
# @click.command(name="generate")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option("--task_id", prompt="Task ID", help="The ID of the task to generate.")
# @click.option(
#     "--objective", prompt="Objective", help="The objective of the task to generate."
# )
# @click.option(
#     "--openai_api_key",
#     default=os.environ.get("OPENAI_API_KEY"),
#     prompt="OpenAI API Key" if not os.environ.get("OPENAI_API_KEY") else False,
#     help="The OpenAI API key for the user.",
# )
# def generate_task(task_id, objective, horizon_api_key, openai_api_key):
#     horizon_ai.api_key = horizon_api_key
#     horizon_ai.openai_api_key = openai_api_key
#     try:
#         result = horizon_ai.generate_task(task_id, objective)
#         click.echo(result)
#     except Exception as e:
#         click.echo(str(e))


# Deploy a task
@click.command(name="deploy")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option("--task_id", prompt="Task ID", help="The ID of the task to deploy.")
@click.option(
    "--inputs", prompt="Inputs", help="The inputs to the task in JSON format."
)
@click.option(
    "--openai_api_key",
    default=os.environ.get("OPENAI_API_KEY"),
    prompt="OpenAI API Key" if not os.environ.get("OPENAI_API_KEY") else False,
    help="The OpenAI API key for the user.",
)
def deploy_task(task_id, inputs, horizon_api_key, openai_api_key):
    horizon_ai.api_key = horizon_api_key
    horizon_ai.openai_api_key = openai_api_key
    try:
        inputs_dict = json.loads(inputs)
        result = horizon_ai.deploy_task(task_id, inputs_dict)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# Upload Evaluation Dataset
# @click.command(name="upload")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option(
#     "--task_id",
#     prompt="Task ID",
#     help="The ID of the task to upload evaluation datasets for.",
# )
# @click.option(
#     "--file_path",
#     prompt="File Path",
#     help="The path to the file containing the evaluation datasets to upload.",
# )
# def upload_evaluation_dataset(task_id, file_path, horizon_api_key):
#     horizon_ai.api_key = horizon_api_key
#     try:
#         result = horizon_ai.upload_evaluation_dataset(task_id, file_path)
#         click.echo(result)
#     except Exception as e:
#         click.echo(str(e))


# View Evaluation Dataset
@click.command(name="view")
@click.option(
    "--horizon_api_key",
    default=os.environ.get("HORIZONAI_API_KEY"),
    prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
    help="The Horizon API key for the user.",
)
@click.option(
    "--task_id",
    prompt="Task ID",
    help="The ID of the task to view evaluation datasets for.",
)
def view_evaluation_dataset(task_id, horizon_api_key):
    horizon_ai.api_key = horizon_api_key
    try:
        result = horizon_ai.view_evaluation_dataset(task_id)
        formatted_output = json.dumps(result, indent=4)
        click.echo(formatted_output)
    except Exception as e:
        click.echo(str(e))


# # Get Evaluation Dataset
# @click.command(name="download")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option(
#     "--task_id",
#     prompt="Task ID",
#     help="The ID of the task to get evaluation datasets for.",
# )
# def get_evaluation_dataset(task_id, horizon_api_key):
#     horizon_ai.api_key = horizon_api_key
#     try:
#         result = horizon_ai.get_evaluation_dataset(task_id)
#         click.echo(result)
#     except Exception as e:
#         click.echo(str(e))


# Delete Evaluation Dataset
# @click.command(name="delete")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option(
#     "--task_id",
#     prompt="Task ID",
#     help="The ID of the task to delete evaluation datasets for.",
# )
# def delete_evaluation_dataset(horizon_api_key, task_id):
#     horizon_ai.api_key = horizon_api_key
#     try:
#         result = horizon_ai.delete_evaluation_dataset(task_id)
#         click.echo(result)
#     except Exception as e:
#         click.echo(str(e))


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
# @click.command(name="get")
# @click.option(
#     "--horizon_api_key",
#     default=os.environ.get("HORIZONAI_API_KEY"),
#     prompt="Horizon API Key" if not os.environ.get("HORIZONAI_API_KEY") else False,
#     help="The Horizon API key for the user.",
# )
# @click.option(
#     "--prompt_id", prompt="Prompt ID", help="The ID of the prompt to retrieve."
# )
# def get_prompt(prompt_id, horizon_api_key):
#     horizon_ai.api_key = horizon_api_key
#     try:
#         result = horizon_ai.get_prompt(prompt_id)
#         formatted_output = json.dumps(result, indent=4)
#         click.echo(formatted_output)
#     except Exception as e:
#         click.echo(str(e))


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
# cli.add_command(prompt)

# User-related commands
user.add_command(register_user)
user.add_command(authenticate_user)
user.add_command(get_user)
# user.add_command(delete_user)

# Project-related commands
project.add_command(list_projects)
project.add_command(create_project)
project.add_command(get_project)
project.add_command(update_project)
project.add_command(delete_project)

# Task-related commands
task.add_command(list_tasks)
task.add_command(generate_task)
task.add_command(get_task)
# task.add_command(get_task_curr_prompt)
# task.add_command(set_task_curr_prompt)
# task.add_command(generate_task)
task.add_command(deploy_task)

# Evaluation Dataset-related commands
# evaluation_dataset.add_command(upload_evaluation_dataset)
evaluation_dataset.add_command(view_evaluation_dataset)
# evaluation_dataset.add_command(get_evaluation_dataset)
# evaluation_dataset.add_command(delete_evaluation_dataset)

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

if __name__ == "__main__":
    cli()
