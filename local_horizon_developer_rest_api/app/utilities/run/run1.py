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
from app.models.component.prompt import Prompt
from app.models.component.task import Task
from app.models.component.project import Project
from app.utilities.adaptive_filtering import adaptive_filtering
from app.utilities.shortlist import shortlist
from app import db
import openai
import pandas as pd
import os
import json
from dotenv import load_dotenv, find_dotenv


def generate_prompt(user_objective: str, prompt_id: int) -> BasePromptTemplate:
    load_dotenv(find_dotenv())
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Get the prompt from the database using the prompt_id
    prompt = Prompt.query.get(prompt_id)
    if not prompt:
        raise ValueError("Prompt not found")

    # Get the task and project associated with the prompt
    task_id = prompt.task_id
    task = Task.query.get(task_id)
    project_id = task.project_id
    project = Project.query.get(project_id)

    # Get the evaluation dataset from the task. If there is no evaluation dataset, return an error
    if not task.evaluation_dataset:
        return {"error": "No evaluation_dataset file associated with this task"}, 404

    # Create the TaskRequest instance
    task_request = TaskRequest(
        user_objective=user_objective,
        dataset_file_name=task.evaluation_dataset,
        num_test_data=2,
    )
    print("TaskRequest instance created", task_request, "\n")

    # Define the starting prompt-model candidate id
    starting_prompt_model_id = 0

    # Define the LLM factory instance
    llm_factory = LLMFactory()

    # Initiate objects to store selected prompt-model candidates and inference and evaluation results
    prompt_model_candidates_selected = PromptModelCandidates()
    aggregated_inference_evaluation_results = InferenceEvaluationResults()

    # Define parameters for algorithm
    algorithm_parameters = {
        "stage_1": {
            "num_prompts_user_objective": 2,
            "num_prompts_pattern_role_play": 2,
            "num_prompts_user_objective_training_data": 2,
            "num_variants": 1,
            "num_clusters": 5,
            "num_shortlist": 3,
            "num_iterations": 2,
        },
        "stage_2": {"num_shortlist": 1, "num_iterations": 2},
        "stage_3": {
            "num_prompts_temperature_variation": 2,
            "num_shortlist": 1,
            "num_iterations": 1,
        },
    }

    # Iterate over applicable llms for this task
    for llm, llm_info in task_request.applicable_llms.items():
        print(f"working on {llm}")

        # Define the OpenAI instance parameters
        openai_params = {
            "model_name": llm,
            "temperature": 0.7,
            "max_tokens": llm_info["max_output_length"],
        }

        # Create the OpenAI instance
        openai_instance = llm_factory.create_llm(
            openai_params["model_name"], **openai_params
        )

        # STAGE 1 - Initial prompt generation
        # Generate prompt-model candidates using user objective method
        prompt_model_candidates_user_objective = (
            prompt_generation_user_objective.prompt_generation_user_objective(
                task_request=task_request,
                model_object=openai_instance,
                num_prompts=algorithm_parameters["stage_1"][
                    "num_prompts_user_objective"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
            )
        )
        starting_prompt_model_id += algorithm_parameters["stage_1"][
            "num_prompts_user_objective"
        ]
        print("finished prompt_generation_user_objective")

        # Generate prompt-model candidates using role play pattern method
        prompt_model_candidates_pattern_role_play = (
            pattern_role_play.prompt_generation_pattern_role_play(
                task_request=task_request,
                model_object=openai_instance,
                num_prompts=algorithm_parameters["stage_1"][
                    "num_prompts_pattern_role_play"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
            )
        )
        starting_prompt_model_id += algorithm_parameters["stage_1"][
            "num_prompts_pattern_role_play"
        ]
        print("finished prompt_generation_pattern_role_play")

        # Generate prompt-model candidates using user objective with training data method
        prompt_model_candidates_user_objective_training_data = (
            user_objective_training_data.prompt_generation_user_objective_training_data(
                task_request=task_request,
                model_object=openai_instance,
                num_prompts=algorithm_parameters["stage_1"][
                    "num_prompts_user_objective_training_data"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
            )
        )
        starting_prompt_model_id += algorithm_parameters["stage_1"][
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
        )

        # Generate syntactic variants of prompt-model candidates and concatenate with previous set of prompt-model candidates
        prompt_model_candidates_syntactic_variants = (
            variants.prompt_generation_variants(
                task_request=task_request,
                prompt_model_candidates=prompt_model_candidates_stage_1_initial,
                num_variants=algorithm_parameters["stage_1"]["num_variants"],
                starting_prompt_model_id=starting_prompt_model_id,
            )
        )
        prompt_model_candidates_stage_1 = pd.concat(
            [
                prompt_model_candidates_stage_1_initial,
                prompt_model_candidates_syntactic_variants,
            ],
            axis=0,
        )
        starting_prompt_model_id += (
            algorithm_parameters["stage_1"]["num_prompts_user_objective"]
            + algorithm_parameters["stage_1"]["num_prompts_pattern_role_play"]
            + algorithm_parameters["stage_1"][
                "num_prompts_user_objective_training_data"
            ]
        ) * algorithm_parameters["stage_1"]["num_variants"]
        print("finished prompt_generation_variants")

        # Cluster shortlist current set of prompt-model candidates
        prompt_model_candidates_stage_1 = cluster_prompts.cluster_shortlist_prompts(
            prompt_model_candidates=prompt_model_candidates_stage_1,
            num_clusters=algorithm_parameters["stage_1"]["num_clusters"],
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
            num_shortlist=algorithm_parameters["stage_1"]["num_shortlist"],
            num_iterations=algorithm_parameters["stage_1"]["num_iterations"],
        )
        aggregated_inference_evaluation_results = pd.concat(
            [aggregated_inference_evaluation_results, inference_evaluation_results],
            axis=0,
        )
        print("finished adaptive_filtering stage_1")

        # STAGE 2 - Few shots
        # Generate few shot-based prompts
        prompt_model_candidates_stage_2 = few_shot.prompt_generation_few_shots(
            task_request=task_request,
            prompt_model_candidates=prompt_model_candidates_stage_1_shortlisted,
            starting_prompt_model_id=starting_prompt_model_id,
        )
        starting_prompt_model_id += algorithm_parameters["stage_1"]["num_shortlist"]
        print("finished prompt_generation_few_shots")

        # Run adaptive filtering
        # TODO: compare against stage 1 prompts in case zero-shot prompts outperform
        (
            prompt_model_candidates_stage_2_shortlisted,
            inference_evaluation_results,
        ) = adaptive_filtering.adaptive_filtering(
            task_request=task_request,
            prompt_model_candidates=prompt_model_candidates_stage_2,
            stage_id="stage_2",
            num_shortlist=algorithm_parameters["stage_2"]["num_shortlist"],
            num_iterations=algorithm_parameters["stage_2"]["num_iterations"],
        )
        aggregated_inference_evaluation_results = pd.concat(
            [aggregated_inference_evaluation_results, inference_evaluation_results],
            axis=0,
        )
        print("finished adaptive_filtering stage_2")

        # STAGE 3 - Temperature variation
        # Generate temperature variants
        prompt_model_candidates_stage_3 = (
            temperature_variation.prompt_generation_temperature_variation(
                prompt_model_candidates=prompt_model_candidates_stage_2_shortlisted,
                num_prompts=algorithm_parameters["stage_3"][
                    "num_prompts_temperature_variation"
                ],
                starting_prompt_model_id=starting_prompt_model_id,
            )
        )
        starting_prompt_model_id += algorithm_parameters["stage_3"][
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
            num_shortlist=algorithm_parameters["stage_3"]["num_shortlist"],
            num_iterations=algorithm_parameters["stage_3"]["num_iterations"],
        )
        aggregated_inference_evaluation_results = pd.concat(
            [aggregated_inference_evaluation_results, inference_evaluation_results],
            axis=0,
        )
        print("finished adaptive_filtering stage_3")

        # Store best prompt-model candidate for this llm
        prompt_model_candidates_selected = pd.concat(
            [
                prompt_model_candidates_selected,
                prompt_model_candidates_stage_3_shortlisted,
            ],
            axis=0,
        )

    # Shortlist best prompt-model candidate across applicable llms
    # TODO: reference stats from aggregated inferance and evaluation results from task object
    prompt_model_candidates_final = shortlist.shortlist_prompt_model_candidates(
        prompt_model_candidates=prompt_model_candidates_selected,
        inference_evaluation_results=aggregated_inference_evaluation_results,
        num_shortlist=1,
    )
    final_prompt_object = prompt_model_candidates_final["prompt_object"].iloc[0]
    final_model_object = prompt_model_candidates_final["model_object"].iloc[0]

    # save the model to the database
    prompt.model_name = final_model_object.model_name
    if final_model_object.model_name == "gpt-3.5-turbo":
        model_params = {
            "model_name": final_model_object.model_name,
            "temperature": final_model_object.model_kwargs["temperature"],
            "max_tokens": final_model_object.max_tokens,
        }
    elif final_model_object.model_name == "text-davinci-003":
        model_params = {
            "model_name": final_model_object.model_name,
            "temperature": final_model_object.temperature,
            "max_tokens": final_model_object.max_tokens,
        }
    prompt.model = json.dumps(model_params)

<<<<<<< HEAD
    # Define the global prompt ID
    global_prompt_id = [0]
    prompt_template_type = "prompt"

    # Generate the prompts using the pattern roleplay method
    num_prompt = 1
    prompts_pattern_role_play = prompt_generation_pattern_roleplay(
        experiment_instance, openai_instance, num_prompt, global_prompt_id, prompt_template_type)

    # Generate the prompts using the user objective method
    num_prompt = 1
    prompts_user_objective = prompt_generation_user_objective(
        experiment_instance, openai_instance, num_prompt, global_prompt_id, prompt_template_type)

    # combine the prompts from the two methods
    prompts_generated = prompts_pattern_role_play.append(
        prompts_user_objective)

    # run the prompts through the inference engine
    inference_results = run_inference(
        experiment_instance, prompts_generated, "test")

    # run the infrence results through the evaluation engine
    run_evaluation(inference_results)

    # put the evaluation results through a shortlist engine
    winning_prompt = prompt_shortlist(inference_results, 1, 0)

    # store the winning prompt template type in the database
    prompt.template_type = prompt_template_type
=======
    # look up the prompt template type for the final prompt and store in the database
    prompt.template_type = list(
        factory.PromptTemplateFactory.prompt_template_classes.keys()
    )[
        list(factory.PromptTemplateFactory.prompt_template_classes.values()).index(
            type(final_prompt_object)
        )
    ]
>>>>>>> 5f9861b (Initial porting of POC functionality)

    # store the winning prompt in the database using the prompt_id as the template parameter
    print(type(final_prompt_object))
    print(final_prompt_object)
    prompt.template_data = json.dumps(final_prompt_object.to_dict())

    # save the prompt to the database

    # commit the changes to the database
    db.session.commit()

    # return the winning prompt
    return final_prompt_object
