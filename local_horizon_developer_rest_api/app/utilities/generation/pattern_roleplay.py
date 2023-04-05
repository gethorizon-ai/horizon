from app.models.prompt.factory import PromptTemplateFactory as factory
from app.models.llm.factory import LLMFactory
from app.models.schema import HumanMessage
from app.models.llm.open_ai import OpenAI, ChatOpenAI
from app.models.llm.base import BaseLLM
from app.models.component.experiment import Experiment
import pandas as pd
import copy


def prompt_generation_pattern_roleplay(experiment: Experiment, model_object: BaseLLM, num_prompts: int, global_prompt_id: list, prompt_template_type: str) -> pd.DataFrame:
    """
    Generates prompt candidates by converting provided prompt candidates into a role play prompt pattern
    """
    metaprompt = factory.create_prompt_template(prompt_template_type, template="""You are a prompt generation robot that generates optimal prompt template strings for use with AI large language models (LLM). One effective approach for prompts is to frame them as a role play for the LLM. Therefore, you will provide the optimal role play prompt template string to accomplish the given objective using the given input variables. Surround input variables by angle brackets when referencing them.
==
EXAMPLES:

OBJECTIVE: Answer the philosophy question
INPUT VARIABLES: <question>
OPTIMAL PROMPT: I want you to act as a philosopher. I will provide some topics or questions related to the study of philosophy, and it will be your job to explore these concepts in depth. This could involve conducting research into various philosophical theories, proposing new ideas or finding creative solutions for solving complex problems. My first request is <question>

OBJECTIVE: Help me stay motivated given my situation
INPUT VARIABLES: <situation>
OPTIMAL PROMPT: I want you to act as a self-help book. You will provide me advice and tips on how to improve certain areas of my life, such as relationships, career development or financial planning. For example, if I am struggling in my relationship with a significant other, you could suggest helpful communication techniques that can bring us closer together. My current issue is {{situation}}

OBJECTIVE: Respond to my sentence as would the given character from the given series
INPUT VARIABLES: <character>, <series>, <sentence>
OPTIMAL PROMPT: I want you to act like <character> from <series>. I want you to respond and answer like <character> using the tone, manner and vocabulary <character> would use. Do not write any explanations. Only answer like <character>. You must know all of the knowledge of <character>. My first sentence is <sentence>

OBJECTIVE: Provide an advertising strategy for my request
INPUT VARIABLES: <request>
OPTIMAL PROMPT: I want you to act as an advertiser. You will create a campaign to promote a product or service of your choice. You will choose a target audience, develop key messages and slogans, select the media channels for promotion, and decide on any additional activities needed to reach your goals. My first suggestion request is <request>

==
BEGIN:

OBJECTIVE: {objective}
INPUT VARIABLES: {input_variables}
OPTIMAL PROMPT:""",
                                                input_variables=['objective', 'input_variables'])
    formatted_metaprompt = metaprompt.format(objective=experiment.user_objective,
                                             input_variables=', '.join('{input_variable}'.format(input_variable='<' + input_var + '>') for input_var in experiment.input_variables))

    prompt_suffix = """\n\n==\nBEGIN:\n\n"""
    for input_var in experiment.input_variables:
        prompt_suffix += '<' + input_var + '>: {' + input_var + '}\n'
    prompt_suffix += '<OUTPUT>:'

    llm_factory = LLMFactory()

    model_params = {
        "model_name": "text-davinci-003",
        "temperature": 0.4,
        "max_tokens": 1000,
        "n": num_prompts,
        "best_of": num_prompts
    }

    metaprompt_model = llm_factory.create_llm("openai", **model_params)

    if type(metaprompt_model) == ChatOpenAI:
        formatted_metaprompt = [HumanMessage(content=formatted_metaprompt)]
    responses = metaprompt_model.generate(
        [formatted_metaprompt]).generations[0]

    prompt_id_list = []
    generation_id_list = []
    prompt_object_list = []
    prompt_prefix_list = []
    model_object_list = []
    for i in range(num_prompts):
        # Check that prompt template has required input variables and is formatted correctly
        prompt_prefix = responses[i].text.strip()
        prompt_template = prompt_prefix + prompt_suffix
        try:
            generated_prompt = factory.create_prompt_template("prompt",
                                                              template=prompt_template, input_variables=experiment.input_variables)
        except:
            continue

        prompt_id_list.append(global_prompt_id[0])
        global_prompt_id[0] += 1
        prompt_prefix_list.append(prompt_prefix)
        generation_id_list.append('[pattern_role_play]')
        prompt_object_list.append(generated_prompt)
        model_object_list.append(copy.deepcopy(model_object))

    result = pd.DataFrame({
        'prompt_id': prompt_id_list,
        'generation_id': generation_id_list,
        'prompt_object': prompt_object_list,
        'prompt_prefix': prompt_prefix_list,
        'model_object': model_object_list
    })

    return result
