# demo.py

import horizon_ai

# Replace 'http://your-api-base-url' with the base URL of your API, for example 'http://127.0.0.1:5000' for local testing
horizon = horizon_ai.APIClient(base_url="http://127.0.0.1:5000")

# Register a new user
register_response = horizon.register_user(
    "testuser_26", "testuser_26@example.com", "testpassword")
print(register_response)
# Extract the user_id from the register_response
user_id = register_response["user_id"]
print("Register response:", register_response)  # Print the register_response

# Authenticate the user
auth_response = horizon.authenticate_user("testuser", "testpassword")
api_key = auth_response["api_key"]

# Get a user's information
# Use the user_id from register_response
get_user_response = horizon.get_user(api_key)
print(get_user_response)

# Test project-related methods
project = horizon.create_project("Test Project", api_key)
print(project)

project_id = project["project"]["id"]
project_info = horizon.get_project(project_id, api_key)
print(project_info)

updated_project = horizon.update_project(
    project_id, api_key, description="New description", status="In progress")
print(updated_project)

# Test tasks-related methods
objective = "Generate the first 1-3 lines of a personalized email to a prospect from the perspective of a sales person at a security tech company"
file_path = "/Users/linatawfik/Documents/horizon/local_horizon_developer_rest_api/demo/data/email_gen_demo.csv"
task = horizon.create_task("Test Task", project_id,
                           "text_generation", objective, file_path, api_key)
print(task)
task_id = task["task_id"]

# task_info = horizon.get_task(task_id, api_key)
# print(task_info)

# upload_response = horizon.upload_evaluation_dataset(
#     task_id, "/Users/linatawfik/Documents/horizon/local_horizon_developer_rest_api/demo/data/email_gen_demo.csv", api_key)
# print(upload_response)

# view_datasets = horizon.view_evaluation_dataset(task_id, api_key)
# print(view_datasets)

# updated_task = horizon.update_task(
#     task_id, api_key, description="New task description", task_type="segmentation", status="In progress")
# print(updated_task)


# Test get_task_curr_prompt
# curr_prompt = horizon.get_task_curr_prompt(task_id, api_key)
# print(curr_prompt)

# Test set_task_curr_prompt
# new_prompt_id = 2  # Replace with a valid prompt ID from your database
# set_curr_prompt = horizon.set_task_curr_prompt(task_id, new_prompt_id, api_key)
# print(set_curr_prompt)


# # define objective and inputs
# objective = "Generate the first 1-3 lines of a personalized email to a prospect from the perspective of a sales person at a security tech company"
inputs = {"name": "Joni Tuominen", "industry": "Sporting Goods", "company": "Rapala VMC", "title": "Vice President, Global Business Development & IT",
          "notes": "They are an experienced leader in the consumer goods industry with expertise in business management, finance, project management, and strategic planning. They are passionate about consumer good brands with great growth\n-5-year anniversary at Rapala VMC is coming up."}


# # Test generate_task
# generated_task = horizon.generate_task(task_id, objective, api_key)
# print(generated_task)

# Test deploy_task
deployed_task = horizon.deploy_task(task_id, inputs, api_key)
print(deployed_task)

######   NEED TO TEST AFTER THIS POINT   #####

# CURRENTLY NOT WORKING!!! NEED TO FIX
# Test update_task
# updated_task = horizon.update_task(
#     task_id, api_key, description="New task description", task_type="segmentation", status="In progress")
# print(updated_task)

# # Test prompt-related methods
# prompt = horizon.create_prompt("Example Prompt", task_id, api_key)
# print(prompt)

# prompt_id = prompt["prompt"]["id"]
# prompt_info = horizon.get_prompt(prompt_id, api_key)
# print(prompt_info)

# updated_prompt = horizon.update_prompt(prompt_id, api_key, status="new status")
# print(updated_prompt)

# generated_prompt = horizon.generate_prompt(
#     objective, prompt_id, api_key)
# print(generated_prompt)

# deployed_prompt = horizon.deploy_prompt(
#     prompt_id, inputs, api_key)
# print(deployed_prompt)


# # Cleanup section
# # Delete prompt
# # delete_prompt = horizon.delete_prompt(prompt_id, api_key)
# # print(delete_prompt)

# # Delete task
# delete_task = horizon.delete_task(task_id, api_key)
# print(delete_task)

# # Delete evaluation datasets
# delete_datasets = horizon.delete_evaluation_dataset(project_id, api_key)
# print(delete_datasets)

# # Delete project
# delete_project = horizon.delete_project(project_id, api_key)
# print(delete_project)

# # Delete user
# delete_user = horizon.delete_user(user_id, api_key)
# print(delete_user)
