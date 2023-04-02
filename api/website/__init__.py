from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import json

db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_file = json.load(open((str(Path(__file__).parents[0]))+'/secrets/secrets.json'))
    app.config['SECRET_KEY'] = app.secret_file['secret_key']

    app.config['SQLALCHEMY_DATABASE_URI'] = str(app.secret_file['db_connection'])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")

    from .models import Users, Team, Rubric, Question, TeamAssignment, RubricAssignment, QuestionAssignment

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(userID):
        return Users.query.get(int(userID))

    return app