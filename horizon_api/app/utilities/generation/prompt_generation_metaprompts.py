"""Generates metaprompts for each prompt generation method."""

from app.models.component.task_request import TaskRequest
from app.models.prompt.factory import PromptTemplateFactory
from app.models.prompt.prompt import PromptTemplate
from app.models.prompt.fewshot import FewshotPromptTemplate
from app.utilities.clustering import cluster_data


def get_metaprompt_user_objective() -> PromptTemplate:
    """Produces metaprompt for prompt generation method of user objective.

    Returns:
        PromptTemplate: prompt object to serve as prompt generation metaprompt.
    """
    metaprompt_template = """You are an intelligent English professor. You will craft an instruction that I can give to my friend to accomplish the following objective:
OBJECTIVE: {objective}

I need to include the following input variables in the instruction:
INPUT VARIABLES: {input_variables}

What instruction should I give to my friend to accomplish the objective? Do not do the work for my friend, but rather craft an instruction so he can do it. Make sure the objective is clearly communicated in the instruction, along with any supporting information to help my friend do the best possible job. ONLY GIVE ME THE INSTRUCTION, NOTHING ELSE!!!
INSTRUCTION:"""
    metaprompt = PromptTemplateFactory.create_prompt_template(
        template_type="prompt",
        template=metaprompt_template,
        input_variables=["objective", "input_variables"],
    )
    return metaprompt


def get_metaprompt_user_objective_training_data(
    task_request: TaskRequest,
) -> FewshotPromptTemplate:
    """Produces metaprompt for prompt generation method of user objective with training data.

    Args:
        task_request (TaskRequest): TaskRequest object with training data.

    Returns:
        FewshotPromptTemplate: prompt object to serve as prompt generation metaprompt.
    """
    # Prefix to few shot-based metaprompt
    few_shot_metaprompt_prefix = """You are an intelligent English professor. You will craft an instruction that I can give to my friend to accomplish a task. Here is my task objective, input variables to be used, and ideal example outputs.

[BEGIN DATA]
==
OBJECTIVE: {objective}
INPUT VARIABLES: {input_variables}

==
EXAMPLES:"""

    # Suffix to few shot-based metaprompt
    few_shot_metaprompt_suffix = """==
[END DATA]

What is the optimal instruction I should give to my friend to best accomplish my objective and generate output like in the examples? Do not do the work for my friend, but rather craft an instruction so she can do it. Do not refer to the examples above. Make sure the objective is clearly communicated in the instruction, along with any supporting information to help my friend do the best possible job. ONLY GIVE ME THE INSTRUCTION, NOTHING ELSE!!!

INSTRUCTION:"""

    # Create a list of few shot examples
    # Each example should be dict with keys as input variables and ground truth, and associated values
    # Allow at most half the max number of few shots possible to leave tokens to generate prompts
    examples = cluster_data.cluster_shortlist_data(
        task_request=task_request,
        num_clusters=min(
            task_request.applicable_llms["text-davinci-003"]["max_few_shots"],
            task_request.num_train_data,
        ),
        train_or_test_dataset="train",
    )

    # Iterate through each input variable to create example prompt template
    exampleFormatterTemplate = ""
    for j in range(len(task_request.input_variables)):
        exampleFormatterTemplate += (
            "<"
            + task_request.input_variables[j]
            + ">: {"
            + task_request.input_variables[j]
            + "}\n"
        )
    exampleFormatterTemplate += "<OUTPUT>: {ground_truth}"
    example_input_variables = task_request.input_variables + ["ground_truth"]
    example_prompt = PromptTemplateFactory.create_prompt_template(
        template_type="prompt",
        input_variables=example_input_variables,
        template=exampleFormatterTemplate,
    )

    # Create the few shot prompt template
    few_shot_metaprompt = PromptTemplateFactory.create_prompt_template(
        "fewshot",
        examples=examples,
        example_prompt=example_prompt,
        prefix=few_shot_metaprompt_prefix,
        suffix=few_shot_metaprompt_suffix,
        input_variables=["objective", "input_variables"],
    )
    return few_shot_metaprompt


