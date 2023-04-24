from ..models.genre import GenreModel
from ..models.director import DirectorModel
from ..models.movie import MovieModel
from ..models.user import UserModel
from ..extentions import extra, db
from flask_login import current_user
from flask import abort


def genres_handler(genres: set[str]) -> list[GenreModel]:
    genres_list = []
    for g in genres:
        genre = GenreModel.find_by_name(g.lower())
        if not genre:
            continue
        genres_list.append(genre)
    return genres_list


def director_handler(data: dict) -> DirectorModel | None:
    director_name = data.get("director", None)
    if not director_name:
        return
    director = DirectorModel.find_by_name(name=director_name)
    if not director:
        director = DirectorModel(name=director_name)
        director.save_to_db()
        extra.info(
            f"User added director {director, director.name}",
            extra={"user": current_user},
        )
    data.pop("director")
    return director


def verify_movie(movie_id: int) -> MovieModel:
    movie = MovieModel.find_by_id(movie_id)
    user = UserModel.find_by_id(current_user.get_id())
    if not movie:
        abort(404, "Movie not found")
    if movie.user_id != user.id and user.role.name != "admin":
        abort(
            403,
            "Only administrator or user who added the movie can make changes",
        )
    return movie


def rollback() -> None:
    db.session.rollback()
    abort(500, "Something is broken")
