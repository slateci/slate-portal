from flask import g, jsonify, request
from functools import wraps

from service import app
from service.errors import (BadRequestError, UnauthorizedError, ForbiddenError,
                            InternalServerError)
from service.utils import load_auth_client, get_token


def authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            raise UnauthorizedError()

        # Get the access token from the request
        token = get_token(request.headers['Authorization'])

        # Call token introspect
        client = load_auth_client()
        token_meta = client.oauth2_token_introspect(token)

        if not token_meta.get('active'):
            raise ForbiddenError()

        # Verify that the "audience" for this token is our service
        if 'GlobusWorld Resource Server' not in token_meta.get('aud', []):
            raise ForbiddenError()

        portal_client_id = app.config['PORTAL_CLIENT_ID']

        # Verify that the identities_set from the token introspection
        # includes the portal client identity id
        if portal_client_id != token_meta.get('sub'):
            raise ForbiddenError()

        # Token has passed verification so we attach it to the
        # request global object and proceed
        g.req_token = token

        return fn(*args, **kwargs)
    return decorated_function


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
