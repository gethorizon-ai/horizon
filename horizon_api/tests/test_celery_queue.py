"""Stress tests Celery queue on server by rapidly issuing task generation requests."""

import horizon_ai
from config import Config
import time


def test_celery_queue():
    """Stress tests Celery queue on server by rapidly issuing task generation requests."""
    # Project and task details
    project_name = "Stress test"
    task_name = "Marketing email generation (test)"
    task_type = "Text generation"
    objective = "Generate the first 1-3 lines of a marketing email"
    allowed_models = ["claude-instant-v1"]
    evaluation_data_file_path = "data/data/email_gen_demo.csv"

    # Generate Horizon API key
    test_email = Config.HORIZON_TEST_EMAIL
    test_password = Config.HORIZON_TEST_PASSWORD
    generate_new_api_key_response = horizon_ai.generate_new_api_key(
        test_email, test_password
    )
    test_api_key = generate_new_api_key_response["api_key"]

    horizon_ai.api_key = test_api_key
    horizon_ai.anthropic_api_key = Config.HORIZON_ANTHROPIC_API_KEY

    # Create new project
    create_project_response = horizon_ai.create_project(project_name)
    project_id = create_project_response["project"]["id"]

    # Conduct stress test
    num_requests = 50
    for i in range(num_requests):
        # Create task record
        task_creation_response = horizon_ai.create_task(
            task_name, task_type, project_id, allowed_models
        )
        task_id = task_creation_response["task"]["id"]

        # Upload evaluation dataset
        upload_dataset_response = horizon_ai.upload_evaluation_dataset(
            task_id, evaluation_data_file_path
        )

        # Generate task
        generate_response = horizon_ai.generate_task(task_id, objective)

        # Pause briefly
        time.sleep(1)
