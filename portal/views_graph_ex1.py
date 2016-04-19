from flask import (flash, redirect, render_template, request,
                   session, url_for)
import requests

from globus_sdk import (TransferClient, TransferAPIError,
                        DeleteData)

from portal import app, datasets
from portal.decorators import authenticated
from portal.processing import render_graphs
from portal.utils import get_portal_tokens


@app.route('/graph', methods=['GET', 'POST'])
@authenticated
def graph():
    """
    Add code here to:

    - Instantiate a Transfer client as the identity of the portal
    - `GET` the CSVs for the selected datasets via HTTPS server as the
      identity of the portal
    - Generate a graph SVG file for the precipitation (`PRCP`) and
      temperature (`TMIN`/`TMAX`) for the selected year and datasets
    - `PUT` the generated graphs onto the predefined share endpoint as
      the identity of the portal
    - Display a confirmation
    """

    # Read the year and the IDs of the datasets the user wants
    if request.method == 'GET':
        return render_template('graph.jinja2', datasets=datasets)

    selected_ids = request.form.getlist('dataset')
    selected_datasets = [dataset for dataset in datasets
                         if dataset['id'] in selected_ids]
    selected_year = request.form.get('year')

    if not (selected_datasets and selected_year):
        flash("Please select at least one dataset and a year to graph.")
        return redirect(url_for('graph'))

    # Get tokens for the portal admin user (not the requesting user)
    transfer_token = get_portal_tokens()['transfer']
    https_token = get_portal_tokens()['https']

    transfer = TransferClient(token=transfer_token)

    source_ep = app.config['DATASET_ENDPOINT_ID']
    source_info = transfer.get_endpoint(source_ep)
    source_https = source_info['https_server']
    source_base = app.config['DATASET_ENDPOINT_BASE']
    source_token = https_token

    dest_ep = app.config['GRAPH_ENDPOINT_ID']
    dest_info = transfer.get_endpoint(dest_ep)
    dest_https = dest_info['https_server']
    dest_base = app.config['GRAPH_ENDPOINT_BASE']
    dest_path = '%sGraphs for %s/' % (dest_base, session['primary_username'])
    dest_token = https_token

    if not (source_https and dest_https):
        flash("Both dataset and graph endpoints must be HTTPS endpoints.")
        return redirect(url_for('graph'))

    svgs = {}

    for dataset in selected_datasets:
        source_path = dataset['path']
        response = requests.get('%s%s%s/%s.csv' % (source_https, source_base,
                                                   source_path, selected_year),
                                headers=dict(
                                    Authorization='Bearer ' + source_token,
                                ),
                                allow_redirects=False)
        response.raise_for_status()
        svgs.update(render_graphs(
            csv_data=response.iter_lines(decode_unicode=True),
            append_titles=" from %s for %s" % (dataset['name'], selected_year),
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
            dict(principal=session['primary_identity'],
                 principal_type='identity', path=dest_path, permissions='r'),
        )
    except TransferAPIError as error:
        if error.code != 'Exists':
            raise

    for filename, svg in svgs.items():
        # n.b. The HTTPS Server will overwrite existing files that you PUT.

        # Add call to put the svg to the dest_https + dest_path + filename
        # Exercise 1 begin

        # Exercise 1 end

    flash("%d-file SVG upload to %s on %s completed!" %
          (len(svgs), dest_path, dest_info['display_name']))
    return redirect(url_for('browse', endpoint_id=dest_ep,
                            endpoint_path=dest_path.lstrip('/')))


@app.route('/graph/clean-up', methods=['POST'])
@authenticated
def graph_cleanup():
    """
    Add code here to:

    - figure out the logged-in user's graph directory
    - find the logged-in user's ACL for the graph directory
    - delete both the directory and the associated ACL
    """

    transfer_token = get_portal_tokens()['transfer']
    transfer = TransferClient(token=transfer_token)

    dest_ep = app.config['GRAPH_ENDPOINT_ID']
    dest_base = app.config['GRAPH_ENDPOINT_BASE']
    dest_path = '%sGraphs for %s/' % (dest_base, session['primary_username'])

    # Find and delete the acl rule for dest_ep
    # Delete the destination foler (dest_ep, dest_base, dest_path)
    # Exercise 1 begin

    # Exercise 1 end

    flash("Your existing processed graphs have been removed.")
    return redirect(url_for('graph'))
