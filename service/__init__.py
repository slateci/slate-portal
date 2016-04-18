from flask import Flask

__author__ = 'Globus Team <info@globus.org>'

app = Flask(__name__)
app.config.from_pyfile('service.conf')

import service.views
