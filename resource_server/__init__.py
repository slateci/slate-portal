from flask import Flask

__author__ = 'Globus Team <info@globus.org>'

app = Flask(__name__)
app.config.from_pyfile('resource_server.conf')

import resource_server.views
