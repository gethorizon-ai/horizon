from flask import request
from flask_restful import Resource, reqparse
from app.models import Prompt
from app import db, api
from app.routes.users import api_key_required


class ListPromptsAPI(Resource):
    @api_key_required
    def get(self):
        prompts = Prompt.query.all()
        return {'prompts': [prompt.to_dict() for prompt in prompts]}, 200


class CreatePromptAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='Prompt name is required')
        parser.add_argument('task_id', type=int,
                            required=True, help='Task ID is required')
        args = parser.parse_args()

        prompt = Prompt(name=args['name'], task_id=args['task_id'])
        db.session.add(prompt)
        db.session.commit()

        return {"message": "Prompt created successfully", "prompt": prompt.to_dict()}, 201


class PromptAPI(Resource):
    @api_key_required
    def get(self, prompt_id):
        prompt = Prompt.query.get(prompt_id)
        if not prompt:
            return {"error": "Prompt not found"}, 404
        return prompt.to_dict(), 200

    @api_key_required
    def put(self, prompt_id):
        prompt = Prompt.query.get(prompt_id)
        if not prompt:
            return {"error": "Prompt not found"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('version', type=str)
        parser.add_argument('status', type=str)
        parser.add_argument('source', type=str)
        parser.add_argument('generation_technique', type=str)
        parser.add_argument('prompt_type', type=str)
        parser.add_argument('template', type=str)
        parser.add_argument('variables', type=str)
        parser.add_argument('few_shot_template', type=str)
        parser.add_argument('few_shot_example_selector', type=str)
        parser.add_argument('model', type=str)
        parser.add_argument('evaluation_job_name', type=str)
        args = parser.parse_args()

        if args['version'] is not None:
            prompt.version = args['version']
        if args['status'] is not None:
            prompt.status = args['status']
        if args['source'] is not None:
            prompt.source = args['source']
        if args['generation_technique'] is not None:
            prompt.generation_technique = args['generation_technique']
        if args['prompt_type'] is not None:
            prompt.prompt_type = args['prompt_type']
        if args['template'] is not None:
            prompt.template = args['template']
        if args['variables'] is not None:
            prompt.variables = args['variables']
        if args['few_shot_template'] is not None:
            prompt.few_shot_template = args['few_shot_template']
        if args['few_shot_example_selector'] is not None:
            prompt.few_shot_example_selector = args['few_shot_example_selector']
        if args['model'] is not None:
            prompt.model = args['model']
        if args['evaluation_job_name'] is not None:
            prompt.evaluation_job_name = args['evaluation_job_name']

        db.session.commit()
        return {"message": "Prompt updated successfully", "prompt": prompt.to_dict()}, 200

    @api_key_required
    def delete(self, prompt_id):
        prompt = Prompt.query.get(prompt_id)
        if not prompt:
            return {"error": "Prompt not found"}, 404

        db.session.delete(prompt)
        db.session.commit()

        return {"message": "Prompt deleted successfully"}, 200


def register_routes(api):
    api.add_resource(ListPromptsAPI, '/api/prompts')
    api.add_resource(CreatePromptAPI, '/api/prompts/new')
    api.add_resource(PromptAPI, '/api/prompts/<int:prompt_id>')
