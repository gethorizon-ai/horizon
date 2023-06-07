from flask_restful import Resource, reqparse
from app.models.component.project import Project
from app.utilities.authentication.api_key_auth import api_key_required
from app import db
from sqlalchemy.exc import IntegrityError
from flask import g

ALLOWED_EXTENSIONS = {"csv"}


class ListProjectsAPI(Resource):
    @api_key_required
    def get(self):
        projects = Project.query.filter_by(user_id=g.user.id).all()
        return {
            "message": "Projects retrieved successfully",
            "projects": [project.to_dict_filtered() for project in projects],
        }, 200


class CreateProjectAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "name", type=str, required=True, help="Project name is required"
        )
        args = parser.parse_args()

        project = Project(name=args["name"], user_id=g.user.id)

        try:
            db.session.add(project)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Project created successfully",
            "project": project.to_dict_filtered(),
        }, 201


class ProjectAPI(Resource):
    @api_key_required
    def get(self, project_id):
        project = Project.query.filter_by(
            user_specific_id=project_id,
            user_id=g.user.id,
        ).first()
        if not project:
            return {"error": "Project not found or not associated with user"}, 404
        return project.to_dict_filtered(), 200

    @api_key_required
    def put(self, project_id):
        project = Project.query.filter_by(
            user_specific_id=project_id,
            user_id=g.user.id,
        ).first()
        if not project:
            return {"error": "Project not found or not associated with user"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("description", type=str)
        parser.add_argument("status", type=str)
        args = parser.parse_args()

        if args["description"] is not None:
            project.description = args["description"]
        if args["status"] is not None:
            project.status = args["status"]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Project updated successfully",
            "project": project.to_dict_filtered(),
        }, 200

    @api_key_required
    def delete(self, project_id):
        project = Project.query.filter_by(
            user_specific_id=project_id,
            user_id=g.user.id,
        ).first()
        if not project:
            return {"error": "Project not found or not associated with user"}, 404

        try:
            db.session.delete(project)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Project deleted successfully"}, 200


def register_routes(api):
    api.add_resource(ListProjectsAPI, "/api/projects")
    api.add_resource(CreateProjectAPI, "/api/projects/create")
    api.add_resource(ProjectAPI, "/api/projects/<int:project_id>")


# curl - X GET - H "Content-Type: application/json" - H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" http: // 54.188.108.247: 5000/api/projects
# curl - X POST - H "Content-Type: application/json" - H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" - d '{"name": "Example Project"}' http: // 54.188.108.247: 5000/api/projects/create
# curl - X GET - H "Content-Type: application/json" - H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" http: // 54.188.108.247: 5000/api/projects/<project_id >
# curl - X PUT - H "Content-Type: application/json" - H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" - d '{"description": "Updated description", "status": "Updated status"}' http: // 54.188.108.247: 5000/api/projects/<project_id >
# curl - X DELETE - H "Content-Type: application/json" - H "X-Api-Key: 44d244b5-d8a9-4b06-94f9-3a57c7d1f805" http: // 54.188.108.247: 5000/api/projects/<project_id >
