from flask import request, send_file, make_response, g, send_from_directory
from flask_restful import Resource, reqparse
from celery import shared_task
from app.models.component import User, Task, Prompt, Project
from app import db, api
from app.utilities.authentication.api_key_auth import api_key_required
from app.utilities.authentication.cognito_auth import get_user_email
from app.utilities.run import generate_prompt
from app.utilities.run import task_confirmation_details
from app.utilities.dataset_processing import data_check
from app.utilities.output_schema import output_schema as output_schema_util
from app.utilities.email_notifications import email_notifications
from app.deploy.prompt import deploy_prompt
from app.models.llm.factory import LLMFactory
from app.utilities.S3.s3_util import (
    upload_file_to_s3,
    download_file_from_s3,
    download_file_from_s3_and_save_locally,
    delete_file_from_s3,
)
import os
import json
import logging
import datamodel_code_generator
from pathlib import Path
import tempfile
from app.utilities.logging.task_logger import TaskLogger

ALLOWED_EVALUTION_DATASET_EXTENSIONS = {"csv"}
ALLOWED_OUTPUT_SCHEMA_EXTENSIONS = {"json"}


def allowed_evaluation_dataset_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EVALUTION_DATASET_EXTENSIONS
    )


def allowed_output_schema_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_OUTPUT_SCHEMA_EXTENSIONS
    )


class ListTasksAPI(Resource):
    @api_key_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "verbose",
            type=int,
            required=False,
            default=None,
            help="Task ID is required",
        )
        args = parser.parse_args()

        # Fetch tasks associated with user
        tasks = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Project.user_id == g.user.id)
            .all()
        )

        return {
            "message": "Tasks retrieved successfully",
            "tasks": [
                task.to_dict_filtered(verbose_prompt_output=args["verbose"])
                for task in tasks
            ],
        }, 200


class CreateTaskAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "name", type=str, required=True, help="Task name is required"
        )
        parser.add_argument(
            "task_type", type=str, required=True, help="Task type is required"
        )
        parser.add_argument(
            "project_id", type=int, required=True, help="Project ID is required"
        )
        parser.add_argument(
            "allowed_models",
            type=list,
            required=True,
            location="json",
            help="Models allowed to be used for this task",
        )
        args = parser.parse_args()

        # Check that project exists and is associated with user
        project = Project.query.filter_by(
            id=args["project_id"], user_id=g.user.id
        ).first()
        if not project:
            return {"error": "Project not found or not associated with user"}, 400

        # Check that there is at least one allowed model and all are valid
        if len(args["allowed_models"]) == 0:
            return {"error": "At least one allowed model must be provided"}, 400
        for model in args["allowed_models"]:
            if model not in LLMFactory.llm_classes:
                return {
                    "error": f"{args['allowed_models']}\nInvalid model {model} provided as allowed model"
                }, 400

        # Create a new task
        task = Task(
            name=args["name"],
            task_type=args["task_type"],
            project_id=args["project_id"],
            allowed_models=json.dumps(args["allowed_models"]),
        )

        try:
            db.session.add(task)
            db.session.commit()  # Commit the task to the database to obtain its ID

            # # Create a new prompt
            # prompt = Prompt(name=f"{args['name']}_prompt", task_id=task.id)
            # db.session.add(prompt)
            # db.session.commit()  # Commit the prompt to the database to obtain its ID

            # # Assign the prompt_id to the active_prompt_id field of the task
            # task.active_prompt_id = prompt.id
            # db.session.commit()

        except Exception as e:
            db.session.rollback()
            logging.exception("Error occurred while creating task: %s", e)
            return {"error": str(e)}, 400

        return {
            "message": "Task created successfully",
            "task": task.to_dict_filtered(),
        }, 201


