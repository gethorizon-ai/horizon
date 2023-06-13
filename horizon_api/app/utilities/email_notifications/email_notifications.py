"""Enables sending transactional emails to users."""

import boto3
import html

client = boto3.client("sesv2", region_name="us-west-2")


def email_task_generation_initiated(user_email: str) -> None:
    """Emails user to inform them that their task generation has initiated.

    Args:
        user_email (str): user_email (str): user email address.
    """
    # Configure email parameters
    subject = "Horizon task generation initiated!"
    html_body = f"""
<html>
<body>
Hi,<br />
Success! Task generation initiated. Check your email for the outputs. (It generally takes 30-60 minutes depending on the selected models, data size, and LLM provider latency).<br /><br />
<b>Horizon AI</b>
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
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                },
            },
        },
    )


def email_task_generation_success(user_email: str, task_details: dict) -> None:
    """Emails user to inform them that their task creation request is completed.

    Args:
        user_email (str): user email address.
        task_details (dict): data to share with the user regarding their new task.
    """
    # Parse task details. Escape certain characters (e.g., angle brackets) for use with html
    name = html.escape(str(task_details["name"]))
    objective = html.escape(str(task_details["objective"]))
    task_id = html.escape(str(task_details["id"]))
    project_id = html.escape(str(task_details["project_id"]))
    output_schema = html.escape(str(task_details["output_schema"]))
    number_of_prompt_model_candidates = task_details["evaluation_statistics"][
        "number_of_prompt_model_candidates_considered"
    ]
    number_of_inferences_evaluations_done = task_details["evaluation_statistics"][
        "number_of_inferences_and_evaluations_done"
    ]
    total_estimated_task_generation_cost = task_details["evaluation_statistics"][
        "total_estimated_task_generation_cost"
    ]
    allowed_models = html.escape(str(task_details["allowed_models"]))
    active_prompt_id = task_details["active_prompt_id"]

    # Prepare email text for each prompt object
    email_text_active_prompt = ""
    email_text_non_active_prompts = ""
    for prompt in task_details["prompts"]:
        prompt_id = html.unescape(str(prompt["id"]))
        template_type = html.escape(str(prompt["template_type"]))
        if template_type == "fewshot":
            prefix = html.escape(str(prompt["template_data"]["prefix"])).replace(
                "\n", "<br>"
            )
        elif template_type == "prompt":
            prefix = html.escape(str(prompt["template_data"]["template"])).replace(
                "\n", "<br>"
            )
        input_variables = html.escape(str(prompt["template_data"]["input_variables"]))
        if template_type == "fewshot":
            few_shot_example_selector = html.escape(
                str(prompt["few_shot_example_selector"])
            )
        elif template_type == "prompt":
            few_shot_example_selector = None
        # Parse model name from model parameters (differs for OpenAI vs Anthropic models)
        try:
            model_name = html.escape(str(prompt["model"]["model_name"]))
        except:
            model_name = html.escape(str(prompt["model"]["model"]))
        inference_quality = prompt["inference_statistics"]["inference_quality"]
        inference_cost = prompt["inference_statistics"]["inference_cost"]
        inference_latency = prompt["inference_statistics"]["inference_latency"]

        if prompt_id == active_prompt_id:
            email_text_active_prompt = f"""
<ul>
<li><b>Model:</b> {model_name}</li>
<li><b>Prompt ID:</b> {prompt_id}</li>
<li><b>Template type:</b> {template_type}</li>
<li><b>Template data:</b></li>
    <ul>
    <li><b>Prefix:</b> {prefix}</li>
    <li><b>Input variables:</b> {input_variables}</li>
    <li><b>Few shot example selector:</b> {few_shot_example_selector}</li>
    </ul>
<li><b>Inference quality:</b> {inference_quality:.2f}</li>
<li><b>Inference cost:</b> ${inference_cost:.2f}</li>
<li><b>Inference latency:</b> {inference_latency:.2f}</li>
</ul>
"""
        else:
            email_text_non_active_prompts += f"""
<ul>
<li><b>Model:</b> {model_name}</li>
    <ul>
    <li><b>Prompt ID:</b> {prompt_id}</li>
    <li><b>Inference quality:</b> {inference_quality:.2f}</li>
    <li><b>Inference cost:</b> ${inference_cost:.2f}</li>
    <li><b>Inference latency:</b> {inference_latency:.2f}</li>
    </ul>
</ul>
"""

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
<li><b>Output schema:</b> {output_schema}</li>
<li><b>Task generation statistics:</b></li>
    <ul> 
    <li><b>Number of prompt-model candidates considered:</b> {number_of_prompt_model_candidates}</li>
    <li><b>Number of inferences and evaluations done:</b> {number_of_inferences_evaluations_done}</li>
    <li><b>Total estimated task generation cost:</b> ${total_estimated_task_generation_cost:.2f}</li>
    </ul>
<li><b>Models considered:</b> {allowed_models}</li>
<li><b>Selected prompt-model configuration:</b></li>

<li><b>Other available prompt-model configurations:</b></li>

<li><b>Model selected:</b> {model_name}</li>
<li><b>Template type:</b> {template_type}</li>
<li><b>Template data:</b></li>
    <ul>
    <li><b>Prefix:</b> {prefix}</li>
    <li><b>Input variables:</b> {input_variables}</li>
    <li><b>Few shot example selector:</b> {few_shot_example_selector}</li>
    </ul>
<li><b>Inference statistics:</b></li>
    <ul>
    <li><b>Inference quality:</b> {inference_quality:.2f}</li>
    <li><b>Inference cost:</b> ${inference_cost:.2f}</li>
    <li><b>Inference latency:</b> {inference_latency:.2f}</li>
    </ul>
</ul><br />
<b>Horizon AI</b>
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
                    "Html": {"Data": html_body, "Charset": "UTF-8"},
                },
            },
        },
    )


def email_task_generation_error(user_email: str, error_message: str) -> None:
    """Emails user to inform them that their task creation request failed.

    Args:
        user_email (str): user email address.
        error_message (str): data to share with the user regarding the error with task creation.
    """
    # Configure email parameters
    subject = "Error with your Horizon task request"
    error_message = html.escape(str(error_message))
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
                },
            },
        },
    )


def email_synthetic_data_generation_success(
    user_email: str, synthetic_dataset_url: str
) -> None:
    """Emails user to inform them that their synthetic data generation request is completed.

    Args:
        user_email (str): user email address.
        synthetic_dataset_url: presigned s3 url to download synthetic dataset.
    """
    # Configure email parameters
    subject = "Your Horizon synthetic dataset is ready!"
    html_body = f"""
<html>
<body>
Hi,<br />
Success - your Horizon synthetic dataset has been generated. You can download it <a href={synthetic_dataset_url}>here</a> (link is valid for 1 day). Please email us at team@gethorizon.ai if you need any help.<br /><br />
<b>Horizon AI</b>
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


def email_synthetic_data_generation_error(user_email: str, error_message: str) -> None:
    """Emails user to inform them that their synthetic data generation request failed.

    Args:
        user_email (str): user email address.
        error_message (str): data to share with the user regarding the error with task creation.
    """
    # Configure email parameters
    subject = "Error with your Horizon synthetic data generation request"
    error_message = html.escape(str(error_message))
    text_body = f"""Hello! Unfortunately, your Horizon synthetic data generation request had the following error. Please email us at team@gethorizon.ai if you need help troubleshooting.

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
                },
            },
        },
    )
