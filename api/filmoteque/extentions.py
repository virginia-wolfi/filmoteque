from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_restx import Api
from flask import Blueprint
import logging
from logging.config import dictConfig


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | %(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
            "extra": {
                "format": "[%(asctime)s] %(levelname)s | %(module)s >>> %(message)s >>> User: %(user)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "record.log",
                "formatter": "extra",
            },
        },
        "root": {"level": "DEBUG", "handlers": ["console"]},
        "loggers": {
            "extra": {
                "level": "DEBUG",
                "handlers": ["file"],
                "propagate": False,
            }
        },
    }
)


extra = logging.getLogger("extra")

db = SQLAlchemy()
blueprint = Blueprint("api", __name__, url_prefix="/api")

api = Api(
    blueprint,
    title="Filmoteque",
    version="1.0",
    description="This is API for managing the movie collection.",
)

login_manager = LoginManager()


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in {
        "pdf",
        "png",
        "jpg",
        "jpeg",
    }
