"""Generate prompt-model candidate for task."""

from app.models.prompt import factory
from app.models.llm.factory import LLMFactory
from app.models.component.task_request import TaskRequest
from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from app.utilities.generation import user_objective as prompt_generation_user_objective
from app.utilities.generation import pattern_role_play
from app.utilities.generation import user_objective_training_data
from app.utilities.generation import variants
from app.utilities.generation import few_shot
from app.utilities.generation import temperature_variation
from app.utilities.clustering import cluster_prompts
from app.utilities.inference import inference
from app.utilities.evaluation import evaluation
from app.models.component.prompt import Prompt
from app.models.component.task import Task
from app.utilities.adaptive_filtering import adaptive_filtering
from app.utilities.shortlist import shortlist
from app.utilities.run.prompt_generation_algorithm_parameters import (
    PROMPT_GENERATION_ALGORITHM_PARAMETERS,
)
from app import db
import pandas as pd
import json
import dotenv
import os
import copy


def generate_prompt_model_configuration(
    user_objective: str,
    task: Task,
    prompt: Prompt,
    openai_api_key: str = None,
    anthropic_api_key: str = None,
) -> dict:
    """Generate the optimal prompt-model candidate for a given objective and evaluation dataset.

    Args:
        user_objective (str): objectuse of the use case.
        task (Task): db record corresponding to task.
        prompt (Prompt): db record corresponding to prompt.
        openai_api_key (str, optional): OpenAI API key to use if wanting to consider OpenAI models. Defaults to None.
        anthropic_api_key (str, optional): Anthropic API key to use if wanting to consider Anthropic models. Defaults to None.

    Raises:
        ValueError: checks if user objective is provided.
        AssertionError: checks if evaluation datatset exists.
        ValueError: checks if OpenAI API key provided to evaluate OpenAI models.
        ValueError: checks if Anthropic API key provided to evaluate Anthropic models.

    Returns:
        dict: overview of task and generated prompt-model candidate.
    """
    if user_objective == None or len(user_objective) == 0:
        raise ValueError("Must provide user objective")

    # Get Horizon's OpenAI API key to use for prompt generation and embeddings (user's API LLM API keys still used for inference)
    dotenv.load_dotenv()
    horizon_openai_api_key = os.getenv("OPENAI_API_KEY")

    # Log user objective with task
    task.objective = user_objective

    # Get the evaluation dataset from the task. If there is no evaluation dataset, return an error
    if not task.evaluation_dataset:
        raise AssertionError("No evaluation dataset associated with this task")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective=task.objective,
        allowed_models=json.loads(task.allowed_models),
        dataset_file_path=task.evaluation_dataset,
        num_test_data_input=1,  # TODO: remove test data points constraint
    )

    # Check that relevant API keys are provided for each allowed model and are valid
    task_request.check_relevant_api_keys(
        openai_api_key=openai_api_key, anthropic_api_key=anthropic_api_key
    )

    # Initiate objects to store selected prompt-model candidates and aggregated inference and evaluation results
    prompt_model_candidates_selected = PromptModelCandidates()
    aggregated_inference_evaluation_results = InferenceEvaluationResults()

    # Define starting prompt-model candidate id
    starting_prompt_model_id = 1

    # STAGE 1 - Initial prompt generation - used as starting point for all applicable llms
    print("Beginning stage 1")

    # Generate prompt-model candidates using user objective method
    prompt_model_candidates_user_objective = (
        prompt_generation_user_objective.prompt_generation_user_objective(
            task_request=task_request,
            model_object=None,
            num_prompts=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_prompts_user_objective"
            ],
            starting_prompt_model_id=starting_prompt_model_id,
            openai_api_key=horizon_openai_api_key,
        )
    )
    starting_prompt_model_id += PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
        "num_prompts_user_objective"
    ]
    print("finished prompt_generation_user_objective")

    # Generate prompt-model candidates using role play pattern method
    prompt_model_candidates_pattern_role_play = (
        pattern_role_play.prompt_generation_pattern_role_play(
            task_request=task_request,
            model_object=None,
            num_prompts=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_prompts_pattern_role_play"
            ],
            starting_prompt_model_id=starting_prompt_model_id,
            openai_api_key=horizon_openai_api_key,
        )
    )
    starting_prompt_model_id += PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
        "num_prompts_pattern_role_play"
    ]
    print("finished prompt_generation_pattern_role_play")

    # Generate prompt-model candidates using user objective with training data method
    prompt_model_candidates_user_objective_training_data = (
        user_objective_training_data.prompt_generation_user_objective_training_data(
            task_request=task_request,
            model_object=None,
            num_prompts=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_prompts_user_objective_training_data"
            ],
            starting_prompt_model_id=starting_prompt_model_id,
            openai_api_key=horizon_openai_api_key,
        )
    )
    starting_prompt_model_id += PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
        "num_prompts_user_objective_training_data"
    ]
    print("finished prompt_generation_user_objective_training_data")

    # Concatenate current set of prompt-model candidates
    prompt_model_candidates_stage_1_initial = pd.concat(
        [
            prompt_model_candidates_user_objective,
            prompt_model_candidates_pattern_role_play,
            prompt_model_candidates_user_objective_training_data,
        ],
        axis=0,
    ).reset_index(drop=True)

    # Generate syntactic variants of prompt-model candidates and concatenate with previous set of prompt-model candidates
    prompt_model_candidates_syntactic_variants = variants.prompt_generation_variants(
        task_request=task_request,
        prompt_model_candidates=prompt_model_candidates_stage_1_initial,
        num_variants=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"]["num_variants"],
        starting_prompt_model_id=starting_prompt_model_id,
        openai_api_key=horizon_openai_api_key,
    )
    prompt_model_candidates_stage_1 = pd.concat(
        [
            prompt_model_candidates_stage_1_initial,
            prompt_model_candidates_syntactic_variants,
        ],
        axis=0,
    ).reset_index(drop=True)

    # Remove prompts with the same prefix
    prompt_model_candidates_stage_1 = prompt_model_candidates_stage_1.drop_duplicates(
        subset="prompt_prefix"
    ).reset_index(drop=True)

    starting_prompt_model_id += (
        PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"]["num_prompts_user_objective"]
        + PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
            "num_prompts_pattern_role_play"
        ]
        + PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
            "num_prompts_user_objective_training_data"
        ]
    ) * PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"]["num_variants"]
    print("finished prompt_generation_variants")

    # Cluster shortlist current set of prompt-model candidates
    prompt_model_candidates_stage_1 = cluster_prompts.cluster_shortlist_prompts(
        prompt_model_candidates=prompt_model_candidates_stage_1,
        num_clusters=min(
            PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"]["num_clusters"],
            len(prompt_model_candidates_stage_1),
        ),
        openai_api_key=horizon_openai_api_key,
    )
    print("finished cluster_shortlist_prompts")

    # Continue task generation with each LLM candidate. Iterate over applicable llms for this task
    for llm, llm_info in task_request.applicable_llms.items():
        # Skip if not one of the allowed models
        if (
            task_request.allowed_models != None
            and llm not in task_request.allowed_models
        ):
            continue
        print(f"working on {llm}")

        # Set llm api key
        if LLMFactory.llm_classes[llm]["provider"] == "OpenAI":
            llm_api_key = openai_api_key
        elif LLMFactory.llm_classes[llm]["provider"] == "Anthropic":
            llm_api_key = anthropic_api_key

        # Define llm instance parameters
        llm_instance_params = LLMFactory.create_model_params(
            llm=llm,
            max_output_length=llm_info["max_output_length"],
            llm_api_key=llm_api_key,
        )

        # Create llm instance
        llm_instance = LLMFactory.create_llm(llm, **llm_instance_params)
        print(f"Created llm instance for {llm}")

        # Create copy of stage 1 prompt candidates and add llm instance to each row
        prompt_model_candidates_stage_1_iteration = (
            prompt_model_candidates_stage_1.copy(deep=True)
        )
        prompt_model_candidates_stage_1_iteration = (
            prompt_model_candidates_stage_1_iteration.assign(
                model_object=prompt_model_candidates_stage_1_iteration[
                    "model_object"
                ].apply(lambda x: copy.deepcopy(llm_instance))
            )
        )

        # Run adaptive filtering and aggregate inference and evaluation results
        (
            prompt_model_candidates_stage_1_shortlisted,
            inference_evaluation_results,
        ) = adaptive_filtering.adaptive_filtering(
            task_request=task_request,
            prompt_model_candidates=prompt_model_candidates_stage_1_iteration,
            stage_id="stage_1",
            num_shortlist=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_shortlist"
            ],
            num_iterations=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_iterations"
            ],
            openai_api_key=horizon_openai_api_key,
        )
        aggregated_inference_evaluation_results = pd.concat(
            [aggregated_inference_evaluation_results, inference_evaluation_results],
            axis=0,
        ).reset_index(drop=True)
        print("finished adaptive_filtering for stage_1")

        # STAGE 2 - Few shots
        # Generate few shot-based prompts
        prompt_model_candidates_stage_2 = few_shot.prompt_generation_few_shots(
            task_request=task_request,
            prompt_model_candidates=prompt_model_candidates_stage_1_shortlisted,
            starting_prompt_model_id=starting_prompt_model_id,
            openai_api_key=horizon_openai_api_key,
        )
        starting_prompt_model_id += PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
            "num_shortlist"
        ]
        print("finished prompt_generation_few_shots")

        # Run inference and evaluation of few-shot based prompts, and store in aggregated results
        inference_evaluation_results_stage_2 = inference.run_inference(
            task_request=task_request,
            prompt_model_candidates=prompt_model_candidates_stage_2,
            train_or_test_dataset="test",
            stage_id="stage_2",
        )
        evaluation.run_evaluation(
            task_request=task_request,
            inference_evaluation_results=inference_evaluation_results_stage_2,
            openai_api_key=horizon_openai_api_key,
        )
        aggregated_inference_evaluation_results = pd.concat(
            [
                aggregated_inference_evaluation_results,
                inference_evaluation_results_stage_2,
            ],
            axis=0,
        ).reset_index(drop=True)

        # Shortlist from stage 1 prompts and few-shot versions in stage 2
        prompt_model_candidates_stage_1_and_2 = pd.concat(
            [
                prompt_model_candidates_stage_1_shortlisted,
                prompt_model_candidates_stage_2,
            ],
            axis=0,
        ).reset_index(drop=True)
        prompt_model_candidates_stage_2_shortlisted = (
            shortlist.shortlist_prompt_model_candidates(
                prompt_model_candidates=prompt_model_candidates_stage_1_and_2,
                inference_evaluation_results=aggregated_inference_evaluation_results,
                num_shortlist=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_2"][
                    "num_shortlist"
                ],
                stage_id_list=["stage_1", "stage_2"],
            )
        )
        print("finished inference, evaluation, and shortlist for stage_2")

        # STAGE 3 - Temperature variation
        # Generate temperature variants
        prompt_model_candidates_stage_3 = (
            temperature_variation.prompt_generation_temperature_variation(
                prompt_model_candidates=prompt_model_candidates_stage_2_shortlisted,
                num_prompts=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_3"][
                    "num_prompts_temperature_variation"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
            )
        )
        starting_prompt_model_id += PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_3"][
            "num_prompts_temperature_variation"
        ]
        print("finished prompt_generation_temperature_variation")

        # Run adaptive filtering
        (
            prompt_model_candidates_stage_3_shortlisted,
            inference_evaluation_results,
        ) = adaptive_filtering.adaptive_filtering(
            task_request=task_request,
            prompt_model_candidates=prompt_model_candidates_stage_3,
            stage_id="stage_3",
            num_shortlist=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_3"][
                "num_shortlist"
            ],
            num_iterations=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_3"][
                "num_iterations"
            ],
            openai_api_key=horizon_openai_api_key,
        )
        aggregated_inference_evaluation_results = pd.concat(
            [aggregated_inference_evaluation_results, inference_evaluation_results],
            axis=0,
        ).reset_index(drop=True)
        print("finished adaptive_filtering for stage_3")

        # Store best prompt-model candidate for this llm
        prompt_model_candidates_selected = pd.concat(
            [
                prompt_model_candidates_selected,
                prompt_model_candidates_stage_3_shortlisted,
            ],
            axis=0,
        ).reset_index(drop=True)
        # TODO: remove break so that other llms also run
        # break

    # Shortlist best prompt-model candidate across applicable llms
    prompt_model_candidates_final = shortlist.shortlist_prompt_model_candidates(
        prompt_model_candidates=prompt_model_candidates_selected,
        inference_evaluation_results=aggregated_inference_evaluation_results,
        num_shortlist=1,
    )
    final_prompt_model_id = prompt_model_candidates_final["prompt_model_id"].iloc[0]
    final_prompt_object = prompt_model_candidates_final["prompt_object"].iloc[0]
    final_model_object = prompt_model_candidates_final["model_object"].iloc[0]

    # Save the model parameters to the database to later reconstruct model. DO NOT STORE USER LLM API KEY!
    prompt.model_name = final_model_object.get_model_name()
    model_params = final_model_object.get_model_params_to_store()
    prompt.model = json.dumps(model_params)

    # Look up the prompt template type for the final prompt and store in the database
    prompt.template_type = list(
        factory.PromptTemplateFactory.prompt_template_classes.keys()
    )[
        list(factory.PromptTemplateFactory.prompt_template_classes.values()).index(
            type(final_prompt_object)
        )
    ]

    # Store the winning prompt in the database
    serialized_prompt_object = final_prompt_object.to_dict()
    prompt.template_data = json.dumps(serialized_prompt_object)

    # Store example selector if few-shot based. CURRENTLY HARDCODED TO MAXMARGINALRELEVANCE
    if prompt.template_type == "fewshot":
        prompt.few_shot_example_selector = "MaxMarginalRelevanceExampleSelector"

    # Store inference statistics with prompt object
    inference_statistics = {
        "inference_quality": aggregated_inference_evaluation_results.loc[
            aggregated_inference_evaluation_results["prompt_model_id"]
            == final_prompt_model_id,
            "inference_quality",
        ].mean(),
        "inference_latency": aggregated_inference_evaluation_results.loc[
            aggregated_inference_evaluation_results["prompt_model_id"]
            == final_prompt_model_id,
            "inference_latency",
        ].mean(),
    }
    prompt.inference_statistics = json.dumps(inference_statistics)

    # Store evaluation statistics with task object
    evaluation_statistics = {
        "number_of_prompt_model_candidates_considered": starting_prompt_model_id,
        "number_of_inferences_and_evaluations_done": len(
            aggregated_inference_evaluation_results
        ),
    }
    task.evaluation_statistics = json.dumps(evaluation_statistics)

    # Set newly created prompt as the active prompt for the task if it is not already so
    task.active_prompt_id = prompt.id

    # Commit the changes to the database
    db.session.commit()

    # Return task overview with selected prompt-model candidate
    return task.to_dict_filtered()
