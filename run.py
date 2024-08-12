from app import create_app
from app.routes import api
from flask import redirect

app = create_app()
app.register_blueprint(api, url_prefix='/api')

@app.route('/')
def home():
    return redirect('/api/')

if __name__ == "__main__":
    app.run(debug=True)
