"""Enables sending transactional emails to users."""

import boto3
import json

client = boto3.client("sesv2")


def email_task_creation_success(user_email: str, task_details: dict) -> None:
    """Emails user to inform them that their task creation request is completed.

    Args:
        user_email (str): user email address.
        task_details (dict): data to share with the user regarding their new task in JSON format.
    """
    # Parse task details
    name = task_details["name"]
    objective = task_details["objective"]
    task_id = task_details["id"]
    project_id = task_details["project_id"]
    number_of_prompt_model_candidates = task_details["evaluation_statistics"][
        "number_of_prompt_model_candidates_considered"
    ]
    number_of_inferences_evaluations_done = task_details["evaluation_statistics"][
        "number_of_inferences_and_evaluations_done"
    ]
    template_type = task_details["prompts"][0]["template_type"]
    if template_type == "fewshot":
        prefix = task_details["prompts"][0]["template_data"]["prefix"]
    elif template_type == "prompt":
        prefix = task_details["prompts"][0]["template_data"]["template"]
    input_variables = task_details["prompts"][0]["template_data"]["input_variables"]
    if template_type == "fewshot":
        few_shot_example_selector = task_details["prompts"][0][
            "few_shot_example_selector"
        ]
    elif template_type == "prompt":
        few_shot_example_selector = None
    allowed_models = task_details["allowed_models"]
    # Parse model name from model parameters (differs for OpenAI vs Anthropic models)
    try:
        model_name = task_details["prompts"][0]["model"]["model_name"]
    except:
        model_name = task_details["prompts"][0]["model"]["model"]
    inference_quality = task_details["prompts"][0]["inference_statistics"][
        "inference_quality"
    ]
    inference_latency = task_details["prompts"][0]["inference_statistics"][
        "inference_latency"
    ]

    # Configure email parameters
    subject = "Your Horizon task is ready!"
    html_body = f"""
<html>
<body>
Hi,<br />
Success - your Horizon Task has completed optimization and is ready for deployment.<br />
Simply refer to the "task id" below to deploy (more information in our <a href="https://docs.gethorizon.ai">docs</a>).<br /><br />

Summary of Task below (access additional details via CLI):<br />
<ul>
<li><b>Name:</b> {name}</li>
<li><b>Objective:</b> {objective}</li>
<li><b>Task ID:</b> {task_id}</li>
<li><b>Project ID:</b> {project_id}</li>
<li><b>Evaluation statistics:</b></li>
    <ul> 
    <li><b>Number of prompt-model candidates considered:</b> {number_of_prompt_model_candidates}</li>
    <li><b>Number of inferences and evaluations done:</b> {number_of_inferences_evaluations_done}</li>
    </ul>
<li><b>Template type:</b> {template_type}</li>
<li><b>Template data:</b></li>
    <ul> 
    <li><b>Prefix:</b> {prefix}</li>
    <li><b>Input variables:</b> {input_variables}</li>
    <li><b>Few shot example selector:</b> {few_shot_example_selector}</li>
    </ul>
<li><b>Models considered:</b> {allowed_models}</li>
<li><b>Model:</b> {model_name}</li>
<li><b>Inference statistics:</b></li>
    <ul> 
    <li><b>Inference quality:</b> {inference_quality:.2f}</li>
    <li><b>Inference latency:</b> {inference_latency:.2f}</li>
    </ul>
</ul>
</body>
</html>"""

    # Send email
    response = client.send_email(
        FromEmailAddress="noreply@gethorizon.ai",
        Destination={
            "ToAddresses": [
                user_email,
            ],
        },
        Content={
            "Simple": {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    # "Text": {"Data": text_body, "Charset": "UTF-8"},
                    "Html": {
                        "Data": html_body,
                        "Charset": "UTF-8",
                    },
                },
            },
        },
    )


def email_task_creation_error(user_email: str, error_message: dict) -> None:
    """Emails user to inform them that their task creation request failed.

    Args:
        user_email (str): user email address.
        task_details (dict): data to share with the user regarding the error with task creation.
    """
    # Configure email parameters
    subject = "Error with your Horizon task request"
    text_body = f"""Hello! Unfortunately, your Horizon task request had the following error. Please email us at team@gethorizon.ai if you need help troubleshooting.

{error_message}"""

    # Send email
    response = client.send_email(
        FromEmailAddress="noreply@gethorizon.ai",
        Destination={
            "ToAddresses": [
                user_email,
            ],
        },
        Content={
            "Simple": {
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": text_body, "Charset": "UTF-8"},
                    # "Html": {
                    #     "Data": html_body,
                    #     "Charset": "UTF-8",
                    # },
                },
            },
        },
    )
