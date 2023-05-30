"""Defines parameters used for prompt generation algorithm."""

# Algorithm parameters reduced from full prompt generation algorithm
PROMPT_GENERATION_ALGORITHM_PARAMETERS = {
    "stage_1": {
        "num_prompts_user_objective": 1,  # 5,
        "num_prompts_pattern_role_play": 1,  # 5,
        "num_prompts_user_objective_training_data": 1,  # 5,
        "num_variants": 1,  # 2,
        "num_clusters": 4,  # 10,
        "num_shortlist": 1,  # 5,
        "num_iterations": 3,  # 3,
    },
    "stage_2": {"num_shortlist": 1},
    "stage_3": {
        "num_prompts_temperature_variation": 2,  # 4,
        "num_shortlist": 1,
        "num_iterations": 1,  # 3,
    },
}
