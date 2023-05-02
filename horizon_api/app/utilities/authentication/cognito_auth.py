"""Provides function wrapper to authenticate user credentials through Cognito."""

from app.models.component import User
from app import db
from flask import g
from flask_restful import reqparse
from functools import wraps
from config import Config
import boto3
from botocore.exceptions import ClientError
import logging
import hashlib
import hmac
import base64
from typing import Callable
from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.DEBUG)


config = Config()
cognito_pool_id = config.COGNITO_POOL_ID
cognito_client_id = config.COGNITO_CLIENT_ID
cognito_client_secret = config.COGNITO_CLIENT_SECRET
region_name = config.AWS_REGION
cognito = boto3.client("cognito-idp", region_name=region_name)


def calculate_secret_hash(client_secret, email, client_id):
    message = email + client_id
    dig = hmac.new(
        bytes(client_secret, "utf-8"),
        msg=bytes(message, "utf-8"),
        digestmod=hashlib.sha256,
    ).digest()
    return base64.b64encode(dig).decode()


def cognito_auth_required(f: Callable) -> Callable:
    """Provides function wrapper to authenticate user credentials through Cognito.

    Args:
        f (Callable): function to wrap.

    Returns:
        Callable: wrapped function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        parser = reqparse.RequestParser()
        parser.add_argument("email", type=str, required=True, help="Email is required")
        parser.add_argument(
            "password", type=str, required=True, help="Password is required"
        )
        auth_args = parser.parse_args()
        email = auth_args["email"]
        password = auth_args["password"]

        if not email or not password:
            return {"error": "Email and password required"}, 401

        secret_hash = calculate_secret_hash(
            cognito_client_secret, email, cognito_client_id
        )

        try:
            response = cognito.admin_initiate_auth(
                UserPoolId=cognito_pool_id,
                ClientId=cognito_client_id,
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                AuthParameters={
                    "USERNAME": email,
                    "PASSWORD": password,
                    "SECRET_HASH": secret_hash,
                },
            )
        except ClientError as e:
            return {"error": str(e)}, 401

        access_token = response["AuthenticationResult"]["AccessToken"]
        cognito_response = cognito.get_user(AccessToken=access_token)

        user = User.query.get(cognito_response["Username"])
        # If user does not yet exist, then create new User record in db
        if user is None:
            try:
                user = User(id=cognito_response["Username"])
                db.session.add(user)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                return {"error": str(e)}, 400

        g.user = user

        return f(*args, **kwargs)

    return decorated_function
