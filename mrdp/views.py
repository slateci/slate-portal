import uuid

from flask import (abort, flash, g, redirect, render_template, request,
                   session, url_for)
from oauth2client import client as oauth
import requests

try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode

from globus_sdk import TransferClient, TransferAPIError

from mrdp import app, database, datasets
from mrdp.decorators import authenticated
from mrdp.utils import basic_auth_header, get_safe_redirect


@app.route('/', methods=['GET'])
def home():
    """Home page - play with it if you must!"""
    return render_template('home.jinja2')


@app.route('/signup', methods=['GET'])
def signup():
    """Send the user to Globus Auth with signup=1."""
    return redirect(url_for('authcallback', signup=1))


@app.route('/login', methods=['GET'])
def login():
    """
    Add code here to:

    - Redirect user to Globus Auth
    - Get an access token and a refresh token
    - Store these tokens in the session
    - Redirect to the repository page or profile page
      if this is the first login
    """
    return redirect(url_for('authcallback'))


@app.route('/logout', methods=['GET'])
@authenticated
def logout():
    """
    Add code here to:

    - Destroy Globus Auth token (remove it from session?)
    - ???
    """
    headers = {'Authorization': basic_auth_header()}
    data = {
        'token_type_hint': 'refresh',
        'token': g.credentials.refresh_token
    }

    # Invalidate the tokens with Globus Auth
    requests.post(app.config['GA_REVOKE_URI'],
                  headers=headers,
                  data=data)

    # Destroy the session state
    session.clear()

    redirect_uri = url_for('home', _external=True)

    ga_logout_url = []
    ga_logout_url.append(app.config['GA_LOGOUT_URI'])
    ga_logout_url.append('?client={}'.format(app.config['GA_CLIENT_ID']))
    ga_logout_url.append('&redirect_uri={}'.format(redirect_uri))
    ga_logout_url.append('&redirect_name=MRDP Demo App')

    # Send the user to the Globus Auth logout page
    return redirect(''.join(ga_logout_url))


@app.route('/profile', methods=['GET', 'POST'])
@authenticated
def profile():
    """User profile information. Assocated with a Globus Auth identity."""
    if request.method == 'GET':
        identity_id = session.get('primary_identity')
        profile = database.load_profile(identity_id)

        if profile:
            name, email, project = profile

            session['name'] = name
            session['email'] = email
            session['project'] = project

        if request.args.get('next'):
            session['next'] = get_safe_redirect()

        return render_template('profile.jinja2')
    elif request.method == 'POST':
        name = session['name'] = request.form['name']
        email = session['email'] = request.form['email']
        project = session['project'] = request.form['project']

        database.save_profile(identity_id=session['primary_identity'],
                              name=name,
                              email=email,
                              project=project)

        flash('Thank you! Your profile has been successfully updated.')

        if 'next' in session:
            redirect_to = session['next']
            session.pop('next')
        else:
            redirect_to = url_for('profile')

        return redirect(redirect_to)


@app.route('/authcallback', methods=['GET'])
def authcallback():
    if 'error' in request.args:
        pass
        # handle error

    scopes = 'urn:globus:auth:scope:transfer.api.globus.org:all'
    config = app.config

    if request.args.get('signup'):
        authorize_uri = '{}?signup=1'.format(config['GA_AUTH_URI'])
    else:
        authorize_uri = config['GA_AUTH_URI']

    flow = oauth.OAuth2WebServerFlow(app.config['GA_CLIENT_ID'],
                                     scope=scopes,
                                     authorization_header=basic_auth_header(),
                                     redirect_uri=config['GA_REDIRECT_URI'],
                                     auth_uri=authorize_uri,
                                     token_uri=config['GA_TOKEN_URI'],
                                     revoke_uri=config['GA_REVOKE_URI'])

    if 'code' not in request.args:
        state = str(uuid.uuid4())

        auth_uri = flow.step1_get_authorize_url(state=state)

        session['oauth2_state'] = state

        return redirect(auth_uri)
    else:
        passed_state = request.args.get('state')

        if passed_state and passed_state == session.get('oauth2_state'):
            code = request.args.get('code')

            try:
                credentials = flow.step2_exchange(code)
            except Exception as err:
                return repr(err)
            else:
                session.pop('oauth2_state')

                id_token = credentials.id_token
                session.update(
                    credentials=credentials.to_json(),
                    is_authenticated=True,
                    primary_username=id_token.get('preferred_username'),
                    primary_identity=id_token.get('sub'),
                )

            return redirect(url_for('transfer'))


