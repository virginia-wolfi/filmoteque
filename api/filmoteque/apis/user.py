from flask import request, abort
from flask_restx import Namespace, Resource, marshal
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from ..logging import extra
from ..handlers import rollback
from ..handlers.user_handler import check_registration_data, verify_user
from .api_models.user import login_fields, registration_fields, user_model
from ..models.user import UserModel
from psycopg2 import OperationalError


users = Namespace("Users", description="Users related operations", path="/")


class UserLogin(Resource):
    @users.doc(
        responses={200: "Success", 401: "Invalid email/password provided"}
    )
    @users.expect(login_fields)
    @users.marshal_with(user_model, envelope="User logged in")
    def post(self):
        """Logs user into the system"""
        input_fields = marshal(request.get_json(), login_fields)
        user = UserModel.find_by_email(input_fields["email"])
        if user and check_password_hash(user.psw, input_fields["psw"]):
            login_user(user)
            extra.info("User logged in", extra={"user": user})
            return user, 200

        abort(401, "Wrong credentials")


class UserRegister(Resource):
    @users.response(201, "New user created")
    @users.response(400, "Client-side input fails validation")
    @users.response(409, "The specified email/nickname already exists")
    @users.expect(registration_fields)
    @users.marshal_with(user_model, envelope="User created")
    def post(self):
        """Creates new user"""
        input_fields = marshal(request.get_json(), registration_fields)
        check_registration_data(input_fields)
        psw_hash = generate_password_hash(input_fields["psw"])
        input_fields["psw"] = psw_hash
        input_fields["role_id"] = 1
        user = UserModel(**input_fields)
        try:
            user.save_to_db()
            extra.info("User created", extra={"user": user})
            return user, 201
        except OperationalError:
            rollback()


class UserProfile(Resource):
    @users.response(200, "Success")
    @users.response(401, "User not authorized")
    @users.response(403, "Access is not allowed")
    @users.marshal_with(user_model, envelope="User profile")
    @login_required
    def get(self, user_id: int):
        """Shows current logged-in user profile"""
        user = verify_user(user_id)
        return user, 200


class UserLogout(Resource):
    @users.response(200, "Success")
    @users.response(401, "User not authorized")
    @login_required
    @users.marshal_with(user_model, envelope="User logged out")
    def post(self):
        """Logs out current logged-in user session"""
        user_id = current_user.get_id()
        user = UserModel.find_by_id(user_id)
        logout_user()
        extra.info("User logged out", extra={"user": user})
        return user, 200
