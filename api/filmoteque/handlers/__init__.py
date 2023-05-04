from flask import abort
from ..db import db


def rollback() -> None:
    db.session.rollback()
    abort(500, "Something is broken")
