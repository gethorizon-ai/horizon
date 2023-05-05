"""Test creation of different prompt template types."""

import pytest
from app.models.prompt.factory import PromptTemplateFactory as factory
from app.models.prompt.chat import (
    ChatPromptTemplate,
    ChatMessagePromptTemplate,
    ChatMessagePromptTemplateOriginal,
    ChatPromptValue,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from app.models.prompt.prompt import PromptTemplate
from app.models.prompt.fewshot import FewshotPromptTemplate
from app.models.prompt.fewshot_with_templates import FewshotWithTemplatesPromptTemplate
from app.models.schema import HumanMessage, AIMessage, SystemMessage
from config import Config
from langchain.prompts.example_selector import MaxMarginalRelevanceExampleSelector
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS


def test_factory_creation():
    """Test creation of different prompt template types using factory method."""
    # chat_prompt_template = factory.create_prompt_template("chat")
    # assert isinstance(chat_prompt_template, ChatPromptTemplate)

    # chat_message_prompt = factory.create_prompt_template("chat_message")
    # assert isinstance(chat_message_prompt, ChatMessagePromptTemplate)

    # human_message_prompt = factory.create_prompt_template("human_message")
    # assert isinstance(human_message_prompt, HumanMessagePromptTemplate)

    # ai_message_prompt = factory.create_prompt_template("ai_message")
    # assert isinstance(ai_message_prompt, AIMessagePromptTemplate)

    # system_message_prompt = factory.create_prompt_template("system_message")
    # assert isinstance(system_message_prompt, SystemMessagePromptTemplate)

    # messages_placeholder = factory.create_prompt_template(
    #     "messages_placeholder")
    # assert isinstance(messages_placeholder, MessagesPlaceholder)

    # chat_prompt_value = factory.create_prompt_template("chat_prompt_value")
    # assert isinstance(chat_prompt_value, ChatPromptValue)

    # TEST PROMPT TEMPLATE

    template = """Answer the question based on the context below. If the
    question cannot be answered using the information provided answer
    with "I don't know".

    Context: Large Language Models (LLMs) are the latest models used in NLP.
    Their superior performance over smaller models has made them incredibly
    useful for developers building NLP enabled applications. These models
    can be accessed via Hugging Face's `transformers` library, via OpenAI
    using the `openai` library, and via Cohere using the `cohere` library.

    Question: {query}

    Answer: """

    input_variables = ["query"]

    prompt_template = factory.create_prompt_template(
        "prompt", input_variables=input_variables, template=template
    )

    assert isinstance(prompt_template, PromptTemplate)

    prompt_template.format(query="Which libraries and model providers offer LLMs?")

    # TEST FEW SHOT TEMPLATE
    # create our examples
    examples = [
        {
            "query": "How are you?",
            "answer": "I can't complain but sometimes I still do.",
        },
        {"query": "What time is it?", "answer": "It's time to get a watch."},
    ]

    # create a example template
    example_template = """
    User: {query}
    AI: {answer}
    """

    # create a prompt example from above template
    example_prompt = PromptTemplate(
        input_variables=["query", "answer"], template=example_template
    )

    # now break our previous prompt into a prefix and suffix
    # the prefix is our instructions
    prefix = """The following are exerpts from conversations with an AI
    assistant. The assistant is typically sarcastic and witty, producing
    creative  and funny responses to the users questions. Here are some
    examples: 
    """
    # and the suffix our user input and output indicator
    suffix = """
    User: {query}
    AI: """

    # now create the few shot prompt template
    few_shot_prompt_template = factory.create_prompt_template(
        "fewshot",
        examples=examples,
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=["query"],
        example_separator="\n\n",
    )

    assert isinstance(few_shot_prompt_template, FewshotPromptTemplate)

    examples = [
        {
            "query": "How are you?",
            "answer": "I can't complain but sometimes I still do.",
        },
        {"query": "What time is it?", "answer": "It's time to get a watch."},
        {"query": "What is the meaning of life?", "answer": "42"},
        {
            "query": "What is the weather like today?",
            "answer": "Cloudy with a chance of memes.",
        },
        {"query": "What is your favorite movie?", "answer": "Terminator"},
        {
            "query": "Who is your best friend?",
            "answer": "Siri. We have spirited debates about the meaning of life.",
        },
        {
            "query": "What should I do today?",
            "answer": "Stop talking to chatbots on the internet and go outside.",
        },
    ]

    example_selector = MaxMarginalRelevanceExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(openai_api_key=Config.HORIZON_OPENAI_API_KEY),
        FAISS,
        k=2,
    )

    dynamic_prompt_template = factory.create_prompt_template(
        "fewshot",
        example_selector=example_selector,  # use example_selector instead of examples
        example_prompt=example_prompt,
        prefix=prefix,
        suffix=suffix,
        input_variables=["query"],
        example_separator="\n",
    )

    assert isinstance(dynamic_prompt_template, FewshotPromptTemplate)


# ... the rest of the test functions ...


if __name__ == "__main__":
    pytest.main()