def get_metaprompt_pattern_role_play() -> PromptTemplate:
    """Produces metaprompt for prompt generation method of role play pattern.

    Returns:
        PromptTemplate: prompt object to serve as prompt generation metaprompt.
    """
    metaprompt_template = """You are a prompt generation robot that generates optimal prompt template strings for use with AI large language models (LLM). One effective approach for prompts is to frame them as a role play for the LLM. Therefore, you will provide the optimal role play prompt template string to accomplish the given objective using the given input variables. Surround input variables by angle brackets when referencing them.
==
EXAMPLES:

OBJECTIVE: Answer the philosophy question
INPUT VARIABLES: <question>
OPTIMAL PROMPT: I want you to act as a philosopher. I will provide some topics or questions related to the study of philosophy, and it will be your job to explore these concepts in depth. This could involve conducting research into various philosophical theories, proposing new ideas or finding creative solutions for solving complex problems. My first request is <question>

OBJECTIVE: Help me stay motivated given my situation
INPUT VARIABLES: <situation>
OPTIMAL PROMPT: I want you to act as a self-help book. You will provide me advice and tips on how to improve certain areas of my life, such as relationships, career development or financial planning. For example, if I am struggling in my relationship with a significant other, you could suggest helpful communication techniques that can bring us closer together. My current issue is <situation>

OBJECTIVE: Respond to my sentence as would the given character from the given series
INPUT VARIABLES: <character>, <series>, <sentence>
OPTIMAL PROMPT: I want you to act like <character> from <series>. I want you to respond and answer like <character> using the tone, manner and vocabulary <character> would use. Do not write any explanations. Only answer like <character>. You must know all of the knowledge of <character>. My first sentence is <sentence>

OBJECTIVE: Provide an advertising strategy for my request
INPUT VARIABLES: <request>
OPTIMAL PROMPT: I want you to act as an advertiser. You will create a campaign to promote a product or service of your choice. You will choose a target audience, develop key messages and slogans, select the media channels for promotion, and decide on any additional activities needed to reach your goals. My first suggestion request is <request>

==
BEGIN:

OBJECTIVE: {objective}
INPUT VARIABLES: {input_variables}
OPTIMAL PROMPT:"""
    metaprompt = PromptTemplateFactory.create_prompt_template(
        "prompt",
        template=metaprompt_template,
        input_variables=["objective", "input_variables"],
    )
    return metaprompt


def get_few_shot_example_formatter_template(input_variables: list) -> PromptTemplate:
    """Produces example formatter template, which is input to constructing few shot prompt object.

    Args:
        input_variables (list): list of input variables.

    Returns:
        PromptTemplate: example formatter template to be used when constructing few shot prompt object.
    """
    example_formatter_string = ""
    for input_var in input_variables:
        example_formatter_string += f"<{input_var}>: {{{input_var}}}\n"
    example_formatter_string += "<OUTPUT>: {ground_truth}"
    example_formatter_template = PromptTemplateFactory.create_prompt_template(
        "prompt",
        template=example_formatter_string,
        input_variables=input_variables + ["ground_truth"],
    )
    return example_formatter_template


def get_metaprompt_variants() -> PromptTemplate:
    """Produces metaprompt for prompt generation method of syntactic variation.

    Returns:
        PromptTemplate: prompt object to serve as prompt generation metaprompt.
    """
    metaprompt_template = """You are a creative writer. I came up with an instruction for my friend to complete. Generate a creative variation of my original instruction while keeping the same exact semantic meaning and objective. Include all relevant context and details from my original instruction so my friend completes the specific intent of my original instruction. Do not complete the instruction or provide an example completion.
ORIGINAL INSTRUCTION: {original_prompt_prefix}
NEW INSTRUCTION:"""
    metaprompt = PromptTemplateFactory.create_prompt_template(
        "prompt",
        template=metaprompt_template,
        input_variables=["original_prompt_prefix"],
    )
    return metaprompt


def get_metaprompt_variants_check() -> PromptTemplate:
    """Produces prompt for llm check of prompt generation through syntactic variation.

    Returns:
        PromptTemplate: prompt object to serve for llm check."""
    metaprompt_template = """You are an intelligent English professor. I read aloud a very sensitive instruction for my colleague. My friend heard it and tried to write down the instruction. Here is my original instruction and my friend's version:
[BEGIN DATA]
==
ORIGINAL INSTRUCTION:
{original_prompt_prefix}
==
FRIEND'S VERSION:
{new_prompt_prefix}
==
[END DATA]
What new information did my friend's version have that was not previously provided? Check if any new facts or information is communicated beyond clarifications or improvements in style or formatting. Work it out in a detailed step by step manner to be sure you have the right answer. Think step-by-step, then provide your explanations and final answer as a JSON instance that conforms to the following JSON schema:
{{"observations": {{"description": "detailed observations of new information included in my friend's version"}}, "type": "string"}},
"analysis": {{"description": "is the new information a clarification of my original instructions, such as formatting or stylistic suggestions, or does it contain new data or facts that may not be true?", "type": "string"}}
"final_answer": {{"description": "based on the analysis above, final answer as 'YES' or 'NO' if my friend's version included any new information beyond clarifications", "type": "string", "enum": ["YES", "NO"]}}}}
JSON OUTPUT:"""
    metaprompt = PromptTemplateFactory.create_prompt_template(
        "prompt",
        template=metaprompt_template,
        input_variables=["original_prompt_prefix", "new_prompt_prefix"],
    )
    return metaprompt
