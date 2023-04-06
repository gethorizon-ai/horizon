from flask import request
from flask_restful import Resource, reqparse, Api
from functools import wraps
from app.models.component import User
from app import db, api
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError


def api_key_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-Api-Key')
        if not api_key:
            return {"error": "API key required"}, 403

        user = User.query.filter_by(api_key=api_key).first()
        if not user:
            return {"error": "Invalid API key"}, 403

        return f(*args, **kwargs)
    return decorated_function


class RegisterAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            required=True, help='Username is required')
        parser.add_argument('email', type=str, required=True,
                            help='Email is required')
        parser.add_argument('password', type=str,
                            required=True, help='Password is required')
        args = parser.parse_args()

        hashed_password = generate_password_hash(
            args['password'], method='sha256')

        new_user = User(
            username=args['username'], email=args['email'], hashed_password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {"error": str(e)}, 400

        # Add the user_id to the response
        return {"message": "User registered successfully", "user_id": new_user.id}, 201


class AuthenticateAPI(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', type=str,
                            required=True, help='Username is required')
        parser.add_argument('password', type=str,
                            required=True, help='Password is required')
        args = parser.parse_args()

        user = User.query.filter_by(username=args['username']).first()

        if not user:
            return {"error": "Invalid username or password"}, 400

        submitted_password_hash = generate_password_hash(
            args['password'], method='sha256')
        print(f"Stored password hash: {user.password_hash}")
        print(f"Submitted password hash: {submitted_password_hash}")

        if not user.check_password(args['password']):
            return {"error": "Invalid username or password"}, 400

        return {
            "api_key": user.api_key,
            "message": "User authenticated successfully"
        }, 200


class GetUserAPI(Resource):
    @api_key_required
    def get(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404
        return user.to_dict(), 200


class DeleteUserAPI(Resource):
    @api_key_required
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": "User deleted successfully"}, 200


def register_routes(api):
    api.add_resource(RegisterAPI, '/api/users/register')
    api.add_resource(AuthenticateAPI, '/api/users/authenticate')
    api.add_resource(GetUserAPI, '/api/users/<int:user_id>')
    api.add_resource(DeleteUserAPI, '/api/users/<int:user_id>')