class TaskAPI(Resource):
    @api_key_required
    def get(self, task_id):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "verbose",
            type=int,
            required=False,
            default=None,
            help="Task ID is required",
        )
        args = parser.parse_args()

        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404
        return {
            "message": "Task retrieved successfully",
            "task": task.to_dict_filtered(verbose_prompt_output=args["verbose"]),
        }, 200

    @api_key_required
    def put(self, task_id):
        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("objective", type=str)
        parser.add_argument("task_type", type=str)
        parser.add_argument("status", type=str)
        parser.add_argument("evaluation_dataset", type=str)
        args = parser.parse_args()

        if args["objective"] is not None:
            task.objective = args["objective"]
        if args["task_type"] is not None:
            task.task_type = args["task_type"]
        if args["status"] is not None:
            task.status = args["status"]
        if args["evaluation_dataset"] is not None:
            task.evaluation_dataset = args["evaluation_dataset"]
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Task updated successfully",
            "task": task.to_dict_filtered(),
        }, 200

    @api_key_required
    def delete(self, task_id):
        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        try:
            db.session.delete(task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Task deleted successfully"}, 200


class GetActivePromptAPI(Resource):
    @api_key_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "task_id", type=int, required=True, help="Task ID is required"
        )
        args = parser.parse_args()

        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == args["task_id"], Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404
        prompt = Prompt.query.get(task.active_prompt_id)
        if not prompt:
            return {"error": "Prompt not found or not associated with user"}, 404
        return {
            "message": "Active prompt retrieved successfully",
            "prompt": prompt.to_dict_filtered(),
        }, 200


class SetActivePromptAPI(Resource):
    @api_key_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "task_id", type=int, required=True, help="Task ID is required"
        )
        parser.add_argument(
            "prompt_id", type=int, required=True, help="Prompt ID is required"
        )
        args = parser.parse_args()

        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == args["task_id"], Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        # Fetch prompt and check it is associated with task
        prompt = (
            Prompt.query.join(Task, Task.id == Prompt.task_id)
            .filter(Prompt.id == args["prompt_id"], Task.id == task.id)
            .first()
        )
        if not prompt:
            return {"error": "Prompt not found or not associated with user"}, 404

        task.active_prompt_id = prompt.id
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Active prompt updated successfully",
            "task": task.to_dict_filtered(),
        }, 200


class GetTaskConfirmationDetailsAPI(Resource):
    @api_key_required
    def get(self, task_id):
        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        # Call the get_task_confirmation_details function with the task_id
        try:
            task_confirmation_details_response = (
                task_confirmation_details.get_task_confirmation_details(task=task)
            )
        except Exception as e:
            return {"error": str(e)}, 400

        return {
            "message": "Task confirmation details produced",
            "task_confirmation_details": task_confirmation_details_response,
        }, 200


@shared_task(ignore_result=True)
def process_generate_prompt_model_configuration(
    user_objective: str,
    task_id: int,
    openai_api_key: str = None,
    anthropic_api_key: str = None,
) -> None:
    """Runs prompt-model configuration algorithm as background job.

    Emails results of algorithm to user upon completion.

    Args:
        user_objective (str): objective of the use case.
        task_id (int): id corresponding to task record.
        openai_api_key (str, optional): OpenAI API key to use if wanting to consider OpenAI models. Defaults to None.
        anthropic_api_key (str, optional): Anthropic API key to use if wanting to consider Anthropic models. Defaults to None.
    """
    try:
        # Get task, prompt, and user objects, along with user's email address
        task = Task.query.get(task_id)
        # prompt = Prompt.query.get(prompt_id)
        user = (
            User.query.join(Project, Project.user_id == User.id)
            .filter(Project.id == task.project_id)
            .first()
        )
        user_email = get_user_email(username=user.id)

        # Email user that task generation has been initiated
        email_notifications.email_task_generation_initiated(user_email=user_email)

        # Attempt prompt-model configuration algorithm
        task_configuration_dict = generate_prompt.generate_prompt_model_configuration(
            user_objective=user_objective,
            task=task,
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key,
        )

        # If successful, email job results to user
        email_notifications.email_task_generation_success(
            user_email=user_email, task_details=task_configuration_dict
        )
    except Exception as e:
        # If failed, email error details to user
        email_notifications.email_task_generation_error(
            user_email=user_email, error_message=str(e)
        )

        # Delete task if task generation fails
        try:
            db.session.delete(task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400


class GenerateTaskAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "task_id", type=int, required=True, help="Task ID is required"
        )
        parser.add_argument(
            "objective", type=str, required=True, help="Objective is required"
        )
        parser.add_argument(
            "openai_api_key",
            type=str,
            required=False,
            default=None,
            help="OpenAI API key needed to evaluate OpenAI models",
        )
        parser.add_argument(
            "anthropic_api_key",
            type=str,
            required=False,
            default=None,
            help="Anthropic API key needed to evaluate Anthropic models",
        )
        args = parser.parse_args()

        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == args["task_id"], Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        # Call the process_generate_prompt_model_configuration function as a background job with the provided details
        try:
            result_id = process_generate_prompt_model_configuration.delay(
                user_objective=args["objective"],
                task_id=task.id,
                openai_api_key=args["openai_api_key"],
                anthropic_api_key=args["anthropic_api_key"],
            )

        except Exception as e:
            return {"error": str(e)}, 400

        return {
            "message": "Success! Task generation initiated. Check your email for the outputs. (It generally takes 30-60 minutes depending on the selected models, data size, and LLM provider latency).",
        }, 200


class DeployTaskAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "task_id", type=int, required=True, help="Task ID is required"
        )
        parser.add_argument(
            "inputs",
            type=dict,
            required=True,
            help="Input variables are required as a dictionary",
        )
        parser.add_argument(
            "openai_api_key",
            type=str,
            required=True,
            default=None,
            help="Provide OpenAI API key to deploy OpenAI models",
        )
        parser.add_argument(
            "anthropic_api_key",
            type=str,
            required=True,
            default=None,
            help="Provide Anthropic API key to deploy Anthropic models",
        )
        parser.add_argument(
            "log_deployment",
            type=bool,
            required=False,
            default=False,
            help="Set to true to log the deployment. Defaults to false.",
        )
        args = parser.parse_args()

        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == args["task_id"], Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        # Fetch prompt
        if not task.active_prompt_id:
            return {"error": "Active prompt not found for the task"}, 404
        prompt = Prompt.query.get(task.active_prompt_id)
        if not prompt:
            return {"error": "Active prompt does not exist for the task"}, 404

        # Call the deploy function with the active prompt id and provided inputs
        try:
            output = deploy_prompt(
                prompt=prompt,
                input_values=args["inputs"],
                openai_api_key=args["openai_api_key"],
                anthropic_api_key=args["anthropic_api_key"],
                log_deployment=args["log_deployment"],
            )
            return {
                "message": "Task deployed successfully",
                "completion": output,
            }, 200
        except Exception as e:
            return {"error": f"Failed with exception: {str(e)}"}, 400


class UploadEvaluationDatasetsAPI(Resource):
    @api_key_required
    def post(self, task_id):
        logging.info("UploadEvaluationDatasetsAPI: Start processing the request")

        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        if "evaluation_dataset" not in request.files:
            return {"error": f"No file provided"}, 400

        evaluation_dataset = request.files["evaluation_dataset"]

        if not allowed_evaluation_dataset_file(evaluation_dataset.filename):
            return {"error": "Invalid file type. Only CSV files are allowed."}, 400

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
            temp_file_path = temp_file.name
            evaluation_dataset.save(temp_file_path)

        try:
            data_check.check_evaluation_dataset_and_data_length(
                dataset_file_path=temp_file_path
            )
        except Exception as e:
            logging.error(
                f"UploadEvaluationDatasetsAPI: Error in check_evaluation_dataset_and_data_length - {str(e)}"
            )
            os.remove(temp_file_path)  # Delete the temporary file
            return {"error": str(e)}, 400

        s3_key = f"evaluation_datasets/{task_id}/{evaluation_dataset.filename}"
        with open(temp_file_path, "rb") as temp_file:
            upload_file_to_s3(temp_file, s3_key)
        os.remove(temp_file_path)

        task.evaluation_dataset = s3_key

        try:
            db.session.commit()
        except Exception as e:
            logging.error(
                f"UploadEvaluationDatasetsAPI: Error during commit - {str(e)}"
            )
            db.session.rollback()
            return {"error": str(e)}, 400

        logging.info("UploadEvaluationDatasetsAPI: Finished processing the request")
        return {
            "message": "Evaluation datasets uploaded successfully",
            "task": task.to_dict_filtered(),
        }, 200


