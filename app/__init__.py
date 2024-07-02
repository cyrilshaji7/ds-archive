# app/__init__.py
from flask import Flask
from app.routes import api
from app.db import Database
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Change this in production
    app.register_blueprint(api, url_prefix="/api")
    jwt = JWTManager(app)

    return app

