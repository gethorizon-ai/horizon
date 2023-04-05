from app.models.prompt.factory import PromptTemplateFactory as factory
from app.models.prompt.prompt import PromptTemplate
from app.models.schema import HumanMessage
from app.models.llm.open_ai import OpenAI, ChatOpenAI
from app.models.llm.base import BaseLLM
from app.models.component.experiment import Experiment
import pandas as pd
import copy


def prompt_generation_user_objective_training_data(experiment: Experiment, model_object: BaseLLM, num_prompts: int, global_prompt_id: list) -> pd.DataFrame:
    """
    Generate prompt candidates based on user-provided objective, input variables, and training data
    """
    # prefix to few shot-based metaprompt
    few_shot_metaprompt_prefix = """You are an intelligent English professor. You will craft an instruction that I can give to my friend to accomplish a task. Here is my task objective, input variables to be used, and ideal example outputs.

    [BEGIN DATA]
    ==
    OBJECTIVE: {objective}
    INPUT VARIABLES: {input_variables}

    ==
    EXAMPLES:

    """

    # suffix
    few_shot_metaprompt_suffix = """==
    [END DATA]

    What is the optimal instruction I should give to my friend to best accomplish my objective and generate output like in the examples? Do not do the work for my friend, but rather craft an instruction so she can do it. Do not refer to the examples above. Make sure the objective is clearly communicated in the instruction, along with any supporting information to help my friend do the best possible job. ONLY GIVE ME THE INSTRUCTION, NOTHING ELSE!!!

    INSTRUCTION:"""

    # create a list of few shot examples. Each example should be a dictionary with the keys being the input variables and the values being the values for those input variables
    examples = cluster_shortlist_data(experiment, 5, 'train')

    # iterate through each input variable to create example prompt template
    exampleFormatterTemplate = ""
    for j in range(len(experiment.input_variables)):
        exampleFormatterTemplate += "<" + \
            experiment.input_variables[j] + \
            ">: {" + experiment.input_variables[j] + "}\n"
    exampleFormatterTemplate += "<OUTPUT>: {output}"
    example_input_variables = experiment.input_variables + ['output']
    example_prompt = PromptTemplate(
        input_variables=example_input_variables,
        template=exampleFormatterTemplate
    )

    # create the few shot prompt template
    few_shot_metaprompt = factory.create_prompt_template(
        "fewshot",
        examples=examples,
        example_prompt=example_prompt,
        prefix=few_shot_metaprompt_prefix,
        suffix=few_shot_metaprompt_suffix,
        input_variables=['objective', 'input_variables']
    )

    formatted_metaprompt = few_shot_metaprompt.format(objective=experiment.user_objective,
                                                      input_variables=', '.join('{input_variable}'.format(input_variable='<' + input_var + '>') for input_var in experiment.input_variables))

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

    prompt_suffix = """\n\n==\nBEGIN:\n\n"""
    for input_var in experiment.input_variables:
        prompt_suffix += '<' + input_var + '>: {' + input_var + '}\n'
    prompt_suffix += '<OUTPUT>:'

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
        generation_id_list.append('[user_objective_training_data]')
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
