from flask import g, jsonify, request

from globus_sdk import (TransferClient, TransferAPIError,
                        DeleteData, AccessTokenAuthorizer)

import requests

from service import app, datasets
from service.decorators import authenticated
from service.errors import BadRequestError, InternalServerError
from service.processing import render_graphs
from service.utils import load_auth_client


@app.route('/api/doit', methods=['POST'])
@authenticated
def doit():
    """
    - Call token introspect
    - Get dependent tokens
    """
    dependent_tokens = get_dependent_tokens(g.req_token)

    # dependent_tokens is a token response object
    # create transfer_token and http_token variables containing
    # the correct token for each resource server
    transfer_token = dependent_tokens.by_resource_server[
        'transfer.api.globus.org']['access_token']
    http_token = dependent_tokens.by_resource_server[
        'tutorial-https-endpoint.globus.org']['access_token']

    selected_ids = request.form.getlist('datasets')
    selected_year = request.form.get('year')
    user_identity_id = request.form.get('user_identity_id')
    user_identity_name = request.form.get('user_identity_name')

    selected_datasets = [dataset for dataset in datasets
                         if dataset['id'] in selected_ids]

    if not (selected_datasets and selected_year):
        raise BadRequestError()

    transfer = TransferClient(authorizer=AccessTokenAuthorizer(transfer_token))

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
        # PermissionDenied can happen if a new Portal client is swapped
        # in and it doesn't have endpoint manager on the dest_ep.
        # The /portal/processed directory has been set to to read/write
        # for all users so the subsequent operations will succeed.
        if error.code == 'PermissionDenied':
            pass
        elif error.code != 'Exists':
            raise

    for filename, svg in svgs.items():
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

    transfer_token = dependent_tokens.by_resource_server[
        'transfer.api.globus.org']['access_token']

    dest_ep = app.config['GRAPH_ENDPOINT_ID']
    dest_base = app.config['GRAPH_ENDPOINT_BASE']
    dest_path = '%sGraphs for %s/' % (dest_base, user_identity_name)

    transfer = TransferClient(authorizer=AccessTokenAuthorizer(transfer_token))

    transfer.endpoint_autoactivate(dest_ep)

    try:
        acl = next(acl for acl in transfer.endpoint_acl_list(dest_ep)
                   if dest_path == acl['path'])
    except StopIteration:
        pass
    except TransferAPIError as ex:
        # PermissionDenied can happen if a new Portal client is swapped
        # in and it doesn't have endpoint manager on the dest_ep.
        # The /portal/processed directory has been set to to writeable
        # for all users so the delete task will succeed even if an ACL
        # can't be set.
        if ex.code == 'PermissionDenied':
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
    client = load_auth_client()
    return client.oauth2_get_dependent_tokens(token)
