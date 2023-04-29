from flask import request, send_file, make_response, g
from flask_restful import Resource, reqparse
from app.models.component import Task, Prompt
from app import db, api
from app.routes.users import api_key_required
from app.utilities.run.run1 import generate_prompt
from app.deploy.prompt import deploy_prompt
import os
import csv
from concurrent.futures import ThreadPoolExecutor
from flask_restful import Resource, reqparse
import logging


ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ListTasksAPI(Resource):
    @api_key_required
    def get(self):
        tasks = Task.query.all()
        return {'tasks': [task.to_dict() for task in tasks]}, 200


class CreateTaskAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='Task name is required')
        parser.add_argument('task_type', type=str,
                            required=True, help='Task type is required')
        parser.add_argument('project_id', type=int,
                            required=True, help='Project ID is required')
        args = parser.parse_args()

        # Create a new task
        task = Task(
            name=args['name'], task_type=args['task_type'], project_id=args['project_id'])

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
            logging.exception("Error occurred while creating task: %s", e)
            return {"error": str(e)}, 400

        return {"message": "Task created successfully", "task": task.to_dict()}, 201


class TaskAPI(Resource):
    @api_key_required
    def get(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404
        return task.to_dict(), 200

    @api_key_required
    def put(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404
        parser = reqparse.RequestParser()
        parser.add_argument('description', type=str)
        parser.add_argument('task_type', type=str)
        parser.add_argument('status', type=str)
        parser.add_argument('evaluation_data', type=str)
        args = parser.parse_args()

        if args['description'] is not None:
            task.description = args['description']
        if args['task_type'] is not None:
            task.task_type = args['task_type']
        # if args['status'] is not None:
        #     try:
        #         task.status = TaskStatus(args['status'])
        #     except ValueError:
        #         return {"error": "Invalid task status"}, 400
        if args['evaluation_data'] is not None:
            task.evaluation_data = args['evaluation_dataset']

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Task updated successfully", "task": task.to_dict()}, 200

    @api_key_required
    def delete(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        try:
            db.session.delete(task)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Task deleted successfully"}, 200


class GetCurrentPromptAPI(Resource):
    @api_key_required
    def get(self, task_id):
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', type=int, required=True,
                            help='Task ID is required')
        args = parser.parse_args()

        task = Task.query.get(args['task_id'])
        if not task:
            return {"error": "Task not found"}, 404
        prompt = Prompt.query.get(task.active_prompt_id)
        if not prompt:
            return {"error": "Prompt not found"}, 404
        return prompt.to_dict(), 200


class SetCurrentPromptAPI(Resource):
    @api_key_required
    def put(self, task_id):
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', type=int, required=True,
                            help='Task ID is required')
        args = parser.parse_args()

        task = Task.query.get(args['task_id'])
        if not task:
            return {"error": "Task not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('prompt_id', type=int,
                            required=True, help='Prompt ID is required')
        args = parser.parse_args()

        prompt = Prompt.query.get(args['prompt_id'])
        if not prompt:
            return {"error": "Prompt not found"}, 404

        task.active_prompt_id = args['prompt_id']
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Current prompt updated successfully", "task": task.to_dict()}, 200


user_executors = {}


def process_generate_prompt(task, objective):
    return generate_prompt(task.active_prompt_id, objective)


class GenerateTaskAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', type=int, required=True,
                            help='Task ID is required')
        parser.add_argument('objective', type=str, required=True,
                            help='Objective is required')
        args = parser.parse_args()

        task = Task.query.get(args['task_id'])
        if not task:
            return {"error": "Task not found"}, 404

        if not task.active_prompt_id:
            return {"error": "Active prompt not found for the task"}, 404

        # Extract the API key from the g variable
        api_key = g.user.api_key

        if api_key not in user_executors:
            user_executors[api_key] = ThreadPoolExecutor(max_workers=5)

        # Call the process_generate_prompt function with the provided objective and prompt_id
        future = user_executors[api_key].submit(
            process_generate_prompt, task, args['objective'])

        try:
            generated_prompt = future.result()
            generated_prompt_dict = generated_prompt
        except Exception as e:
            return {"error": str(e)}, 400

        return {"message": "Task generation completed", "generated_prompt": generated_prompt_dict}, 200


class DeployTaskAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('task_id', type=int, required=True,
                            help='Task ID is required')
        parser.add_argument('inputs', type=dict, required=True,
                            help='Input variables are required as a dictionary')
        args = parser.parse_args()

        task = Task.query.get(args['task_id'])
        if not task:
            return {"error": "Task not found"}, 404
        if not task.active_prompt_id:
            return {"error": "Active prompt not found for the task"}, 404

        # Call the deploy function with the provided task.active_prompt_id and inputs
        return_value = deploy_prompt(task.active_prompt_id, args['inputs'])
        return {"completion": return_value}, 200


