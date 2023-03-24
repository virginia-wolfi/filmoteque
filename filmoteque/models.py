from filmoteque.extentions import db
from datetime import datetime
from flask_login import UserMixin


movies_genres = db.Table('movies_genres',
                        db.Column('id', db.Integer, primary_key=True, autoincrement=True),
                        db.Column('movie_id', db.Integer, db.ForeignKey('movies.id', ondelete="CASCADE"),
                                  primary_key=True),
                        db.Column('genre_id', db.Integer, db.ForeignKey('genres.id', ondelete="CASCADE"),
                                  primary_key=True))

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    director_id = db.Column(db.Integer, db.ForeignKey('directors.id', ondelete="SET NULL"))
    rate = db.Column(db.Float, db.CheckConstraint('rate between 0 and 10'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete="SET NULL"))
    description = db.Column(db.Text, nullable=True)
    poster = db.Column(db.LargeBinary)

    genres = db.relationship('Genres', secondary=movies_genres, backref='movies')

    def __repr__(self):
        return f'<Movies {self.id}>'

class Genres(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self):
        return f'<Genres {self.id}>'

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    psw = db.Column(db.String(500), nullable=False)
    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    movies = db.relationship('Movies', backref='user')


    def __repr__(self):
        return f'<Users {self.id}>'

class Roles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship('Users', backref='role', lazy='subquery')

class Directors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    info = db.Column(db.Text, nullable=True)
    movies = db.relationship('Movies', backref='director')

    def __repr__(self):

        return f'<Directors {self.id}>'


