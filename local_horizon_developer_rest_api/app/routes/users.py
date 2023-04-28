from flask import request, g
from flask_restful import Resource, reqparse, Api
from functools import wraps
from app.models.component import User
from app import db, api
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from warrant import Cognito
import os
import boto3
from config import Config
import logging
import hashlib


logging.basicConfig(level=logging.DEBUG)


config = Config()
cognito_pool_id = config.COGNITO_POOL_ID
cognito_client_id = config.COGNITO_CLIENT_ID
cognito_client_secret = config.COGNITO_CLIENT_SECRET

cognito = Cognito(
    cognito_pool_id, cognito_client_id, client_secret=cognito_client_secret
)


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-Api-Key")
        if not api_key:
            return {"error": "API key required"}, 401

        # Hash API key and look up user
        api_key_hash = hashlib.sha256(api_key.encode("UTF-8")).hexdigest()
        user = User.query.filter_by(api_key_hash=api_key_hash).first()
        if not user:
            return {"error": "Invalid API key"}, 401

        # Attach user object to app context for function to reference
        g.user = user

        return f(*args, **kwargs)

    return decorated_function


def cognito_auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"error": "Authorization header required"}, 401

        access_token = auth_header.split(" ")[-1]
        if not access_token:
            return {"error": "Access token required"}, 401

        try:
            cognito.verify_token(access_token, "access_token")
        except Exception as e:
            return {"error": str(e)}, 401

        g.user = cognito.get_user()

        return f(*args, **kwargs)

    return decorated_function


class RegisterAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("name", type=str, required=True, help="Name is required")
        parser.add_argument("email", type=str, required=True, help="Email is required")
        parser.add_argument(
            "password", type=str, required=True, help="Password is required"
        )
        args = parser.parse_args()

        try:
            user = User(args["name"], args["email"], password=args["password"])
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            return {"error": str(e)}, 400

        return {"message": "User registered successfully"}, 201


class GenerateAPIKeyAPI(Resource):
    @cognito_auth_required
    def post(self):
        user = g.user
        if not user:
            return {"error": "User not found"}, 404

        api_key = user.generate_new_api_key()
        try:
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        return {
            "api_key": api_key,
            "message": "API key generated successfully. Please store this securely as it cannot be retrieved. If lost, a new API key will need to be generated.",
        }, 200


class GetUserAPI(Resource):
    @cognito_auth_required
    def get(self):
        user = g.user
        if not user:
            return {"error": "User not found"}, 404
        return user.to_dict(), 200


class DeleteUserAPI(Resource):
    @cognito_auth_required
    def delete(self):
        user = g.user
        if not user:
            return {"error": "User not found"}, 404

        try:
            user.cognito.admin_delete_user()
        except Exception as e:
            return {"error": str(e)}, 400

        return {"message": "User deleted successfully"}, 200


def register_routes(api):
    api.add_resource(RegisterAPI, "/api/users/register")
    # api.add_resource(AuthenticateAPI, '/api/users/authenticate')
    api.add_resource(GenerateAPIKeyAPI, "/api/users/generate_new_api_key")
    # api.add_resource(GetUserAPI, "/api/users/")
    # api.add_resource(DeleteUserAPI, "/api/users/")


# Register a new user:
# curl - X POST - H "Content-Type: application/json" - d '{"username": "test", "email": "team@gethorizon.ai", "password": "test!12Pasword!L89"}' "http://54.188.108.247:5000/api/users/register"

# Authenticate a user:
# curl - X POST - H "Content-Type: application/json" - d '{"username": "your_username", "password": "MhoG98s#fr55"}' "http://54.188.108.247:5000/api/users/authenticate"
# curl - X POST - H "Content-Type: application/json" - d '{"username": "ltawfik", "password": "your_password"}' "http://54.188.108.247:5000/api/users/authenticate"

# Get the authenticated user's information:
# curl - X GET - H "Content-Type: application/json" - H "Authorization: Bearer your_access_token" "http://54.188.108.247:5000/api/users/"

# Delete the authenticated user:
# curl - X DELETE - H "Content-Type: application/json" - H "Authorization: Bearer your_access_token" "http://54.188.108.247:5000/api/users/"

# def api_key_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         api_key = request.headers.get('X-Api-Key')
#         if not api_key:
#             return {"error": "API key required"}, 401

#         user = User.query.filter_by(api_key=api_key).first()
#         if not user:
#             return {"error": "Invalid API key"}, 401

#         g.user = user

#         return f(*args, **kwargs)
#     return decorated_function


# class RegisterAPI(Resource):
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('username', type=str,
#                             required=True, help='Username is required')
#         parser.add_argument('email', type=str, required=True,
#                             help='Email is required')
#         parser.add_argument('password', type=str,
#                             required=True, help='Password is required')
#         args = parser.parse_args()

#         hashed_password = generate_password_hash(
#             args['password'], method='sha256')

#         new_user = User(
#             username=args['username'], email=args['email'], hashed_password=hashed_password)

#         try:
#             db.session.add(new_user)
#             db.session.commit()
#         except IntegrityError as e:
#             db.session.rollback()
#             return {"error": str(e)}, 400

#         # Add the user_id to the response
#         return {"message": "User registered successfully", "user_id": new_user.id}, 201


# class AuthenticateAPI(Resource):
#     def post(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('username', type=str,
#                             required=True, help='Username is required')
#         parser.add_argument('password', type=str,
#                             required=True, help='Password is required')
#         args = parser.parse_args()

#         user = User.query.filter_by(username=args['username']).first()

#         if not user:
#             return {"error": "Invalid username or password"}, 400

#         submitted_password_hash = generate_password_hash(
#             args['password'], method='sha256')
#         print(f"Stored password hash: {user.password_hash}")
#         print(f"Submitted password hash: {submitted_password_hash}")

#         if not user.check_password(args['password']):
#             return {"error": "Invalid username or password"}, 400

#         return {
#             "api_key": user.api_key,
#             "message": "User authenticated successfully"
#         }, 200


# class GetUserAPI(Resource):
#     @api_key_required
#     def get(self):
#         api_key = request.headers.get("X-Api-Key")
#         user = User.query.filter_by(api_key=api_key).first()
#         if not user:
#             return {"error": "User not found"}, 404
#         return user.to_dict(), 200


# class DeleteUserAPI(Resource):
#     @api_key_required
#     def delete(self):
#         api_key = request.headers.get("X-Api-Key")
#         user = User.query.filter_by(api_key=api_key).first()
#         if not user:
#             return {"error": "User not found"}, 404

#         try:
#             db.session.delete(user)
#             db.session.commit()
#         except Exception as e:
#             db.session.rollback()
#             return {"error": str(e)}, 400

#         return {"message": "User deleted successfully"}, 200


# def register_routes(api):
#     api.add_resource(RegisterAPI, '/api/users/register')
#     api.add_resource(AuthenticateAPI, '/api/users/authenticate')
#     api.add_resource(GetUserAPI, '/api/users/')
#     api.add_resource(DeleteUserAPI, '/api/users/')
