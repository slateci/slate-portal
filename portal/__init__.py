from flask import Flask
import json

from portal.database import Database
from flask_misaka import markdown
from flask_misaka import Misaka
import logging.handlers
import logging

__author__ = 'Jeremy Van'

md = Misaka()
app = Flask(__name__)
app.config.from_pyfile('portal.conf')
md.__init__(app, tables=True)

# set up logging
handler = logging.handlers.RotatingFileHandler(
    filename=app.config['SLATE_WEBSITE_LOGFILE'])
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)

import portal.views
