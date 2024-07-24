# run.py
from app import create_app
from app.routes import api

if __name__ == "__main__":
    app = create_app()
    app.register_blueprint(api, url_prefix='/api')
    app.run(debug=True)
