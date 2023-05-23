import boto3
from config import Config
import tempfile
import requests
import datetime

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