@app.route('/transfer', methods=['GET', 'POST'])
@authenticated
def transfer():
    """
    Add code here to:

    - Send to Globus to select a destination endpoint
    - Submit a Globus transfer request and get the task ID
    - Return to a transfer "status" page

    The target template expects a 'task_id' (str) and a
    'transfer_status' (dictionary) containing various details about the
    task. Since this route is called only once after a transfer request
    is submitted, it only provides a 'task_id'.
    """
    if request.method == 'GET':
        return render_template('transfer.jinja2', datasets=datasets)

    if request.method == 'POST':
        if not request.form.get('dataset'):
            flash('Please select at least one dataset.')
            return redirect(url_for('transfer'))

        params = {
            'method': 'POST',
            'action': url_for('submit_transfer', _external=True,
                              _scheme='https'),
            'filelimit': 0,
            'folderlimit': 1
        }

        browse_endpoint = 'https://www.globus.org/app/browse-endpoint?{}' \
            .format(urlencode(params))

        session['form'] = {
            'datasets': request.form.getlist('dataset')
        }

        return redirect(browse_endpoint)


@app.route('/submit-transfer', methods=['POST'])
@authenticated
def submit_transfer():
    globus_form = request.form

    selected = session['form']['datasets']
    filtered_datasets = [ds for ds in datasets if ds['id'] in selected]

    transfer = TransferClient(auth_token=g.credentials.access_token)

    source_endpoint_id = app.config['DATASET_ENDPOINT_ID']
    destination_endpoint_id = globus_form['endpoint_id']

    transfer_items = []
    for ds in filtered_datasets:
        source_path = ds['path']
        dest_path = globus_form['path']

        if globus_form.get('folder[0]'):
            dest_path += globus_form['folder[0]'] + '/'

        dest_path += ds['name'] + '/'

        transfer_items.append({
            'DATA_TYPE': 'transfer_item',
            'source_path': source_path,
            'destination_path': dest_path,
            'recursive': True
        })

    submission_id = transfer.get_submission_id().data['value']
    transfer_data = {
        'DATA_TYPE': 'transfer',
        'submission_id': submission_id,
        'source_endpoint': source_endpoint_id,
        'destination_endpoint': destination_endpoint_id,
        'label': globus_form.get('label') or None,
        'DATA': transfer_items
    }

    transfer.endpoint_autoactivate(source_endpoint_id)
    transfer.endpoint_autoactivate(destination_endpoint_id)
    task_id = transfer.submit_transfer(transfer_data).data['task_id']

    flash('Transfer request submitted successfully. Task ID: ' + task_id)

    return(redirect(url_for('transfer_status', task_id=task_id)))


@app.route('/graph', methods=['GET', 'POST'])
@authenticated
def graph():
    """
    Add code here to:

    - Send to Globus to select a destination endpoint
    - `GET` all years CSVs for the selected datasets via HTTPS server
    - Generate a graph SVG/HTML file for the precipitation (`PRCP`),
      temperature (`TMIN`/`TMAX`), or both, depending on the user's
      selection, for each dataset
    - `PUT` the generated graphs onto the user's destination endpoint
    - Display a confirmation message
    """

    if request.method == 'GET':
        return render_template('graph.jinja2', datasets=datasets)

    from csv import reader
    import pygal
    from time import strftime

    if not request.form.get('dataset'):
        flash('Please select at least one dataset.')
        return redirect(url_for('graph'))

    transfer = TransferClient(auth_token=g.credentials.access_token)

    previous = session.get('form') or abort(400)
    selected_ids = previous.get('datasets')
    selected_datasets = [dataset
                         for dataset in datasets
                         if not selected_ids or dataset['id'] in selected_ids]
    selected_type = previous.get('graph_type') or 'all'

    source_infos = {endpoint_id: transfer.get_endpoint(endpoint_id).data
                    for endpoint_id in set(dataset['endpoint_id']
                                           for dataset in selected_datasets)}
    for source_info in source_infos.values():
        if not source_info.get('https_server'):  # source does not support GETs
            # FIXME this should abort() / return an error message to the user
            source_info['https_server'] = 'https://mrdp-demo.appspot.com'

    form = request.form
    dest_ep = form.get('endpoint_id')
    dest_info = transfer.get_endpoint(dest_ep).data
    dest_https = dest_info.get('https_server')
    dest_base = form.get('path')
    dest_folder = form.get('folder[0]')
    dest_path = ('%s%s/' % (dest_base, dest_folder) if dest_folder
                 else dest_base) + strftime('Climate Graphs %F %I%M%S%P/')

    if not dest_https:  # destination does not support PUTs
        # FIXME this should abort() / return an error message to the user
        dest_https = 'https://mrdp-demo.appspot.com'

    # FIXME We need a Bearer token to PUT onto the destination endpoint and a
    # Bearer token for each individual source endpoint to GET the all.csv file
    # -or-
    # The application needs a refresh token to get credentials for accessing
    # the destination endpoint (and maybe the source endpoint too), and the
    # application will create a new directory with a new ACL for the logged-in
    # user so they can access the files.
    authorizations = dict([
        (dest_ep, 'Bearer XXX')
    ] + [
        (endpoint_id, 'Bearer XXX')
        for endpoint_id, endpoint_info in source_infos.items()
        if endpoint_id != dest_ep
    ])

    svgs = {}

    for dataset in selected_datasets:
        source_ep = dataset['endpoint_id']
        source_https = source_infos[source_ep]['https_server']
        source_path = dataset['path']

        response = requests.get(
            '%s/%s/all.csv' % (source_https, source_path),
            headers={'Authorization': authorizations[source_ep]},
        )
        csv = reader(response.iter_lines())

        header = next(csv)
        date_index = header.index('DATE')
        prcp_index = header.index('PRCP')
        tmin_index = header.index('TMIN')
        tmax_index = header.index('TMAX')

        annuals = {}
        for row in csv:
            year = int(row[date_index][:4])
            try:
                data = annuals[year]
            except KeyError:
                data = annuals[year] = dict(days_of_data=0,
                                            precipitation_total=0,
                                            min_temperature_total=0,
                                            max_temperature_total=0)
            data['days_of_data'] += 1
            data['precipitation_total'] += int(row[prcp_index])
            data['min_temperature_total'] += int(row[tmin_index])
            data['max_temperature_total'] += int(row[tmax_index])

        if selected_type in ['all', 'precipitation']:
            x_axis = []
            y_values = []

            for year, data in sorted(annuals.items()):
                x_axis.append(year)
                y_values.append(data['precipitation_total'] / 10.)

            line = pygal.Line(x_label_rotation=90)
            line.x_labels = x_axis
            line.add("Precip(mm)", y_values)

            svgs["%s %s" % (dataset['name'],
                            "Total Annual Precipitation")] = line.render()

        if selected_type in ['all', 'temperature']:
            x_axis = []
            y_min_values = []
            y_max_values = []

            for year, data in sorted(annuals.items()):
                x_axis.append(year)
                y_min_values.append(data['min_temperature_total'] / 10. /
                                    data['days_of_data'])
                y_max_values.append(data['max_temperature_total'] / 10. /
                                    data['days_of_data'])

            line = pygal.Line(x_label_rotation=90)
            line.x_labels = x_axis
            line.add("Avg Max Temp(C)", y_max_values)
            line.add("Avg Min Temp(C)", y_min_values)

            svgs["%s %s" % (dataset['name'],
                            "Average Temperatures")] = line.render()

    transfer.operation_mkdir(dest_ep, dest_path)

    for filename, svg in svgs.items():
        requests.put(
            '%s%s%s.svg' % (dest_https, dest_path, filename),
            headers={'Authorization': authorizations[dest_ep]},
            data=data,
        )

    flash("%d-file SVG upload to %s on %s completed!" %
          (len(svgs), dest_path, dest_info['display_name']))
    return redirect(url_for('repository'))


