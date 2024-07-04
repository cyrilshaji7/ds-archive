# app/__init__.py
from flask import Flask
from app.routes import api
from app.db import Database
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "jhsdjklfhlskdhfklsdhflkjhsdlfhsdf"  # Change this in production
    #app.config['JWT_TOKEN_LOCATION'] = ['headers', 'query_string']
    app.config['PROPAGATE_EXCEPTIONS'] = False
    app.register_blueprint(api, url_prefix="/api")
    jwt = JWTManager(app)
    jwt.init_app(app)
    return app

