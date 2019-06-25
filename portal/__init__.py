from flask import Flask
import json

from portal.database import Database
# from flask import Markup
from flask_misaka import markdown
from flask_misaka import Misaka
import logging.handlers
import logging

__author__ = 'Jeremy Van'
# set up Flask App
app = Flask(__name__, instance_relative_config=True)
app.config.from_pyfile('portal.conf')
app.url_map.strict_slashes = False

# set up Markdown Rendering
md = Misaka()
md.__init__(app, tables=True, autolink=True, fenced_code=True, smartypants=True, quote=True, math=True, math_explicit=True)

# set up logging
handler = logging.handlers.RotatingFileHandler(
    filename=app.config['SLATE_WEBSITE_LOGFILE'])
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
handler.setFormatter(formatter)

import portal.views
