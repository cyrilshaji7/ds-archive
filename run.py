# run.py
from app import create_app
from flask import Flask, redirect
from app.routes import api

if __name__ == "__main__":
    app = create_app()
    app.register_blueprint(api, url_prefix='/api')
    @app.route('/')
    def home():
        return redirect('/api/')
    app.run(debug=True)
