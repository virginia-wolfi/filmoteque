from flask import request, abort, session
from .constants.http_status_codes import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from werkzeug.security import check_password_hash, generate_password_hash
import validators
from .models import Users
from .extentions import db, api, extra
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import insert
from flask_restx import Namespace, Resource, fields

users = Namespace(
    "Users", description="Users related operations", path="/"
)

login_request_body_model = api.model(
    "Login_data_model",
    {
        "email": fields.String(
            required=True, description="User's email", example="admin@gmail.com"
        ),
        "psw": fields.String(
            required=True, description="User's password", example="123456"
        ),
    },
)
register_request_body_model = api.model(
    "Registration_data_model",
    {
        "nickname": fields.String(
            required=True, description="User's nickname", example="newuser"
        ),
        "email": fields.String(
            required=True, description="User's email", example="newuser@gmail.com"
        ),
        "psw": fields.String(
            required=True, description="User's password", example="123456"
        ),
    },
)

users_model = api.model(
    "Users_model",
    {"id": fields.Integer, "nickname": fields.String, "email": fields.String},
)


@users.route("/login", doc={"description": "User authorization"})
class Login(Resource):
    @users.response(200, "Success")
    @users.response(401, "Invalid email/password supplied")
    @users.expect(login_request_body_model)
    @users.marshal_with(users_model, envelope="User logged in")
    def post(self):
        """Logs user into the system"""
        email = request.json.get("email", "")
        psw = request.json.get("psw", "")
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.psw, psw):
            login_user(user)
            extra.info("User logged in", extra={"user": current_user})
            return user, HTTP_200_OK

        abort(HTTP_401_UNAUTHORIZED, "Wrong credentials")


@users.route("/registration", doc={"description": "User registration"})
class Registration(Resource):
    @users.response(201, "New user created")
    @users.response(400, "Client-side input fails validation")
    @users.response(409, "The specified email/nickname already exists")
    @users.expect(register_request_body_model)
    @users.marshal_with(users_model, envelope="User created")
    def post(self):
        """Creates new user"""
        nickname = request.json.get("nickname", "")
        email = request.json.get("email", "")
        psw = request.json.get("psw", "")

        if len(psw) < 6:
            abort(HTTP_400_BAD_REQUEST, "Password must be 6 characters or more")

        if len(nickname) < 3:
            abort(HTTP_400_BAD_REQUEST, "Nickname must be 3 or more characters")

        if not nickname.isalnum() or " " in nickname:
            abort(HTTP_400_BAD_REQUEST, "Nickname should be alphanumeric")

        if not validators.email(email):
            abort(HTTP_400_BAD_REQUEST, "Email is not valid")

        if Users.query.filter_by(nickname=nickname).first():
            abort(HTTP_409_CONFLICT, "Nickname is taken")

        if Users.query.filter_by(email=email).first():
            abort(HTTP_409_CONFLICT, "Email is taken")

        pwd_hash = generate_password_hash(psw)
        request.json["psw"] = pwd_hash
        request.json["role_id"] = 1
        user_id = db.session.execute(
            insert(Users).values(request.json)
        ).inserted_primary_key[0]
        user = db.session.get(Users, user_id)
        try:
            db.session.commit()
            extra.info("User created", extra={"user": current_user})
            return user, HTTP_201_CREATED
        except:
            db.session.rollback()
            abort(HTTP_500_INTERNAL_SERVER_ERROR, "Something is broken")


@users.route("/profile", doc={"description": "User profile"})
class Profile(Resource):
    @users.response(200, "Success")
    @users.response(401, "User not authorized")
    @login_required
    @users.marshal_with(users_model, envelope="User profile")
    def get(self):
        """Shows current logged-in user profile"""
        user_id = current_user.get_id()
        user = db.session.get(Users, user_id)
        return user, HTTP_200_OK


@users.route("/logout", doc={"description": "User logout"})
class Logout(Resource):
    @users.response(200, "Success")
    @users.response(401, "User not authorized")
    @login_required
    @users.marshal_with(users_model, envelope="User logged out")
    def post(self):
        """Logs out current logged-in user session"""
        user_id = current_user.get_id()
        user = db.session.get(Users, user_id)
        logout_user()
        extra.info("User logged out", extra={"user": current_user})
        return user, HTTP_200_OK
