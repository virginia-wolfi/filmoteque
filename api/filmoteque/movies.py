from flask import jsonify, request, make_response, abort
from flask_login import login_required, current_user
from .models import Movies, Genres, Directors, Users, movies_genres
from .extentions import db, allowed_file, api, extra
from .constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR,\
     HTTP_403_FORBIDDEN, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT
from sqlalchemy import insert, select, intersect,  text
from collections import OrderedDict
from flask_restx import Namespace, Resource, fields
from werkzeug.datastructures import FileStorage

movies = Namespace('Movies', description='Movies related operations', path='/movies')


add_request_body_model = api.model('Add movie data model', {
                                   'title': fields.String(required=True, description='Movie\'s title',
                                                          example='Gattaca'),
                                   'year': fields.Integer(required=True, description='Movie\'s release year',
                                                          example=1997),
                                   'director': fields.String(required=True, description='Movie\'s director',
                                                             example='Andrew Niccol'),
                                   'rate': fields.Float(required=True, description='Movie\'s rate', min=0, max=10,
                                                        example=7.8),
                                   'description': fields.String(description='Movie\'s description',
                                                                example='A genetically inferior man assumes '
                                                                        'the identity of a superior one in order to '
                                                                        'pursue his lifelong dream of space travel.'),
})

edit_request_body_model = api.model('Edit movie data model', {
                                   'title': fields.String(description='Movies\' title', example='Full Metal Jacket'),
                                   'year': fields.Integer(description='Movies\' release year'),
                                   'director': fields.String(description='Movies\' director'),
                                   'rate': fields.Float(description='Movies\' rate', min=0, max=10, example=8.5),
                                   'description': fields.String(description='Movies\' description')
})
movie_model = api.model('Movie data model', {
                       'id': fields.Integer,
                       'title': fields.String,
                       'year': fields.Integer,
                       'director': fields.String(attribute='director.name'),
                       'rate': fields.Float,
                       'genres': fields.List(fields.String, attribute=lambda x: [i.name for i in x.genres]),
                       'description': fields.String

})


upload_parser = api.parser()
upload_parser.add_argument('file', location='files',
                           type=FileStorage, required=True)

genres_names = ['action', 'adventure', 'animation', 'biography', 'comedy', 'crime',
                'documentary', 'drama', 'family', 'fantasy', 'film-noir', 'game-show',
                'history', 'horror', 'music', 'musical', 'mystery', 'news', 'reality-tv',
                'romance', 'sci-fi', 'sport', 'talk-show', 'thriller', 'war', 'western']
genres_parser = api.parser()
genres_parser.add_argument('genre_1', choices=genres_names, location='values')
genres_parser.add_argument('genre_2', choices=genres_names, location='values')
genres_parser.add_argument('genre_3', choices=genres_names, location='values')



parser = api.parser()
parser.add_argument('rate', choices=['ASC', 'DESC'], location='values', help='sort ascending or descending')
parser.add_argument('year', choices=['ASC', 'DESC'], location='values', help='sort ascending or descending')
parser.add_argument('filter_by_title', type=str, location='values', help='maintains a partial match')
parser.add_argument('filter_by_director', type=str, location='values', help='maintains a partial match')
parser.add_argument('filter_by_year_after', type=int, location='values', default=1900)
parser.add_argument('filter_by_year_before', type=int, location='values', default=2025)
parser.add_argument('page', type=int, location='query', help='which search page to display')
parser.add_argument('per_page', type=int, location='query', help='movies per page')

def add_genre(genres):
    genres_list = []
    for g in genres:
        genre = Genres.query.filter_by(name=g.lower()).first()
        if not genre:
            continue
        genres_list.append(genre)
    return genres_list

def add_director(director_):
    director = Directors.query.filter_by(name=director_).first()
    if not director:
        director = Directors(name=director_)
        db.session.add(director)
        db.session.flush()
        extra.info(f"User added director {director.name}", extra={"user": current_user})
    return director

def before_actions(movie_id):
    movie = db.session.get(Movies, movie_id)
    user = db.session.get(Users, current_user.get_id())
    if not movie:
        abort(HTTP_404_NOT_FOUND, "The movie does not exist")
    if movie.user_id != user.id and user.role.name != 'admin':
        abort(HTTP_403_FORBIDDEN, "Only administrator or user who added the movie can make changes")
    return movie