class ViewEvaluationDatasetsAPI(Resource):
    @api_key_required
    def get(self, task_id):
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        if not task.evaluation_dataset:
            return {
                "error": "No evaluation dataset file associated with this task"
            }, 404

        s3_key = task.evaluation_dataset
        presigned_url = download_file_from_s3(s3_key)

        return {
            "message": "Evaluation dataset retrieved successfully",
            "evaluation_dataset_url": presigned_url,
        }, 200


class DeleteEvaluationDatasetsAPI(Resource):
    @api_key_required
    def delete(self, task_id):
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        if not task.evaluation_dataset:
            return {
                "error": "No evaluation dataset file associated with this task"
            }, 404

        s3_key = task.evaluation_dataset
        delete_file_from_s3(s3_key)

        task.evaluation_dataset = None

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Evaluation datasets deleted successfully",
            "task": task.to_dict_filtered(),
        }, 200


class UploadOutputSchemasAPI(Resource):
    @api_key_required
    def post(self, task_id):
        logging.info("UploadOutputSchemaAPI: Start processing the request")

        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        if "output_schema" not in request.files:
            return {"error": f"No file provided"}, 400

        if not task.evaluation_dataset:
            return {
                "error": "Evaluation dataset must be uploaded before output schema"
            }, 404

        output_schema = request.files["output_schema"]

        if not allowed_output_schema_file(output_schema.filename):
            return {"error": "Invalid file type. Only .json files are allowed."}, 400

        # Store output schema in temp file
        with tempfile.NamedTemporaryFile(delete=False) as output_schema_temp_file:
            output_schema_temp_file.write(output_schema.read())
            output_schema_temp_file_path = output_schema_temp_file.name

        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".py"
        ) as pydantic_model_temp_file:
            pydantic_model_temp_file_path = pydantic_model_temp_file.name

        try:
            # Check and process output schema
            output_schema_util.check_and_process_output_schema(
                output_schema_file_path=output_schema_temp_file_path
            )

            # Convert output schema into Python file with Pydantic model representation
            datamodel_code_generator.generate(
                input_=Path(output_schema_temp_file_path),
                input_file_type="jsonschema",
                output=Path(pydantic_model_temp_file_path),
            )

        except Exception as e:
            logging.error(f"UploadOutputSchemasAPI: Invalid output schema - {str(e)}")
            os.remove(output_schema_temp_file_path)
            os.remove(pydantic_model_temp_file_path)
            return {
                "error": f"UploadOutputSchemasAPI: Invalid output schema - {str(e)}"
            }, 400

        # Check ground truth in evaluation dataset matches output schema
        try:
            dataset_file_path = download_file_from_s3_and_save_locally(
                key=task.evaluation_dataset
            )
            output_schema_util.check_evaluation_dataset_aligns_with_pydantic_model(
                dataset_file_path=dataset_file_path,
                pydantic_model_file_path=pydantic_model_temp_file_path,
            )
            os.remove(path=dataset_file_path)
        except Exception as e:
            logging.error(
                f"UploadOutputSchemasAPI: Ground truth data could not be parsed according to output schema - {str(e)}"
            )
            os.remove(output_schema_temp_file_path)
            os.remove(pydantic_model_temp_file_path)
            return {
                "error": f"UploadOutputSchemasAPI: Ground truth data could not be parsed according to output schema - {str(e)}"
            }, 400

        # Upload output schema to s3 with given filename and extension
        output_schema_s3_key = f"output_schemas/{task_id}/{output_schema.filename}"
        with open(output_schema_temp_file_path, "rb") as output_schema_temp_file:
            upload_file_to_s3(output_schema_temp_file, output_schema_s3_key)
        os.remove(output_schema_temp_file_path)

        # Upload Pydantic model to s3 with given filename converted to Python extension
        pydantic_model_s3_key = f"pydantic_models/{task_id}/{os.path.splitext(output_schema.filename)[0]}.py"
        with open(pydantic_model_temp_file_path, "rb") as pydantic_model_temp_file:
            upload_file_to_s3(pydantic_model_temp_file, pydantic_model_s3_key)
        os.remove(pydantic_model_temp_file_path)

        # Set s3 keys in task object
        task.output_schema = output_schema_s3_key
        task.pydantic_model = pydantic_model_s3_key

        try:
            db.session.commit()
        except Exception as e:
            logging.error(f"UploadOutputSchemasAPI: Error during commit - {str(e)}")
            db.session.rollback()
            return {"error": str(e)}, 400

        logging.info("UploadOutputSchemasAPI: Finished processing the request")
        return {
            "message": "Output schemas uploaded successfully",
            "task": task.to_dict_filtered(),
        }, 200


