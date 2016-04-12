from flask import g, jsonify, request
from functools import wraps

from resource_server import app
from resource_server.errors import UnauthorizedError, ForbiddenError
from resource_server.utils import token_introspect, get_token


def authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            raise UnauthorizedError()

        token = get_token(request.headers['Authorization'])
        # do token introspection
        # if request.headers['Authorization'] != 'Bearer good':
        token_meta = token_introspect(token)

        if token_meta.get('active', False) is False:
            raise ForbiddenError()

        g.req_token = token

        return fn(*args, **kwargs)
    return decorated_function


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
