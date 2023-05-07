"""Enables sending transactional emails to users."""

import boto3
import html

client = boto3.client("sesv2", region_name="us-west-2")


def email_task_creation_success(user_email: str, task_details: dict) -> None:
    """Emails user to inform them that their task creation request is completed.

    Args:
        user_email (str): user email address.
        task_details (dict): data to share with the user regarding their new task.
    """

    # Parse task details
    name = html.escape(str(task_details["name"]))
    objective = html.escape(str(task_details["objective"]))
    task_id = html.escape(str(task_details["id"]))
    project_id = html.escape(str(task_details["project_id"]))
    number_of_prompt_model_candidates = task_details["evaluation_statistics"][
        "number_of_prompt_model_candidates_considered"
    ]
    number_of_inferences_evaluations_done = task_details["evaluation_statistics"][
        "number_of_inferences_and_evaluations_done"
    ]
    template_type = html.escape(str(task_details["prompts"][0]["template_type"]))
    if template_type == "fewshot":
        prefix = html.escape(str(task_details["prompts"][0]["template_data"]["prefix"]))
    elif template_type == "prompt":
        prefix = html.escape(
            str(task_details["prompts"][0]["template_data"]["template"])
        )
    # TODO: Remove
    prefix = html.escape(
        str(
            """Please compose a creative opener for a marketing email to <var_name> who is in the <var_industry> sector, employed by <var_company> as <var_title>. Incorporate their name, industry, company, and title together with the following details: <var_notes>.\n\n==\nEXAMPLES:"""
        )
    ).replace("\n", "<br>")
    input_variables = html.escape(
        str(task_details["prompts"][0]["template_data"]["input_variables"])
    )
    if template_type == "fewshot":
        few_shot_example_selector = html.escape(
            str(task_details["prompts"][0]["few_shot_example_selector"])
        )
    elif template_type == "prompt":
        few_shot_example_selector = None
    allowed_models = html.escape(str(task_details["allowed_models"]))
    # Parse model name from model parameters (differs for OpenAI vs Anthropic models)
    try:
        model_name = html.escape(str(task_details["prompts"][0]["model"]["model_name"]))
    except:
        model_name = html.escape(str(task_details["prompts"][0]["model"]["model"]))
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
<li><b>Model selected:</b> {model_name}</li>
<li><b>Inference statistics:</b></li>
    <ul>
    <li><b>Inference quality:</b> {inference_quality:.2f}</li>
    <li><b>Inference latency:</b> {inference_latency:.2f}</li>
    </ul>
</ul><br />
<b>Horizon AI</b>
</body>
</html>"""

    print(html_body)

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


def email_task_creation_error(user_email: str, error_message: str) -> None:
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
                    # "Html": {
                    #     "Data": html_body,
                    #     "Charset": "UTF-8",
                    # },
                },
            },
        },
    )
