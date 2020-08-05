from flask import Flask
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
import json
import datetime
# from flask import Markup
from flask_misaka import markdown
from flask_misaka import Misaka
import logging.handlers
import logging

__author__ = 'Jeremy Van'
# set up Flask App
app = Flask(__name__, instance_relative_config=True)
# Enable CSRF protection globally for Flask app
csrf = CSRFProtect(app)
csrf.init_app(app)
app.config.from_pyfile('portal.conf')
app.url_map.strict_slashes = False
app.config['DEBUG'] = True
app.permanent_session_lifetime = timedelta(minutes=1440)
app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax')
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

slate_api_token = app.config['SLATE_API_TOKEN']
slate_api_endpoint = app.config['SLATE_API_ENDPOINT']

def format_datetime(value, format="%b %d %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""

    if value is None:
        return ""
    
    date_time_obj = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%SZ')
    date_time_pretty_format = date_time_obj.strftime(format)

    return date_time_pretty_format

# Register the template filter with the Jinja Environment
app.jinja_env.filters['formatdatetime'] = format_datetime

import portal.views
