from .insertion_data import psw, ordinary_user_2, ordinary_user_1, not_user, admin_user


user_registration_params = (
    ("user1", "user1@gmail.com", psw, 201, b"User created"),
    ("user1", "user1111@gmail.com", psw, 409, b"Nickname is taken"),
    ("user111", "user1@gmail.com", psw, 409, b"Email is taken"),
    ("user*_", "user1@gmail.com", psw, 400, b"Nickname should be alphanumeric"),
    ("", "user1@gmail.com", psw, 400, b"Nickname must be 3 or more characters"),
    ("user111", "user1111@gmail.com", "", 400, b"Password must be 6 characters or more"),
    ("user111", "user@gmail@com", psw, 400, b"Email is not valid"),
)

user_login_validation_params = (
    ("1@gmail.com", psw, 401, b"Wrong credentials"),
    ("user1@gmail.com", "1234", 401, b"Wrong credentials"),
    ("user1@gmail.com", psw, 200, b"User logged in"),
)

movie_creation_params = (
    (
        "Pulp Fiction",
        "Quentin Tarantino",
        8.9,
        1997,
        "crime",
        "comedy",
        "",
        201,
        b"Movie was added successfully",
    ),
    (
        "Pulp Fiction",
        "Quentin Tarantino",
        8.9,
        1997,
        "crime",
        "comedy",
        "",
        400,
        b"This movie title is already in the database",
    ),
    (
        "Django Unchained",
        "Quentin Tarantino",
        "",
        2012,
        "crime",
        "comedy",
        "",
        400,
        b"Insert value for rate",
    ),
    (
        "Django Unchained",
        "Que",
        8.4,
        2012,
        "crime",
        "comedy",
        "",
        400,
        b"Director's name must be 4 or more letters",
    ),
    (
        "Django Unchained",
        "Quentin Tarantino",
        8.4,
        1812,
        "crime",
        "comedy",
        "",
        400,
        b"Movie's release date is a number between 1900 and 2025 inclusive",
    ),
    (
        "Django Unchained",
        "Quentin Tarantino",
        8.4,
        2012,
        "",
        "",
        "",
        400,
        b"Insert at least one genre",
    ),
)

movie_edit_params = (
    (
        ordinary_user_1,
        {"genre_1": "western", "genre_2": "comedy"},
        {},
        200,
        b"Movie data updated",
    ),
    (
        ordinary_user_1,
        {"genre_1": "western"},
        {"director": "Quentin"},
        200,
        b"Movie data updated",
    ),
    (
        admin_user,
        {},
        {"title": "Django unchained", "director": "Quentin"},
        200,
        b"Movie data updated",
    ),
    (ordinary_user_1, {}, {}, 400, b"No input data was provided"),
    (ordinary_user_1, {}, {"title": ""}, 400, b"Title can't be blank"),
    (
        ordinary_user_1,
        {"genre_1": "western", "genre_2": "comedy"},
        {"title": "Pulp Fiction"},
        400,
        b"This movie title is already in the database",
    ),
    (
        admin_user,
        {},
        {"director": "Que"},
        400,
        b"Director's name must be 4 or more letters",
    ),
    (
        admin_user,
        {},
        {"year": 2050, "title": "Django unchained"},
        400,
        b"Movie's release date is a number between 1900 and 2025 inclusive",
    ),
    (
        not_user,
        {"genre_1": "western", "genre_2": "comedy"},
        {},
        401,
        b"Log in to view this page",
    ),
    (
        ordinary_user_2,
        {},
        {"title": "Django unchained"},
        403,
        b"Only administrator or user who added the movie can make changes",
    ),
)

movie_search_params = (
    ({"genre_1": "western", "director": "tara"}, 200, b"Quentin Tarantino", 1),
    ({"before year": 1985}, 200, b"The Shining", 1),
    ({"genre_1": "thriller"}, 200, b"No Country for Old Men", 4),
    ({"after year": 2018}, 200, b"The Banshees of Inisherin", 5),
    ({"per page": 5}, 200, b"Birdman or", 5),
    ({"per page": 15, "page": 2}, 200, b"Youth", 1),
    ({"title": "jacket"}, 200, b"Full Metal Jacket", 1),
    ({"after year": 2026}, 400, b"'after_year' field must be earlier than 2026", 1),
    ({"before year": 1899}, 400, b"'before_year' field value must be later than 1899", 1),
    ({"title": "not title"}, 404, b"No data to show", 1),
    ({"per page": 20, "page": 2}, 404, b"No data to show", 1),
)

movie_creation_unauth_params = (
        (
            "Django Unchained",
            "Quentin Tarantino",
            "8.4",
            2012,
            "crime",
            "comedy",
            "",
            401,
            b"Log in to view this page",
        ),
    )


movie_delete_params = (
    (ordinary_user_1, 204, b""),
    (admin_user, 204, b""),
    (ordinary_user_2, 403, b"Only administrator or user who added the movie can make changes"),
    (not_user, 401, b"Log in to view this page"),
)

poster_upload_unath_params = (
    (ordinary_user_2, 403, b"Only administrator or user who added the movie can make changes"),
    (not_user, 401, b"Log in to view this page")
)

poster_delete_params = (
    (ordinary_user_1, 204, b""),
    (admin_user, 204, b""),
    (ordinary_user_2, 403, b"Only administrator or user who added the movie can make changes"),
    (not_user, 401, b"Log in to view this page")
)

poster_upload_params = (
    ("file", "poster.jpeg", 201, b"Movie poster added"),
    ("no_file", "poster.jpeg", 400, b"No file part in the request"),
    ("file", "", 400, b"No file selected for uploading"),
    ("file", "poster.xml", 400, b"Allowed file types are : 'pdf', 'png', 'jpg', 'jpeg'"),
)