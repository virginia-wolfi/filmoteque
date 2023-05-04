from flask import jsonify, make_response, request, abort
from flask_login import login_required, current_user
from collections import OrderedDict
from flask_restx import Namespace, Resource, marshal
from .api_models.movie import add_movie_model, edit_movie_model, movie_model
from .parsers import upload_parser, genres_parser, movies_parser
from ..handlers import rollback
from ..handlers.movie_handler import (
    handle_genres,
    handle_director,
    verify_movie,
)
from ..handlers.movie_browse import handle_query
from ..handlers.movie_fields import (
    check_post_data,
    check_patch_data,
    verify_poster,
)
from ..models.movie import MovieModel
from psycopg2 import OperationalError
from ..db import db
from ..logging import extra


movies = Namespace(
    "Movies", description="Movies related operations", path="/movies"
)


class MovieCreation(Resource):
    @movies.response(201, "The movie was created successfully")
    @movies.response(400, "Client-side input fails validation")
    @movies.response(401, "User not authorized")
    @movies.expect(add_movie_model, genres_parser)
    @movies.marshal_with(
        movie_model, skip_none=True, envelope="Movie was added successfully"
    )
    @login_required
    def post(self):
        """Adds movie to the movie collection"""
        input_fields = request.get_json()
        genres_names = set(request.args.values())
        genres = handle_genres(genres_names)
        check_post_data(input_fields, genres)
        director = handle_director(input_fields)
        movie = MovieModel(**input_fields)
        movie.genres = genres
        movie.director_id = director.id
        movie.user_id = int(current_user.get_id())
        try:
            movie.save_to_db()
            extra.info(
                f"User added movie {movie, movie.title}",
                extra={"user": current_user},
            )
            return movie, 201
        except OperationalError:
            rollback()


@movies.param("movie_id", "Specify the id associated with the movie")
class MoviePoster(Resource):
    @movies.response(201, "Movie poster added")
    @movies.response(403, "Access is not allowed")
    @movies.response(400, "Client-side input fails validation")
    @movies.response(404, "The movie does not exist")
    @movies.response(401, "User not authorized")
    @movies.expect(upload_parser)
    @login_required
    def post(self, movie_id: int):
        """Uploads poster to an existing movie"""
        movie = verify_movie(movie_id)
        attachment = request.files
        movie.poster = verify_poster(attachment)
        try:
            db.session.commit()
            extra.info(
                f"User added poster to movie {movie, movie.title}",
                extra={"user": current_user},
            )
            return make_response(
                jsonify(
                    {
                        "message": "Movie poster added",
                        "movie": f"{movie, movie.title}",
                    }
                ),
                201,
            )
        except OperationalError:
            rollback()

    @movies.response(204, "Poster was deleted")
    @movies.response(403, "Access is not allowed")
    @movies.response(404, "The movie does not exist")
    @movies.response(401, "User not authorized")
    @login_required
    def delete(self, movie_id: int):
        """Deletes poster from an existing movie"""
        movie = verify_movie(movie_id)
        movie.poster = None
        db.session.commit()
        extra.info(
            f"User deleted poster from movie {movie, movie.title}",
            extra={"user": current_user},
        )
        return {}, 204


@movies.param("movie_id", "Specify the id associated with the movie")
class Movie(Resource):
    @movies.response(200, "Success")
    @movies.response(404, "The movie does not exist")
    @movies.marshal_with(movie_model)
    def get(self, movie_id: int):
        """Fetches movie by provided id"""
        movie = MovieModel.find_by_id(movie_id)
        if not movie:
            abort(404, "Movie not found")
        return movie, 200

    @movies.response(200, "Data was updated successfully")
    @movies.response(403, "Access is not allowed")
    @movies.response(400, "Client-side input fails validation")
    @movies.response(404, "The movie does not exist")
    @movies.expect(edit_movie_model, genres_parser)
    @movies.marshal_with(movie_model, envelope="Movie data updated")
    @login_required
    def patch(self, movie_id: int):
        """Updates an existing movie with fields"""
        movie = verify_movie(movie_id)
        genres = handle_genres(set(request.args.values()))
        input_fields = request.get_json()
        check_patch_data(input_fields, genres, movie)
        director = handle_director(input_fields)
        if input_fields:
            MovieModel.update_movie(input_fields, movie_id)
        if genres:
            movie.genres = genres
        if director:
            movie.director_id = director.id
        try:
            db.session.commit()
            extra.info(
                f"User edited movie {movie, movie.title}: "
                f"{request.json if request.json else ''},"
                f" {request.args.values() if genres else ''}",
                extra={"user": current_user},
            )
            return movie, 200
        except OperationalError:
            rollback()

    @movies.response(204, "Movie was deleted")
    @movies.response(403, "Access is not allowed")
    @login_required
    def delete(self, movie_id: int):
        """Deletes an existing movie"""
        movie = verify_movie(movie_id)
        try:
            movie.delete_from_db()
            extra.info(
                f"User deleted movie {movie, movie.title}",
                extra={"user": current_user},
            )
            return {}, 204
        except OperationalError:
            rollback()


class MovieBrowse(Resource):
    @movies.response(200, "Success")
    @movies.response(400, "Client-side input is not correct")
    @movies.response(404, "Data not found")
    @movies.expect(movies_parser, genres_parser)
    def get(self):
        """Fetches movies by provided filtering and sorting options"""
        filters = request.args
        movies_slice = handle_query(filters)
        output = OrderedDict()
        for movie in movies_slice:
            output[str(movie)] = marshal(movie, movie_model)
        if not output:
            abort(404, "No data to show")
        return make_response(jsonify(output), 200)
