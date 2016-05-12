from flask import g, jsonify, request
from functools import wraps
import requests

from service import app
from service.errors import (BadRequestError, UnauthorizedError, ForbiddenError,
                            InternalServerError)
from service.utils import basic_auth_header, get_token


def authenticated(fn):
    """Mark a route as requiring authentication."""
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        if 'Authorization' not in request.headers:
            raise UnauthorizedError()

        # Get the access token from the request
        token = get_token(request.headers['Authorization'])
        auth_header = basic_auth_header()
        ga_token_url = app.config['GA_INTROSPECT_URI']

        # Call /token/introspect
        token_meta = requests.post(ga_token_url,
                                   headers=dict(Authorization=auth_header),
                                   data=dict(token=token)).json()

        if not token_meta.get('active'):
            raise ForbiddenError()

        service_id = app.config['GA_SERVICE_ID']
        portal_admin_id = app.config['PORTAL_ADMIN_ID']

        # Verify that the "audience" for this token is our service
        if service_id not in token_meta.get('aud', []):
            raise ForbiddenError()

        # Verify that the identities_set from the token introspection
        # includes the portal admin identity id (mrdpdemo@globusid.org)
        if portal_admin_id != token_meta.get('sub'):
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
