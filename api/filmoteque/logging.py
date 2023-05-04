import logging
from logging.config import dictConfig


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s | "
                "%(module)s] %(message)s",
                "datefmt": "%B %d, %Y %H:%M:%S %Z",
            },
            "extra": {
                "format": "[%(asctime)s] %(levelname)s | "
                "%(module)s >>> %(message)s >>> User: %(user)s",
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
