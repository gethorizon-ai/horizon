from app.models.component.prompt import Prompt
import os
from dotenv import load_dotenv
import openai
from app import db
from app.models.llm.factory import LLMFactory
from app.models.prompt.factory import PromptTemplateFactory


def deploy_prompt(prompt_id, input_values):
    """
    Deploy a prompt with the given prompt_id and input_values.

    Args:
        prompt_id (int): The ID of the prompt to deploy.
        input_values (dict): A dictionary of key-value pairs representing the input variables for the prompt.

    Returns:
        str: The return value of the deployed prompt.
    """

    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    # Get the prompt from the database using the prompt_id
    prompt = Prompt.query.get(prompt_id)
    if not prompt:
        raise ValueError("Prompt not found")

    # get the model_name from the prompt
    model_name = prompt.model_name

    # get the model_params from the prompt
    model_params = prompt.model

    # define the LLM factory instance
    llm_factory = LLMFactory()

    # Create the model instance
    model_instance = llm_factory.create_llm(model_name, **model_params)

    # get the prompt_template from the prompt
    prompt_template = prompt.template

    # define the prompt factory instance
    prompt_factory = PromptTemplateFactory()

    # Create the prompt instance
    prompt_instance = prompt_factory.create_prompt_template(prompt_template)

    # format the prompt
    prompt_instance.template.format(**input_values)

    # generate the output
    output = model_instance.generate([prompt_instance.template])

    # return the output
    return output


# TODOOO
# OVERRIDE GENERATE FUNCTIONS FOR DIFFERENT PROMPT TYPES

    #  """
    #     Generate output using the provided prompt_object and model_object.
    #     Arguments must be passed in as a key-value pair for each input variable
    #     """
    #   prompt = self.prompt_object.format(**input_values)

    #    if type(self.model_object) == ChatOpenAI:
    #         prompt = [HumanMessage(content=prompt)]
    #     output = self.model_object.generate(
    #         [prompt]).generations[0][0].text.strip()

    #     return output
