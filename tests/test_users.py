import pytest
from api.filmoteque import UserModel
from flask import session
from .helper.insertion_data import admin_user, ordinary_user_1
from .helper.parameters import (
    user_registration_params,
    user_login_validation_params,
)


@pytest.mark.parametrize(
    ("nickname", "email", "psw", "status_code", "message"),
    user_registration_params,
)
def test_registration(client, app, nickname, email, psw, status_code, message):
    response = client.post(
        "/api/registration",
        json=({"nickname": nickname, "email": email, "psw": psw}),
    )
    assert response.status_code == status_code
    if status_code == 201:
        with app.app_context():
            user_id = response.json["User created"]["id"]
            assert UserModel.find_by_id(user_id) is not None
    assert message in response.data


@pytest.mark.parametrize(
    ("email", "psw", "status_code", "message"),
    user_login_validation_params,
)
def test_login(auth, client, email, psw, status_code, message, app):
    response = auth.login(email, psw)
    assert response.status_code == status_code
    assert message in response.data


def test_profile(auth, client):
    auth.login(*admin_user)
    with client:
        response = client.get("/api/users/3")
        assert session["_user_id"] == "3"
        assert response.status_code == 200

        response = client.get("/api/users/0")
        assert response.status_code == 404
        assert b"User not found" in response.data

    auth.logout()
    with client:
        response = client.get("/api/users/3")
        assert response.status_code == 401
        assert b"Log in to view this page" in response.data

    auth.login(*ordinary_user_1)
    with client:
        response = client.get("/api/users/3")
        assert session["_user_id"] == "1"
        assert response.status_code == 403
        assert b"Access is not allowed" in response.data


def test_profile_unauthorized(client):
    with client:
        response = client.get("/api/users/3")
        assert "_user_id" not in session
        assert response.status_code == 401
        assert b"Log in to view this page" in response.data


def test_logout(client, auth):
    auth.login(*admin_user)
    with client:
        response = auth.logout()
        assert "_user_id" not in session
        assert response.status_code == 200
        assert b"User logged out" in response.data


def test_logout_unathorized(client, auth):
    with client:
        response = auth.logout()
        assert "_user_id" not in session
        assert response.status_code == 401
        assert b"Log in to view this page" in response.data