class UploadEvaluationDatasetsAPI(Resource):
    @api_key_required
    def post(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        if 'evaluation_dataset' not in request.files:
            return {"error": "No file provided"}, 400
        # Get the current working directory (your project folder)
        project_dir = os.getcwd()

        evaluation_dataset = request.files['evaluation_dataset']

        if not allowed_file(evaluation_dataset.filename):
            return {"error": "Invalid file type. Only CSV files are allowed."}, 400

        # Create the file path to store the CSV file in the data folder
        file_path = os.path.join(
            project_dir, 'data', evaluation_dataset.filename)

        # Save the file to the file path
        evaluation_dataset.save(file_path)

        task.evaluation_dataset = file_path
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Evaluation datasets uploaded successfully", "task": task.to_dict()}, 200


class ViewEvaluationDatasetsAPI(Resource):
    @api_key_required
    def get(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        if not task.evaluation_dataset:
            return {"error": "No evaluation_dataset file associated with this task"}, 404

        with open(task.evaluation_dataset, 'r', encoding='utf-8') as evaluation_dataset_file:
            reader = csv.DictReader(evaluation_dataset_file)
            evaluation_dataset = [row for row in reader]

        return {"evaluation_dataset": evaluation_dataset}, 200


class EvaluationDatasetsAPI(Resource):
    @api_key_required
    def get(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        if not task.evaluation_dataset:
            return {"error": "No evaluation datasets available"}, 404

        response = make_response(send_file(task.evaluation_dataset,
                                           attachment_filename='evaluation_dataset.csv',
                                           as_attachment=True))
        response.headers['Content-Type'] = 'text/csv'
        return response


class DeleteEvaluationDatasetsAPI(Resource):
    @api_key_required
    def delete(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        if not task.evaluation_dataset:
            return {"error": "No evaluation_dataset file associated with this task"}, 404

        task.evaluation_dataset = None
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Evaluation datasets deleted successfully", "task": task.to_dict()}, 200


def register_routes(api):
    api.add_resource(ListTasksAPI, '/api/tasks')
    api.add_resource(CreateTaskAPI, '/api/tasks/create')
    api.add_resource(TaskAPI, '/api/tasks/<int:task_id>')
    api.add_resource(GetCurrentPromptAPI,
                     '/api/tasks/get_curr_prompt')
    api.add_resource(SetCurrentPromptAPI,
                     '/api/tasks/set_curr_prompt')
    api.add_resource(GenerateTaskAPI, '/api/tasks/generate')
    api.add_resource(DeployTaskAPI, '/api/tasks/deploy')
    api.add_resource(UploadEvaluationDatasetsAPI,
                     '/api/tasks/<int:task_id>/upload_evaluation_dataset')
    api.add_resource(ViewEvaluationDatasetsAPI,
                     '/api/tasks/<int:task_id>/view_evaluation_dataset')
    api.add_resource(EvaluationDatasetsAPI,
                     '/api/tasks/<int:task_id>/evaluation_dataset')
    api.add_resource(DeleteEvaluationDatasetsAPI,
                     '/api/tasks/<int:task_id>/delete_evaluation_dataset')

# # ListTasksAPI
# curl -X GET -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" http://54.188.108.247:5000/api/tasks

# # CreateTaskAPI
# curl -X POST -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" -d '{"name": "<name>", "task_type": "<task_type>", "project_id": <project_id>}' http://54.188.108.247:5000/api/tasks/create

# # TaskAPI - GET
# curl -X GET -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" http://54.188.108.247:5000/api/tasks/<task_id>

# # TaskAPI - PUT
# curl -X PUT -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" -d '{"description": "<description>", "task_type": "<task_type>", "status": "<status>", "evaluation_data": "<evaluation_data>"}' http://54.188.108.247:5000/api/tasks/<task_id>

# # TaskAPI - DELETE
# curl -X DELETE -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" http://54.188.108.247:5000/api/tasks/<task_id>

# # GetCurrentPromptAPI
# curl -X GET -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" -d '{"task_id": <task_id>}' http://54.188.108.247:5000/api/tasks/get_curr_prompt

# # SetCurrentPromptAPI
# curl -X PUT -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" -d '{"task_id": <task_id>, "prompt_id": <prompt_id>}' http://54.188.108.247:5000/api/tasks/set_curr_prompt


# Upload evaluation dataset
# curl - X POST - H "Content-Type: multipart/form-data" - H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" - F "file=@/path/to/your/file.csv" http: // 54.188.108.247: 5000/api/tasks/1/upload_evaluation_dataset


# # # GenerateTaskAPI
# curl - X POST - H "Content-Type: application/json" - H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" - d '{"task_id": 2, "objective": "Generate the title for a slide that addresses the request and is targeted for elementary school students"}' http: // 54.188.108.247: 5000/api/tasks/generate

# # DeployTaskAPI
# curl -X POST -H "Content-Type: application/json" -H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3
