import datetime
import json
import logging
import sys
from datetime import timedelta

from flask import Flask

# from flask import Markup
from flask_misaka import Misaka, markdown
from flask_wtf.csrf import CSRFProtect

from portal.logtools import StackdriverJsonFormatter

__author__ = "Jeremy Van"

# Set up logging behavior:
handler = logging.StreamHandler(sys.stdout)
formatter = StackdriverJsonFormatter()
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(handler)

# set up Flask App
app = Flask(__name__, instance_relative_config=True)

try:
    # Change to location of slate_portal_user file
    f = open("/slate/users/slate_portal_user", "r")
    minislate_user = f.read().split()
except:
    minislate_user = None


if not minislate_user:
    # Enable CSRF protection globally for Flask app
    csrf = CSRFProtect(app)
    csrf.init_app(app)

app.config.from_pyfile("portal.conf")
app.url_map.strict_slashes = False
app.permanent_session_lifetime = timedelta(minutes=1440)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
# set up Markdown Rendering
md = Misaka()
md.__init__(
    app,
    tables=True,
    autolink=True,
    fenced_code=True,
    smartypants=True,
    quote=True,
    math=True,
    math_explicit=True,
)

# Set up debugger behavior:
if app.debug:
    # set up jinja2 livehtml for localdev
    app.jinja_env.auto_reload = True

if minislate_user:
    slate_api_token = minislate_user[5]
else:
    slate_api_token = app.config["SLATE_API_TOKEN"]

slate_api_endpoint = app.config["SLATE_API_ENDPOINT"]
mailgun_api_token = app.config["MAILGUN_API_TOKEN"]


def format_datetime(value, format="%b %d %Y %I:%M %p"):
    """Format a date time to (Default): d Mon YYYY HH:MM P"""

    if value is None:
        return ""

    date_time_obj = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    date_time_pretty_format = date_time_obj.strftime(format)

    return date_time_pretty_format


# Register the template filter with the Jinja Environment
app.jinja_env.filters["formatdatetime"] = format_datetime

import portal.views