@movies.route('/adding_movie', doc={"description": 'Adding movie to the filmoteque'})
class AddMovie(Resource):
    @movies.response(201, 'The movie was created successfully')
    @movies.response(400, 'Client-side input fails validation')
    @movies.response(401, 'User not authorized')
    @movies.expect(add_request_body_model, genres_parser)
    @movies.marshal_with(movie_model, skip_none=True, envelope='Movie was added successfully')
    @login_required
    def post(self):
        """Add movie"""
        to_insert = dict(request.json)
        for val in ['title', 'director', 'rate', 'year']:
            is_filled = to_insert.get(val, None)
            if not is_filled:
                abort(HTTP_400_BAD_REQUEST, f'Insert value for {val}')
        if to_insert['title']:
            is_in_database = Movies.query.filter(Movies.title.ilike(to_insert['title'])).first()
            if is_in_database:
                abort(HTTP_400_BAD_REQUEST, "This movie title is already in the database")
        director = to_insert.get('director')
        if len(director) < 4:
            return abort(HTTP_400_BAD_REQUEST, "Director's name must be 4 or more letters")
        director = add_director(director)
        to_insert.pop('director')
        if not str(to_insert["year"]).isdigit() or not (1900 < int(to_insert["year"]) < 2025):
            return abort(HTTP_400_BAD_REQUEST, "Check if the movie's release date is correct")
        genres = add_genre(set(request.args.values()))
        if not genres:
            return abort(HTTP_400_BAD_REQUEST, f'Insert at least one genre')
        try:
            movie_id = db.session.execute(insert(Movies).values(to_insert)).inserted_primary_key[0]
            movie = db.session.get(Movies, movie_id)
            movie.genres = genres
            movie.director_id = director.id
            movie.user_id = int(current_user.get_id())
            db.session.commit()
            extra.info(f"User added movie {movie}", extra={"user": current_user})
            return movie, HTTP_201_CREATED
        except:
            db.session.rollback()
            abort(HTTP_500_INTERNAL_SERVER_ERROR, "Something is broken")


@movies.route('/<int:movie_id>/poster', doc={"description": 'Movie poster related operations'})
@movies.param('movie_id', 'Specify the id associated with the movie')
class Poster(Resource):
    @movies.response(201, 'Movie poster added')
    @movies.response(403, 'Access is not allowed')
    @movies.response(400, 'Client-side input fails validation')
    @movies.response(404, 'The movie does not exist')
    @movies.response(401, 'User not authorized')
    @movies.expect(upload_parser)
    @login_required
    def post(self, movie_id):
        """Upload poster to an existing movie"""
        if repr(type(before_actions(movie_id))) == "<class 'flask.wrappers.Response'>":
            return before_actions(movie_id)
        movie = before_actions(movie_id)
        if 'file' not in request.files:
            abort(HTTP_400_BAD_REQUEST, "No file part in the request")
        file = request.files['file']
        if file.filename == '':
            return abort(HTTP_400_BAD_REQUEST, "No file selected for uploading")
        if not allowed_file(file.filename):
            return abort(HTTP_400_BAD_REQUEST, "Allowed file types are : 'pdf', 'png', 'jpg', 'jpeg'")
        if file and allowed_file(file.filename):
            try:
                movie.poster = file.read()
                db.session.add(movie)
                db.session.commit()
                extra.info(f"User added poster to movie {movie}", extra={"user": current_user})
                return make_response(jsonify(
                    {'message': "Movie poster added",
                     "movie": str(movie)}), HTTP_201_CREATED)
            except:
                db.session.rollback()
                abort(HTTP_500_INTERNAL_SERVER_ERROR, "Something is broken")

    @movies.response(204, 'Poster was deleted')
    @movies.response(403, 'Access is not allowed')
    @movies.response(404, 'The movie does not exist')
    @movies.response(401, 'User not authorized')
    @login_required
    def delete(self, movie_id):
        """Delete poster from an existing movie"""
        if repr(type(before_actions(movie_id))) == "<class 'flask.wrappers.Response'>":
            return before_actions(movie_id)
        movie = before_actions(movie_id)
        movie.poster = None
        db.session.commit()
        extra.info(f"User deleted poster from movie {movie}", extra={"user": current_user})
        return {}, HTTP_204_NO_CONTENT




