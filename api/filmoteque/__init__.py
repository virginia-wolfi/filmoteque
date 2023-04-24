from flask import Flask
import os

from .models.user import UserModel
from .models.movie import MovieModel, movies_genres
from .models.director import DirectorModel
from .models.genre import GenreModel
from .models.role import RoleModel
from .cli import bp
from .config import *
from .apis import blueprint as api1
from flask import abort
from .extentions import db, login_manager


def create_app(object=DevelopmentConfig()):
    app = Flask(__name__)
    app.config.from_object(object)
    if os.getenv("DATABASE_URL"):
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.json.sort_keys = False
    app.json.ensure_ascii = False
    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(UserModel, user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        return abort(401, "Log in to view this page")

    login_manager.init_app(app)
    app.register_blueprint(api1)
    app.register_blueprint(bp)

    return app
