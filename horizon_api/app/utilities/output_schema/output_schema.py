"""Helper functions to manage output schemas and associated Pydantic objects."""

from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
from app.utilities.dataset_processing import data_check
from pydantic import BaseModel
import json
import os
import importlib
import sys
from typing import Any


ASSUMED_PYDANTIC_CLASS_NAME = "OutputSchema"
VALID_JSON_KEYS_FOR_OUTPUT_SCHEMA = [
    "title",
    "type",
    "properties",
    "description",
    "maxLength",
    "minLength",
    "enum",
    "items",
    "required",
    "definitions",
]


def get_pydantic_object_from_s3(pydantic_model_s3_key: str) -> BaseModel:
    """Downloads Python file defining Pydantic model from s3, then imports it and creates corresponding Pydantic object.

    Args:
        pydantic_model_s3_key (str): s3 key for Python file defining Pydantic model.

    Returns:
        BaseModel: Pydantic object.
    """
    # Download Pydantic model file from s3
    pydantic_model_file_path = download_file_from_s3_and_save_locally(
        pydantic_model_s3_key
    )

    # Add .py extension to the file path
    new_pydantic_model_file_path = os.path.splitext(pydantic_model_file_path)[0] + ".py"
    os.rename(pydantic_model_file_path, new_pydantic_model_file_path)
    pydantic_model_file_path = new_pydantic_model_file_path

    # Get Pydantic object from file path
    pydantic_object = get_pydantic_object_from_file_path(
        pydantic_model_file_path=pydantic_model_file_path
    )

    # Clean up temp file
    os.remove(pydantic_model_file_path)

    # Return Pydantic object
    return pydantic_object


def get_pydantic_object_from_file_path(pydantic_model_file_path: str) -> BaseModel:
    """Given path to local Python file defining Pydantic model, imports it and creates corresponding Pydantic object.

    Assumes that file path has .py extension.

    Args:
        pydantic_model_file_path (str): path to Python file defining Pydantic model.

    Returns:
        BaseModel: Pydantic object.
    """
    # Try to import Pydantic model from file path
    pydantic_module_name = os.path.basename(pydantic_model_file_path)[:-3]
    pydantic_module_spec = importlib.util.spec_from_file_location(
        pydantic_module_name, pydantic_model_file_path
    )
    pydantic_module_object = importlib.util.module_from_spec(pydantic_module_spec)
    sys.modules[pydantic_module_name] = pydantic_module_object
    pydantic_module_spec.loader.exec_module(pydantic_module_object)

    # Pydantic class / object assumed to be called "OutputSchema"
    pydantic_object = getattr(pydantic_module_object, ASSUMED_PYDANTIC_CLASS_NAME)

    # Delete module from system reference and remove temp file
    del sys.modules[pydantic_module_name]

    return pydantic_object


