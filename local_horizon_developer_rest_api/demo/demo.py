# demo.py

# Replace 'http://your-api-base-url' with the base URL of your API, for example 'http://127.0.0.1:5000' for local testing
import horizon_ai

horizon = horizon_ai.APIClient(base_url="http://127.0.0.1:5000")



# Register a new user
register_response = horizon.register_user(
    "ltawfik", "ltawfik@horizonai.com", "123TestPassword!45"
)
print(register_response)


# Extract the user_id from the register_response
user_id = register_response["user_id"]

# Authenticate the user
auth_response = horizon.authenticate_user("ltawfik", "123TestPassword!45")
auth_response = horizon.authenticate_user("ltawfik", "123TestPassword!45")
api_key = auth_response["api_key"]

# Create Project
project = horizon.create_project("Test Project", api_key)
project_id = project["project"]["id"]


# Create a task
objective = "Generate the first 1-3 lines of a personalized marketing email"
file_path = "./data/email_gen_demo.csv"
task = horizon.create_task("Test Task", project_id,
                           "text_generation", objective, file_path, api_key)
task_id = task["task_id"]

# Deploy a task
inputs = {"name": "John", "industry": "Sporting Goods", "company": "Nike", "title": "VP of Marketing",
          "notes": "They are experienced in marketing and sales and recently got promoted to VP of Marketing after 10 year of working at Nike."}

deployed_task = horizon.deploy_task(task_id, inputs, api_key)


# # Cleanup section
# # Delete prompt
# # delete_prompt = horizon.delete_prompt(prompt_id, api_key)
# # print(delete_prompt)
# # Cleanup section
# # Delete prompt
# # delete_prompt = horizon.delete_prompt(prompt_id, api_key)
# # print(delete_prompt)

# # Delete task
# delete_task = horizon.delete_task(task_id, api_key)
# print(delete_task)
# # Delete task
# delete_task = horizon.delete_task(task_id, api_key)
# print(delete_task)

# # Delete evaluation datasets
# delete_datasets = horizon.delete_evaluation_dataset(project_id, api_key)
# print(delete_datasets)
# # Delete evaluation datasets
# delete_datasets = horizon.delete_evaluation_dataset(project_id, api_key)
# print(delete_datasets)

# # Delete project
# delete_project = horizon.delete_project(project_id, api_key)
# print(delete_project)
# # Delete project
# delete_project = horizon.delete_project(project_id, api_key)
# print(delete_project)

# # Delete user
# delete_user = horizon.delete_user(user_id, api_key)
# print(delete_user)
# # Delete user
# delete_user = horizon.delete_user(user_id, api_key)
# print(delete_user)
