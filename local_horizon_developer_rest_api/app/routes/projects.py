from flask_restful import Resource, reqparse
from app.models import Project, Task
from app import db, api
from app.routes.users import api_key_required
from sqlalchemy.exc import IntegrityError
from flask_restful import Api
from flask import request, send_file, make_response
from io import BytesIO
import os
import csv
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from flask import Response

ALLOWED_EXTENSIONS = {'csv'}


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

        project = Project(name=args['name'], user_id=args['user_id'])

        try:
            db.session.add(project)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        # Check if a file was uploaded
        if 'evaluation_datasets' in request.files:
            file = request.files['evaluation_datasets']
            project.evaluation_datasets = file.read()
            db.session.commit()

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


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class UploadEvaluationDatasetsAPI(Resource):
    @api_key_required
    def post(self, project_id):
        project = Project.query.get(project_id)
        if not project:
            return {"error": "Project not found"}, 404

        if 'evaluation_datasets' not in request.files:
            return {"error": "No file provided"}, 400

        file = request.files['evaluation_datasets']

        if not allowed_file(file.filename):
            return {"error": "Invalid file type. Only CSV files are allowed."}, 400

        project.evaluation_datasets = file.read()
        db.session.commit()

        return {"message": "Evaluation datasets uploaded successfully", "project": project.to_dict()}, 200


class ViewEvaluationDatasetsAPI(Resource):
    @api_key_required
    def get(self, project_id):
        project = Project.query.get(project_id)
        if not project:
            return {"error": "Project not found"}, 404

        if not project.evaluation_datasets:
            return {"error": "No evaluation_datasets file associated with this project"}, 404

        evaluation_datasets_file = BytesIO(project.evaluation_datasets)
        reader = csv.DictReader(
            evaluation_datasets_file.read().decode('utf-8').splitlines())

        evaluation_datasets = [row for row in reader]
        return {"evaluation_datasets": evaluation_datasets}, 200


class EvaluationDatasetsAPI(Resource):
    def get(self, project_id):
        project = Project.query.get(project_id)
        if not project:
            return {"error": "Project not found"}, 404

        if not project.evaluation_datasets:
            return {"error": "No evaluation datasets available"}, 404

        response = make_response(send_file(BytesIO(project.evaluation_datasets),
                                           attachment_filename='evaluation_datasets.csv',
                                           as_attachment=True))
        response.headers['Content-Type'] = 'text/csv'
        return response


def register_routes(api):
    api.add_resource(ListProjectsAPI, '/api/projects')
    api.add_resource(CreateProjectAPI, '/api/projects/create')
    api.add_resource(ProjectAPI, '/api/projects/<int:project_id>')
    api.add_resource(UploadEvaluationDatasetsAPI,
                     '/api/projects/<int:project_id>/upload_evaluation_datasets')
    api.add_resource(ViewEvaluationDatasetsAPI,
                     '/api/projects/<int:project_id>/view_evaluation_datasets')
    api.add_resource(EvaluationDatasetsAPI,
                     '/api/projects/<int:project_id>/evaluation_datasets')
