"""Generate prompt-model candidate for task."""

from app.models.prompt.base import BasePromptTemplate
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
from app import db
import pandas as pd
import json
import math

# Define parameters for algorithm
# TODO: update to parameters for full prompt generation algorithm
PROMPT_GENERATION_ALGORITHM_PARAMETERS = {
    "stage_1": {
        "num_prompts_user_objective": 2,
        "num_prompts_pattern_role_play": 2,
        "num_prompts_user_objective_training_data": 2,
        "num_variants": 1,
        "num_clusters": 5,
        "num_shortlist": 3,
        "num_iterations": 1,
    },
    "stage_2": {"num_shortlist": 1},
    "stage_3": {
        "num_prompts_temperature_variation": 1,
        "num_shortlist": 1,
        "num_iterations": 1,
    },
}


def generate_prompt(
    user_objective: str,
    task: Task,
    prompt: Prompt,
    openai_api_key: str,
    anthropic_api_key: str = None,
) -> dict:
    """Generate the optimal prompt-model candidate for a given objective and evaluation dataset.

    Args:
        user_objective (str): objectuse of the use case.
        task (Task): db record corresponding to task.
        prompt (Prompt): db record corresponding to prompt.
        openai_api_key (str): OpenAI API key to use.
        anthropic_api_key (str, optional): Anthropic API key to use if wanting to consider Anthropic models. Defaults to None.

    Raises:
        ValueError: checks if user objective is provided.
        AssertionError: checks if evaluation datatset exists.
        ValueError: checks if Anthropic API key provided to evaluate Anthropic models.

    Returns:
        dict: overview of task and generated prompt-model candidate.
    """
    if user_objective == None or len(user_objective) == 0:
        raise ValueError("Must provide user objective")

    # Log user objective with task
    task.objective = user_objective

    # Get the evaluation dataset from the task. If there is no evaluation dataset, return an error
    if not task.evaluation_dataset:
        raise AssertionError("No evaluation_dataset file associated with this task")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective=task.objective,
        allowed_models=json.loads(task.allowed_models),
        dataset_file_path=task.evaluation_dataset,
        num_test_data_input=1,  # TODO: remove test data points constraint
    )
    print("TaskRequest instance created", task_request, "\n")

    # Define the starting prompt-model candidate id
    starting_prompt_model_id = 0

    # Define the LLM factory instance
    llm_factory = LLMFactory()

    # Initiate objects to store selected prompt-model candidates and aggregated inference and evaluation results
    prompt_model_candidates_selected = PromptModelCandidates()
    aggregated_inference_evaluation_results = InferenceEvaluationResults()

    # Iterate over applicable llms for this task
    for llm, llm_info in task_request.applicable_llms.items():
        # Skip if not one of the allowed models
        if (
            task_request.allowed_models != None
            and llm not in task_request.allowed_models
        ):
            continue
        print(f"working on {llm}")

        # Determine llm api key
        if LLMFactory.llm_classes[llm]["provider"] == "OpenAI":
            llm_api_key = openai_api_key
        elif LLMFactory.llm_classes[llm]["provider"] == "Anthropic":
            # Evaluate Anthropic models only if Anthropic API key is provided
            if anthropic_api_key == None:
                raise ValueError(
                    "Anthropic API key required to evaluate Anthropic models"
                )
            llm_api_key = anthropic_api_key

        # Define the llm instance parameters
        llm_instance_params = LLMFactory.create_model_params(
            llm=llm,
            max_output_length=llm_info["max_output_length"],
            llm_api_key=llm_api_key,
        )

        # Create the llm instance
        llm_instance = llm_factory.create_llm(llm, **llm_instance_params)
        print(f"Created llm instance for {llm}")

        # STAGE 1 - Initial prompt generation
        # Generate prompt-model candidates using user objective method
        prompt_model_candidates_user_objective = (
            prompt_generation_user_objective.prompt_generation_user_objective(
                task_request=task_request,
                model_object=llm_instance,
                num_prompts=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                    "num_prompts_user_objective"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
                openai_api_key=openai_api_key,
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
                model_object=llm_instance,
                num_prompts=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                    "num_prompts_pattern_role_play"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
                openai_api_key=openai_api_key,
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
                model_object=llm_instance,
                num_prompts=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                    "num_prompts_user_objective_training_data"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
                openai_api_key=openai_api_key,
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
        prompt_model_candidates_syntactic_variants = (
            variants.prompt_generation_variants(
                task_request=task_request,
                prompt_model_candidates=prompt_model_candidates_stage_1_initial,
                num_variants=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                    "num_variants"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
                openai_api_key=openai_api_key,
            )
        )
        prompt_model_candidates_stage_1 = pd.concat(
            [
                prompt_model_candidates_stage_1_initial,
                prompt_model_candidates_syntactic_variants,
            ],
            axis=0,
        ).reset_index(drop=True)
        starting_prompt_model_id += (
            PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_prompts_user_objective"
            ]
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
            num_clusters=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_clusters"
            ],
            openai_api_key=openai_api_key,
        )
        print("finished cluster_shortlist_prompts")

        # Run adaptive filtering and aggregate inference and evaluation results
        (
            prompt_model_candidates_stage_1_shortlisted,
            inference_evaluation_results,
        ) = adaptive_filtering.adaptive_filtering(
            task_request=task_request,
            prompt_model_candidates=prompt_model_candidates_stage_1,
            stage_id="stage_1",
            num_shortlist=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_shortlist"
            ],
            num_iterations=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                "num_iterations"
            ],
            openai_api_key=openai_api_key,
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
            openai_api_key=openai_api_key,
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
            openai_api_key=openai_api_key,
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
            openai_api_key=openai_api_key,
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
        break

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

    # look up the prompt template type for the final prompt and store in the database
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
        "number_of_prompt_model_candidates_considered": len(
            pd.unique(aggregated_inference_evaluation_results["prompt_model_id"])
        ),
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


