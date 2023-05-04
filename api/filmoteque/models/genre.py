from ..db import db


class GenreModel(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    def __repr__(self) -> str:
        return f"<Genres {self.id}>"

    @classmethod
    def find_by_name(cls, name: str) -> "GenreModel":
        return cls.query.filter_by(name=name).first()
