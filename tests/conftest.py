import pytest
from api.filmoteque.insert_setup import *
from api.filmoteque import MovieModel, movies_genres
from api.filmoteque import create_app
from api.filmoteque.config import TestingConfig
from sqlalchemy import insert
from .helper.insertion_data import *
from .helper.fixtures_classes import *


@pytest.fixture(scope="module")
def app():
    app = create_app(object=TestingConfig())
    with app.app_context():
        db.drop_all()
        db.create_all()
        insert_roles()
        insert_users()
        insert_genres()
        insert_directors()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth(client):
    return AuthActions(client)



@pytest.fixture
def movie(client):
    return MoviesActions(client)


@pytest.fixture
def created_movie(client, app, auth, movie):
    auth.login(*ordinary_user_1)
    with client:
        response = movie.create_movie(
            "Django Unchained", "Quentin Tarantino", 8.4, 2012, "crime", "comedy", ""
        )
        movie_id = response.json["Movie was added successfully"]["id"]
        auth.logout()
    yield movie_id
    with app.app_context():
        if db.session.get(MovieModel, movie_id):
            db.session.delete(db.session.get(MovieModel, movie_id))
            db.session.commit()


@pytest.fixture(scope="module")
def insert_data(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        insert_roles()
        insert_users()
        insert_genres()
        insert_directors()
        db.session.execute(insert(MovieModel).values(movies_list))
        db.session.commit()
        db.session.execute(insert(movies_genres).values(movies_genres_list))
        db.session.commit()

