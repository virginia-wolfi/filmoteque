from ..extentions import db


class DirectorModel(db.Model):
    __tablename__ = "directors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    info = db.Column(db.Text, nullable=True)
    movies = db.relationship("MovieModel", backref="director")

    def __repr__(self):
        return f"<Directors {self.id}>"

    @classmethod
    def find_by_name(cls, name: str) -> "DirectorModel":
        return cls.query.filter_by(name=name).first()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
