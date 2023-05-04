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
Simply refer to the "task id" below to deploy (more information <a href="https://docs.gethorizon.ai">here</a>).<br /><br />

Summary of Task below (access additional details via CLI):<br /><br />

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
<li><b>Model:</b> {model_name}</li>
<li><b>Inference statistics:</b></li>
    <ul> 
    <li><b>Inference quality:</b> {inference_quality:02d}</li>
    <li><b>Inference latency:</b> {inference_latency:02d}</li>
    </ul>
</ul><br /><br />


<img src="data:image/png;base64,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">
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
