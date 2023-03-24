from flask import Flask, abort
from filmoteque.extentions import db, login_manager, api, blueprint as api_1, dictConfig
from filmoteque.auth import users as ns1
from filmoteque.movies import movies as ns2
from filmoteque.models import *
from filmoteque.constants.http_status_codes import HTTP_401_UNAUTHORIZED

api.add_namespace(ns1)
api.add_namespace(ns2)

def create_app(database='postgresql+psycopg2://postgres:8066@localhost/film_collection'):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = database
    app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False
    app.config['SECRET_KEY'] = '20d59e04e26833e150ee3da1ea0f175905685e91'
    app.config['RESTX_MASK_SWAGGER'] = False
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

    return app
