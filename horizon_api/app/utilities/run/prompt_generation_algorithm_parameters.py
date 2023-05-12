"""Defines parameters used for prompt generation algorithm."""

# TODO: update to parameters for full prompt generation algorithm
PROMPT_GENERATION_ALGORITHM_PARAMETERS = {
    "stage_1": {
        "num_prompts_user_objective": 10,  # 11,
        "num_prompts_pattern_role_play": 10,  # 1,
        "num_prompts_user_objective_training_data": 10,  # 1,
        "num_variants": 2,  # 1,
        "num_clusters": 20,  # 5,
        "num_shortlist": 10,  # 2,
        "num_iterations": 3,  # 3,
    },
    "stage_2": {"num_shortlist": 1},
    "stage_3": {
        "num_prompts_temperature_variation": 5,  # 2,
        "num_shortlist": 1,
        "num_iterations": 3,  # 1,
    },
}
