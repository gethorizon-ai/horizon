from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from config import Config


db = SQLAlchemy()
migrate = Migrate()
auth = HTTPBasicAuth()
api = Api()
cors = CORS()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    api = Api()
    from app.register_endpoints import register_all_routes
    register_all_routes(api)  # Pass the app object here
    api.init_app(app)

    return app
