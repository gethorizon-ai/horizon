import boto3
from config import Config
import tempfile
import requests
import os

s3 = boto3.client("s3")
S3_BUCKET = Config.S3_BUCKET


def upload_file_to_s3(file, key):
    s3.upload_fileobj(file, S3_BUCKET, key)


def download_file_from_s3(key, expiration_seconds=3600):
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": S3_BUCKET, "Key": key},
        ExpiresIn=expiration_seconds,
    )


def delete_file_from_s3(key):
    s3.delete_object(Bucket=S3_BUCKET, Key=key)


def download_file_from_s3_and_save_locally(key):
    presigned_url = download_file_from_s3(key)
    response = requests.get(presigned_url)

    # Create a temporary file and write the content of the response
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(response.content)
        temp_file_path = temp_file.name

    return temp_file_path


def upload_directory_to_s3(local_directory_path: str, s3_base_directory: str):
    for root, dirs, files in os.walk(local_directory_path):
        for file in files:
            # Create the full local path to the file
            local_path = os.path.join(root, file)

            # Create the S3 object key by removing the local base directory path
            s3_key = os.path.relpath(local_path, local_directory_path)

            # Prepend the S3 base directory to the object key
            s3_key = os.path.join(s3_base_directory, s3_key)

            # Upload the file to S3
            s3.upload_file(local_path, S3_BUCKET, s3_key)


def download_directory_from_s3_and_save_locally(s3_directory: str):
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # List all objects in the specified S3 directory
    objects = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix=s3_directory)["Contents"]

    # Download each object to the temporary directory
    for obj in objects:
        s3_key = obj["Key"]
        local_path = os.path.join(temp_dir, os.path.relpath(s3_key, s3_directory))
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        s3.download_file(S3_BUCKET, s3_key, local_path)

    # Return temp directory
    return temp_dir
