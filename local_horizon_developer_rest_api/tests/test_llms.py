"""Test creation of LLM model object and ability to generate completions."""
import pytest
from app.models.llm.open_ai import OpenAI, ChatOpenAI
import os
from dotenv import load_dotenv
import openai
from app.models.schema import HumanMessage, SystemMessage, AIMessage


def test_factory_creation():
    """Test creation of LLM model object and ability to generate completions."""
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = """Answer the question based on the context below. If the
    question cannot be answered using the information provided answer
    with "I don't know".

    Context: Large Language Models (LLMs) are the latest models used in NLP.
    Their superior performance over smaller models has made them incredibly
    useful for developers building NLP enabled applications. These models
    can be accessed via Hugging Face's `transformers` library, via OpenAI
    using the `openai` library, and via Cohere using the `cohere` library.

    Question: Which libraries and model providers offer LLMs?

    Answer:"""
    # initialize the models

    testllm = OpenAI(
        model_name="text-davinci-003",
    )
    print(testllm(prompt))
    chat = ChatOpenAI(temperature=0)
    chat(
        [
            HumanMessage(
                content="Translate this sentence from English to French. I love programming."
            )
        ]
    )

    messages = [
        SystemMessage(
            content="You are a helpful assistant that translates English to French."
        ),
        HumanMessage(
            content="Translate this sentence from English to French. I love programming."
        ),
    ]
    chat(messages)


if __name__ == "__main__":
    pytest.main()
