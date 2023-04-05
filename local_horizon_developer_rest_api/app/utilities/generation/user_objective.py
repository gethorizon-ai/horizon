from app.models.prompt.factory import PromptTemplateFactory as factory
from app.models.prompt.prompt import PromptTemplate
from app.models.schema import HumanMessage
from app.models.llm.open_ai import OpenAI, ChatOpenAI
from app.models.llm.base import BaseLLM
from app.models.component.experiment import Experiment
import pandas as pd
import copy


def prompt_generation_user_objective(experiment: Experiment, model_object: BaseLLM, num_prompts: int, global_prompt_id: list) -> pd.DataFrame:
    """
    Generate prompt candidates based on user-provided objective and input variables
    """
    metaprompt = PromptTemplate(
        template="""You are an intelligent English professor. You will craft an instruction that I can give to my friend to accomplish the following objective:
    OBJECTIVE: {objective}
    I need to include the following input variables in the instruction:
    INPUT VARIABLES: {input_variables}
    What instruction should I give to my friend to accomplish the objective? Do not do the work for my friend, but rather craft an instruction so he can do it. Make sure the objective is clearly communicated in the instruction, along with any supporting information to help my friend do the best possible job. ONLY GIVE ME THE INSTRUCTION, NOTHING ELSE!!!
    INSTRUCTION:""",
        input_variables=['objective', 'input_variables'])
    formatted_metaprompt = metaprompt.format(objective=experiment.user_objective,
                                             input_variables=', '.join('{input_variable}'.format(input_variable='<' + input_var + '>') for input_var in experiment.input_variables))

    prompt_suffix = """\n\n==\nBEGIN:\n\n"""
    for input_var in experiment.input_variables:
        prompt_suffix += '<' + input_var + '>: {' + input_var + '}\n'
    prompt_suffix += '<OUTPUT>:'

    # metaprompt_model = ChatOpenAI(max_tokens=1000, temperature=0.7, n=num_prompts)
    metaprompt_model = OpenAI(model_name="text-davinci-003", temperature=0.4,
                              max_tokens=1000, n=num_prompts, best_of=num_prompts)

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
            generated_prompt = PromptTemplate(
                template=prompt_template, input_variables=experiment.input_variables)
        except:
            continue

        prompt_id_list.append(global_prompt_id[0])
        global_prompt_id[0] += 1
        generation_id_list.append('[user_objective]')
        prompt_object_list.append(tuple([generated_prompt]))
        prompt_prefix_list.append(prompt_prefix)
        model_object_list.append(copy.deepcopy(model_object))

    result = pd.DataFrame({
        'prompt_id': prompt_id_list,
        'generation_id': generation_id_list,
        'prompt_object': prompt_object_list,
        'prompt_prefix': prompt_prefix_list,
        'model_object': model_object_list
    })

    return result
