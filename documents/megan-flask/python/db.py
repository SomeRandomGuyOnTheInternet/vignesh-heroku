import sqlite3
import click
from flask import *
from flask.cli import with_appcontext
DATABASE = '../foodhub.db'
app.config.from_object(__name__)
def connect_to_database():
    return sqlite3.connect(app.config[DATABASE])



def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    """Clear existing data and create new tables."""
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
    for idx, value in enumerate(row))

def init_app(app):
    def init_db():
        with app.app_context():
            db = get_db()
            with app.open_resource('schema.sql', mode='r') as f:
                db.cursor().executescript(f.read())
            db.commit()
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
