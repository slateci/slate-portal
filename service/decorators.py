from flask import jsonify

from service import app
from service.errors import (BadRequestError, UnauthorizedError, ForbiddenError,
                            InternalServerError)


def token_is_valid(data):
    return (data.get('active') and
            'GlobusWorld Resource Server' in data.get('aud', []))


@app.errorhandler(BadRequestError)
def handle_badrequest_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.errorhandler(InternalServerError)
def handle_internalserver_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.errorhandler(UnauthorizedError)
def handle_unauthorized_error(error):
    response = jsonify(error.to_dict())
    response.headers['WWW-Authenticate'] = \
        'Bearer realm="urn:globus:auth:scope:demo-resource-server:all"'
    response.status_code = error.status_code

    return response


@app.errorhandler(ForbiddenError)
def handle_forbidded_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response
