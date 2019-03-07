from flask import Flask
import json

from portal.database import Database
# from flask_misaka import markdown
# from flask_misaka import Misaka

__author__ = 'Jeremy Van'

# md = Misaka()
app = Flask(__name__)
app.config.from_pyfile('portal.conf')
# md.__init__(app, tables=True)

# database = Database(app)
#
# with open(app.config['DATASETS']) as f:
#     datasets = json.load(f)

import portal.views
