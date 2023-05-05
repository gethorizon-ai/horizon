"""Script to deploy tasks for Tome demo."""

import horizon_ai
import dotenv
import os

dotenv.load_dotenv()
horizon_ai.api_key = os.getenv("HORIZON_API_KEY")
horizon_ai.openai_api_key = os.getenv("OPENAI_API_KEY")
horizon_ai.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

# Horizon task IDs
corporate_content_task_id = 113
corporate_title_task_id = 114

# Get user's request for Tome page
user_request = input("WHAT PAGE DO YOU WANT TO CREATE? ")
task_request = {"request": user_request}

# Deploy tasks
title = horizon_ai.deploy_task(task_id=corporate_title_task_id, inputs=task_request)[
    "completion"
]
content = horizon_ai.deploy_task(
    task_id=corporate_content_task_id, inputs=task_request
)["completion"]

# Print outputs
print("=====\nRESULTS:")
print(f"Title: {title}")
print(f"Content: {content}")
