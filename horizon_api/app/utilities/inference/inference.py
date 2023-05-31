"""Runs inference on a given set of prompt-model candidates and input dataset."""

from app.models.llm.open_ai import ChatOpenAI
from app.models.llm.anthropic import ChatAnthropic
from app.models.schema import HumanMessage
from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from app.models.component.post_processing.post_processing import PostProcessing
import time
from typing import List
import pandas as pd


def run_inference(
    task_request: TaskRequest,
    prompt_model_candidates: PromptModelCandidates,
    train_or_test_dataset: str,
    stage_id: str,
    evaluation_data_id_list: List[int] = None,
    post_processing: PostProcessing = None,
) -> InferenceEvaluationResults:
    """Run inference with given set of prompt candidates on either train or test input dataset.

    Args:
        task_request (TaskRequest): data structure holding task request information such input variables and input dataset.
        prompt_model_candidates (PromptModelCandidates): data structure with each prompt-model candidate.
        train_or_test_dataset (str): indicates which dataset to use; must be either "train" or "test".
        stage_id (str): id for this inference stage.
        evaluation_data_id_list (List[int], optional): list of evaluation data ids to filter to for inference. Defaults to None.
        post_processing (PostProcessing, optional): details on llm output post-processing operations. Defaults to None.

    Returns:
        InferenceEvaluationResults: data structure with inference results.
    """
    # Get input data from vector db
    if train_or_test_dataset == "train":
        db_results = (
            task_request.evaluation_dataset_vector_db.get_data_per_evaluation_data_id(
                evaluation_data_id_list=task_request.train_data_id_list,
                query=task_request.user_objective,
                include_embeddings=False,
                include_ground_truth_in_metadata=False,
            )
        )
    elif train_or_test_dataset == "test":
        db_results = (
            task_request.evaluation_dataset_vector_db.get_data_per_evaluation_data_id(
                evaluation_data_id_list=task_request.test_data_id_list,
                query=task_request.user_objective,
                include_embeddings=False,
                include_ground_truth_in_metadata=False,
            )
        )
    else:
        assert ValueError("train_or_test_dataset must be either 'train' or 'test'")
    input_data = pd.DataFrame(db_results["metadatas"])

    # Filter data to selected evaluation_data_ids, if provided
    if evaluation_data_id_list is not None:
        input_data = input_data.loc[
            input_data["evaluation_data_id"].isin(evaluation_data_id_list)
        ]

    # Setup object to track and return inference results for every combination of prompt-model candidate and input data
    inference_evaluation_results = InferenceEvaluationResults(
        prompt_model_id_list=prompt_model_candidates["prompt_model_id"].to_list(),
        evaluation_data_id_list=input_data["evaluation_data_id"].to_list(),
        stage_id=stage_id,
    )
    print(f"Number of inferences to conduct: {len(inference_evaluation_results)}")

    # Create reference DataFrame which includes prompt-model candidates and input data for faster iteration
    reference_table = inference_evaluation_results.join(
        prompt_model_candidates.set_index("prompt_model_id"), on="prompt_model_id"
    )
    reference_table = reference_table.join(
        input_data.set_index("evaluation_data_id"), on="evaluation_data_id"
    )

    # Run inference on each row
    for index, row in reference_table.iterrows():
        # Get input values
        input_values = row[task_request.input_variables].to_dict()

        # Format prompt and generate inference
        print(
            f"prompt_model_id: {row['prompt_model_id']} | evaluation_data_id: {row['evaluation_data_id']} | generation_id: {row['generation_id']}"
        )

        original_formatted_prompt = row["prompt_object"].format(**input_values)
        formatted_prompt_for_llm = original_formatted_prompt
        model_object = row["model_object"]
        # If model is ChatOpenAI or ChatAnthropic, then wrap message with HumanMessage object
        if type(model_object) == ChatOpenAI or type(model_object) == ChatAnthropic:
            formatted_prompt_for_llm = [HumanMessage(content=formatted_prompt_for_llm)]

        start_time = time.time()
        output = (
            model_object.generate([formatted_prompt_for_llm])
            .generations[0][0]
            .text.strip()
        )

        # Conduct post-processing if applicable
        if post_processing:
            try:
                updated_output = post_processing.parse_and_retry_if_needed(
                    original_output=output, prompt_string=original_formatted_prompt
                )
                output = updated_output
            except:
                # If output fails to satisfy output schema requirements, continue with original output
                print("-----FAILED IN INFERENCE-----")
                print(f"Original output: {output}")
                print("-----FAILED IN INFERENCE-----")

        end_time = time.time()
        inference_latency = end_time - start_time

        # Record output and inference latency
        inference_evaluation_results.loc[index, "output"] = output
        inference_evaluation_results.loc[index, "inference_latency"] = inference_latency

    return inference_evaluation_results
