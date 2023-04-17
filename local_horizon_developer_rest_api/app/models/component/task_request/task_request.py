"""Data structure to track information related to user's Task request.

Class organizes information around Task request, including objective, input variables, and evaluation dataset.
"""

from app.utilities.dataset_processing import dataset_processing


class TaskRequest:
    """Data structure to track information related to user's Task request."""

    def __init__(
        self,
        user_objective: str,
        dataset_file_path: str,
        synthetic_data_generation: bool = False,
        num_test_data_input: int = None,
    ):
        """Initializes task_request object based on provided user_objective and dataset_file_path.

        Args:
            user_objective (str): task objective.
            dataset_file_path (str): path to evaluation dataset.
            synthetic_data_generation (bool, optional): whether this task request is to generate synthetic data. Defaults to False.
            num_test_data (int, optional): how many test data points to use. Used if it does not exceed the algorithm's normal
                assignment of test data points Defaults to None.

        Raises:
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
        self.applicable_llms = None

        if len(user_objective) > 500:
            raise ValueError(
                "User objective can be at most 500 characters to manage token limits."
            )

        # Check evaluation dataset meets requirements
        dataset_processing.check_evaluation_dataset(
            dataset_file_path=dataset_file_path,
            synthetic_data_generation=synthetic_data_generation,
        )

        # Set evaluation dataset
        self.evaluation_dataset = dataset_processing.get_evaluation_dataset(
            dataset_file_path=dataset_file_path
        )

        # Set input variables
        self.input_variables = dataset_processing.get_input_variables(
            evaluation_dataset=self.evaluation_dataset
        )

        # Set evaluation data length
        evaluation_data_length = dataset_processing.get_evaluation_data_length(
            evaluation_dataset=self.evaluation_dataset
        )
        self.max_input_tokens = evaluation_data_length["max_input_tokens"]
        self.max_ground_truth_tokens = evaluation_data_length["max_ground_truth_tokens"]
        self.max_input_characters = evaluation_data_length["max_input_characters"]
        self.max_ground_truth_characters = evaluation_data_length[
            "max_ground_truth_characters"
        ]

        # Set applicable llms
        self.applicable_llms = dataset_processing.get_applicable_llms(
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

        # Check that text-davinci-003 is an applicable LLM and that at least 3 few shot examples fit (needed for prompt generation)
        if (
            "text-davinci-003" not in self.applicable_llms
            or self.applicable_llms["text-davinci-003"]["max_few_shots"] < 3
        ):
            raise AssertionError(
                "Input and output data length exceed context length of available LLMs (assumes few shot examples are used)."
            )

        # Segment evaluation dataset into input and ground_truth datasets
        evaluation_dataset_segments = dataset_processing.segment_evaluation_dataset(
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
