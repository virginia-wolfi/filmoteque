from flask import Blueprint
from .insert_setup import insert_all
from .db import db

bp = Blueprint("commands", __name__)


@bp.cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()


@bp.cli.command("insert_db")
def insert_db():
    insert_all()
