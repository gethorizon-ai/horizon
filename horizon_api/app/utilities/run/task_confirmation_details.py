from app.models.llm.factory import LLMFactory
from app.models.component.task import Task
from app.models.component.task_request import TaskRequest
from app.utilities.run.prompt_generation_algorithm_parameters import (
    PROMPT_GENERATION_ALGORITHM_PARAMETERS,
)
from app.utilities.adaptive_filtering import adaptive_filtering
import math
import json


def estimate_task_creation_cost(task_request: TaskRequest) -> dict:
    """Returns estimated task creation cost range given evaluation data and applicable LLMs.

    Assumes that task_request object is initialized fully (e.g., has defined applicable llms, max data lengths).

    Args:
        task_request (TaskRequest): task request object with details about task.

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
            task_request.allowed_models is not None
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
                # For stage 1, only count inference_evaluation cost since Horizon sponsors other steps
                if stage == "stage_1" and step != "inference_evaluation":
                    continue
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
    # Get evaluation dataset from task. If there is no evaluation dataset, raise error
    if not task.evaluation_dataset:
        raise AssertionError("No evaluation_dataset file associated with this task")

    # Create TaskRequest instance
    task_request = TaskRequest(
        raw_dataset_s3_key=task.evaluation_dataset,
        allowed_models=json.loads(task.allowed_models),
        use_vector_db=False,
    )

    # Get normalized input variables
    input_variables = task_request.get_normalized_input_variables()

    # Estimate task creation cost
    cost_estimate = estimate_task_creation_cost(task_request=task_request)

    # Return key information
    return {"input_variables": input_variables, "cost_estimate": cost_estimate}