@app.route('/browse/<dataset_id>', methods=['GET'])
@authenticated
def browse(dataset_id):
    """
    Add code here to:

    - Get list of files for the selected dataset
    - Return a list of files to a browse view

    The target template (browse.jinja2) expects a unique dataset
    identifier 'dataset_id' (str) and 'file_list' (list of
    dictionaries) containing the following information about each file
    in the dataset:

    {'name': 'file name', 'size': 'file size', 'id': 'file uri/path'}

    'dataset_uri' is passed to the route in the URL as 'target_uri'.

    If you want to display additional information about each file, you
    must add those keys to the dictionary and modify the browse.jinja2
    template accordingly.
    """

    filtered_datasets = [ds for ds in datasets if ds['id'] == dataset_id]

    if len(filtered_datasets):
        dataset = filtered_datasets[0]
    else:
        abort(404)

    endpoint_id = app.config['DATASET_ENDPOINT_ID']
    path = dataset['path']

    transfer = TransferClient(auth_token=g.credentials.access_token)

    try:
        transfer.endpoint_autoactivate(endpoint_id)
        res = transfer.operation_ls(endpoint_id, path=path)
    except TransferAPIError as err:
        flash('Error [{}]: {}'.format(err.code, err.message))
        return redirect(url_for('transfer'))
    else:
        listing = res.data['DATA']

    file_list = [e for e in listing if e['type'] == 'file']

    ep = transfer.get_endpoint(endpoint_id).data

    dataset_uri = '{}/{}'.format(ep.get('https_server') or
                                 'https://mrdp-demo.appspot.com',  # FIXME
                                 path)

    return render_template('browse.jinja2', dataset_uri=dataset_uri,
                           file_list=file_list)


@app.route('/status/<task_id>', methods=['GET'])
@authenticated
def transfer_status(task_id):
    """
    Add code here to call Globus to get status/details of transfer with
    task_id.

    The target template (tranfer_status.jinja2) expects a 'task_id'
    (str) and a 'transfer_status' (dictionary) containing various
    details about the task. 'transfer_status' is expected to contain the
    following keys:

    {
        'source_ep_name': 'display name of source endpoint',
        'dest_ep_name': 'display name of destination endpoint',
        'request_time': time that the transfer request was submitted,
        'status': 'status of the transfer task',
        'files_transferred': number of files transferred so far,
        'fault': number of faults encountered,
    }

    'task_id' is passed to the route in the URL as 'task_id'.

    If you want to display additional information about the transfer,
    you must add those keys to the dictionary and modify the
    transfer_status.jinja2 template accordingly.
    """
    transfer = TransferClient(auth_token=g.credentials.access_token)
    task = transfer.get_task(task_id)

    return render_template('transfer_status.jinja2', task=task.data)
