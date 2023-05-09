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
    print(
        f"Downloaded Pydantic model file from s3 with file path: {pydantic_model_file_path}"
    )

    # Add .py extension to the file path
    new_pydantic_model_file_path = os.path.splitext(pydantic_model_file_path)[0] + ".py"
    os.rename(pydantic_model_file_path, new_pydantic_model_file_path)
    pydantic_model_file_path = new_pydantic_model_file_path
    print(f"Updated file path to {pydantic_model_file_path}")

    # Try to import Pydantic model
    pydantic_module_name = os.path.basename(pydantic_model_file_path)[:-3]
    pydantic_module_spec = importlib.util.spec_from_file_location(
        pydantic_module_name, pydantic_model_file_path
    )
    print("Imported module spec")
    pydantic_module_object = importlib.util.module_from_spec(pydantic_module_spec)
    print("Imported module object")
    sys.modules[pydantic_module_name] = pydantic_module_object
    pydantic_module_spec.loader.exec_module(pydantic_module_object)

    # Pydantic class / object assumed to be called "OutputSchema"
    pydantic_object = pydantic_module_object.OutputSchema
    print("Imported pydantic object")

    # Delete module from system reference and remove temp file
    del sys.modules[pydantic_module_name]
    os.remove(pydantic_model_file_path)

    # Return Pydantic object
    return pydantic_object
