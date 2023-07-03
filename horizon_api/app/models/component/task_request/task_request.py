"""Data structure to track information related to user's Task request.

Class organizes information around Task request, including objective, input variables, and evaluation dataset.
"""

from app.models.llm.factory import LLMFactory
from app.models.schema import HumanMessage
from app.utilities.dataset_processing import input_variable_naming
from app.utilities.dataset_processing import data_check
from app.utilities.dataset_processing import data_length
from app.utilities.dataset_processing import llm_applicability
from app.utilities.dataset_processing import segment_data
from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
from app.utilities.vector_db import vector_db
from typing import List
import os


class TaskRequest:
    """Data structure to track information related to user's Task request."""

    def __init__(
        self,
        raw_dataset_s3_key: str,
        task_id: int = None,
        openai_api_key: str = None,
        vector_db_metadata: dict = None,
        user_objective: str = None,
        allowed_models: list = None,
        num_test_data_input: int = None,
        input_variables_to_chunk: List[str] = None,
        use_vector_db: bool = True,
    ):
        """Initializes task_request object based on provided user_objective and dataset_file_path.

        Args:
            raw_dataset_s3_key (str): s3 key for raw evaluation dataset.
            task_id (int, optional): id of task. Defaults to None.
            openai_api_key (str, optional): OpenAI API key to use for embeddings. Defaults to None.
            vector_db_metadata (dict): metadata about vector db usage for this task. Defaults to None.
            user_objective (str, optional): objective of the use case.. Defaults to None.
            allowed_models (list, optional): list of allowed models for this task. Defaults to None.
            num_test_data_input (int, optional): how many test data points to use. Used if it does not exceed the algorithm's normal
                assignment of test data points. Defaults to None.
            input_variables_to_chunk (List[str], optional): list of input variables to chunk. Defaults to None.
            use_vector_db (bool, optional): whether to store data in vector db. If False, stores data in DataFrame. Defaults to True.

        Raises:
            ValueError: checks that user objective is provided and has >0 characters.
            ValueError: checks if evaluation dataset passed if not using vector db.
            AssertionError: checks if input and output data lengths exceed token limits of available llms.
            AssertionError: checks if input and output data lengths exceed token limits of available llms.
            ValueError: checks if vector db or raw dataset and task id passed if proceeding with vector db.
        """
        self.user_objective = user_objective
        self.input_variables = None
        self.evaluation_dataset_dataframe = None
        self.evaluation_dataset_vector_db = None
        self.num_train_data = None
        self.num_test_data = num_test_data_input
        self.train_data_id_list = None
        self.test_data_id_list = None
        self.max_input_tokens = None
        self.max_ground_truth_tokens = None
        self.max_input_characters = None
        self.max_ground_truth_characters = None
        self.allowed_models = allowed_models
        self.applicable_llms = None

        if user_objective is not None and len(user_objective) > 1000:
            raise ValueError(
                "User objective can be at most 1000 characters to manage token limits."
            )

        if not raw_dataset_s3_key:
            raise ValueError("Must pass raw dataset")

        # Get raw dataset
        raw_dataset_file_path = download_file_from_s3_and_save_locally(
            raw_dataset_s3_key
        )
        self.evaluation_dataset_dataframe = data_check.get_evaluation_dataset(
            dataset_file_path=raw_dataset_file_path,
            escape_curly_braces=True,
            input_variables_to_chunk=input_variables_to_chunk,
        )
        os.remove(raw_dataset_file_path)

        # Set input variables
        self.input_variables = input_variable_naming.get_input_variables(
            dataset_fields=self.evaluation_dataset_dataframe.columns.to_list()
        )

        # Set evaluation data length
        evaluation_data_length = data_length.get_evaluation_data_length(
            evaluation_dataset=self.evaluation_dataset_dataframe,
            unescape_curly_braces=True,
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

        # Check that text-davinci-003 is an applicable LLM (needed for prompt generation)
        if "text-davinci-003" not in self.applicable_llms:
            raise AssertionError(
                "Input and output data length exceed context length of available LLMs needed for prompt generation."
            )

        # Get number of test and train data points, which will be used to index data points
        evaluation_dataset_segments = segment_data.segment_evaluation_dataset(
            num_unique_data=len(self.evaluation_dataset_dataframe),
            num_test_data_input=self.num_test_data,
        )
        self.num_train_data = evaluation_dataset_segments["num_train_data"]
        self.num_test_data = evaluation_dataset_segments["num_test_data"]
        self.train_data_id_list = evaluation_dataset_segments["train_data_id_list"]
        self.test_data_id_list = evaluation_dataset_segments["test_data_id_list"]

        # Proceed with vector db if allowed
        if use_vector_db:
            # Load evaluation dataset from vector db if available
            if vector_db_metadata:
                self.evaluation_dataset_vector_db = vector_db.load_vector_db(
                    vector_db_metadata=vector_db_metadata,
                    openai_api_key=openai_api_key,
                )

            # Otherwise, load raw dataset and setup evaluation dataset in vector db
            elif task_id:
                self.evaluation_dataset_vector_db = (
                    vector_db.initialize_vector_db_from_dataset(
                        task_id=task_id,
                        evaluation_dataset=self.evaluation_dataset_dataframe,
                        openai_api_key=openai_api_key,
                    )
                )

            # Throw error if no raw or vector db version of evaluation dataset
            else:
                raise ValueError(
                    "Must provide either vector db or raw dataset and task id."
                )

    def get_normalized_input_variables(self) -> List[str]:
        """Get input variables from evaluation dataset without "var_" prepended to them.

        Assumes evaluation dataset has been checked and processed appropriately.

        Returns:
            List[str]: list of input variable names.
        """
        return input_variable_naming.get_normalized_input_variables(
            processed_input_variables=self.input_variables
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
