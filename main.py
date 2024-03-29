#!/usr/bin/env python

from portal import app
import os

if __name__ == '__main__':
    if os.environ.get('UWSGI_FRAMEWORK').__eq__("werkzeug"):
        app.run(
            host='0.0.0.0',
            port=os.environ.get('FLASK_PORT')
        )
