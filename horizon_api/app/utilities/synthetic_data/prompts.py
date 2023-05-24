"""Helper functions to return appropriate prompt for each step in synthetic data generation algorithm."""

from app.models.component.task_request import TaskRequest
from app.models.prompt.factory import PromptTemplateFactory
from app.models.prompt.prompt import PromptTemplate


def get_categorization_prompt(task_request: TaskRequest) -> PromptTemplate:
    """Returns prompt to use to categorize each evaluation data point.

    Args:
        task_request (TaskRequest): details for this task creation run.

    Returns:
        PromptTemplate: prompt to use.
    """
    prompt_string_category = """You are an intelligent professor. I have some data in a file and need to categorize it. Generate this category label for me and keep it to no more than 3 words.
==
BEGIN:
"""

    for input_var in task_request.input_variables:
        prompt_string_category += f"<{input_var}>: {{{input_var}}}\n"
    prompt_string_category += "<OUTPUT>: {ground_truth}"
    prompt_string_category += "<CATEGORY LABEL>:"

    prompt_category = PromptTemplateFactory.create_prompt_template(
        template_type="prompt",
        template=prompt_string_category,
        input_variables=task_request.input_variables + ["ground_truth"],
    )
    return prompt_category


def get_category_generation_prompt() -> PromptTemplate:
    """Returns prompt to use to generate new categories for synthetic data points.

    Returns:
        PromptTemplate: prompt to use.
    """
    prompt_string_category_generation = """You are an intelligent professor. I generated a set of category labels for my files. Each category label is no more than 3 words. Based on the examples below, generate the next {num_synthetic_data} category labels. Ensure each is different. Separate each label by a single newline.
    
{category_labels}
<NEXT CATEGORY LABELS>:"""

    prompt_category_generation = PromptTemplateFactory.create_prompt_template(
        template_type="prompt",
        template=prompt_string_category_generation,
        input_variables=["num_synthetic_data", "category_labels"],
    )
    return prompt_category_generation


def get_synthetic_data_generation_prompt_prefix() -> PromptTemplate:
    """Returns prefix of prompt to use to generate synthetic data.

    Returns:
        PromptTemplate: prompt to use.
    """
    prompt_string_synthetic_data_prefix = """You are an intelligent professor. I am creating a test for my students. First, I created an instruction for my students to use for every question in the test. Then, I determined the category for each question. Finally, I came up with each question by developing the input values and desired output that best satisfies my overall test instruction and category for each question. Using the following examples, generate an exceptional, realistic question and desired output that I can use with my students. Generate fresh new content for each input and output value for the new question that aligns with its category.

==
INSTRUCTION: {user_objective}

==
EXAMPLES:

"""

    prompt_prefix_synthetic_data_generation = (
        PromptTemplateFactory.create_prompt_template(
            template_type="prompt",
            template=prompt_string_synthetic_data_prefix,
            input_variables=["user_objective"],
        )
    )
    return prompt_prefix_synthetic_data_generation


def get_synthetic_data_generation_example_prompt(
    task_request: TaskRequest,
) -> PromptTemplate:
    """Returns prompt to use to format few shot examples used to generate synthetic data.

    Args:
        task_request (TaskRequest): details for this task creation run.

    Returns:
        PromptTemplate: prompt to use.
    """
    prompt_string_synthetic_data_generation_example = "<category>: {category}\n"
    for input_var in task_request.input_variables:
        prompt_string_synthetic_data_generation_example += (
            f"<{input_var}>: {{{input_var}}}\n"
        )
    prompt_string_synthetic_data_generation_example += "<OUTPUT>: {ground_truth}\n\n"

    prompt_template_synthetic_data_generation_example = (
        PromptTemplateFactory.create_prompt_template(
            template_type="prompt",
            template=prompt_string_synthetic_data_generation_example,
            input_variables=["category"]
            + task_request.input_variables
            + ["ground_truth"],
        )
    )
    return prompt_template_synthetic_data_generation_example


def get_synthetic_data_generation_prompt_suffix(
    task_request: TaskRequest,
) -> PromptTemplate:
    """Returns suffix of prompt to use to generate synthetic data.

    Args:
        task_request (TaskRequest): details for this task creation run.

    Returns:
        PromptTemplate: prompt to use.
    """
    prompt_string_synthetic_data_generation_suffix = """==
BEGIN:
<category>: {new_category}
Provide your answer as a JSON instance that conforms to the JSON schema below. For example, the object {{"foo": "bar"}} conforms to the schema {{"foo": {{"type": "string"}}}}.
Here is the output schema:
```
"""
    output_schema = "{{"
    for input_var in task_request.input_variables:
        output_schema += f""""{input_var}": {{{{"type": "string"}}}},\n"""
    output_schema += """"OUTPUT": {{"type": "string"}}}}"""
    prompt_string_synthetic_data_generation_suffix += output_schema
    prompt_string_synthetic_data_generation_suffix += """\n\nJSON OUTPUT:"""

    prompt_suffix_synthetic_data_generation = (
        PromptTemplateFactory.create_prompt_template(
            template_type="prompt",
            template=prompt_string_synthetic_data_generation_suffix,
            input_variables=["new_category"],
        )
    )
    return prompt_suffix_synthetic_data_generation
