from flask_restx import reqparse
from werkzeug.datastructures import FileStorage
from ..database.insertion_data import genre_names


upload_parser = reqparse.RequestParser()
upload_parser.add_argument(
    "file", location="files", type=FileStorage, required=True
)


genres_parser = reqparse.RequestParser()
genres_parser.add_argument("genre_1", choices=genre_names, location="values")
genres_parser.add_argument("genre_2", choices=genre_names, location="values")
genres_parser.add_argument("genre_3", choices=genre_names, location="values")

movies_parser = reqparse.RequestParser()
movies_parser.add_argument(
    "rate",
    choices=["ASC", "DESC"],
    location="values",
    help="sort ascending or descending",
)
movies_parser.add_argument(
    "year",
    choices=["ASC", "DESC"],
    location="values",
    help="sort ascending or descending",
)
movies_parser.add_argument(
    "title", type=str, location="values", help="maintains a partial match"
)
movies_parser.add_argument(
    "director", type=str, location="values", help="maintains a partial match"
)
movies_parser.add_argument(
    "after year", type=int, location="values", help="not later than 2025"
)
movies_parser.add_argument(
    "before year", type=int, location="values", help="not earlier than 1900"
)
movies_parser.add_argument(
    "page", type=int, location="query", help="which search page to display"
)
movies_parser.add_argument(
    "per page", type=int, location="query", help="movies per page"
)
