from .pagination import paginate_query
from ..models.genre import GenreModel
from ..models.director import DirectorModel
from ..models.movie import MovieModel, movies_genres
from ..db import db
from flask import abort
from sqlalchemy import select, intersect, text
from werkzeug.datastructures import MultiDict


filters_titles = (
    "title",
    "director",
    "genre_1",
    "genre_2",
    "genre_3",
    "after_year",
    "before_year",
)


class QueryHandler:
    def __init__(self, filters: MultiDict[str, str]) -> None:
        self.select_query = db.session.query(MovieModel)
        self.filter_criteria = {}
        self.filters = filters
        self.page = int(filters.get("page", 1))
        self.per_page = int(filters.get("per page", 10))

    def apply_order_by(self) -> None:
        order_by_ = {}
        if "rate" in self.filters:
            order_by_["rate"] = self.filters.get("rate")
        if "year" in self.filters:
            order_by_["year"] = self.filters.get("year")
        if order_by_:
            sort = [
                (text(f"movies.{i} DESC"), text(f"movies.{i}"))[
                    order_by_.get(i) == "ASC"
                ]
                for i in order_by_
            ]
            self.select_query = self.select_query.order_by(*sort)

    def handle_years_filters(self) -> None:
        after_year = int(self.filters.get("after year", 1900))
        before_year = int(self.filters.get("before year", 2025))
        if after_year > 2025:
            abort(400, "'after_year' field must be earlier than 2026")
        if before_year < 1900:
            abort(400, "'before_year' field value must be later than 1899")
        filter_by_year = (
            False if after_year == 1900 and before_year == 2025 else True
        )
        if filter_by_year:
            if after_year > before_year:
                abort(
                    400, "Check if the movie's release year range is correct"
                )
            self.filter_criteria["after year"] = after_year
            self.filter_criteria["before year"] = before_year
            self.filter_criteria["filter_by_year"] = True

    def construct_query(self) -> None:
        if not self.filter_criteria:
            return
        search = []
        all_ids = select(MovieModel.id)
        genres = [
            self.filter_criteria.get(g)
            for g in ["genre_1", "genre_2", "genre_3"]
            if self.filter_criteria.get(g, None)
        ]
        if "title" in self.filter_criteria:
            sub_title = select(MovieModel.id).where(
                MovieModel.title.icontains(self.filter_criteria["title"])
            )
            search.append(sub_title)
        if "director" in self.filter_criteria:
            sub_director = (
                select(MovieModel.id)
                .join(DirectorModel)
                .where(
                    DirectorModel.name.icontains(
                        self.filter_criteria["director"]
                    )
                )
            )
            search.append(sub_director)
        if genres:
            sub_genres = (
                select(MovieModel.id)
                .join(movies_genres)
                .join(GenreModel)
                .where(GenreModel.name.in_(genres))
            )
            search.append(sub_genres)
        if "filter_by_year" in self.filter_criteria:
            sub_year = select(MovieModel.id).where(
                MovieModel.year.between(
                    self.filter_criteria["after year"],
                    self.filter_criteria["before year"],
                )
            )
            search.append(sub_year)
        ints = intersect(all_ids, *search).subquery()
        self.select_query = db.session.query(MovieModel).join(
            ints, ints.c.id == MovieModel.id
        )


def handle_query(filters: MultiDict[str, str]) -> list[MovieModel]:
    query_handler = QueryHandler(filters)
    for title in filters_titles:
        if filters.get(title, None):
            query_handler.filter_criteria[title] = filters.get(title)
    query_handler.handle_years_filters()
    query_handler.construct_query()
    query_handler.apply_order_by()
    return paginate_query(
        query_handler.select_query, query_handler.per_page, query_handler.page
    )
