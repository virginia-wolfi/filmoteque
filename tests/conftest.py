import pytest
from filmoteque import create_app, db
from filmoteque.insert_setup import *
from filmoteque.models import Movies
from pathlib import Path
from sqlalchemy import delete

resources = Path(__file__).parent / "resources"


psw = '123456'
pwd_hash = generate_password_hash(psw)
admin_user = ('admin@gmail.com', '123456')
ordinary_user_1 = ('user_1@gmail.com', '123456')
ordinary_user_2 = ('user_2@gmail.com', '123456')
not_user = ('no_email', 'no_psw')

movies_list = (
{'title': 'Pulp Fiction', 'year': 1994, 'director_id': 1, 'rate': 8.9, 'user_id': 1},
{'title': 'Django Unchained', 'year': 2012, 'director_id': 1, 'rate': 8.4, 'user_id': 1},
{'title': 'Parasite', 'year': 2019, 'director_id': 2, 'rate': 8.5, 'user_id': 1},
{'title': 'Memories of Murder', 'year': 2003, 'director_id': 2, 'rate': 8.1, 'user_id': 1},
{'title': 'Birdman or (The Unexpected Virtue of Ignorance)', 'year': 2014, 'director_id': 3, 'rate': 7.7, 'user_id': 1},
{'title': 'Bardo, False Chronicle of a Handful of Truths', 'year': 2022, 'director_id': 3, 'rate': 6.7, 'user_id': 1},
{'title': 'Eyes Wide Shut', 'year': 1999, 'director_id': 4, 'rate': 7.5, 'user_id': 1},
{'title': 'Full Metal Jacket', 'year': 1987, 'director_id': 4, 'rate': 8.4, 'user_id': 1},
{'title': 'The Shining', 'year': 1980, 'director_id': 4, 'rate': 8.4, 'user_id': 1},
{'title': 'Fargo', 'year': 1996, 'director_id': 5, 'rate': 8.1, 'user_id': 1},
{'title': 'No Country for Old Men', 'year': 2007, 'director_id': 5, 'rate': 8.2, 'user_id': 1},
{'title': 'The Big Lebowski', 'year': 1998, 'director_id': 5, 'rate': 8.1, 'user_id': 1},
{'title': 'The Banshees of Inisherin', 'year': 2022, 'director_id': 6, 'rate': 7.7, 'user_id': 1},
{'title': 'Three Billboards Outside Ebbing, Missouri', 'year': 2022, 'director_id': 6, 'rate': 7.7, 'user_id': 1},
{'title': 'Loro', 'year': 2018, 'director_id': 7, 'rate': 6.7, 'user_id': 1},
{'title': 'Youth', 'year': 2015, 'director_id': 7, 'rate': 7.3, 'user_id': 1}
)

movies_genres_list = ({'genre_id': 6, 'movie_id': 1}, {'genre_id': 5, 'movie_id': 1}, {'genre_id': 8, 'movie_id': 2},
                 {'genre_id': 26, 'movie_id': 2}, {'genre_id': 8, 'movie_id': 3},
                 {'genre_id': 24, 'movie_id': 3}, {'genre_id': 8, 'movie_id': 4}, {'genre_id': 6, 'movie_id': 4},
                 {'genre_id': 17, 'movie_id': 4}, {'genre_id': 8, 'movie_id': 5}, {'genre_id': 5, 'movie_id': 5},
                 {'genre_id': 5, 'movie_id': 6}, {'genre_id': 8, 'movie_id': 6}, {'genre_id': 8, 'movie_id': 7},
                 {'genre_id': 17, 'movie_id': 7}, {'genre_id': 24, 'movie_id': 7}, {'genre_id': 8, 'movie_id': 8},
                 {'genre_id': 25, 'movie_id': 8}, {'genre_id': 8, 'movie_id': 9}, {'genre_id': 14, 'movie_id': 9},
                 {'genre_id': 6, 'movie_id': 10}, {'genre_id': 8, 'movie_id': 10}, {'genre_id': 24, 'movie_id': 10},
                 {'genre_id': 6, 'movie_id': 11}, {'genre_id': 8, 'movie_id': 11}, {'genre_id': 24, 'movie_id': 11},
                 {'genre_id': 6, 'movie_id': 12}, {'genre_id': 5, 'movie_id': 12}, {'genre_id': 8, 'movie_id': 13},
                 {'genre_id': 5, 'movie_id': 13}, {'genre_id': 8, 'movie_id': 14}, {'genre_id': 5, 'movie_id': 14},
                 {'genre_id': 6, 'movie_id': 14}, {'genre_id': 8, 'movie_id': 15}, {'genre_id': 4, 'movie_id': 15},
                 {'genre_id': 5, 'movie_id': 16}, {'genre_id': 8, 'movie_id': 16}, {'genre_id': 15, 'movie_id': 16},
                 )

@pytest.fixture(scope='module')
def app():
    app = create_app(database='postgresql+psycopg2://postgres:8066@localhost/film_collection_test')
    app.config.update({
        "TESTING": True,
    })
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

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email, psw):
        return self._client.post(
            '/api/login',
            json={'email': email, 'psw': psw}
        )

    def logout(self):
        return self._client.post('/api/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)


class MoviesActions(object):
    def __init__(self, client):
        self._client = client

    def create_movie(self, title, director, rate, year, genre_1, genre_2, genre_3):
        return self._client.post(
            '/api/movies/adding_movie',
            query_string={'genre_1': genre_1, 'genre_2': genre_2, 'genre_3': genre_3},
            json=({'title': title, 'director': director, 'rate': rate, 'year': year}))

    def edit_movie(self, movie_id, query_string, json):
        return self._client.patch(
            f'/api/movies/{movie_id}/',
            query_string=query_string,
            json=(json))

    def delete_movie(self, movie_id):
        return self._client.delete(f'/api/movies/{movie_id}/')

    def upload_poster(self, movie_id, file_part, file_name):
        return self._client.post(f'/api/movies/{movie_id}/poster',
                    data={
                        file_part: (open(resources / 'poster.jpeg', 'rb'), file_name)
                    })

    def delete_poster(self, movie_id):
        return self._client.delete(f'/api/movies/{movie_id}/poster')

    def search_movies(self, query_string):
        return self._client.get(f'/api/movies/',
            query_string=query_string)


@pytest.fixture
def movie(client):
    return MoviesActions(client)


@pytest.fixture
def add_movie(client, app, auth, movie):
    auth.login(*ordinary_user_1)
    with client:
        response = movie.create_movie('Django Unchained', 'Quentin Tarantino', 8.4, 2012, 'crime', 'comedy', '')
        movie_id = response.json['Movie was added successfully']['id']
        auth.logout()
    yield movie_id
    with app.app_context():
        if db.session.get(Movies, movie_id):
            db.session.delete(db.session.get(Movies, movie_id))
            db.session.commit()

@pytest.fixture(scope='module')
def insert_data(app):
    with app.app_context():
        db.drop_all()
        db.create_all()
        insert_roles()
        insert_users()
        insert_genres()
        insert_directors()
        db.session.execute(insert(Movies).values(movies_list))
        db.session.commit()
        db.session.execute(insert(movies_genres).values(movies_genres_list))
        db.session.commit()

