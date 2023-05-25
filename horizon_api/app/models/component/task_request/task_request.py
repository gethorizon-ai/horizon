"""Data structure to track information related to user's Task request.

Class organizes information around Task request, including objective, input variables, and evaluation dataset.
"""

from app.utilities.dataset_processing import data_check
from app.utilities.dataset_processing import input_variable_naming
from app.utilities.dataset_processing import data_length
from app.utilities.dataset_processing import llm_applicability
from app.utilities.dataset_processing import segment_data
from app.models.llm.factory import LLMFactory
from app.models.schema import HumanMessage
from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
from typing import List
import os


class TaskRequest:
    """Data structure to track information related to user's Task request."""

    def __init__(
        self,
        dataset_s3_key: str,
        user_objective: str = None,
        allowed_models: list = None,
        num_test_data_input: int = None,
    ):
        """Initializes task_request object based on provided user_objective and dataset_file_path.

        Args:
            dataset_s3_key (str): s3 key for evaluation dataset.
            user_objective (str, optional): task objective. Defaults to None.
            allowed_models (list, optional): list of allowed models for this task. Defaults to None.
            synthetic_data_generation (bool, optional): whether this task request is to generate synthetic data. Defaults to False.
            num_test_data (int, optional): how many test data points to use. Used if it does not exceed the algorithm's normal
                assignment of test data points Defaults to None.

        Raises:
            ValueError: checks that user objective is provided and has >0 characters.
            ValueError: checks that user objective is at most 500 characters to manage token limits.
            AssertionError: checks if input and output data lengths exceed token limits of available llms.
            AssertionError: checks if input and output data lengths exceed token limits of available llms.
        """
        self.user_objective = user_objective
        self.input_variables = None
        self.evaluation_dataset = None
        self.input_data_train = None
        self.ground_truth_data_train = None
        self.input_data_test = None
        self.ground_truth_data_test = None
        self.num_train_data = None
        self.num_test_data = num_test_data_input
        self.max_input_tokens = None
        self.max_ground_truth_tokens = None
        self.max_input_characters = None
        self.max_ground_truth_characters = None
        self.allowed_models = allowed_models
        self.applicable_llms = None

        if user_objective is not None and len(user_objective) > 500:
            raise ValueError(
                "User objective can be at most 500 characters to manage token limits."
            )

        # Download the evaluation dataset from S3 and save it locally
        dataset_file_path = download_file_from_s3_and_save_locally(dataset_s3_key)

        # Set evaluation dataset
        self.evaluation_dataset = data_check.get_evaluation_dataset(
            dataset_file_path=dataset_file_path, escape_curly_braces=True
        )

        # Delete dataset file from the local file system
        os.remove(dataset_file_path)

        # Set input variables
        self.input_variables = input_variable_naming.get_input_variables(
            evaluation_dataset=self.evaluation_dataset
        )

        # Set evaluation data length
        evaluation_data_length = data_length.get_evaluation_data_length(
            evaluation_dataset=self.evaluation_dataset, unescape_curly_braces=True
        )
        self.max_input_tokens = evaluation_data_length["max_input_tokens"]
        self.max_ground_truth_tokens = evaluation_data_length["max_ground_truth_tokens"]
        self.max_input_characters = evaluation_data_length["max_input_characters"]
        self.max_ground_truth_characters = evaluation_data_length[
            "max_ground_truth_characters"
        ]

        # Set applicable llms
        self.applicable_llms = llm_applicability.get_applicable_llms(
            max_input_tokens=self.max_input_tokens,
            max_ground_truth_tokens=self.max_ground_truth_tokens,
            max_input_characters=self.max_input_characters,
            max_ground_truth_characters=self.max_ground_truth_characters,
        )

        # Check that at least one llm is applicable
        if len(self.applicable_llms) == 0:
            raise AssertionError(
                "Input and output data length exceed context length of available LLMs."
            )

        # # Check that text-davinci-003 is an applicable LLM and that at least 3 few shot examples fit (needed for prompt generation)
        # if (
        #     "text-davinci-003" not in self.applicable_llms
        #     or self.applicable_llms["text-davinci-003"]["max_few_shots"] < 3
        # ):
        # TODO: revert
        if "text-davinci-003" not in self.applicable_llms:
            raise AssertionError(
                "Input and output data length exceed context length of available LLMs (assumes few shot examples are used)."
            )

        # Segment evaluation dataset into input and ground_truth datasets
        evaluation_dataset_segments = segment_data.segment_evaluation_dataset(
            evaluation_dataset=self.evaluation_dataset,
            num_test_data_input=self.num_test_data,
        )
        self.num_train_data = evaluation_dataset_segments["num_train_data"]
        self.num_test_data = evaluation_dataset_segments["num_test_data"]
        self.input_data_train = evaluation_dataset_segments["input_data_train"]
        self.ground_truth_data_train = evaluation_dataset_segments[
            "ground_truth_data_train"
        ]
        self.input_data_test = evaluation_dataset_segments["input_data_test"]
        self.ground_truth_data_test = evaluation_dataset_segments[
            "ground_truth_data_test"
        ]

    def get_normalized_input_variables(self) -> List[str]:
        """Get input variables from evaluation dataset without "var_" prepended to them.

        Assumes evaluation dataset has been checked and processed appropriately.

        Returns:
            List[str]: list of input variable names.
        """
        return input_variable_naming.get_normalized_input_variables(
            evaluation_dataset=self.evaluation_dataset
        )

    def check_relevant_api_keys(
        self, openai_api_key: str = None, anthropic_api_key: str = None
    ) -> None:
        """Checks that relevant API keys are provided for each allowed model and that they are valid.

        Runs a small call to the cheapest model of the selected model vendor to validate key.

        Args:
            openai_api_key (str, optional): OpenAI API key to use. Defaults to None.
            anthropic_api_key (str, optional): Anthropic API key to use. Defaults to None.

        Raises:
            AssertionError: checks that applicable_llms has been initialized.
            ValueError: checks that OpenAI key provided for OpenAI model.
            Exception: checks that OpenAI test inference worked.
            ValueError: checks that Anthropic key provided for Anthropic model.
            Exception: checks that Anthropic test inference worked.
        """
        # Check that applicable_llms is initialized
        if self.applicable_llms == None:
            raise AssertionError("Need to initialize applicable llms first")

        validated_openai_api_key = False
        validated_anthropic_api_key = False

        for llm, llm_info in self.applicable_llms.items():
            # Skip if not one of the allowed models
            if self.allowed_models is not None and llm not in self.allowed_models:
                continue

            if LLMFactory.llm_classes[llm]["provider"] == "OpenAI":
                if not validated_openai_api_key:
                    # Evaluate OpenAI models only if OpenAI API key is provided
                    if openai_api_key == None:
                        raise ValueError(
                            "OpenAI API key required to evaluate OpenAI models"
                        )

                    # Run test generation to check that OpenAI API key is valid
                    try:
                        test_model_name = "gpt-3.5-turbo"
                        test_model_params = LLMFactory.create_model_params(
                            llm=test_model_name,
                            max_output_length=1,
                            llm_api_key=openai_api_key,
                        )
                        test_model_instance = LLMFactory.create_llm(
                            test_model_name, **test_model_params
                        )
                        test_model_instance.generate(
                            [[HumanMessage(content="test")]]
                        ).generations[0][0].text.strip()
                    except Exception as e:
                        raise Exception(
                            f"Error when validating OpenAI API key: {str(e)}"
                        )

                    validated_openai_api_key = True
            elif LLMFactory.llm_classes[llm]["provider"] == "Anthropic":
                if not validated_anthropic_api_key:
                    # Evaluate Anthropic models only if Anthropic API key is provided
                    if anthropic_api_key == None:
                        raise ValueError(
                            "Anthropic API key required to evaluate Anthropic models"
                        )

                    # Run test generation to check that Anthropic API key is valid
                    try:
                        test_model_name = "claude-instant-v1"
                        test_model_params = LLMFactory.create_model_params(
                            llm=test_model_name,
                            max_output_length=1,
                            llm_api_key=anthropic_api_key,
                        )
                        test_model_instance = LLMFactory.create_llm(
                            test_model_name, **test_model_params
                        )
                        test_model_instance.generate(
                            [[HumanMessage(content="test")]]
                        ).generations[0][0].text.strip()
                    except Exception as e:
                        raise Exception(
                            f"Error when validating Anthropic API key: {str(e)}"
                        )

                    validated_anthropic_api_key = True
