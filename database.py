"""Manage access to the database."""

import sqlite3
from flask import g


class Database:
    """Database access."""

    def __init__(self, app):
        """Constructor."""
        self.app = app

        @app.teardown_appcontext
        def close_connection(exception):
            """Close database connection when finished handling request."""
            db = getattr(g, '_database', None)

            if db is not None:
                db.close()

    def connect_to_db(self):
        """Open database and return a connection handle."""
        return sqlite3.connect(self.app.config['DATABASE'])

    def get_db(self):
        """Return the app global db connection or create one."""
        db = getattr(g, '_database', None)

        if db is None:
            db = g._database = self.connect_to_db()
            db.row_factory = sqlite3.Row

        return db

    def query_db(self, query, args=(), one=False):
        """Query the database."""
        cur = self.get_db().execute(query, args)

        rv = cur.fetchall()
        cur.close()

        return (rv[0] if rv else None) if one else rv
