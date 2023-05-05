"""Shortlists prompt-model candidates based on provided evaluation results."""

from app.models.component.prompt_model_candidates import PromptModelCandidates
from app.models.component.inference_evaluation_results import InferenceEvaluationResults
from typing import List


def shortlist_prompt_model_candidates(
    prompt_model_candidates: PromptModelCandidates,
    inference_evaluation_results: InferenceEvaluationResults,
    num_shortlist: int,
    stage_id_list: List[str] = None,
) -> PromptModelCandidates:
    """Shortlists prompt-model candidates based on average of min and mean inference quality score.

    Args:
        prompt_model_candidates (PromptModelCandidates): data structure with each prompt-model candidate.
        inference_evaluation_results (InferenceEvaluationResults): data structure with evaluation results.
        num_shortlist (int): number of prompt-model candidates to shortlist.
        stage_id_list (List[str], optional): list of stage ids in inference_evaluation results to filter to when shortlisting
            prompt-model candidates. Defaults to None.

    Returns:
        PromptModelCandidates: shortlisted set of prompt_model_candidates
    """
    # If number of prompt-model candidates equals target shortlist amount, then return original prompt-model candidates immediately
    if len(prompt_model_candidates) == num_shortlist:
        return prompt_model_candidates.copy()

    # Create copy of inference_evaluation_results to manipulate
    summary_results = inference_evaluation_results.copy()

    # Filter to provided set of prompt_model_ids
    summary_results = summary_results.loc[
        summary_results["prompt_model_id"].isin(
            prompt_model_candidates["prompt_model_id"].to_list()
        )
    ]

    # Filter to selected stage_ids, if given
    if stage_id_list is not None:
        summary_results = summary_results.loc[
            summary_results["stage_id"].isin(stage_id_list)
        ]
    # print(f"Length of summary_results: {len(summary_results)}")
    # print(summary_results)

    # Aggregate by prompt_model_id
    summary_results = (
        summary_results.groupby(["prompt_model_id"])
        .agg(
            {
                "inference_quality": [
                    "min",
                    "max",
                    "mean",
                    ("median", lambda x: x.median()),
                ]
            }
        )
        .reset_index()
    )
    summary_results.columns = [
        "_".join(col).strip("_") for col in summary_results.columns.values
    ]
    # print(f"Length of aggregated summary_results: {len(summary_results)}")

    # Add score that computes average of min and mean inference quality score
    summary_results["inference_quality_min_mean"] = (
        summary_results["inference_quality_min"]
        + summary_results["inference_quality_mean"]
    ) / 2

    # Sort the DataFrame by the min-mean inference quality score in descending order
    sorted_summary_results = summary_results.sort_values(
        "inference_quality_min_mean", ascending=False
    )

    # Get the top n rows with highest score overall
    shortlisted_prompt_model_ids = sorted_summary_results.head(num_shortlist)[
        "prompt_model_id"
    ].to_list()

    # Filter prompt_model_candidates to shortlisted_prompt_model_ids and return it
    shortlisted_prompt_model_candidates = prompt_model_candidates.loc[
        prompt_model_candidates["prompt_model_id"].isin(shortlisted_prompt_model_ids)
    ]
    return shortlisted_prompt_model_candidates
