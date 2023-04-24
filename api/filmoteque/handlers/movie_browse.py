from ..models.genre import GenreModel
from ..models.director import DirectorModel
from ..models.movie import MovieModel, movies_genres
from ..extentions import db
from flask import abort
from sqlalchemy import select, intersect, text


class QueryHandler:
    def __init__(self, select_query, data, filter_params):
        self.select_query = select_query
        self.data = data
        self.filter_params = filter_params
        self.page = data.get("page", 1, type=int)
        self.per_page = data.get("per page", 10, type=int)
        self.result = None

    def pagination(self):
        order_by_ = {}
        if "rate" in self.data:
            order_by_["rate"] = self.data.get("rate")
        if "year" in self.data:
            order_by_["year"] = self.data.get("year")
        if order_by_:
            sort = [
                (text(f"movies.{i} DESC"), text(f"movies.{i}"))[
                    order_by_.get(i) == "ASC"
                ]
                for i in order_by_
            ]
            self.select_query = self.select_query.order_by(*sort)
        try:
            self.result = self.select_query.paginate(
                per_page=self.per_page, page=self.page
            )
        except:
            abort(404, "No data to show")

    def years_filter(self):
        after_year = int(self.data.get("after year", 1900))
        before_year = int(self.data.get("before year", 2025))
        if after_year > 2025:
            abort(400, "'after_year' field must be earlier than 2026")
        if before_year < 1900:
            abort(400, "'before_year' field value must be later than 1899")
        filter_by_year = False if after_year == 1900 and before_year == 2025 else True
        if filter_by_year:
            if after_year > before_year:
                abort(400, "Check if the movie's release year range is correct")
            self.filter_params["after year"] = after_year
            self.filter_params["before year"] = before_year
            self.filter_params["filter_by_year"] = True

    def filtering_query(self):
        if not self.filter_params:
            return
        search_params = []
        all_ids = select(MovieModel.id)
        genres = [
            self.filter_params.get(g)
            for g in ["genre_1", "genre_2", "genre_3"]
            if self.filter_params.get(g, None)
        ]
        if "title" in self.filter_params:
            sub_title = select(MovieModel.id).where(
                MovieModel.title.icontains(self.filter_params["title"])
            )
            search_params.append(sub_title)
        if "director" in self.filter_params:
            sub_director = (
                select(MovieModel.id)
                .join(DirectorModel)
                .where(DirectorModel.name.icontains(self.filter_params["director"]))
            )
            search_params.append(sub_director)
        if genres:
            sub_genres = (
                select(MovieModel.id)
                .join(movies_genres)
                .join(GenreModel)
                .where(GenreModel.name.in_(genres))
            )
            search_params.append(sub_genres)
        if "filter_by_year" in self.filter_params:
            sub_year = select(MovieModel.id).where(
                MovieModel.year.between(
                    self.filter_params["after year"], self.filter_params["before year"]
                )
            )
            search_params.append(sub_year)
        ints = intersect(all_ids, *search_params).subquery()
        self.select_query = db.session.query(MovieModel).join(
            ints, ints.c.id == MovieModel.id
        )


def query_handler(data, select_query):
    search_handler = QueryHandler(select_query, data, {})
    for i in ("title", "director", "genre_1", "genre_2", "genre_3"):
        if data.get(i, None):
            search_handler.filter_params[i] = data.get(i)
    search_handler.years_filter()
    search_handler.filtering_query()
    search_handler.pagination()
    return search_handler.result
