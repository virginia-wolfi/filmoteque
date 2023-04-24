from ..models.user import UserModel
from flask import abort
from flask_login import current_user
import validators
from ..extentions import db


def check_registration_data(data: dict) -> None:
    nickname = data.get("nickname", "")
    email = data.get("email", "")
    psw = data.get("psw", "")
    if len(nickname) < 3:
        abort(400, "Nickname must be 3 or more characters")

    if not nickname.isalnum() or " " in nickname:
        abort(400, "Nickname should be alphanumeric")

    if not validators.email(email):
        abort(400, "Email is not valid")

    if UserModel.find_by_nickname(nickname):
        abort(409, "Nickname is taken")

    if UserModel.find_by_email(email):
        abort(409, "Email is taken")

    if len(psw) < 6:
        abort(400, "Password must be 6 characters or more")


def verify_user(user_id: int) -> UserModel:
    user = UserModel.find_by_id(user_id)
    if not user:
        abort(404, "User not found")
    if current_user != user and current_user.role.name != "admin":
        abort(403, "Access is not allowed")
    return user


def rollback() -> None:
    db.session.rollback()
    abort(500, "Something is broken")
