"""Data structure to track information related to user's Task request.

Class organizes information around Task request, including objective, input variables, and evaluation dataset.
"""

from app.models.llm.factory import LLMFactory
import os
import csv
import pandas as pd
import re
import tiktoken


class TaskRequest:
    """Data structure to track information related to user's Task request."""

    def __init__(
        self,
        user_objective: str,
        dataset_file_name: str,
        synthetic_data_generation: bool = False,
        num_test_data: int = None,
    ):
        """Initializes task_request object based on provided user_objective and dataset_file_name.

        Args:
            user_objective (str): task objective.
            dataset_file_name (str): path to evaluation dataset.
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
        self.num_test_data = None
        self.max_input_tokens = None
        self.max_ground_truth_tokens = None
        self.max_input_characters = None
        self.max_ground_truth_characters = None
        self.applicable_llms = None

        if len(user_objective) > 500:
            raise ValueError(
                "User objective can be at most 500 characters to manage token limits."
            )

        # Initialize each attribute through dataset processing helper functions
        self.check_and_get_evaluation_dataset(
            dataset_file_name=dataset_file_name,
            synthetic_data_generation=synthetic_data_generation,
        )
        self.get_evaluation_data_length()

        self.get_applicable_llms()
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
        self.segment_evaluation_dataset(num_test_data=num_test_data)

    def check_and_get_evaluation_dataset(
        self, dataset_file_name: str, synthetic_data_generation: bool = False
    ) -> None:
        """Checks that evaluation dataset meets requirements, then processes and converts it to a DataFrame.

        Adds evaluation dataset to task_request object.

        Args:
            file_name (str): file path to evaluation dataset.
            synthetic_data_generation (bool, optional): whether this task request is to generate synthetic data. Defaults to False.

        Raises:
            AssertionError: file size is >1 MB.
            AssertionError: file type is not csv.
            AssertionError: insufficient rows of data (must have at least 1 row plus column headers).
            AssertionError: insufficient rows of data for Task creation (must have at least 15 rows of data).
            AssertionError: insufficient number of columns (must have at least 1).
            AssertionError: improper naming of input variables (must be alphanumeric + underscores, no spaces).
            AssertionError: duplicate input variable names.
        """
        # Check that evaluation data is at most 1 MB file size
        if os.path.getsize(dataset_file_name) > 1000000:
            raise AssertionError("Evaluation dataset can be at most 1 MB large.")

        # Try to import evaluation dataset
        try:
            csvfile = open(dataset_file_name, newline="")
            data = list(csv.reader(csvfile))
        except:
            raise AssertionError(
                "Could not import evaluation data. Make sure to upload in csv format."
            )

        # Check that there is at least 1 row of evaluation data
        if len(data) < 2:
            raise AssertionError(
                "There must be at least 1 row of evaluation data plus column headers."
            )

        # For Task creation request and not synthetic data generation, check that there is at least 15 rows of data
        if (not synthetic_data_generation) and len(data) < 16:
            raise AssertionError("There must be at least 15 rows of evaluation data.")

        # Check that there is at least 1 column. Last column is assumed to be the ground truth
        columns = data[0]
        if len(columns) == 0:
            raise AssertionError(
                "There must be at least 1 column. The rightmost column is assumed to be the ground truth."
            )

        # Check that each input variable is a single non-empty string with letters, numbers, and underscores only (no spaces)
        input_variables = columns[:-1]
        for input_var in input_variables:
            if not re.match(r"^[A-Za-z0-9_]+$", input_var):
                raise AssertionError(
                    "Input variable names must be a single string letters, numbers, and underscores only (no spaces allowed)."
                )

        # Check that there are no duplicate input variable names
        if len(input_variables) != len(set(input_variables)):
            raise AssertionError("Input variable names must be unique.")

        # Rename each input variable by prepending "var_" (to avoid duplicating with columns names in internal DataFrames)
        columns[:-1] = [f"var_{input_var}" for input_var in columns[:-1]]
        self.input_variables = columns[:-1]

        # Rename last column to "ground_truth" in case it is not already named as such
        columns[-1] = "ground_truth"

        # Convert dataset to DataFrame and shuffle data
        evaluation_dataset = (
            pd.DataFrame(data=data[1:], columns=columns)
            .sample(frac=1)
            .reset_index(drop=True)
        )

        # Add evaluation_data_id column
        evaluation_dataset["evaluation_data_id"] = evaluation_dataset.index

        # Add evaluation dataset to object
        self.evaluation_dataset = evaluation_dataset

    def get_evaluation_data_length(self) -> None:
        """Determines max count of tokens and characters across input and ground truth data.

        Adds max tokens and characters for input and ground truth data to task_request object.

        Raises:
            AssertionError: task_request must have evaluation dataset.
        """
        if (not isinstance(self.evaluation_dataset, pd.DataFrame)) and (
            self.evaluation_dataset == None
        ):
            raise AssertionError(
                "Must add evalution dataset first before computing data lengths in evaluation dataset."
            )

        # Drop evaluation_data_id column
        evaluation_dataset_analysis = self.evaluation_dataset.drop(
            "evaluation_data_id", axis=1
        )

        # Extract list of input variables
        input_variables = evaluation_dataset_analysis.columns.to_list()[:-1]
        input_data_analysis = evaluation_dataset_analysis.iloc[:, :-1]
        ground_truth_data_analysis = evaluation_dataset_analysis.iloc[:, -1:]

        # Calculate data length used for input values and ground truth for each row based on
        # count of tokens and characters. Use max value of different encodings to be conservative
        encoding_turbo = tiktoken.encoding_for_model("gpt-3.5-turbo")
        encoding_davinci = tiktoken.encoding_for_model("text-davinci-003")

        def count_tokens(row: dict):
            string = "\n".join([f"<{key}>: {value}" for key, value in row.items()])
            token_count = max(
                len(encoding_turbo.encode(string)), len(encoding_davinci.encode(string))
            )
            return token_count

        def count_chars(row: dict):
            string = "\n".join([f"<{key}>: {value}" for key, value in row.items()])
            char_count = len(string)
            return char_count

        max_input_tokens = input_data_analysis.apply(
            lambda row: count_tokens(row.to_dict()), axis=1
        ).max()
        max_ground_truth_tokens = ground_truth_data_analysis.apply(
            lambda row: count_tokens(row.to_dict()), axis=1
        ).max()
        max_input_characters = input_data_analysis.apply(
            lambda row: count_chars(row.to_dict()), axis=1
        ).max()
        max_ground_truth_characters = ground_truth_data_analysis.apply(
            lambda row: count_chars(row.to_dict()), axis=1
        ).max()

        # Correct for fact that "<OUTPUT>:" is part of prompt, while "<ground_truth>: " is not
        # part of LLM completion
        output_string = "\n<OUTPUT>:"
        ground_truth_string = "\n<ground_truth>: "
        max_input_tokens += max(
            len(encoding_turbo.encode(output_string)),
            len(encoding_davinci.encode(output_string)),
        )
        max_ground_truth_tokens -= max(
            len(encoding_turbo.encode(ground_truth_string)),
            len(encoding_davinci.encode(ground_truth_string)),
        )
        max_input_characters += len(output_string)
        max_ground_truth_characters -= len(ground_truth_string)

        # Add max data lengths to object
        self.max_input_tokens = max_input_tokens
        self.max_ground_truth_tokens = max_ground_truth_tokens
        self.max_input_characters = max_input_characters
        self.max_ground_truth_characters = max_ground_truth_characters

    def get_applicable_llms(self) -> None:
        """Determines applicable models and associated parameters for given evaluation data.

        Adds applicable models and associated parameters (e.g., max few shots) to task_request object.

        Raises:
            AssertionError: task_request must have evaluation dataset length statistics.
        """
        if (
            self.max_input_tokens == None
            or self.max_ground_truth_tokens == None
            or self.max_input_characters == None
            or self.max_ground_truth_characters == None
        ):
            raise AssertionError(
                "Must compute evalution dataset length statistics first before determining applicable llms."
            )

        # Determine data length of zero-shot prompt
        zero_shot_tokens = int(
            LLMFactory.llm_data_assumptions["buffer_tokens"]
            + LLMFactory.llm_data_assumptions["instruction_tokens"]
            + (
                self.max_input_tokens
                * LLMFactory.llm_data_assumptions["input_output_multiplier"]
            )
        )
        zero_shot_characters = int(
            LLMFactory.llm_data_assumptions["buffer_characters"]
            + LLMFactory.llm_data_assumptions["instruction_characters"]
            + (
                self.max_input_characters
                * LLMFactory.llm_data_assumptions["input_output_multiplier"]
            )
        )

        # Determine data length of single few shot example
        max_few_shot_example_tokens = int(
            (self.max_input_tokens + self.max_ground_truth_tokens)
            * LLMFactory.llm_data_assumptions["input_output_multiplier"]
        )
        max_few_shot_example_characters = int(
            (self.max_input_characters + self.max_ground_truth_characters)
            * LLMFactory.llm_data_assumptions["input_output_multiplier"]
        )

        # Determine max output data length
        max_output_tokens = int(
            self.max_ground_truth_tokens
            * LLMFactory.llm_data_assumptions["input_output_multiplier"]
        )
        max_output_characters = int(
            self.max_ground_truth_characters
            * LLMFactory.llm_data_assumptions["input_output_multiplier"]
        )

        applicable_llms = {}
        for llm, llm_info in LLMFactory.llm_classes.items():
            if llm_info["data_unit"] == "token":
                if zero_shot_tokens > llm_info["data_limit"]:
                    pass
                tokens_left_for_few_shots = llm_info["data_limit"] - zero_shot_tokens
                # Assume up to 10 few shot examples
                max_few_shots = min(
                    10, tokens_left_for_few_shots // max_few_shot_example_tokens
                )
                applicable_llms[llm] = {
                    "max_few_shots": max_few_shots,
                    "max_few_shot_example_length": max_few_shot_example_tokens,
                    "max_output_length": max_output_tokens,
                }
            elif llm_info["data_unit"] == "character":
                if zero_shot_characters > llm_info["data_limit"]:
                    pass
                characters_left_for_few_shots = (
                    llm_info["data_limit"] - zero_shot_characters
                )
                # Assume up to 10 few shot examples
                max_few_shots = min(
                    10, characters_left_for_few_shots // max_few_shot_example_characters
                )
                applicable_llms[llm] = {
                    "max_few_shots": max_few_shots,
                    "max_few_shot_example_length": max_few_shot_example_characters,
                    "max_output_length": max_output_characters,
                }

        # Add applicable_llms to object
        self.applicable_llms = applicable_llms

    def segment_evaluation_dataset(self, num_test_data: int = None) -> None:
        """Segment evaluation data into training and test data.

        Stores segmented training and test datasets into task_request object.

        Args:
            num_test_data (int, optional): how many test data points to use. Used if it does not exceed the algorithm's normal
                assignment of test data points Defaults to None.


        Raises:
            AssertionError: task_request must have evaluation dataset.
        """
        if (not isinstance(self.evaluation_dataset, pd.DataFrame)) and (
            self.evaluation_dataset == None
        ):
            raise AssertionError(
                "Must add evalution dataset first before computing data lengths in evaluation dataset."
            )

        # Assume 80/20 split with at least 5 and at most 10 training data points
        self.num_train_data = min(10, max(5, int(len(self.evaluation_dataset) * 0.2)))

        # Assume at most 15 test data points
        self.num_test_data = min(15, len(self.evaluation_dataset) - self.num_train_data)

        # Use num_test_data input value if provided
        if num_test_data != None:
            self.num_test_data = min(num_test_data, self.num_test_data)

        # Assign input and ground truth data. Keep evaluation_data_id column in all.
        self.input_data_train = (
            self.evaluation_dataset.iloc[: self.num_train_data, :]
            .drop("ground_truth", axis=1)
            .reset_index(drop=True)
        )
        self.ground_truth_data_train = self.evaluation_dataset.iloc[
            : self.num_train_data, :
        ][["evaluation_data_id", "ground_truth"]].reset_index(drop=True)
        self.input_data_test = (
            self.evaluation_dataset.iloc[
                self.num_train_data : self.num_train_data + self.num_test_data,
                :,
            ]
            .drop("ground_truth", axis=1)
            .reset_index(drop=True)
        )
        self.ground_truth_data_test = self.evaluation_dataset.iloc[
            self.num_train_data : self.num_train_data + self.num_test_data,
            :,
        ][["evaluation_data_id", "ground_truth"]].reset_index(drop=True)

    def estimate_task_creation_cost(self) -> float:
        """Returns estimated task creation cost given evaluation data and applicable LLMs.

        Returns:
            float: estimated task creation cost.
        """
        cost = 0

        # Iterate over each of the selected LLMs
        for llm in self.applicable_llms:
            if LLMFactory.llm_classes[llm]["data_unit"] == "token":
                instruction_length = LLMFactory.llm_data_assumptions[
                    "instruction_tokens"
                ]
                few_shot_length = llm["max_few_shot_tokens"]
                input_length = self.max_input_tokens
                output_length = self.max_ground_truth_tokens
                metaprompt_context = 500
            elif LLMFactory.llm_classes[llm]["data_unit"] == "character":
                instruction_length = LLMFactory.llm_data_assumptions[
                    "instruction_characters"
                ]
                few_shot_length = llm["max_few_shot_characters"]
                input_length = self.max_input_characters
                output_length = self.max_ground_truth_characters
                metaprompt_context = (
                    500 / LLMFactory.llm_data_assumptions["tokens_per_character"]
                )
            num_few_shots = llm["max_few_shots"]
            generation_price = LLMFactory.llm_classes["text-davinci-003"][
                "price_per_data_unit"
            ]
            inference_price = LLMFactory.llm_classes[llm]["price_per_data_unit"]

            llm_usage = {
                # STAGE 1 - initial prompt generation
                "stage_1": {
                    # Prompt generation based on user objective has instruction string and produces <5> prompt candidates with the
                    # same assumed instruction length
                    "prompt_generation_user_objective": {
                        "total_data_length": instruction_length
                        + instruction_length * 5,
                        "price": generation_price,
                    },
                    # Prompt generation based on role play pattern uses few shot examples (accounted for in metaprompt_context) and
                    # produces <5> prompt candidates with assumed instruction length
                    "prompt_generation_pattern_role_play": {
                        "total_data_length": instruction_length
                        + metaprompt_context
                        + instruction_length * 5,
                        "price": generation_price,
                    },
                    # Prompt generation based on user objective with training data uses few shot examples from evaluation dataset and
                    # produces <5> prompt candidates with assumed instruction length
                    "prompt_generation_user_objective_training_data": {
                        "total_data_length": instruction_length
                        + few_shot_length
                        * self.applicable_llms["text_davinci_003"]["max_few_shots"]
                        + instruction_length * 5,
                        "price": generation_price,
                    },
                    # Prompt variant generations generates 2 variant prompts for each original prompt candidate from prior prompt
                    # generation methods, then checks for overfitting (accounted for in metaprompt_context)
                    "prompt_generation_variants": {
                        "total_data_length": 5
                        * 3
                        * (
                            instruction_length
                            + metaprompt_context
                            + instruction_length * 2
                        ),
                        "price": generation_price,
                    },
                    # Stage 1 evaluation with adaptive filtering
                    "inference_evaluation": {
                        "total_data_length": (
                            instruction_length + input_length + output_length
                        )
                        * ((30 * 3) + (15 * 3) + (7 * 4)),
                        "price": inference_price,
                    },
                },
                # STAGE 2 - Few shots
                "stage_2": {
                    # Generation of few shots generation does not cost anything. Evaluation of new few shot prompts incurs fee
                    "inference_evaluation": {
                        "total_data_length": 10
                        * (
                            instruction_length
                            + num_few_shots * few_shot_length
                            + input_length
                            + output_length
                        )
                        * 10,
                        "price": inference_price,
                    }
                },
                # STAGE 3 - Temperature variant
                "stage_3": {
                    # Generation of temperature variants does not use llms
                    # For inference and evaluation, run <4> different temperature variants of a few shot prompt
                    "inference_evaluation": {
                        "total_data_length": 4
                        * (
                            instruction_length
                            + num_few_shots * few_shot_length
                            + input_length
                            + output_length
                        )
                        * 10,
                        "price": inference_price,
                    }
                },
            }

            # Sum up costs across all stages
            for stage in llm_usage:
                for step in stage:
                    cost += step["total_data_length"] * step["price"]

        return cost
