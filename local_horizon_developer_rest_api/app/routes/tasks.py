from flask import request
from flask_restful import Resource, reqparse
from app.models.component import Task
from app import db, api
from app.routes.users import api_key_required


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

        task = Task(
            name=args['name'], task_type=args['task_type'], project_id=args['project_id'])
        db.session.add(task)
        db.session.commit()

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
        args = parser.parse_args()

        if args['description'] is not None:
            task.description = args['description']
        if args['task_type'] is not None:
            task.task_type = args['task_type']
        if args['status'] is not None:
            task.status = args['status']

        db.session.commit()
        return {"message": "Task updated successfully", "task": task.to_dict()}, 200

    @api_key_required
    def delete(self, task_id):
        task = Task.query.get(task_id)
        if not task:
            return {"error": "Task not found"}, 404

        db.session.delete(task)
        db.session.commit()

        return {"message": "Task deleted successfully"}, 200


def register_routes(api):
    api.add_resource(ListTasksAPI, '/api/tasks')
    api.add_resource(CreateTaskAPI, '/api/tasks/create')
    api.add_resource(TaskAPI, '/api/tasks/<int:task_id>')
