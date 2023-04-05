from flask import request
from flask_restful import Resource, reqparse
from app.models.component import Prompt
from app import db, api
from app.routes.users import api_key_required
from app.utilities.run.run1 import generate_prompt
from app.deploy.prompt import deploy_prompt


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


class GeneratePromptAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('objective', type=str, required=True,
                            help='Objective is required')
        parser.add_argument('prompt_id', type=int, required=True,
                            help='Prompt ID is required')
        args = parser.parse_args()

        # Call the generate_prompt function with the provided objective and prompt_id
        generated_prompt = generate_prompt(
            args['objective'], args['prompt_id'])
        generated_prompt_dict = generated_prompt
        return {"message": "Prompt generation completed", "generated_prompt": generated_prompt_dict}, 200


class DeployPromptAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('prompt_id', type=int, required=True,
                            help='Prompt ID is required')
        parser.add_argument('api_key', type=str, required=True,
                            help='API key is required')
        parser.add_argument('inputs', type=dict, required=True,
                            help='Input variables are required as a dictionary')
        args = parser.parse_args()

        # Call the deploy function with the provided prompt_id and inputs
        return_value = deploy_prompt(args['prompt_id'], args['inputs'])

        return {"message": "Prompt deployment completed", "return_value": return_value}, 200


def register_routes(api):
    api.add_resource(ListPromptsAPI, '/api/prompts')
    api.add_resource(CreatePromptAPI, '/api/prompts/new')
    api.add_resource(PromptAPI, '/api/prompts/<int:prompt_id>')
    api.add_resource(GeneratePromptAPI, '/api/prompts/generate')
    api.add_resource(DeployPromptAPI, '/api/prompts/deploy')
