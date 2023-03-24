from werkzeug.security import generate_password_hash
import pytest
from filmoteque import db
from filmoteque.models import Users
from flask import session
from .conftest import admin_user
psw = '123456'
pwd_hash = generate_password_hash(psw)


@pytest.mark.parametrize(('nickname', 'email', 'psw', 'status_code', 'message'), (
                         ('user1', 'user1@gmail.com', psw, 201, b'User created'),
                         ('user1', 'user1111@gmail.com', psw, 409, b'Nickname is taken'),
                         ('user111', 'user1@gmail.com', psw, 409, b'Email is taken'),
                         ('user*_', 'user1@gmail.com', psw, 400, b'Nickname should be alphanumeric'),
                         ('', 'user1@gmail.com', psw, 400, b'Nickname must be 3 or more characters'),
                         ('user111', 'user1111@gmail.com', '', 400, b'Password must be 6 characters or more'),
                         ('user111', 'user@gmail@com', psw, 400, b'Email is not valid')))
def test_registation(client, app, nickname, email, psw, status_code, message):
    response = client.post('/api/registration', json=({'nickname': nickname, 'email': email, 'psw': psw}))
    assert response.status_code == status_code
    if status_code == 201:
        with app.app_context():
            user_id = response.json['User created']['id']
            assert db.session.get(Users, user_id) is not None
    assert message in response.data


def test_login(client, auth):
    response = auth.login(*admin_user)
    assert response.status_code == 200
    with client:
        client.get('/api/profile')
        assert session['_user_id'] == '3'


@pytest.mark.parametrize(('email', 'psw', 'status_code', 'message'), (
        ('1@gmail.com', psw, 401, b'Wrong credentials'),
        ('user1@gmail.com', '1234', 401, b'Wrong credentials'),
        ('user1@gmail.com', psw, 200, b'User logged in')))
def test_login_validate_input(auth, email, psw, status_code, message, app):
    response = auth.login(email, psw)
    assert response.status_code == status_code
    assert message in response.data


def test_profile(auth, client):
    auth.login(*admin_user)
    with client:
        response = client.get('/api/profile')
        assert session['_user_id'] == '3'
        assert response.status_code == 200
    with client:
        auth.logout()
        response = client.get('/api/profile')
        assert response.status_code == 401
        assert b'Log in to view this page' in response.data

def test_profile_unauthorized(client):
    with client:
        response = client.get('/api/profile')
        assert '_user_id' not in session
        assert response.status_code == 401


def test_logout(client, auth):
    auth.login(*admin_user)
    with client:
        response = auth.logout()
        assert '_user_id' not in session
        assert response.status_code == 200


def test_logout_unathorized(client, auth):
    with client:
        response = auth.logout()
        assert '_user_id' not in session
        assert response.status_code == 401