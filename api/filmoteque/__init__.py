import os
from flask import Flask

from flask import abort
from .models.user import UserModel
from .cli import bp
from .config import DevelopmentConfig
from .apis import blueprint as api1
from .db import db
from .lm import login_manager


def create_app(config_obj=DevelopmentConfig()):
    app = Flask(__name__)
    app.config.from_object(config_obj)
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
