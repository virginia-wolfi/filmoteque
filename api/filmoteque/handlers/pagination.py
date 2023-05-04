from werkzeug.exceptions import HTTPException
from flask import abort
from flask_sqlalchemy.query import Query
from ..models.movie import MovieModel


def paginate_query(query: Query, per_page: int, page: int) -> list[MovieModel]:
    try:
        movies_slice = query.paginate(per_page=per_page, page=page).items
        return movies_slice
    except HTTPException:
        abort(404, "No data to show")
