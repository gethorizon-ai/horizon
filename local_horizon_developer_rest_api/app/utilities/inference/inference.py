from app.models.llm.base import BaseLLM
from app.models.prompt.base import BasePromptTemplate
import copy
import time
from app.models.prompt.factory import PromptTemplateFactory as factory
from app.models.prompt.prompt import PromptTemplate
from app.models.schema import HumanMessage
from app.models.llm.open_ai import OpenAI, ChatOpenAI
from app.models.llm.base import BaseLLM
from app.models.component.experiment import Experiment
import pandas as pd
import copy


def run_single_inference(prompt_id: int, generation_id: int, prompt_object: BasePromptTemplate, prompt_prefix: str, model_object: BaseLLM, input_values: dict, ground_truth: str) -> dict:
    """
    Completes a single inference with the given prompt template by substituting the input values for the input variable placeholders
    """
    input_values = copy.deepcopy(input_values)
    formatted_prompt = prompt_object.format(**input_values)
    if type(model_object) == ChatOpenAI:
        formatted_prompt = [HumanMessage(content=formatted_prompt)]

    start_time = time.time()
    output = model_object.generate(
        [formatted_prompt]).generations[0][0].text.strip()
    end_time = time.time()
    latency = end_time - start_time

    result = {
        'prompt_id': prompt_id,
        'generation_id': generation_id,
        'prompt_object': prompt_object.to_dict(),
        'prompt_prefix': prompt_prefix,
        'model_object': model_object,
        'input_values': input_values,
        'output': output,
        'ground_truth': ground_truth,
        'latency': latency
    }
    return result


def run_inference(experiment: Experiment, prompt_candidates: pd.DataFrame, train_or_test_dataset: str) -> pd.DataFrame:
    """
    Run inference with given set of prompt candidates and either train or test dataset
    """
    inferences = []
    input_values_iter = dict((input_variable, '')
                             for input_variable in experiment.input_variables)
    for index, prompt_candidate_iter in prompt_candidates.iterrows():
        if train_or_test_dataset == 'test':
            input_values = experiment.input_values_test
            ground_truth = experiment.ground_truth_test
        elif train_or_test_dataset == 'train':
            input_values = experiment.input_values_train
            ground_truth = experiment.ground_truth_train

        for input_value_index in range(len(input_values[0])):
            for input_variable_index in range(len(experiment.input_variables)):
                input_values_iter[experiment.input_variables[input_variable_index]
                                  ] = input_values[input_variable_index].iloc[input_value_index]
            result = run_single_inference(prompt_candidate_iter['prompt_id'], prompt_candidate_iter['generation_id'], prompt_candidate_iter['prompt_object'],
                                          prompt_candidate_iter['prompt_prefix'], prompt_candidate_iter['model_object'],
                                          input_values_iter, ground_truth.iloc[input_value_index])
            inferences.append(result)
    result = pd.DataFrame(inferences)
    return result
