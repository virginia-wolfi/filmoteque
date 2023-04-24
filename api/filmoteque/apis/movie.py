from flask import jsonify, make_response
from flask_login import login_required
from collections import OrderedDict
from flask_restx import Namespace, Resource, marshal
from .api_models.movie import *
from .parsers import *
from ..handlers.movie_handler import *
from ..handlers.movie_browse import *
from ..handlers.movie_fields import *
from ..models.movie import MovieModel

movies = Namespace("Movies", description="Movies related operations", path="/movies")


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
        data = request.get_json()
        genres_names = set(request.args.values())
        genres = genres_handler(genres_names)
        check_fields(data, genres)
        director = director_handler(data)
        movie = MovieModel(**data)
        movie.genres = genres
        movie.director_id = director.id
        movie.user_id = int(current_user.get_id())
        try:
            movie.save_to_db()
            extra.info(
                f"User added movie {movie, movie.title}", extra={"user": current_user}
            )
            return movie, 201
        except:
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
    def post(self, movie_id):
        """Uploads poster to an existing movie"""
        movie = verify_movie(movie_id)
        data = request.files
        movie.poster = poster_image(data)
        try:
            db.session.commit()
            extra.info(
                f"User added poster to movie {movie, movie.title}",
                extra={"user": current_user},
            )
            return make_response(
                jsonify(
                    {"message": "Movie poster added", "movie": f"{movie, movie.title}"}
                ),
                201,
            )
        except:
            rollback()

    @movies.response(204, "Poster was deleted")
    @movies.response(403, "Access is not allowed")
    @movies.response(404, "The movie does not exist")
    @movies.response(401, "User not authorized")
    @login_required
    def delete(self, movie_id):
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
    def get(self, movie_id):
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
    def patch(self, movie_id):
        """Updates an existing movie with fields"""
        movie = verify_movie(movie_id)
        genres = genres_handler(set(request.args.values()))
        data = request.get_json()
        check_fields_patch(data, genres, movie)
        director = director_handler(data)
        if director:
            data["director_id"] = director.id
        if data:
            MovieModel.update_movie(data, movie_id)
        if genres:
            movie.genres = genres
        try:
            db.session.commit()
            extra.info(
                f"User edited movie {movie, movie.title}: {request.json if request.json else ''},"
                f" {request.args.values() if genres else ''}",
                extra={"user": current_user},
            )
            return movie, 200
        except:
            rollback()

    @movies.response(204, "Movie was deleted")
    @movies.response(403, "Access is not allowed")
    @login_required
    def delete(self, movie_id):
        """Deletes an existing movie"""
        movie = verify_movie(movie_id)
        try:
            movie.delete_from_db()
            extra.info(
                f"User deleted movie {movie, movie.title}", extra={"user": current_user}
            )
            return {}, 204
        except:
            rollback()


class MovieBrowse(Resource):
    @movies.response(200, "Success")
    @movies.response(400, "Client-side input is not correct")
    @movies.response(404, "Data not found")
    @movies.expect(movies_parser, genres_parser)
    def get(self):
        """Fetches movies by provided filtering and sorting options"""
        data = request.args
        select_query = db.session.query(MovieModel)
        result = query_handler(data, select_query)
        output = OrderedDict()
        for movie in result:
            output[str(movie)] = marshal(movie, movie_model)
        if not output:
            abort(404, "No data to show")
        return make_response(jsonify(output), 200)

