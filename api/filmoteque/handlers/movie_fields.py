from flask import abort, request
from ..models.movie import MovieModel
from ..models.genre import GenreModel
from werkzeug.datastructures import ImmutableMultiDict, FileStorage
from collections.abc import Mapping


movie_fields = ("title", "director", "rate", "year")
allowed_types = ("pdf", "png", "jpg", "jpeg")


class CheckFields:
    def __init__(self, data: Mapping[str, ...]) -> None:
        self.data = data

    def check_json(self) -> None:
        for field in movie_fields:
            is_filled = self.data.get(field, None)
            if not is_filled:
                abort(400, f"Insert value for {field}")

    def check_title(self, movie: MovieModel | None = None) -> None:
        if self.data["title"] == "":
            abort(400, "Title can't be blank")
        is_in_database = MovieModel.find_by_title(self.data["title"])
        if is_in_database and is_in_database != movie:
            abort(400, "This movie title is already in the database")

    def check_director(self) -> None:
        if len(self.data.get("director")) < 4:
            abort(400, "Director's name must be 4 or more letters")

    def check_year(self) -> None:
        if not str(self.data["year"]).isdigit() or not (
            1900 <= int(self.data["year"]) <= 2025
        ):
            abort(
                400,
                "Movie's release date is a number "
                "between 1900 and 2025 inclusive",
            )

    def check_rate(self) -> None:
        try:
            rate = float(self.data["rate"])
            if not (0 <= rate <= 10):
                abort(
                    400,
                    "Movie rate is a floating point number "
                    "between 0 and 10 inclusive",
                )
        except ValueError:
            abort(
                400,
                "Movie rate is a floating point number "
                "between 0 and 10 inclusive",
            )

    def check_poster(self) -> None:
        if "file" not in self.data:
            abort(400, "No file part in the request")
        file = self.data["file"]
        if file.filename == "":
            abort(400, "No file selected for uploading")
        if not allowed_file(file.filename):
            abort(400, "Allowed file types are : 'pdf', 'png', 'jpg', 'jpeg'")


def allowed_file(filename: str) -> bool:
    return (
        "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_types
    )


def check_post_data(
    input_fields: dict[str, ...], genres: list[GenreModel]
) -> None:
    checker = CheckFields(input_fields)
    checker.check_json()
    checker.check_title()
    checker.check_director()
    checker.check_year()
    checker.check_rate()

    if not genres:
        abort(400, "Insert at least one genre")


def check_patch_data(
    input_fields: dict[str, ...], genres: list[GenreModel | None], movie: MovieModel
) -> None:
    if not input_fields and not genres:
        abort(400, "No input data was provided")
    if input_fields:
        checker = CheckFields(input_fields)
        if "title" in input_fields:
            checker.check_title(movie)
        if "director" in input_fields:
            checker.check_director()
        if "year" in input_fields:
            checker.check_year()
        if "rate" in input_fields:
            checker.check_rate()


def verify_poster(attachment: ImmutableMultiDict[str, FileStorage]) -> bytes:
    checker = CheckFields(attachment)
    checker.check_poster()
    file = request.files["file"]
    return file.read()
