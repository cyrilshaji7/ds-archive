# app/__init__.py
from flask import Flask
from app.routes import api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os


def create_app():
    app = Flask(__name__)
    #app.config["SECRET_KEY"] = "aaaaaaadcsdhjfklsdhfksdhfslkdjhfsjkldhfljksdf"  # Change this in production
    #app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'hjsdfhosidfjsdf798sd')
    app.config['PROPAGATE_EXCEPTIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost:5432/defaultdb'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
    #app.register_blueprint(api, url_prefix="/api")
    db = SQLAlchemy(app)
    jwt = JWTManager(app)
    jwt.init_app(app)
    return app



