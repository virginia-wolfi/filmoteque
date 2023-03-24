import pytest
from .conftest import admin_user, ordinary_user_1, ordinary_user_2, not_user
from filmoteque.models import Movies
from filmoteque import db



@pytest.mark.parametrize(('title', 'director', 'rate', 'year', 'genre_1', 'genre_2', 'genre_3', 'status_code', 'message'), (
        ('Pulp Fiction', 'Quentin Tarantino', 8.9, 1997, 'crime', 'comedy', '', 201, b'Movie was added successfully'),
        ('Pulp Fiction', 'Quentin Tarantino', 8.9, 1997, 'crime', 'comedy', '', 400,
         b'This movie title is already in the database'),
        ('Django Unchained', 'Quentin Tarantino', '', 2012, 'crime', 'comedy', '', 400, b'Insert value for rate'),
        ('Django Unchained', 'Que', 8.4, 2012, 'crime', 'comedy', '', 400,
         b'Director\'s name must be 4 or more letters'),
        ('Django Unchained', 'Quentin Tarantino', 8.4, 1812, 'crime', 'comedy', '', 400,
         b'Check if the movie\'s release date is correct'),
        ('Django Unchained', 'Quentin Tarantino', 8.4, 2012, '', '', '', 400,
         b'Insert at least one genre')
))
def test_adding_movie(client, auth, app, movie, title, director, rate, year, genre_1, genre_2, genre_3, status_code, message):
    auth.login(*ordinary_user_1)
    with client:
        response = movie.create_movie(title, director, rate, year, genre_1, genre_2, genre_3)
        assert response.status_code == status_code
        if status_code == 201:
            with app.app_context():
                movie_id = response.json['Movie was added successfully']['id']
                assert db.session.get(Movies, movie_id) is not None
        assert message in response.data



@pytest.mark.parametrize(('title', 'director', 'rate', 'year', 'genre_1', 'genre_2', 'genre_3', 'status_code', 'message'), (
        ('Django Unchained', 'Quentin Tarantino', '8.4', 2012, 'crime', 'comedy', '', 401, b'Log in to view this page'),
))
def test_adding_movie_unathorized(client, movie, title, director, rate, year, genre_1, genre_2, genre_3, status_code, message):
    response = movie.create_movie(title, director, rate, year, genre_1, genre_2, genre_3)
    assert response.status_code == status_code

@pytest.mark.parametrize(('file_part', 'file_name', 'status_code', 'message'),(
                         ('file', 'poster.jpeg', 201, b'Movie poster added'),
                         ('no_file', 'poster.jpeg', 400, b'No file part in the request'),
                         ('file', '', 400, b'No file selected for uploading'),
                         ('file', 'poster.xml', 400, b"Allowed file types are : 'pdf', 'png', 'jpg', 'jpeg'")
                         ))
def test_uploading_poster(app, client, auth, movie, add_movie, file_part, file_name, status_code, message):
    users = [admin_user, ordinary_user_1]
    for u in users:
        movie_id = add_movie
        auth.login(*u)
        with client:
            response = movie.upload_poster(movie_id, file_part, file_name)
        assert response.status_code == status_code
        assert message in response.data


@pytest.mark.parametrize(('user', 'status_code', 'message'), (
        (ordinary_user_2, 403, b'Only administrator or user who added the movie can make changes'),
        (not_user, 401, b'Log in to view this page')
))
def test_uploading_poster_user_unathorized(client, auth, add_movie, movie, user, status_code, message):
    movie_id = add_movie
    with client:
        auth.login(*user)
        response = movie.upload_poster(movie_id, 'file', 'poster.jpeg')
    assert response.status_code == status_code
    assert message in response.data


def test_upload_poster_not_exist(client, auth, app, movie):
    auth.login(*admin_user)
    with app.app_context():
        movie_id = db.session.query(db.func.max(Movies.id)).scalar() + 1
    with client:
        response = movie.upload_poster(movie_id, 'file', 'poster.jpeg')
        assert response.status_code == 404


@pytest.mark.parametrize(('user', 'status_code', 'message'), (
        (ordinary_user_1, 204, b''),
        (admin_user, 204, b''),
        (ordinary_user_2, 403, b'Only administrator or user who added the movie can make changes'),
        (not_user, 401, b'Log in to view this page')
))
def test_delete_poster(client, auth, movie, add_movie, user, status_code, message):
    movie_id = add_movie
    auth.login(*user)
    with client:
        response = movie.delete_poster(movie_id)
    assert response.status_code == status_code
    assert message in response.data

