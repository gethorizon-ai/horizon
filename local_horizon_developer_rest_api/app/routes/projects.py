from flask import request
from flask_restful import Resource, reqparse
from app.models import Project, Task
from app import db, api
from app.routes.users import api_key_required
from sqlalchemy.exc import IntegrityError
from flask_restful import Api


class ListProjectsAPI(Resource):
    @api_key_required
    def get(self):
        projects = Project.query.all()
        return {'projects': [project.to_dict() for project in projects]}, 200


class CreateProjectAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='Project name is required')
        parser.add_argument('user_id', type=int,
                            required=True, help='User ID is required')
        args = parser.parse_args()
        print(args)
        project = Project(name=args['name'], user_id=args['user_id'])

        try:
            db.session.add(project)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Project created successfully", "project": project.to_dict()}, 201


class ProjectAPI(Resource):
    @api_key_required
    def get(self, project_id):
        project = Project.query.get(project_id)
        if not project:
            return {"error": "Project not found"}, 404
        return project.to_dict(), 200

    @api_key_required
    def put(self, project_id):
        project = Project.query.get(project_id)
        if not project:
            return {"error": "Project not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('description', type=str)
        parser.add_argument('status', type=str)
        parser.add_argument('evaluation_datasets', type=str)
        parser.add_argument('delete_evaluation_datasets', type=bool)
        args = parser.parse_args()

        if args['description'] is not None:
            project.description = args['description']
        if args['status'] is not None:
            project.status = args['status']
        if args['evaluation_datasets'] is not None:
            project.evaluation_datasets = args['evaluation_datasets']
        if args['delete_evaluation_datasets']:
            project.evaluation_datasets = None

        db.session.commit()
        return {"message": "Project updated successfully", "project": project.to_dict()}, 200

    @api_key_required
    def delete(self, project_id):
        project = Project.query.get(project_id)
        if not project:
            return {"error": "Project not found"}, 404

        db.session.delete(project)
        db.session.commit()

        return {"message": "Project deleted successfully"}, 200


def register_routes(api):
    api.add_resource(ListProjectsAPI, '/api/projects')
    api.add_resource(CreateProjectAPI, '/api/projects/create')
    api.add_resource(ProjectAPI, '/api/projects/<int:project_id>')