def estimate_task_creation_cost(task_request: TaskRequest) -> dict:
    """Returns estimated task creation cost range given evaluation data and applicable LLMs.

    Args:
        task_request (TaskRequest): data structure holding task request information.

    Returns:
        dict: estimated low and high end of task creation cost range.
    """
    # Setup dict to track cost
    cost = {}

    # Set percentage from which to determine low and high end of range from estimated cost
    range_factor = 0.25

    # Iterate over each of the selected LLMs
    for llm, llm_info in task_request.applicable_llms.items():
        # Skip if not one of the allowed models
        if (
            task_request.allowed_models != None
            and llm not in task_request.allowed_models
        ):
            continue

        # Prepare necessary parameters (e.g., data length, number of few shots used, llm price)
        if LLMFactory.llm_classes[llm]["data_unit"] == "token":
            instruction_length = LLMFactory.llm_data_assumptions["instruction_tokens"]
            input_length = task_request.max_input_tokens
            output_length = task_request.max_ground_truth_tokens
            metaprompt_context = (
                LLMFactory.llm_data_assumptions["instruction_tokens"] * 3
            )
        elif LLMFactory.llm_classes[llm]["data_unit"] == "character":
            instruction_length = LLMFactory.llm_data_assumptions[
                "instruction_characters"
            ]
            input_length = task_request.max_input_characters
            output_length = task_request.max_ground_truth_characters
            metaprompt_context = (
                LLMFactory.llm_data_assumptions["instruction_tokens"]
                * 3
                / LLMFactory.llm_data_assumptions["tokens_per_character"]
            )
        few_shot_length = input_length + output_length
        num_few_shots = llm_info["max_few_shots"]
        num_test_data = task_request.num_test_data
        generation_price_prompt = LLMFactory.llm_classes["text-davinci-003"][
            "price_per_data_unit_prompt"
        ]
        generation_price_completion = LLMFactory.llm_classes["text-davinci-003"][
            "price_per_data_unit_completion"
        ]
        inference_price_prompt = LLMFactory.llm_classes[llm][
            "price_per_data_unit_prompt"
        ]
        inference_price_completion = LLMFactory.llm_classes[llm][
            "price_per_data_unit_completion"
        ]

        llm_usage = {
            # STAGE 1 - initial prompt generation
            "stage_1": {
                # Prompt generation based on user objective has instruction string with the same assumed instruction length
                "prompt_generation_user_objective": {
                    "data_length_prompt": instruction_length,
                    "data_length_completion": instruction_length
                    * PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                        "num_prompts_user_objective"
                    ],
                    "price_prompt": generation_price_prompt,
                    "price_completion": generation_price_completion,
                },
                # Prompt generation based on role play pattern uses few shot examples (accounted for in metaprompt_context) and
                # produces prompt candidates with assumed instruction length
                "prompt_generation_pattern_role_play": {
                    "data_length_prompt": instruction_length + metaprompt_context,
                    "data_length_completion": instruction_length
                    * PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                        "num_prompts_pattern_role_play"
                    ],
                    "price_prompt": generation_price_prompt,
                    "price_completion": generation_price_completion,
                },
                # Prompt generation based on user objective with training data uses few shot examples from evaluation dataset and
                # produces prompt candidates with assumed instruction length
                "prompt_generation_user_objective_training_data": {
                    "data_length_prompt": instruction_length
                    + few_shot_length
                    * task_request.applicable_llms["text-davinci-003"]["max_few_shots"],
                    "data_length_completion": instruction_length
                    * PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                        "num_prompts_user_objective_training_data"
                    ],
                    "price_prompt": generation_price_prompt,
                    "price_completion": generation_price_completion,
                },
                # Prompt variant generations generates variant prompts for each original prompt candidate from prior prompt
                # generation methods, then checks for overfitting (accounted for in metaprompt_context)
                "prompt_generation_variants": {
                    "data_length_prompt": (
                        PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_prompts_user_objective"
                        ]
                        + PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_prompts_pattern_role_play"
                        ]
                        + PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_prompts_user_objective_training_data"
                        ]
                    )
                    * (instruction_length + metaprompt_context),
                    "data_length_completion": (
                        PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_prompts_user_objective"
                        ]
                        + PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_prompts_pattern_role_play"
                        ]
                        + PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_prompts_user_objective_training_data"
                        ]
                    )
                    * (
                        instruction_length
                        * PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_variants"
                        ]
                    ),
                    "price_prompt": generation_price_prompt,
                    "price_completion": generation_price_completion,
                },
                # Stage 1 inference and evaluation with adaptive filtering
                "inference_evaluation": {
                    "data_length_prompt": (instruction_length + input_length)
                    * adaptive_filtering.get_total_num_inferences(
                        num_original_prompt_model_candidates=PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                            "stage_1"
                        ][
                            "num_clusters"
                        ],
                        num_data=num_test_data,
                        num_shortlist=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_shortlist"
                        ],
                        num_iterations=PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                            "stage_1"
                        ]["num_iterations"],
                    ),
                    "data_length_completion": output_length
                    * adaptive_filtering.get_total_num_inferences(
                        num_original_prompt_model_candidates=PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                            "stage_1"
                        ][
                            "num_clusters"
                        ],
                        num_data=num_test_data,
                        num_shortlist=PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_1"][
                            "num_shortlist"
                        ],
                        num_iterations=PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                            "stage_1"
                        ]["num_iterations"],
                    ),
                    "price_prompt": inference_price_prompt,
                    "price_completion": inference_price_completion,
                },
            },
            # STAGE 2 - Few shots
            "stage_2": {
                # Generation of few shots generation does not cost anything
                # Inference and evaluation of new few shot prompts incurs fee
                "inference_evaluation": {
                    "data_length_prompt": PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                        "stage_1"
                    ]["num_shortlist"]
                    * (
                        instruction_length
                        + num_few_shots * few_shot_length
                        + input_length
                        + output_length
                    )
                    * num_test_data,
                    "data_length_completion": PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                        "stage_1"
                    ]["num_shortlist"]
                    * output_length
                    * num_test_data,
                    "price_prompt": inference_price_prompt,
                    "price_completion": inference_price_completion,
                }
            },
            # STAGE 3 - Temperature variant
            "stage_3": {
                # Generation of temperature variants does not use llms
                # For inference and evaluation, run different temperature variants assuming use of a few shot prompt
                "inference_evaluation": {
                    "data_length_prompt": PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                        "stage_2"
                    ]["num_shortlist"]
                    * PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_3"][
                        "num_prompts_temperature_variation"
                    ]
                    * (
                        instruction_length
                        + num_few_shots * few_shot_length
                        + input_length
                    )
                    * num_test_data,
                    "data_length_completion": PROMPT_GENERATION_ALGORITHM_PARAMETERS[
                        "stage_2"
                    ]["num_shortlist"]
                    * PROMPT_GENERATION_ALGORITHM_PARAMETERS["stage_3"][
                        "num_prompts_temperature_variation"
                    ]
                    * output_length
                    * num_test_data,
                    "price_prompt": inference_price_prompt,
                    "price_completion": inference_price_completion,
                }
            },
        }

        # Sum up costs across all stages
        llm_cost = 0
        for stage in llm_usage.values():
            for step in stage.values():
                llm_cost += (step["data_length_prompt"] * step["price_prompt"]) + (
                    step["data_length_completion"] * step["price_completion"]
                )

        # Store llm cost
        cost[llm] = {
            "low": math.ceil(llm_cost * (1 - range_factor)),
            "high": math.ceil(llm_cost * (1 + range_factor)),
        }

    # Store total cost across llms
    total_cost_low = 0
    total_cost_high = 0
    for llm_cost in cost.values():
        total_cost_low += llm_cost["low"]
        total_cost_high += llm_cost["high"]
    cost["total_cost"] = {"low": total_cost_low, "high": total_cost_high}

    return cost


def get_task_confirmation_details(task: Task) -> dict:
    """Return key information to confirm with user before proceeding with task creation process.

    Args:
        task (Task): db record corresponding to task.

    Raises:
        AssertionError: checks if evaluation dataset exists.

    Returns:
        dict: information to confirm with user (e.g., estimated cost).
    """
    # Get the evaluation dataset from the task. If there is no evaluation dataset, return an error
    if not task.evaluation_dataset:
        raise AssertionError("No evaluation_dataset file associated with this task")

    # Create the TaskRequest instance
    task_request = TaskRequest(
        dataset_file_path=task.evaluation_dataset,
        allowed_models=json.loads(task.allowed_models),
    )

    # Get normalized input variables
    input_variables = task_request.get_normalized_input_variables()

    # Estimate task creation cost
    cost_estimate = estimate_task_creation_cost(task_request=task_request)

    # Return key information
    return {"input_variables": input_variables, "cost_estimate": cost_estimate}
