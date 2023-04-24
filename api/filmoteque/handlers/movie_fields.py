from flask import abort, request
from ..models.movie import MovieModel


class CheckFields:
    def __init__(self, data):
        self.data = data

    def check_json(self):
        for val in ["title", "director", "rate", "year"]:
            is_filled = self.data.get(val, None)
            if not is_filled:
                abort(400, f"Insert value for {val}")

    def check_title(self, movie=None):
        if self.data["title"] == "":
            abort(400, "Title can't be blank")
        is_in_database = MovieModel.find_by_title(self.data["title"])
        if is_in_database and is_in_database != movie:
            abort(400, "This movie title is already in the database")

    def check_director(self):
        if len(self.data.get("director")) < 4:
            abort(400, "Director's name must be 4 or more letters")

    def check_year(self):
        if not str(self.data["year"]).isdigit() or not (
            1900 <= int(self.data["year"]) <= 2025
        ):
            abort(
                400, "Movie's release date is a number between 1900 and 2025 inclusive"
            )

    def check_rate(self):
        try:
            float(self.data["rate"])
        except:
            abort(
                400, "Movie rate is a floating point number between 0 and 10 inclusive"
            )
        if not (0 <= float(self.data["rate"]) <= 10):
            abort(
                400, "Movie rate is a floating point number between 0 and 10 inclusive"
            )

    def check_poster(self):
        if "file" not in self.data:
            abort(400, "No file part in the request")
        file = self.data["file"]
        if file.filename == "":
            abort(400, "No file selected for uploading")
        if not allowed_file(file.filename):
            abort(
                400,
                "Allowed file types are : 'pdf', 'png', 'jpg', 'jpeg'",
            )


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "pdf",
        "png",
        "jpg",
        "jpeg",
    }


def check_fields(data, genres):
    checker = CheckFields(data)
    checker.check_json()
    checker.check_title()
    checker.check_director()
    checker.check_year()
    checker.check_rate()

    if not genres:
        abort(400, f"Insert at least one genre")


def check_fields_patch(data, genres, movie):
    if not data and not genres:
        abort(400, "No input data was provided")
    if data:
        checker = CheckFields(data)
        if "title" in data:
            checker.check_title(movie)
        if "director" in data:
            checker.check_director()
        if "year" in data:
            checker.check_year()
        if "rate" in data:
            checker.check_rate()


def poster_image(data):
    checker = CheckFields(data)
    checker.check_poster()
    file = request.files["file"]
    return file.read()
