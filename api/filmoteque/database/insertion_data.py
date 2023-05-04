from werkzeug.security import generate_password_hash


psw_hash = generate_password_hash("123456")

genre_names = (
    "action",
    "adventure",
    "animation",
    "biography",
    "comedy",
    "crime",
    "documentary",
    "drama",
    "family",
    "fantasy",
    "film-noir",
    "game-show",
    "history",
    "horror",
    "music",
    "musical",
    "mystery",
    "news",
    "reality-tv",
    "romance",
    "sci-fi",
    "sport",
    "talk-show",
    "thriller",
    "war",
    "western",
)

directors = (
    "Quentin Tarantino",
    "Bong Joon Ho",
    "Alejandro Gonzalez Inarritu",
    "Stanley Kubrick",
    "Coen brothers",
    "Martin McDonagh",
    "Paolo Sorrentino",
    "Peter Farrelly",
    "Peter Weir",
    "Francis Ford Coppola",
    "Lars von Trier",
    "Julie Taymor",
    "Darren Aronofsky",
    "Martin Scorsese",
    "Damien Chazelle",
    "Jordan Peele",
    "Kar-Wai Wong",
    "Sofia Coppola",
    "Tim Berton",
)

users = (
    {
        "nickname": "user_1",
        "email": "user_1@gmail.com",
        "psw": psw_hash,
        "role_id": 1,
    },
    {
        "nickname": "user_2",
        "email": "user_2@gmail.com",
        "psw": psw_hash,
        "role_id": 1,
    },
    {
        "nickname": "admin",
        "email": "admin@gmail.com",
        "psw": psw_hash,
        "role_id": 2,
    },
)

roles = ({"name": "user"}, {"name": "admin"})
