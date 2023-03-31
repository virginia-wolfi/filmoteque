import sys
import os
sys.path.append(os.getcwd())
from werkzeug.security import generate_password_hash
from sqlalchemy import insert
from .models import *
from .extentions import db
import csv


pwd_hash = generate_password_hash('123456')

def insert_roles():
    db.session.execute(insert(Roles), [
                       {"name": "user"},
                       {"name": "admin"}
                   ])
    db.session.commit()

def insert_users():
    db.session.execute(insert(Users),
                   [
                       {"nickname": "user_1", "email": "user_1@gmail.com", "psw": pwd_hash, "role_id": 1},
                       {"nickname": "user_2", "email": "user_2@gmail.com", "psw": pwd_hash, "role_id": 1},
                       {"nickname": "admin", "email": "admin@gmail.com", "psw": pwd_hash, "role_id": 2}
                   ]
                   )
    db.session.commit()

def insert_genres():
    db.session.execute(insert(Genres), [
                   {'name': 'action'}, {'name': 'adventure'}, {'name': 'animation'},
                   {'name': 'biography'}, {'name': 'comedy'},  {'name': 'crime'},
                   {'name': 'documentary'}, {'name': 'drama'}, {'name': 'family'},
                   {'name': 'fantasy'}, {'name': 'film-noir'}, {'name': 'game-show'},
                   {'name': 'history'}, {'name': 'horror'}, {'name': 'music'},
                   {'name': 'musical'}, {'name': 'mystery'}, {'name': 'news'},
                   {'name': 'reality-tv'}, {'name': 'romance'}, {'name': 'sci-fi'},
                   {'name': 'sport'}, {'name': 'talk-show'}, {'name': 'thriller'},
                   {'name': 'war'}, {'name': 'western'}
                   ])
    db.session.commit()

def insert_directors():
    db.session.execute(insert(Directors), [
                       {"name": "Quentin Tarantino"},
                       {"name": "Bong Joon Ho"},
                       {"name": "Alejandro Gonzalez Inarritu"},
                       {"name": "Stanley Kubrick"},
                       {"name": "Coen brothers"},
                       {"name": "Martin McDonagh"},
                       {"name": "Paolo Sorrentino"},
                       {"name": "Peter Farrelly"},
                       {"name": "Peter Weir"},
                       {"name": "Francis Ford Coppola"},
                       {"name": "Lars von Trier"},
                       {"name": "Julie Taymor"},
                       {"name": "Darren Aronofsky"},
                       {"name": "Martin Scorsese"},
                       {"name": "Damien Chazelle"},
                       {"name": "Jordan Peele"},
                       {"name": "Kar-Wai Wong"},
                       {"name": "Sofia Coppola"},
                       {"name": "Tim Berton"}
                   ])
    db.session.commit()

def insert_movies():
    with open("filmoteque/database/movies.csv") as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')
        header = next(reader)
        for i in reader:
            kwargs = {column: value for column, value in zip(header, i)}
            new_entry = Movies(**kwargs)
            db.session.add(new_entry)
        db.session.commit()

def insert_movies_genres():
    with open("filmoteque/database/movies-genres_data.csv") as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)
        for i in reader:
            kwargs = {column: value for column, value in zip(header, i)}
            db.session.execute(insert(movies_genres).values(kwargs))
        db.session.commit()

    db.session.commit()


def insert_all():
    insert_roles()
    insert_users()
    insert_genres()
    insert_directors()
    insert_movies()
    insert_movies_genres()