@pytest.mark.parametrize(('user', 'status_code', 'message'), (
        (ordinary_user_1, 204, b''),
        (admin_user, 204, b''),
        (ordinary_user_2, 403, b'Only administrator or user who added the movie can make changes'),
        (not_user, 401, b'Log in to view this page')
))
def test_delete_movie(client, auth, movie, add_movie, user, status_code, message):
    movie_id = add_movie
    auth.login(*user)
    with client:
        response = movie.delete_movie(movie_id)
    assert response.status_code == status_code
    assert message in response.data

@pytest.mark.parametrize(('user', 'query_string', 'json', 'status_code', 'message'), (
        (ordinary_user_1, {'genre_1': 'western', 'genre_2': 'comedy'}, {}, 200, b'Movie data updated'),
        (ordinary_user_1, {'genre_1': 'western'}, {'director': 'Quentin'}, 200, b'Movie data updated'),
        (admin_user, {}, {'title': 'Django unchained', 'director': 'Quentin'}, 200, b'Movie data updated'),
        (ordinary_user_1, {}, {}, 400, b'No input data was provided'),
        (ordinary_user_1, {}, {'title': ''}, 400, b'Title can\'t be blank'),
        (ordinary_user_1, {'genre_1': 'western', 'genre_2': 'comedy'}, {'title': 'Pulp Fiction'}, 400,
         b'This movie title is already in the database'),
        (admin_user, {}, {'director': 'Que'}, 400, b'Director\'s name must be 4 or more letters'),
        (admin_user, {}, {'year': 2050, 'title': 'Django unchained'}, 400,
         b'Check if the movie\'s release year is correct'),
        (not_user, {'genre_1': 'western', 'genre_2': 'comedy'}, {}, 401, b'Log in to view this page'),
        (ordinary_user_2, {}, {'title': 'Django unchained'}, 403,
         b'Only administrator or user who added the movie can make changes')
))
def test_edit_movie(client, auth, movie, add_movie, user, query_string, json, status_code, message):
    movie_id = add_movie
    auth.login(*user)
    with client:
        response = movie.edit_movie(movie_id, query_string, json)
    assert response.status_code == status_code
    assert message in response.data

@pytest.mark.parametrize(('query_string', 'status_code', 'response_data', 'len_items'), (
        ({'genre_1': 'western', 'filter_by_director': 'tara'}, 200, b'Quentin Tarantino', 1),
        ({'filter_by_year_before': 1985}, 200, b'The Shining', 1),
        ({'genre_1': 'thriller'}, 200, b'No Country for Old Men', 4),
        ({'filter_by_year_after': 2018}, 200, b'The Banshees of Inisherin', 5),
        ({'per_page': 5}, 200, b'Birdman or', 5),
        ({'per_page': 15, 'page': 2}, 200, b'Youth', 1),
        ({'filter_by_title': 'jacket'}, 200, b'Full Metal Jacket', 1),
        ({'filter_by_year_after': 2026}, 400, b'Check if the movie\'s release year is correct', 1),
        ({'filter_by_year_before': 1899}, 400, b'Check if the movie\'s release year is correct', 1),
        ({'filter_by_title': 'not title'}, 404, b'No data to show', 1),
        ({'per_page': 20, 'page': 2}, 404, b'No data to show', 1)
))
def test_search_movie(movie, insert_data, query_string, status_code, response_data, len_items):
    response = movie.search_movies(query_string)
    assert response.status_code == status_code
    assert response_data in response.data
    assert len(response.json) == len_items


def test_search_movie_orderby(movie, insert_data):
    response = movie.search_movies({'year': 'DESC', 'filter_by_director': 'Sorrentino'})
    assert response.status_code == 200
    assert list(response.json.values())[0]['title'] == 'Loro'
    assert list(response.json.values())[1]['title'] == 'Youth'

    response = movie.search_movies({'rate': 'ASC', 'year': 'ASC', 'filter_by_director': 'Stanley'})
    assert response.status_code == 200
    assert list(response.json.values())[0]['title'] == 'Eyes Wide Shut'
    assert list(response.json.values())[2]['title'] == 'Full Metal Jacket'