@movies.route('/<int:movie_id>/', doc={"description": 'Added movies related operations'})
@movies.param('movie_id', 'Specify the id associated with the movie')
class MoviesActions(Resource):
    @movies.response(200, 'Data was updated successfully')
    @movies.response(403, 'Access is not allowed')
    @movies.response(400, 'Client-side input fails validation')
    @movies.response(404, 'The movie does not exist')
    @movies.expect(edit_request_body_model, genres_parser)
    @movies.marshal_with(movie_model, envelope='Movie data updated')
    @login_required
    def patch(self, movie_id):
        """Update an existing movie"""
        if repr(type(before_actions(movie_id))) == "<class 'flask.wrappers.Response'>":
            return before_actions(movie_id)
        movie = before_actions(movie_id)
        genres = add_genre(set(request.args.values()))
        if not request.json and not genres:
            abort(HTTP_400_BAD_REQUEST, "No input data was provided")
        if request.json:
            if 'title' in request.json:
                if request.json['title'] == '':
                    abort(HTTP_400_BAD_REQUEST, "Title can't be blank")
                is_in_database = Movies.query.filter(Movies.title.ilike(request.json['title'])).first()
                if is_in_database and is_in_database != movie:
                    abort(HTTP_400_BAD_REQUEST, "This movie title is already in the database")
            if 'director' in request.json:
                director = request.json['director']
                if len(director) < 4:
                    return abort(HTTP_400_BAD_REQUEST, "Director's name must be 4 or more letters")
                director = add_director(director)
                request.json['director_id'] = director.id
                request.json.pop('director')
            if 'year' in request.json:
                if not str(request.json["year"]).isdigit() or not (1900 < int(request.json["year"]) < 2025):
                    return abort(HTTP_400_BAD_REQUEST, "Check if the movie's release year is correct")
            db.session.query(Movies).filter(Movies.id == movie_id).update(request.json)
        if genres:
            movie.genres = genres
        try:
            db.session.commit()
            extra.info(f"User edited movie {movie}: {request.json if request.json else ''},"
                       f" {request.args.values() if genres else ''}",
                       extra={"user": current_user})
            return movie, HTTP_200_OK
        except:
            db.session.rollback()
            abort(HTTP_500_INTERNAL_SERVER_ERROR, "Something is broken")


    @movies.response(204, 'Movie was deleted')
    @movies.response(403, 'Access is not allowed')
    @login_required
    def delete(self, movie_id):
        """Delete existing movie"""
        if repr(type(before_actions(movie_id))) == "<class 'flask.wrappers.Response'>":
            return before_actions(movie_id)
        movie = before_actions(movie_id)
        try:
            db.session.delete(movie)
            db.session.commit()
            extra.info(f"User deleted movie {movie}", extra={"user": current_user})
            return {}, HTTP_204_NO_CONTENT
        except:
            db.session.rollback()
            abort(HTTP_500_INTERNAL_SERVER_ERROR, "Something is broken")

@movies.route('/', doc={"description": 'Searching movies in database'})
class SearchMovies(Resource):
    @movies.response(200, 'Success')
    @movies.response(400, 'Client-side input is not correct')
    @movies.response(404, 'Data not found')
    @movies.expect(parser, genres_parser)
    def get(self):
        """Get movies"""
        select_query = db.session.query(Movies)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        title = request.args.get('filter_by_title', None)
        director = request.args.get('filter_by_director', None)
        genres = [request.args.get(g) for g in ('genre_1', 'genre_2', 'genre_3') if request.args.get(g, None)]
        lower_year = int(request.args.get('filter_by_year_after', 1900))
        higher_year = int(request.args.get('filter_by_year_before', 2025))
        if lower_year > higher_year:
            abort(HTTP_400_BAD_REQUEST, "Check if the movie's release year is correct")
        year = False if lower_year == 1900 and higher_year == 2025 else True
        filter_params = [title, director, genres]
        if filter_params or year:
            search_params = []
            all_ids = select(Movies.id)
            if title:
                sub_title = select(Movies.id).where(Movies.title.icontains(title))
                search_params.append(sub_title)
            if director:
                sub_director = select(Movies.id).join(Directors).where(Directors.name.icontains(director))
                search_params.append(sub_director)
            if genres:
                sub_genres = select(Movies.id).join(movies_genres).join(Genres).where(Genres.name.in_(genres))
                search_params.append(sub_genres)
            if year:
                sub_year = select(Movies.id).where(Movies.year.between(lower_year, higher_year))
                search_params.append(sub_year)
            ints = intersect(all_ids, *search_params).subquery()
            select_query = db.session.query(Movies).join(ints, ints.c.id == Movies.id)
        order_by_ = {}
        if 'rate' in request.args:
            order_by_['rate'] = request.args.get('rate')
        if 'year' in request.args:
            order_by_['year'] = request.args.get('year')
        if order_by_:
            sort = [(text(f'movies.{i} DESC'), text(f'movies.{i}'))[order_by_.get(i) == 'ASC'] for i in order_by_]
            select_query = select_query.order_by(*sort)
        try:
            result = select_query.paginate(per_page=per_page, page=page)
        except:
            abort(HTTP_404_NOT_FOUND, "No data to show")
        output = OrderedDict()
        for f in result:
            output[str(f)] = {"title": f.title, "year": f.year, "director": f.director.name if f.director else 'Null',
                              "rate": f.rate,
                              "genres": [g.name for g in f.genres]}
        if not output:
            abort(HTTP_404_NOT_FOUND, "No data to show")

        return make_response(jsonify(output), HTTP_200_OK)




