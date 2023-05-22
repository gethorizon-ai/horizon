from flask import request, g
from flask_restful import Resource, reqparse, inputs
from celery import shared_task
from app import db, api
from app.utilities.authentication.api_key_auth import api_key_required
from app.utilities.authentication.cognito_auth import get_user_email
from app.utilities.dataset_processing import data_check
from app.utilities.email_notifications import email_notifications
from app.utilities.synthetic_data import synthetic_data
from app.utilities.S3.s3_util import (
    upload_file_to_s3,
    delete_file_from_s3,
    download_file_from_s3,
)
from datetime import datetime
import logging
import tempfile
import os
import werkzeug

ALLOWED_EVALUTION_DATASET_EXTENSIONS = {"csv"}


def allowed_evaluation_dataset_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EVALUTION_DATASET_EXTENSIONS
    )


class GetSyntheticDataGenerationConfirmationDetailsAPI(Resource):
    @api_key_required
    def get(self):
        pass


class GenerateSyntheticDataAPI(Resource):
    @api_key_required
    def post(self):
        logging.info("GenerateSyntheticDataAPI: Start processing the request")

        parser = reqparse.RequestParser()
        # parser.add_argument(
        #     "objective",
        #     type=str,
        #     required=True,
        #     help="Objective is required",
        # )
        # parser.add_argument(
        #     "num_synthetic_data",
        #     type=int,
        #     required=True,
        #     help="Number of synthetic data points to generate is required",
        # )
        # parser.add_argument(
        #     "openai_api_key",
        #     type=str,
        #     required=True,
        #     help="OpenAI API key is required",
        # )
        # parser.add_argument(
        #     "original_dataset",
        #     type=werkzeug.datastructures.FileStorage,
        #     required=True,
        #     location="files",
        #     help="Original dataset file is required",
        # )
        parser.add_argument("json_data", type=str, location="form")
        parser.add_argument("original_dataset", type=str, location="files")
        args = parser.parse_args()
        logging.info("GenerateSyntheticDataAPI: Parsed args")

        print(args)
        print(args["json_data"])
        print(args["original_dataset"])

        original_dataset = args["original_dataset"]

        if not allowed_evaluation_dataset_file(original_dataset.filename):
            return {"error": "Invalid file type. Only CSV files are allowed."}, 400

        return

        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as temp_file:
            temp_file_path = temp_file.name
            original_dataset.save(temp_file_path)

        try:
            data_check.check_evaluation_dataset_and_data_length(
                dataset_file_path=temp_file_path, synthetic_data_generation=True
            )
        except Exception as e:
            logging.error(
                f"GenerateSyntheticDataAPI: Error in check_evaluation_dataset_and_data_length - {str(e)}"
            )
            return {"error": str(e)}, 400

        dataset_s3_key = f"synthetic_data_generation/original_datasets/{datetime.now().strftime('%Y/%m/%d/%H%M%SZ')}/{original_dataset.filename}"
        with open(temp_file_path, "rb") as temp_file:
            upload_file_to_s3(temp_file, dataset_s3_key)
        os.remove(temp_file_path)

        logging.info("GenerateSyntheticDataAPI: Finished uploading original dataset")

        # Call the process_generate_synthetic_data function as a background job with the provided details
        try:
            result_id = process_generate_synthetic_data.delay(
                user_id=g.user.id,
                user_objective=args["objective"],
                dataset_s3_key=dataset_s3_key,
                num_synthetic_data=args["num_synthetic_data"],
                openai_api_key=args["openai_api_key"],
            )
        except Exception as e:
            return {"error": str(e)}, 400

        return {
            "message": "Synthetic data generation initiated. This generally takes 0.5-1.0 hour depending on the data size and LLM provider latency. You will be emailed once the job is completed.",
        }, 200


@shared_task(ignore_result=True)
def process_generate_synthetic_data(
    user_id: str,
    user_objective: str,
    dataset_s3_key: str,
    num_synthetic_data: int,
    openai_api_key: str,
) -> None:
    try:
        # Get user's email address
        user_email = get_user_email(username=user_id)

        # Attempt synthetic data generation algorithm
        synthetic_dataset_s3_key = synthetic_data.generate_synthetic_data(
            user_objective=user_objective,
            dataset_s3_key=dataset_s3_key,
            num_synthetic_data=num_synthetic_data,
            openai_api_key=openai_api_key,
        )
        synthetic_dataset_url = download_file_from_s3(synthetic_dataset_s3_key)

        # If successful, email job results to user
        email_notifications.email_synthetic_data_generation_success(
            user_email=user_email, synthetic_dataset_url=synthetic_dataset_url
        )

    except Exception as e:
        # If failed, email error details to user
        email_notifications.email_synthetic_data_generation_error(
            user_email=user_email, error_message=str(e)
        )

    # Clean up dataset file
    delete_file_from_s3(key=dataset_s3_key)


def register_routes(api):
    api.add_resource(
        GetSyntheticDataGenerationConfirmationDetailsAPI,
        "/api/enablers/get_synthetic_data_generation_confirmation_details",
    )
    api.add_resource(GenerateSyntheticDataAPI, "/api/enablers/generate_synthetic_data")
