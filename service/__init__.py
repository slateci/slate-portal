from flask import Flask
import json

__author__ = 'Globus Team <info@globus.org>'

app = Flask(__name__)
app.config.from_pyfile('service.conf')

with open(app.config['DATASETS']) as f:
    datasets = json.load(f)

import service.views
