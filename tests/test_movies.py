import pytest
from .conftest import admin_user, ordinary_user_1
from api.filmoteque import MovieModel
from api.filmoteque import db
from .helper.parameters import (
    movie_creation_params,
    poster_upload_params,
    movie_edit_params,
    movie_search_params,
    movie_creation_unauth_params,
    poster_upload_unath_params,
    poster_delete_params,
    movie_delete_params
)


@pytest.mark.parametrize(
    ("title", "director", "rate", "year", "genre_1", "genre_2", "genre_3", "status_code", "message"),
    movie_creation_params,
)
def test_movie_creation(
    client,
    auth,
    app,
    movie,
    title,
    director,
    rate,
    year,
    genre_1,
    genre_2,
    genre_3,
    status_code,
    message,
):
    auth.login(*ordinary_user_1)
    with client:
        response = movie.create_movie(
            title, director, rate, year, genre_1, genre_2, genre_3
        )
        assert response.status_code == status_code
        if status_code == 201:
            with app.app_context():
                movie_id = response.json["Movie was added successfully"]["id"]
                assert db.session.get(MovieModel, movie_id) is not None
        assert message in response.data


@pytest.mark.parametrize(
    ("title", "director", "rate", "year", "genre_1", "genre_2", "genre_3", "status_code", "message"),
    movie_creation_unauth_params
)
def test_movie_creation_unathorized(
    client,
    movie,
    title,
    director,
    rate,
    year,
    genre_1,
    genre_2,
    genre_3,
    status_code,
    message,
):
    response = movie.create_movie(
        title, director, rate, year, genre_1, genre_2, genre_3
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    ("user", "status_code", "message"),
    movie_delete_params
)
def test_movie_delete(app, client, auth, movie, created_movie, user, status_code, message):
    movie_id = created_movie
    auth.login(*user)
    with client:
        response = movie.delete_movie(movie_id)
    assert response.status_code == status_code
    assert message in response.data
    if user in [ordinary_user_1, admin_user]:
        with app.app_context():
            assert db.session.get(MovieModel, movie_id) is None


@pytest.mark.parametrize(
    ("user", "query_string", "json", "status_code", "message"),
    movie_edit_params,
)
def test_movie_edit(
    client, auth, movie, created_movie, user, query_string, json, status_code, message
):
    movie_id = created_movie
    auth.login(*user)
    with client:
        response = movie.edit_movie(movie_id, query_string, json)
    assert response.status_code == status_code
    assert message in response.data

def test_movie_get(
    client, auth, movie, created_movie
):
    movie_id = created_movie
    response = movie.get_movie(movie_id)
    assert response.status_code == 200
    assert response.json['id'] == movie_id

@pytest.mark.parametrize(
    ("file_part", "file_name", "status_code", "message"),
    poster_upload_params
)
def test_poster_upload(
    app, client, auth, movie, created_movie, file_part, file_name, status_code, message
):
    users = [admin_user, ordinary_user_1]
    for u in users:
        movie_id = created_movie
        auth.login(*u)
        with client:
            response = movie.upload_poster(movie_id, file_part, file_name)
        assert response.status_code == status_code
        if status_code == 201:
            with app.app_context():
                assert db.session.get(MovieModel, movie_id).poster is not None
        assert message in response.data


@pytest.mark.parametrize(
    ("user", "status_code", "message"),
    poster_upload_unath_params
)
def test_poster_upload_unathorized(
    app, client, auth, created_movie, movie, user, status_code, message
):
    movie_id = created_movie
    auth.login(*user)
    with client:
        response = movie.upload_poster(movie_id, "file", "poster.jpeg")
    assert response.status_code == status_code
    assert message in response.data
    with app.app_context():
        assert db.session.get(MovieModel, movie_id).poster is None


def test_poster_upload_not_exists(client, auth, app, movie):
    auth.login(*admin_user)
    with app.app_context():
        movie_id = db.session.query(db.func.max(MovieModel.id)).scalar() + 1
    with client:
        response = movie.upload_poster(movie_id, "file", "poster.jpeg")
        assert response.status_code == 404


@pytest.mark.parametrize(
    ("user", "status_code", "message"),
    poster_delete_params
)
def test_poster_delete(app, client, auth, movie, created_movie, user, status_code, message):
    movie_id = created_movie
    auth.login(*user)
    with client:
        response = movie.delete_poster(movie_id)
    assert response.status_code == status_code
    assert message in response.data
    if user in [ordinary_user_1, admin_user]:
        with app.app_context():
            assert db.session.get(MovieModel, movie_id).poster is None


@pytest.mark.parametrize(
    ("query_string", "status_code", "response_data", "len_items"),
    movie_search_params
)
def test_movie_search(
    movie, insert_data, query_string, status_code, response_data, len_items
):
    response = movie.search_movies(query_string)
    assert response.status_code == status_code
    assert response_data in response.data
    assert len(response.json) == len_items


def test_movie_search_orderby(movie, insert_data):
    response = movie.search_movies({"year": "DESC", "director": "Sorrentino"})
    assert response.status_code == 200
    assert list(response.json.values())[0]["title"] == "Loro"
    assert list(response.json.values())[1]["title"] == "Youth"

    response = movie.search_movies(
        {"rate": "ASC", "year": "ASC", "director": "Stanley"}
    )
    assert response.status_code == 200
    assert list(response.json.values())[0]["title"] == "Eyes Wide Shut"
    assert list(response.json.values())[2]["title"] == "Full Metal Jacket"

