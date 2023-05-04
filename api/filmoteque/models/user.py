from ..db import db
from datetime import datetime
from flask_login import UserMixin


class UserModel(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    psw = db.Column(db.String(500), nullable=False)
    reg_date = db.Column(db.DateTime, default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    movies = db.relationship("MovieModel", backref="user")

    def __repr__(self) -> str:
        return f"<Users {self.id}>"

    @classmethod
    def find_by_email(cls, email: str) -> "UserModel":
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_nickname(cls, nickname: str) -> "UserModel":
        return cls.query.filter_by(nickname=nickname).first()

    @classmethod
    def find_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
