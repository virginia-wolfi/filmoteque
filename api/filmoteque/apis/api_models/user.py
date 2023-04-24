from flask_restx import fields, Model


login_fields = Model(
    "Login_model",
    {
        "email": fields.String(
            required=True, description="User's email", example="admin@gmail.com"
        ),
        "psw": fields.String(
            required=True, description="User's password", example="123456"
        ),
    },
)
registration_fields = Model(
    "Registration_model",
    {
        "nickname": fields.String(
            required=True, description="User's nickname", example="newuser"
        ),
        "email": fields.String(
            required=True, description="User's email", example="newuser@gmail.com"
        ),
        "psw": fields.String(
            required=True, description="User's password", example="123456"
        ),
    },
)

user_model = Model(
    "User_model",
    {"id": fields.Integer, "nickname": fields.String, "email": fields.String},
)
