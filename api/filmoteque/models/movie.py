from ..extentions import db
from sqlalchemy import update


class MovieModel(db.Model):
    __tablename__ = "movies"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    year = db.Column(
        db.Integer, db.CheckConstraint("year between 1900 and 2025"), nullable=False
    )
    director_id = db.Column(
        db.Integer, db.ForeignKey("directors.id", ondelete="SET NULL")
    )
    rate = db.Column(
        db.Float, db.CheckConstraint("rate between 0 and 10"), nullable=False
    )
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="SET NULL"))
    description = db.Column(db.Text, nullable=True)
    poster = db.Column(db.LargeBinary)

    genres = db.relationship("GenreModel", secondary="movies_genres", backref="movies")

    def __repr__(self):
        return f"<Movies {self.id}>"

    @classmethod
    def find_by_id(cls, _id: int) -> "MovieModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_title(cls, title: str) -> "MovieModel":
        return cls.query.filter(cls.title.ilike(title)).first()

    @classmethod
    def update_movie(cls, data: list, movie_id: int) -> None:
        db.session.execute(update(cls).where(cls.id == movie_id).values(**data))
        db.session.commit()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()


movies_genres = db.Table(
    "movies_genres",
    db.Column("id", db.Integer, primary_key=True, autoincrement=True),
    db.Column(
        "movie_id",
        db.Integer,
        db.ForeignKey("movies.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "genre_id",
        db.Integer,
        db.ForeignKey("genres.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
