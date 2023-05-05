from flask import g
from flask_restful import Resource, reqparse
from app.models.component import Prompt, Task, Project
from app import db
from app.utilities.authentication.api_key_auth import api_key_required
from app.utilities.run.generate_prompt import generate_prompt_model_configuration
from app.deploy.prompt import deploy_prompt


class ListPromptsAPI(Resource):
    @api_key_required
    def get(self):
        # Fetch prompts associated with user
        prompts = (
            Prompt.query.join(Task, Task.id == Prompt.task_id)
            .join(Project)
            .filter(Project.user_id == g.user.id)
            .all()
        )
        return {"prompts": [prompt.to_dict() for prompt in prompts]}, 200


class CreatePromptAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "name", type=str, required=True, help="Prompt name is required"
        )
        parser.add_argument(
            "task_id", type=int, required=True, help="Task ID is required"
        )
        args = parser.parse_args()

        # Check that task exists and is associated with user
        task = (
            Task.query.join(Project)
            .filter(Task.id == args["task_id"], Project.user_id == g.user.id)
            .first()
        )
        if not task:
            return {"error": "Task not found or not associated with user"}, 404

        # Create prompt and associate with given task id
        prompt = Prompt(name=args["name"], task_id=args["task_id"])

        try:
            db.session.add(prompt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400
        return {
            "message": "Prompt created successfully",
            "prompt": prompt.to_dict(),
        }, 201


class PromptAPI(Resource):
    @api_key_required
    def get(self, prompt_id):
        # Fetch prompt and check it is associated with user
        prompt = (
            Prompt.query.join(Task, Task.id == Prompt.task_id)
            .join(Project)
            .filter(Prompt.id == prompt_id, Project.user_id == g.user.id)
            .first()
        )
        if not prompt:
            return {"error": "Prompt not found or not associated with user"}, 404
        return prompt.to_dict(), 200

    @api_key_required
    def put(self, prompt_id):
        # Fetch prompt and check it is associated with user
        prompt = (
            Prompt.query.join(Task, Task.id == Prompt.task_id)
            .join(Project)
            .filter(Prompt.id == prompt_id, Project.user_id == g.user.id)
            .first()
        )
        if not prompt:
            return {"error": "Prompt not found or not associated with user"}, 404

        parser = reqparse.RequestParser()
        parser.add_argument("version", type=str)
        parser.add_argument("status", type=str)
        parser.add_argument("source", type=str)
        parser.add_argument("generation_technique", type=str)
        parser.add_argument("prompt_type", type=str)
        parser.add_argument("template", type=str)
        parser.add_argument("variables", type=str)
        parser.add_argument("few_shot_template", type=str)
        parser.add_argument("few_shot_example_selector", type=str)
        parser.add_argument("model", type=str)
        parser.add_argument("evaluation_job_name", type=str)
        args = parser.parse_args()

        if args["version"] is not None:
            prompt.version = args["version"]
        if args["status"] is not None:
            prompt.status = args["status"]
        if args["source"] is not None:
            prompt.source = args["source"]
        if args["generation_technique"] is not None:
            prompt.generation_technique = args["generation_technique"]
        if args["prompt_type"] is not None:
            prompt.prompt_type = args["prompt_type"]
        if args["template"] is not None:
            prompt.template = args["template"]
        if args["variables"] is not None:
            prompt.variables = args["variables"]
        if args["few_shot_template"] is not None:
            prompt.few_shot_template = args["few_shot_template"]
        if args["few_shot_example_selector"] is not None:
            prompt.few_shot_example_selector = args["few_shot_example_selector"]
        if args["model"] is not None:
            prompt.model = args["model"]
        if args["evaluation_job_name"] is not None:
            prompt.evaluation_job_name = args["evaluation_job_name"]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "message": "Prompt updated successfully",
            "prompt": prompt.to_dict(),
        }, 200

    @api_key_required
    def delete(self, prompt_id):
        # Fetch prompt and check it is associated with user
        prompt = (
            Prompt.query.join(Task, Task.id == Prompt.task_id)
            .join(Project)
            .filter(Prompt.id == prompt_id, Project.user_id == g.user.id)
            .first()
        )
        if not prompt:
            return {"error": "Prompt not found or not associated with user"}, 404

        try:
            db.session.delete(prompt)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {"message": "Prompt deleted successfully"}, 200


class GeneratePromptAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "objective", type=str, required=True, help="Objective is required"
        )
        parser.add_argument(
            "prompt_id", type=int, required=True, help="Prompt ID is required"
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

        # Fetch prompt and check it is associated with user
        prompt = (
            Prompt.query.join(Task, Task.id == Prompt.task_id)
            .join(Project)
            .filter(Prompt.id == args["prompt_id"], Project.user_id == g.user.id)
            .first()
        )
        if not prompt:
            return {"error": "Prompt not found or not associated with user"}, 404

        # Fetch associated task
        task = Task.query.get(prompt.task_id)
        if not task:
            return {
                "error": "Task associated with prompt not found or not associated with user"
            }, 404

        # Call generate_prompt function with provided objective and prompt_id
        try:
            generated_prompt = generate_prompt_model_configuration(
                user_objective=args["objective"],
                task=task,
                prompt=prompt,
                openai_api_key=args["openai_api_key"],
                anthropic_api_key=args["anthropic_api_key"],
            )
            generated_prompt_dict = generated_prompt.to_dict()
        except Exception as e:
            return {"error": str(e)}, 400

        return {
            "message": "Prompt generation completed",
            "generated_prompt": generated_prompt_dict,
        }, 200


class DeployPromptAPI(Resource):
    @api_key_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "prompt_id", type=int, required=True, help="Prompt ID is required"
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

        # Fetch prompt and check it is associated with user
        prompt = (
            Prompt.query.join(Task, Task.id == Prompt.task_id)
            .join(Project, Project.id == Task.project_id)
            .filter(Prompt.id == args["prompt_id"], Project.user_id == g.user.id)
            .first()
        )
        if not prompt:
            return {"error": "Prompt not found or not associated with user"}, 404

        # Call deploy function with provided prompt_id and inputs
        try:
            return_value = deploy_prompt(
                prompt=prompt,
                input_values=args["inputs"],
                openai_api_key=args["openai_api_key"],
                anthropic_api_key=args["anthropic_api_key"],
            )
        except Exception as e:
            return {"error": str(e)}, 400

        return {
            "message": "Prompt deployment completed",
            "return_value": return_value,
        }, 200


# def register_routes(api):
#     api.add_resource(ListPromptsAPI, "/api/prompts")
#     api.add_resource(CreatePromptAPI, "/api/prompts/new")
#     api.add_resource(PromptAPI, "/api/prompts/<int:prompt_id>")
#     api.add_resource(GeneratePromptAPI, "/api/prompts/generate")
#     api.add_resource(DeployPromptAPI, "/api/prompts/deploy")
