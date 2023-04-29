from flask import request, send_file, make_response, g
from flask_restful import Resource, reqparse
from app.models.component import Task, Prompt, Project
from app import db, api
from app.utilities.authentication.api_key_auth import api_key_required
from app.utilities.run import generate_prompt
from app.utilities.run import task_confirmation_details
from app.utilities.dataset_processing import dataset_processing
from app.deploy.prompt import deploy_prompt
from app.models.llm.factory import LLMFactory
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from flask_restful import Resource, reqparse
import json
from app.utilities.context import RequestContext


ALLOWED_EXTENSIONS = {"csv"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


class ListTasksAPI(Resource):
    @api_key_required
    def get(self):
        # Fetch tasks associated with user
        tasks = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Project.user_id == g.user.id)
            .all()
        )

        return {
            "message": "Tasks retrieved successfully",
            "tasks": [task.to_dict_filtered() for task in tasks],
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

            # Create a new prompt
            prompt = Prompt(name=f"{args['name']}_prompt", task_id=task.id)
            db.session.add(prompt)
            db.session.commit()  # Commit the prompt to the database to obtain its ID

            # Assign the prompt_id to the active_prompt_id field of the task
            task.active_prompt_id = prompt.id
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Task created successfully",
            "task": task.to_dict_filtered(),
        }, 201


class TaskAPI(Resource):
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
        return {
            "message": "Task retrieved successfully",
            "task": task.to_dict_filtered(),
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


class GetCurrentPromptAPI(Resource):
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
            "message": "Prompt retrieved successfully",
            "prompt": prompt.to_dict_filtered(),
        }, 200


class SetCurrentPromptAPI(Resource):
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

        # Fetch task and check it is associated with task
        prompt = (
            Prompt.query.join(Task)
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
            "message": "Current prompt updated successfully",
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
                task_confirmation_details.get_task_confirmation_details(
                    task=task)
            )
        except Exception as e:
            return {"error": str(e)}, 400

        return {
            "message": "Task confirmation details produced",
            "task_confirmation_details": task_confirmation_details_response,
        }, 200


user_executors = {}


def process_generate_prompt_model_configuration(
    user_objective: str,
    task: Task,
    prompt: Prompt,
    openai_api_key: str,
    anthropic_api_key: str,
):
    return generate_prompt.generate_prompt_model_configuration(
        user_objective=user_objective,
        task=task,
        prompt=prompt,
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key,
    )


class GenerateTaskAPI(Resource):
    @api_key_required
    def post(self, g):
        from app import create_app
        app_instance = create_app()
        with app_instance.app_context():
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
                help="OpenAI API needed to evaluate OpenAI models",
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

            # Fetch prompt
            if not task.active_prompt_id:
                return {"error": "Active prompt not found for the task"}, 404
            prompt = Prompt.query.get(task.active_prompt_id)
            if not prompt:
                return {"error": "Active prompt does not exist for the task"}, 404

            # Extract the user's hashed API key from the g variable
            api_key_hash = g.user.api_key_hash

            if api_key_hash not in user_executors:
                user_executors[api_key_hash] = ThreadPoolExecutor(
                    max_workers=5)

            # Call the process_generate_prompt_model_configuration function with the provided objective and prompt_id
            future = user_executors[api_key_hash].submit(
                process_generate_prompt_model_configuration,
                args["objective"],
                task,
                prompt,
                args["openai_api_key"],
                args["anthropic_api_key"],
            )

            try:
                generated_prompt = future.result()
                generated_prompt_dict = generated_prompt
            except Exception as e:
                return {"error": str(e)}, 400

            return {
                "message": "Task generation completed",
                "generated_prompt": generated_prompt_dict,
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
        # Fetch task and check it is associated with user
        task = (
            Task.query.join(Project, Project.id == Task.project_id)
            .filter(Task.id == task_id, Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        if "evaluation_dataset" not in request.files:
            return {"error": f"No file provided\n{request.files}"}, 400

        # Get the current working directory (your project folder)
        project_dir = os.getcwd()

        evaluation_dataset = request.files["evaluation_dataset"]

        if not allowed_file(evaluation_dataset.filename):
            return {"error": "Invalid file type. Only CSV files are allowed."}, 400

        # Create the file path to store the CSV file in the data folder
        file_path = os.path.join(
            project_dir, "data", evaluation_dataset.filename)

        # Save the file to the file path
        evaluation_dataset.save(file_path)

        # Check validity of evaluation dataset
        try:
            dataset_processing.check_evaluation_dataset_and_data_length(
                dataset_file_path=file_path
            )
        except Exception as e:
            # If invalid dataset, remove file from storage and return error
            os.remove(path=file_path)
            return {"error": str(e)}, 400

        task.evaluation_dataset = file_path
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Evaluation datasets uploaded successfully",
            "task": task.to_dict_filtered(),
        }, 200


class ViewEvaluationDatasetsAPI(Resource):
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

        if not task.evaluation_dataset:
            return {
                "error": "No evaluation dataset file associated with this task"
            }, 404

        with open(
            task.evaluation_dataset, "r", encoding="utf-8"
        ) as evaluation_dataset_file:
            reader = csv.DictReader(evaluation_dataset_file)
            evaluation_dataset = [row for row in reader]

        return {
            "message": "Evaluation dataset retrieved successfully",
            "evaluation_dataset": evaluation_dataset,
        }, 200


class EvaluationDatasetsAPI(Resource):
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

        if not task.evaluation_dataset:
            return {"error": "No evaluation datasets available"}, 404

        response = make_response(
            send_file(
                task.evaluation_dataset,
                attachment_filename="evaluation_dataset.csv",
                as_attachment=True,
            )
        )
        response.headers["Content-Type"] = "text/csv"
        return response


class DeleteEvaluationDatasetsAPI(Resource):
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

        if not task.evaluation_dataset:
            return {
                "error": "No evaluation dataset file associated with this task"
            }, 404

        os.remove(path=task.evaluation_dataset)
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


def register_routes(api):
    api.add_resource(ListTasksAPI, "/api/tasks")
    api.add_resource(CreateTaskAPI, "/api/tasks/create")
    api.add_resource(TaskAPI, "/api/tasks/<int:task_id>")
    api.add_resource(GetCurrentPromptAPI, "/api/tasks/get_curr_prompt")
    # api.add_resource(SetCurrentPromptAPI, "/api/tasks/set_curr_prompt")
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
    api.add_resource(
        ViewEvaluationDatasetsAPI, "/api/tasks/<int:task_id>/view_evaluation_dataset"
    )
    api.add_resource(
        EvaluationDatasetsAPI, "/api/tasks/<int:task_id>/evaluation_dataset"
    )
    api.add_resource(
        DeleteEvaluationDatasetsAPI,
        "/api/tasks/<int:task_id>/delete_evaluation_dataset",
    )
