from flask import g, jsonify, request

from globus_sdk import (TransferClient, TransferAPIError,
                        DeleteData)

import requests

from service import app, datasets
from service.decorators import authenticated
from service.errors import BadRequestError, InternalServerError
from service.processing import render_graphs
from service.utils import get_dependent_tokens


@app.route('/api/doit', methods=['POST'])
@authenticated
def doit():
    """
    Add code here to:

    - Read the year and the IDs of the datasets the user wants
    - Instantiate a Transfer client as the identity of the portal
    - `GET` the CSVs for the selected datasets via HTTPS server as the
      identity of the portal
    - Generate a graph SVG file for the precipitation (`PRCP`) and
      temperature (`TMIN`/`TMAX`) for the selected year and datasets
    - `PUT` the generated graphs onto the predefined share endpoint as
      the identity of the portal
    - Display a confirmation
    """

    dependent_tokens = get_dependent_tokens(g.req_token)

    transfer_scope = 'urn:globus:auth:scope:transfer.api.globus.org:all'
    http_scope = 'urn:globus:auth:scope:tutorial-https-endpoint.globus.org:all'

    try:
        transfer_token = next(token['access_token']
                              for token in dependent_tokens
                              if token['scope'] == transfer_scope)
    except StopIteration:
        raise InternalServerError(message='Problem with dependent token grant')

    try:
        http_token = next(token['access_token']
                          for token in dependent_tokens
                          if token['scope'] == http_scope)
    except StopIteration:
        raise InternalServerError(message='Problem with dependent token grant')

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
    """
    Add code here to:

    - figure out the logged-in user's graph directory
    - find the logged-in user's ACL for the graph directory
    - delete both the directory and the associated ACL
    """
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
