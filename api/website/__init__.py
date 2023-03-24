from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import json

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_file = json.load(open((str(Path(__file__).parents[0]))+'/secrets/secrets.json'))
    app.config['SECRET_KEY'] = app.secret_file['secret_key']

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    return app