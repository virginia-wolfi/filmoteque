import click
from flask import Blueprint
from .insert_setup import insert_all
from .extentions import db

bp = Blueprint('commands', __name__)

@bp.cli.command("say_my_name")
@click.argument('name', default="Noname")
def say_my_name(name):
    print("say_my_name %s " % name)

@bp.cli.command("create_db")
@click.argument('name', default="Noname")
def create_db(name):
    print(db)
    db.drop_all()
    db.create_all()
    db.session.commit()

@bp.cli.command("insert_db")
def insert_db():
    insert_all()
