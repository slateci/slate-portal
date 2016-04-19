from flask import g, jsonify, request
from functools import wraps

from globus_sdk import (TransferClient, TransferAPIError,
                        DeleteData)

import requests

from service import app, datasets
from service.errors import (BadRequestError, InternalServerError,
                            ForbiddenError, UnauthorizedError)
from service.processing import render_graphs
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
        # Validate that the token is active
        # Validate that the token audience contains
        # 'GlobusWorld Resource Server'
        # Exercise 2 begin

        # Exercise 2 end

        portal_admin_id = 'e12630ca-fcd2-11e5-9123-33cb1a3964b1'

        # Verify that the identities_set from the token introspection
        # includes the portal admin identity id (mrdpdemo@globusid.org)
        # Exercise 2 begin

        # Exercise 2 end

        # Token has passed verification so we attach it to the
        # request global object and proceed
        g.req_token = token

        return fn(*args, **kwargs)
    return decorated_function


@app.route('/api/doit', methods=['POST'])
@authenticated
def doit():
    """
    Add code here to:
    - Call token introspect
    - Get dependent tokens
    """
    dependent_tokens = get_dependent_tokens(g.req_token)

    transfer_scope = 'urn:globus:auth:scope:transfer.api.globus.org:all'
    http_scope = 'urn:globus:auth:scope:tutorial-https-endpoint.globus.org:all'

    # dependent_tokens is a list of token response objects
    # create transfer_token and http_token variables containing
    # the correct token for each scope
    # Exercise 2 begin

    # Exercise 2 end

    selected_ids = request.form.getlist('datasets')
    selected_year = request.form.get('year')
    user_identity_id = request.form.get('user_identity_id')
    user_identity_name = request.form.get('user_identity_name')

    selected_datasets = [dataset for dataset in datasets
                         if dataset['id'] in selected_ids]

    if not (selected_datasets and selected_year):
        raise BadRequestError()

    transfer = TransferClient(token=transfer_token)

    source_ep = app.config['DATASET_ENDPOINT_ID']
    source_info = transfer.get_endpoint(source_ep)
    source_https = source_info['https_server']
    source_base = app.config['DATASET_ENDPOINT_BASE']
    source_token = http_token

    dest_ep = app.config['GRAPH_ENDPOINT_ID']
    dest_info = transfer.get_endpoint(dest_ep)
    dest_https = dest_info['https_server']
    dest_base = app.config['GRAPH_ENDPOINT_BASE']
    dest_path = '%sGraphs for %s/' % (dest_base, user_identity_name)
    dest_token = http_token

    if not (source_https and dest_https):
        raise InternalServerError(message='Endpoints must be HTTPS servers')

    svgs = {}

    for dataset in selected_datasets:
        source_path = dataset['path']
        response = requests.get('%s%s%s/%s.csv' % (source_https, source_base,
                                                   source_path, selected_year),
                                headers=dict(
                                    Authorization='Bearer ' + source_token),
                                allow_redirects=False)
        response.raise_for_status()
        svgs.update(render_graphs(
            csv_data=response.iter_lines(decode_unicode=True),
            append_titles=' from %s for %s' % (dataset['name'], selected_year),
        ))

    transfer.endpoint_autoactivate(dest_ep)

    try:
        transfer.operation_mkdir(dest_ep, dest_path)
    except TransferAPIError as error:
        if 'MkdirFailed.Exists' not in error.code:
            raise

    try:
        transfer.add_endpoint_acl_rule(
            dest_ep,
            dict(principal=user_identity_id,
                 principal_type='identity', path=dest_path, permissions='r'),
        )
    except TransferAPIError as error:
        if error.code != 'Exists':
            raise

    for filename, svg in svgs.items():
        # n.b. The HTTPS Server will overwrite existing files that you PUT.

        requests.put('%s%s%s.svg' % (dest_https, dest_path, filename),
                     data=svg,
                     headers=dict(Authorization='Bearer ' + dest_token),
                     allow_redirects=False).raise_for_status()

    results = {
        'dest_ep': dest_ep,
        'dest_path': dest_path,
        'dest_name': dest_info['display_name'],
        'graph_count': len(svgs) or 0
    }

    return jsonify(results)


@app.route('/api/cleanup', methods=['POST'])
@authenticated
def cleanup():
    user_identity_name = request.form.get('user_identity_name')

    dependent_tokens = get_dependent_tokens(g.req_token)

    transfer_scope = 'urn:globus:auth:scope:transfer.api.globus.org:all'

    try:
        transfer_token = next(token['access_token']
                              for token in dependent_tokens
                              if token['scope'] == transfer_scope)
    except StopIteration:
        raise InternalServerError(message='Problem with dependent token grant')

    dest_ep = app.config['GRAPH_ENDPOINT_ID']
    dest_base = app.config['GRAPH_ENDPOINT_BASE']
    dest_path = '%sGraphs for %s/' % (dest_base, user_identity_name)

    transfer = TransferClient(token=transfer_token)

    try:
        acl = next(acl for acl in transfer.endpoint_acl_list(dest_ep)
                   if dest_path == acl['path'])
    except StopIteration:
        pass
    else:
        transfer.delete_endpoint_acl_rule(dest_ep, acl['id'])

    delete_request = DeleteData(transfer_client=transfer, endpoint=dest_ep,
                                label="Delete Graphs from the Service Demo",
                                recursive=True)
    delete_request.add_item(dest_path)

    try:
        task = transfer.submit_delete(delete_request)
    except TransferAPIError as ex:
        raise InternalServerError(message=ex.message)
    else:
        return jsonify(dict(task_id=task['task_id']))


def get_dependent_tokens(token):
    # Call Globus Auth dependent token grant
    # Exercise 2 begin

    # Exercise 2 end

    return tokens.json()
