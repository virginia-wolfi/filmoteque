from flask_restx import Api
from flask import Blueprint
from .user import *
from .movie import *
from .api_models.user import *
from .api_models.movie import *

blueprint = Blueprint("api", __name__, url_prefix="/api")
api = Api(
    blueprint,
    title="Filmoteque",
    version="1.0",
    description="This is API for managing the movie collection.",
)
users.add_resource(UserLogin, "/login")
users.add_resource(UserLogout, "/logout")
users.add_resource(UserRegister, "/registration")
users.add_resource(UserProfile, "/users/<int:user_id>")
movies.add_resource(MovieCreation, "/movie_creation")
movies.add_resource(MoviePoster, "/<int:movie_id>/poster")
movies.add_resource(Movie, "/<int:movie_id>")
movies.add_resource(MovieBrowse, "")

users.add_model("Registration_model", registration_fields)
users.add_model("Login_model", login_fields)
users.add_model("User_model", user_model)
movies.add_model("Add_movie_data_model", add_movie_model)
movies.add_model("Edit_movie_data_model", edit_movie_model)
movies.add_model("Movie_data_model", movie_model)

api.add_namespace(users)
api.add_namespace(movies)