class DeleteOutputSchemasAPI(Resource):
    @api_key_required
    def delete(self, task_id):
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        if not task.output_schema or not task.pydantic_model:
            return {"error": "No output schema associated with this task"}, 404

        output_schema_s3_key = task.output_schema
        delete_file_from_s3(output_schema_s3_key)
        task.output_schema = None

        pydantic_model_s3_key = task.pydantic_model
        delete_file_from_s3(pydantic_model_s3_key)
        task.pydantic_model = None

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Output schemas deleted successfully",
            "task": task.to_dict_filtered(),
        }, 200


class ViewDeploymentLogsAPI(Resource):
    @api_key_required
    def get(self, task_id):
        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        task_logger = TaskLogger()
        log_file_name = task_logger.get_logs(task_id)

        if not log_file_name:
            return {"error": "Logs not found for this task"}, 404

        s3_key = log_file_name
        presigned_url = download_file_from_s3(s3_key)

        return {
            "message": "Logs retrieved successfully. Please download them using the url provided below (valid for 1 hour).",
            "deployment_logs_url": presigned_url,
        }, 200


def register_routes(api):
    api.add_resource(ListTasksAPI, "/api/tasks")
    api.add_resource(CreateTaskAPI, "/api/tasks/create")
    api.add_resource(TaskAPI, "/api/tasks/<int:task_id>")
    api.add_resource(GetActivePromptAPI, "/api/tasks/get_active_prompt")
    api.add_resource(SetActivePromptAPI, "/api/tasks/set_active_prompt")
    api.add_resource(
        GetTaskConfirmationDetailsAPI,
        "/api/tasks/<int:task_id>/get_task_confirmation_details",
    )
    api.add_resource(GenerateTaskAPI, "/api/tasks/generate")
    api.add_resource(DeployTaskAPI, "/api/tasks/deploy")
    api.add_resource(
        UploadEvaluationDatasetsAPI,
        "/api/tasks/<int:task_id>/upload_evaluation_dataset",
    )
    # api.add_resource(
    #     ViewEvaluationDatasetsAPI, "/api/tasks/<int:task_id>/view_evaluation_dataset"
    # )
    # api.add_resource(
    #     DeleteEvaluationDatasetsAPI,
    #     "/api/tasks/<int:task_id>/delete_evaluation_dataset",
    # )
    api.add_resource(
        UploadOutputSchemasAPI,
        "/api/tasks/<int:task_id>/upload_output_schema",
    )
    # api.add_resource(
    #     DeleteOutputSchemasAPI,
    #     "/api/tasks/<int:task_id>/delete_output_schema",
    # )
    api.add_resource(
        ViewDeploymentLogsAPI, "/api/tasks/<int:task_id>/view_deployment_logs"
    )
