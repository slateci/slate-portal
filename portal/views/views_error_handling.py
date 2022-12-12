from portal import app
from werkzeug.exceptions import HTTPException
import traceback
import time
from flask import (render_template, request, session)
import sys

# Create a custom error handler for Exceptions
@app.errorhandler(Exception)
def exception_occurred(e):
    app.logger.error(e)
    trace = traceback.format_tb(sys.exc_info()[2])
    app.logger.error("{0} Traceback occurred:\n".format(time.ctime()) +
                     "{0}\nTraceback completed".format("n".join(trace)))
    trace = "<br>".join(trace)
    trace.replace('\n', '<br>')
    return render_template('error.html', exception=trace)


@app.route('/error/<message>', methods=['GET'])
def errorpage(message):
    if request.method == 'GET':
        return render_template('error.html', message=message)


@app.errorhandler(404)
def not_found(e):
    app.logger.error(e)
    return render_template("404.html", e=e)

@app.errorhandler(504)
def handle_gateway_timeout(e):
    app.logger.error("GATEWAY TIMEOUT CAUGHT: {}".format(e))
    return render_template("404.html", e=e)


# @app.errorhandler(Exception)
# def handle_exception(e):
#     # pass through HTTP errors
#     if isinstance(e, HTTPException):
#         return e
#     print("Triggered Exception: {}".format(Exception.with_traceback))
#     print("Error: {}".format(e))
#     # now you're handling non-HTTP exceptions only
#     return render_template("500.html", e=e), 500
