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
    # Convert task details to printable json
    task_details_formatted = json.dumps(task_details, indent=4)

    # Configure email parameters
    subject = "Your Horizon task is ready!"
    text_body = f"""Hello!

Your Horizon task has been successfully created and is ready for deployment. Please see details on it below. You may deploy it by using the task id noted below. Additional information is available at https://docs.gethorizon.ai.

{task_details_formatted}"""

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


def email_task_creation_error(user_email: str, error_message: dict) -> None:
    """Emails user to inform them that their task creation request failed.

    Args:
        user_email (str): user email address.
        task_details (dict): data to share with the user regarding the error with task creation.
    """
    # Configure email parameters
    subject = "Error with your Horizon task request"
    text_body = f"""Hello! Unfortunately, your Horizon task request had the following error. Please reach out to us at team@gethorizon.ai if you need help troubleshooting.

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
