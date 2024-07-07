# app/__init__.py
from flask import Flask
from app.routes import api
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "jhsdjklfhlskdhfklsdhflkjhsdlfhsdf"  # Change this in production
    #app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
    app.config['PROPAGATE_EXCEPTIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking
    app.register_blueprint(api, url_prefix="/api")
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)
    jwt.init_app(app)
    return app

