"""Helper functions to manage output schemas and associated Pydantic objects."""

from app.utilities.S3.s3_util import download_file_from_s3_and_save_locally
from pydantic import BaseModel
import os
import importlib
import sys


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

    print(pydantic_model_file_path)

    with open(pydantic_model_file_path, "r") as file:
        print(file.read())

    # Try to import Pydantic model
    pydantic_module_name = os.path.basename(pydantic_model_file_path)[:-3]
    pydantic_module_spec = importlib.util.spec_from_file_location(
        pydantic_module_name, pydantic_model_file_path
    )
    pydantic_module_object = importlib.util.module_from_spec(pydantic_module_spec)
    sys.modules[pydantic_module_name] = pydantic_module_object
    pydantic_module_spec.loader.exec_module(pydantic_module_object)

    # Pydantic class / object assumed to be called "OutputSchema"
    pydantic_object = pydantic_module_object.OutputSchema
    del sys.modules[pydantic_module_name]

    # Remove temp file
    os.remove(pydantic_model_file_path)

    # Return Pydantic object
    return pydantic_object
