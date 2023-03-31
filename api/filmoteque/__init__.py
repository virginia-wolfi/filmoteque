from flask import Flask, abort
import os

from .extentions import db, login_manager, api, blueprint as api_1
from .auth import users as ns1
from .movies import movies as ns2
from .models import *
from .constants.http_status_codes import HTTP_401_UNAUTHORIZED
from .cli import bp
from .config import *

api.add_namespace(ns1)
api.add_namespace(ns2)


def create_app(object=DevelopmentConfig()):
    app = Flask(__name__)
    app.config.from_object(object)
    if os.getenv('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.json.sort_keys = False
    app.json.ensure_ascii = False
    db.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Users, user_id)

    @login_manager.unauthorized_handler
    def unauthorized():
        return abort(HTTP_401_UNAUTHORIZED, "Log in to view this page")


    login_manager.init_app(app)
    app.register_blueprint(api_1)
    app.register_blueprint(bp)


    return app