def check_and_process_output_schema(output_schema_file_path: str) -> None:
    """Checks contents of output schema for potential errors and standardizes Pydantic class / object name for later reference.

    Currently restricts output schema to only use VALID_JSON_KEYS_FOR_OUTPUT_SCHEMA.

    Args:
        output_schema_file_path (str): file path to output schema.
    """
    # Check that output schema is at most 5 KB in size
    if os.path.getsize(output_schema_file_path) > 5000:
        raise AssertionError("Output schema can be at most 5 KB large.")

    # Read output schema from file path and check it is JSON object
    with open(output_schema_file_path, "r") as file:
        try:
            output_schema = json.load(file)
        except json.JSONDecodeError:
            raise AssertionError("Output schema is not a valid JSON object.")

    # Check that each JSON key is valid
    for key in output_schema.keys():
        if key not in VALID_JSON_KEYS_FOR_OUTPUT_SCHEMA:
            raise AssertionError(f"Invalid key in output schema: '{key}'")

    # Check that "properties" key is part of JSON
    if "properties" not in output_schema or not isinstance(
        output_schema["properties"], dict
    ):
        raise AssertionError('Output schema missing "properties" key.')

    # Check that there at most 5 fields (to limit complexity)
    if len(output_schema["properties"].keys()) > 5:
        raise AssertionError(
            'Cannot have more than 5 fields in "properties" (to limit complexity).'
        )

    # Check that each field in properties is only a single level dict, except for "items"
    for field in output_schema["properties"].keys():
        if not isinstance(output_schema["properties"][field], dict):
            raise AssertionError(
                f"Invalid field in output schema (must be a dict): '{field}'"
            )
        for key, value in output_schema["properties"][field].items():
            if key not in VALID_JSON_KEYS_FOR_OUTPUT_SCHEMA:
                raise AssertionError(
                    f"Invalid field in output schema 'properties': '{key}'"
                )
            if (
                key != "enum"
                and key != "items"
                and key != "maxLength"
                and key != "minLength"
                and not isinstance(value, str)
            ):
                raise AssertionError(
                    f"Invalid value in output schema (must be str): '{key}': '{value}'"
                )
            if key == "enum" and (
                not isinstance(value, list)
                or not all(isinstance(element, str) for element in value)
            ):
                raise AssertionError(
                    f"Invalid value in output schema ('enum' must be list of str): '{key}': '{value}'"
                )
            if key == "items":
                if not isinstance(value, dict):
                    raise AssertionError(f"Value of 'items' field must be a dict")
                for sub_key, sub_value in value.items():
                    if sub_key not in VALID_JSON_KEYS_FOR_OUTPUT_SCHEMA:
                        raise AssertionError(f"Invalid key in output schema: '{key}'")
                    if sub_key != "enum" and not isinstance(sub_value, str):
                        raise AssertionError(
                            f"Invalid value in output schema (must be str) or too many levels in output schema: '{key}': '{value}'"
                        )
                    if sub_key == "enum" and (
                        not isinstance(sub_value, list)
                        or not all(isinstance(element, str) for element in sub_value)
                    ):
                        raise AssertionError(
                            f"Invalid value in output schema ('enum' must be list of str): '{key}': '{value}'"
                        )
            if key == "maxLength" and not isinstance(value, int):
                raise AssertionError(
                    f"Invalid value in output schema ('maxLength' must be int): '{key}': '{value}'"
                )
            if key == "minLength" and not isinstance(value, int):
                raise AssertionError(
                    f"Invalid value in output schema ('minLength' must be int): '{key}': '{value}'"
                )

    # Check that any required fields are listed in properties
    if "required" in output_schema:
        if not isinstance(output_schema["required"], list):
            raise AssertionError(f"Required fields must be provided as a list")
        for field in output_schema["required"]:
            if field not in output_schema["properties"]:
                raise AssertionError(
                    f"The following field is required but not defined in properties: '{field}'"
                )

    # Update output schema to use standard title
    output_schema["title"] = ASSUMED_PYDANTIC_CLASS_NAME

    # Write the updated output schema back to the file
    with open(output_schema_file_path, "w") as file:
        json.dump(output_schema, file)


def check_evaluation_dataset_aligns_with_pydantic_model(
    dataset_file_path: str, pydantic_model_file_path: str
) -> None:
    """Checks that each ground truth element in evaluation dataset can be parsed as an instance of the Pydantic model for the given
        output schema.

    Args:
        dataset_file_path (str): file path to evaluation dataset.
        pydantic_model_file_path (str): file path to pydantic model.

    Raises:
        ValueError: ground truth element cannot be parsed as JSON object.
        ValueError: ground truth element cannot be parsed as instance of the Pydantic model for the given output schema.
    """
    # Get evaluation dataset
    evaluation_dataset = data_check.get_evaluation_dataset(
        dataset_file_path=dataset_file_path, escape_curly_braces=False
    )

    # Get Pydantic object
    pydantic_object = get_pydantic_object_from_file_path(
        pydantic_model_file_path=pydantic_model_file_path
    )

    # Iterate across each ground_truth element
    ground_truth_list = evaluation_dataset["ground_truth"].to_list()
    for element in ground_truth_list:
        # Try to load as JSON object
        try:
            print(element)
            element_JSON = json.loads(element, strict=False)
        except Exception as e:
            raise ValueError(
                f"""Could not parse the following ground truth element as JSON object:
Ground truth element: {element}
Error: {str(e)}"""
            )

        # Try to parse element using Pydantic object
        try:
            pydantic_object.parse_obj(element_JSON)
        except Exception as e:
            raise ValueError(
                f"""Could not parse the following ground truth element according to given output schema:
Ground truth element: {element}
Error: {str(e)}"""
            )
