from flask import (flash, redirect, render_template, request,
                   session, url_for)
import requests

from portal import app, datasets
from portal.decorators import authenticated
from portal.utils import get_portal_tokens


@app.route('/graph', methods=['GET', 'POST'])
@authenticated
def graph():
    if request.method == 'GET':
        return render_template('graph.jinja2', datasets=datasets)

    selected_ids = request.form.getlist('dataset')
    selected_year = request.form.get('year')

    if not (selected_ids and selected_year):
        flash("Please select at least one dataset and a year to graph.")
        return redirect(url_for('graph'))

    service_token = get_portal_tokens()['service']
    service_url = '{}/{}'.format(app.config['SERVICE_URL_BASE'], 'api/doit')
    req_headers = dict(Authorization='Bearer {}'.format(service_token))

    req_data = dict(datasets=selected_ids,
                    year=selected_year,
                    user_identity_id=session.get('primary_identity'),
                    user_identity_name=session.get('primary_username'))

    resp = requests.post(service_url, headers=req_headers, data=req_data,
                         verify=False)

    resp.raise_for_status()

    dest_ep = resp.json().get('dest_ep')
    dest_path = resp.json().get('dest_path')
    dest_name = resp.json().get('dest_name')
    graph_count = resp.json().get('graph_count')

    flash("%d-file SVG upload to %s on %s completed!" %
          (graph_count, dest_path, dest_name))

    return redirect(url_for('browse', endpoint_id=dest_ep,
                            endpoint_path=dest_path.lstrip('/')))


@app.route('/graph/clean-up', methods=['POST'])
@authenticated
def graph_cleanup():
    service_token = get_portal_tokens()['service']
    service_url = '{}/{}'.format(app.config['SERVICE_URL_BASE'], 'api/cleanup')
    req_headers = dict(Authorization='Bearer {}'.format(service_token))

    resp = requests.post(service_url,
                         headers=req_headers,
                         data=dict(
                             user_identity_name=session['primary_username']
                         ),
                         verify=False)

    resp.raise_for_status()

    task_id = resp.json()['task_id']
    msg = '{} ({}).'.format('Your existing processed graphs have been removed',
                            task_id)
    flash(msg)
    return redirect(url_for('graph'))
