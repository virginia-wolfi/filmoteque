from flask_restx import fields, Model


add_movie_model = Model(
    "Add_movie_data_model",
    {
        "title": fields.String(
            required=True, description="Movie's title", example="Gattaca"
        ),
        "year": fields.Integer(
            required=True,
            description="Movie's release year",
            min=1900,
            max=2025,
            example=1997,
        ),
        "director": fields.String(
            required=True, description="Movie's director", example="Andrew Niccol"
        ),
        "rate": fields.Float(
            required=True, description="Movie's rate", min=0, max=10, example=7.8
        ),
        "description": fields.String(
            description="Movie's description",
            example="A genetically inferior man assumes "
            "the identity of a superior one in order to "
            "pursue his lifelong dream of space travel.",
        ),
    },
)

edit_movie_model = Model(
    "Edit_movie_data_model",
    {
        "title": fields.String(
            description="Movies' title", example="Full Metal Jacket"
        ),
        "year": fields.Integer(
            description="Movies' release year", min=1900, max=2025, example=1987
        ),
        "rate": fields.Float(description="Movies' rate", min=0, max=10, example=8.5),
    },
)

movie_model = Model(
    "Movie_data_model",
    {
        "id": fields.Integer,
        "title": fields.String,
        "year": fields.Integer,
        "director": fields.String(
            attribute=lambda x: x.director.name if x.director else "Null"
        ),
        "rate": fields.Float,
        "genres": fields.List(
            fields.String, attribute=lambda x: [i.name for i in x.genres]
        ),
        "description": fields.String,
    },
)
