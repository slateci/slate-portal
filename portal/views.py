from flask import (abort, flash, redirect, render_template, request,
                   session, url_for)
import requests
import sqlite3
import uuid
import textwrap

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from globus_sdk import (TransferClient, TransferAPIError,
                        TransferData, RefreshTokenAuthorizer)

from portal import app, database
from portal.decorators import authenticated
from portal.utils import (load_portal_client, get_portal_tokens,
                          get_safe_redirect)

# try:
#     db = sqlite3.connect('data/clusters.db')
#     cursor = db.cursor()
#     cursor.execute(
#         '''CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, name TEXT, accesstoken TEXT unique, endpoint TEXT, email TEXT)''')
# except Exception as e:
#     db.rollback()
#     raise e
# finally:
#     db.close()


@app.route('/', methods=['GET'])
def home():
    """Home page - play with it if you must!"""
    return render_template('home.html')


@app.route('/community', methods=['GET'])
def community():
    """Community page"""
    return render_template('community.html')


@app.route('/faq', methods=['GET'])
def faq():
    """FAQs page"""
    return render_template('faq.html')


@app.route('/signup', methods=['GET'])
def signup():
    """Send the user to Globus Auth with signup=1."""
    return redirect(url_for('authcallback', signup=1))


@app.route('/login', methods=['GET'])
def login():
    """Send the user to Globus Auth."""
    return redirect(url_for('authcallback'))


@app.route('/logout', methods=['GET'])
@authenticated
def logout():
    """
    - Revoke the tokens with Globus Auth.
    - Destroy the session state.
    - Redirect the user to the Globus Auth logout page.
    """
    client = load_portal_client()

    # Revoke the tokens with Globus Auth
    for token, token_type in (
            (token_info[ty], ty)
            # get all of the token info dicts
            for token_info in session['tokens'].values()
            # cross product with the set of token types
            for ty in ('access_token', 'refresh_token')
            # only where the relevant token is actually present
            if token_info[ty] is not None):
        client.oauth2_revoke_token(
            token, additional_params={'token_type_hint': token_type})

    # Destroy the session state
    session.clear()

    redirect_uri = url_for('home', _external=True)

    ga_logout_url = []
    ga_logout_url.append(app.config['GLOBUS_AUTH_LOGOUT_URI'])
    ga_logout_url.append('?client={}'.format(app.config['PORTAL_CLIENT_ID']))
    ga_logout_url.append('&redirect_uri={}'.format(redirect_uri))
    ga_logout_url.append('&redirect_name=Globus Sample Data Portal')

    # Redirect the user to the Globus Auth logout page
    return redirect(''.join(ga_logout_url))


@app.route('/cli', methods=['GET', 'POST'])
@authenticated
def cli_access():
    if request.method == 'GET':
        access_token = session['tokens']['auth.globus.org']['access_token']
        access_token = textwrap.fill(access_token, 60)

        # Schema and query for getting user info and access token from Slate DB
        globus_id = session['primary_identity']
        query = {'token': '3acc9bdc-1243-40ea-96df-373c8a616a16',
                 'globus_id': globus_id}

        r = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/find_user', params=query)
        user_info = r.json()

        return render_template('cli_access.html', user_info=user_info)


@app.route('/vos', methods=['GET', 'POST'])
@authenticated
def list_vos():
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        s = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/users/' + slate_user_id + '/vos', params=token_query)

        s_info = s.json()
        vo_list = s_info['items']

        return render_template('vos.html', vo_list=vo_list)


@app.route('/vos/new', methods=['GET', 'POST'])
@authenticated
def create_vo():
    if request.method == 'GET':
        return render_template('vos_create.html')

    elif request.method == 'POST':
        """Route method to handle query to create a new VO"""

        name = request.form['name']
        token_query = {'token': session['slate_token']}
        add_vo = {"apiVersion": 'v1alpha1',
                  'metadata': {'name': name}}

        requests.post(
            'https://api-dev.slateci.io:18080/v1alpha1/vos', params=token_query, json=add_vo)

        return redirect(url_for('view_vo', name=name))


@app.route('/vos/<name>', methods=['GET', 'POST'])
@authenticated
def view_vo(name):
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        s = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/users/' + slate_user_id + '/vos', params=token_query)
        s_info = s.json()
        vo_list = s_info['items']
        vo_id = None
        for vo in vo_list:
            if vo['metadata']['name'] == name:
                vo_id = vo['metadata']['id']

        users = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/users', params=token_query)
        users = users.json()['items']

        vo_members = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/vos/' + vo_id + '/members', params=token_query)
        vo_members = vo_members.json()['items']

        return render_template('vos_profile.html', vo_list=vo_list, users=users, name=name, vo_members=vo_members)


@app.route('/vos/<name>/add_member', methods=['POST'])
@authenticated
def vo_add_member(name):
    if request.method == 'POST':
        new_user_id = request.form['newuser']
        token_query = {'token': session['slate_token']}
        vo_id = name

        s = requests.put(
            'https://api-dev.slateci.io:18080/v1alpha1/users/' + new_user_id + '/vos/' + vo_id, params=token_query)

        return redirect(url_for('view_vo', name=name))


@app.route('/vos/<name>/remove_member', methods=['POST'])
@authenticated
def vo_remove_member(name):
    if request.method == 'POST':
        remove_user_id = request.form['remove_member']
        token_query = {'token': session['slate_token']}
        vo_id = name

        s = requests.delete(
            'https://api-dev.slateci.io:18080/v1alpha1/users/' + remove_user_id + '/vos/' + vo_id, params=token_query)

        return redirect(url_for('view_vo', name=name))


@app.route('/testing', methods=['GET', 'POST'])
@authenticated
def testing():
    """testing route function to retrieve user info by id"""
    if request.method == 'GET':
        return render_template('testing.html')

    elif request.method == 'POST':
        user_id = request.form['name']
        return redirect(url_for('user_info', user_id=user_id))


@app.route('/testing/<user_id>', methods=['GET', 'POST'])
@authenticated
def user_info(user_id):
    if request.method == 'GET':
        cat_url = (
            'https://api-dev.slateci.io:18080/v1alpha1/users?token=' + user_id)
        response = requests.get(cat_url)
        user_info = response.json()

        return render_template('testing_user.html', user_info=user_info)


@app.route('/profile', methods=['GET', 'POST'])
@authenticated
def profile():
    """User profile information. Assocated with a Globus Auth identity."""
    if request.method == 'GET':
        identity_id = session.get('primary_identity')
        # profile = database.load_profile(identity_id)
        globus_id = identity_id
        query = {'token': '3acc9bdc-1243-40ea-96df-373c8a616a16',
                 'globus_id': globus_id}

        profile = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/find_user', params=query)

        if profile:
            profile = profile.json()['metadata']
            session['slate_token'] = profile['access_token']
            session['slate_id'] = profile['id']
        #     name, email, institution = profile
        #
        #     session['name'] = name
        #     session['email'] = email
        #     session['institution'] = institution
        else:
            flash(
                'Please complete any missing profile fields and press Save.')

        if request.args.get('next'):
            session['next'] = get_safe_redirect()

        return render_template('profile.html')
    elif request.method == 'POST':
        name = session['name'] = request.form['name']
        email = session['email'] = request.form['email']
        # Chris should maybe add institution into user info within DB?
        institution = session['institution'] = request.form['institution']
        globus_id = session['primary_identity']
        admin = False
        # Schema and query for adding users to Slate DB
        add_user = {"apiVersion": 'v1alpha1',
                    'metadata': {'globusID': globus_id,
                                 'name': name, 'email': email, 'admin': admin}}
        query = {'token': '3acc9bdc-1243-40ea-96df-373c8a616a16'}

        requests.post(
            'https://api-dev.slateci.io:18080/v1alpha1/users', params=query, json=add_user)

        flash('Your profile has successfully been updated!')

        if 'next' in session:
            redirect_to = session['next']
            session.pop('next')
        else:
            redirect_to = url_for('profile')

        return redirect(redirect_to)


@app.route('/authcallback', methods=['GET'])
def authcallback():
    """Handles the interaction with Globus Auth."""
    # If we're coming back from Globus Auth in an error state, the error
    # will be in the "error" query string parameter.
    if 'error' in request.args:
        flash("You could not be logged into the portal: " +
              request.args.get('error_description', request.args['error']))
        return redirect(url_for('home'))

    # Set up our Globus Auth/OAuth2 state
    redirect_uri = url_for('authcallback', _external=True)

    client = load_portal_client()
    client.oauth2_start_flow(redirect_uri, refresh_tokens=True)

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    if 'code' not in request.args:
        additional_authorize_params = (
            {'signup': 1} if request.args.get('signup') else {})

        auth_uri = client.oauth2_get_authorize_url(
            additional_params=additional_authorize_params)

        return redirect(auth_uri)
    else:
        # If we do have a "code" param, we're coming back from Globus Auth
        # and can start the process of exchanging an auth code for a token.
        code = request.args.get('code')
        tokens = client.oauth2_exchange_code_for_tokens(code)

        id_token = tokens.decode_id_token(client)
        session.update(
            tokens=tokens.by_resource_server,
            is_authenticated=True,
            name=id_token.get('name', ''),
            email=id_token.get('email', ''),
            institution=id_token.get('institution', ''),
            primary_username=id_token.get('preferred_username'),
            primary_identity=id_token.get('sub'),
        )

        # profile = database.load_profile(session['primary_identity'])
        # Need to query a request to view all users in Slate DB, then iterate
        # to see if profile exists by matching globus_id ideally. Get rid of
        # database.load_profile line above this once done
        globus_id = session['primary_identity']
        query = {'token': '3acc9bdc-1243-40ea-96df-373c8a616a16',
                 'globus_id': globus_id}

        profile = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/find_user', params=query)

        if profile:
            # name, email, institution = profile

            # session['name'] = name
            # session['email'] = email
            # session['institution'] = institution
            globus_id = session['primary_identity']
            query = {'token': '3acc9bdc-1243-40ea-96df-373c8a616a16',
                     'globus_id': globus_id}

            profile = requests.get(
                'https://api-dev.slateci.io:18080/v1alpha1/find_user', params=query)
            slate_user_info = profile.json()
            session['slate_token'] = slate_user_info['metadata']['access_token']
            session['slate_id'] = slate_user_info['metadata']['id']

        else:
            return redirect(url_for('profile',
                                    next=url_for('profile')))

        return redirect(url_for('profile'))


@app.route('/register', methods=['GET', 'POST'])
@authenticated
def register():
    if request.method == 'GET':
        globus_id = session['primary_identity']
        query = {'token': '3acc9bdc-1243-40ea-96df-373c8a616a16',
                 'globus_id': globus_id}

        r = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/find_user', params=query)
        user_info = r.json()
        slate_user_id = user_info['metadata']['id']
        # vo_url = 'https://api-dev.slateci.io:18080/v1alpha1/users/' + slate_user_id + '/vos'

        token_query = {'token': '3acc9bdc-1243-40ea-96df-373c8a616a16'}
        s = requests.get(
            'https://api-dev.slateci.io:18080/v1alpha1/users/' + slate_user_id + '/vos', params=token_query)

        s_info = s.json()
        vo_list = s_info['items']

        return render_template('register.html', user_info=user_info,
                               vo_list=vo_list, slate_user_id=slate_user_id)
    elif request.method == 'POST':
        name = request.form['name']
        vo = request.form['vo']
        return render_template('clusters.html', name=name, vo=vo)

        # if 'next' in session:
        #     redirect_to = session['next']
        #     session.pop('next')
        # else:
        #     redirect_to = url_for('clusters', name=name, vo=vo)
        #
        # return redirect(redirect_to)


@app.route('/clusters', methods=['GET'])
@authenticated
def clusters():
    """
    - Save the submitted form to the session.
    - Send to Globus to select a destination endpoint using the
      Browse Endpoint helper page.
    """
    # clusters = []
    # db = sqlite3.connect('data/clusters.db')
    # c = db.cursor()
    # try:
    #     with db:
    #         n = (session['name'],)
    #         for row in c.execute('''SELECT * FROM users WHERE name=?''', n):
    #             """
    #             Returns the clusters owned by the user of this session name
    #             (1, u'Lincoln Bryant', u'1b9a2d06-ffa7-4e66-8587-b624e291c499', u'UChicago', u'lincolnb@uchicago.edu')
    #
    #             """
    #             clusters += [{'name': str(row[1]), 'accesstoken': str(
    #                 row[2]), 'endpoint': str(row[3]), 'email': str(row[4])}]
    # finally:
    #     db.close()
    if request.method == 'GET':
        return render_template('clusters.html')


@app.route('/browse/dataset/<dataset_id>', methods=['GET'])
@app.route('/browse/endpoint/<endpoint_id>/<path:endpoint_path>',
           methods=['GET'])
@authenticated
def browse(dataset_id=None, endpoint_id=None, endpoint_path=None):
    """
    - Get list of files for the selected dataset or endpoint ID/path
    - Return a list of files to a browse view

    The target template (browse.html) expects an `endpoint_uri` (if
    available for the endpoint), `target` (either `"dataset"`
    or `"endpoint"`), and 'file_list' (list of dictionaries) containing
    the following information about each file in the result:

    {'name': 'file name', 'size': 'file size', 'id': 'file uri/path'}

    If you want to display additional information about each file, you
    must add those keys to the dictionary and modify the browse.html
    template accordingly.
    """

    assert bool(dataset_id) != bool(endpoint_id and endpoint_path)

    if dataset_id:
        try:
            dataset = next(ds for ds in datasets if ds['id'] == dataset_id)
        except StopIteration:
            abort(404)

        endpoint_id = app.config['DATASET_ENDPOINT_ID']
        endpoint_path = app.config['DATASET_ENDPOINT_BASE'] + dataset['path']

    else:
        endpoint_path = '/' + endpoint_path

    transfer_tokens = session['tokens']['transfer.api.globus.org']

    authorizer = RefreshTokenAuthorizer(
        transfer_tokens['refresh_token'],
        load_portal_client(),
        access_token=transfer_tokens['access_token'],
        expires_at=transfer_tokens['expires_at_seconds'])

    transfer = TransferClient(authorizer=authorizer)

    try:
        transfer.endpoint_autoactivate(endpoint_id)
        listing = transfer.operation_ls(endpoint_id, path=endpoint_path)
    except TransferAPIError as err:
        flash('Error [{}]: {}'.format(err.code, err.message))
        return redirect(url_for('transfer'))

    file_list = [e for e in listing if e['type'] == 'file']

    ep = transfer.get_endpoint(endpoint_id)

    https_server = ep['https_server']
    endpoint_uri = https_server + endpoint_path if https_server else None
    webapp_xfer = 'https://www.globus.org/app/transfer?' + \
        urlencode(dict(origin_id=endpoint_id, origin_path=endpoint_path))

    return render_template('browse.html', endpoint_uri=endpoint_uri,
                           target="dataset" if dataset_id else "endpoint",
                           description=(dataset['name'] if dataset_id
                                        else ep['display_name']),
                           file_list=file_list, webapp_xfer=webapp_xfer)


@app.route('/transfer', methods=['GET', 'POST'])
@authenticated
def transfer():
    """
    - Save the submitted form to the session.
    - Send to Globus to select a destination endpoint using the
      Browse Endpoint helper page.
    """
    if request.method == 'GET':
        return render_template('transfer.html', datasets=datasets)

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
    """
    - Take the data returned by the Browse Endpoint helper page
      and make a Globus transfer request.
    - Send the user to the transfer status page with the task id
      from the transfer.
    """
    browse_endpoint_form = request.form

    selected = session['form']['datasets']
    filtered_datasets = [ds for ds in datasets if ds['id'] in selected]

    transfer_tokens = session['tokens']['transfer.api.globus.org']

    authorizer = RefreshTokenAuthorizer(
        transfer_tokens['refresh_token'],
        load_portal_client(),
        access_token=transfer_tokens['access_token'],
        expires_at=transfer_tokens['expires_at_seconds'])

    transfer = TransferClient(authorizer=authorizer)

    source_endpoint_id = app.config['DATASET_ENDPOINT_ID']
    source_endpoint_base = app.config['DATASET_ENDPOINT_BASE']
    destination_endpoint_id = browse_endpoint_form['endpoint_id']
    destination_folder = browse_endpoint_form.get('folder[0]')

    transfer_data = TransferData(transfer_client=transfer,
                                 source_endpoint=source_endpoint_id,
                                 destination_endpoint=destination_endpoint_id,
                                 label=browse_endpoint_form.get('label'))

    for ds in filtered_datasets:
        source_path = source_endpoint_base + ds['path']
        dest_path = browse_endpoint_form['path']

        if destination_folder:
            dest_path += destination_folder + '/'

        dest_path += ds['name'] + '/'

        transfer_data.add_item(source_path=source_path,
                               destination_path=dest_path,
                               recursive=True)

    transfer.endpoint_autoactivate(source_endpoint_id)
    transfer.endpoint_autoactivate(destination_endpoint_id)
    task_id = transfer.submit_transfer(transfer_data)['task_id']

    flash('Transfer request submitted successfully. Task ID: ' + task_id)

    return(redirect(url_for('transfer_status', task_id=task_id)))


@app.route('/status/<task_id>', methods=['GET'])
@authenticated
def transfer_status(task_id):
    """
    Call Globus to get status/details of transfer with
    task_id.

    The target template (tranfer_status.html) expects a Transfer API
    'task' object.

    'task_id' is passed to the route in the URL as 'task_id'.
    """
    transfer_tokens = session['tokens']['transfer.api.globus.org']

    authorizer = RefreshTokenAuthorizer(
        transfer_tokens['refresh_token'],
        load_portal_client(),
        access_token=transfer_tokens['access_token'],
        expires_at=transfer_tokens['expires_at_seconds'])

    transfer = TransferClient(authorizer=authorizer)
    task = transfer.get_task(task_id)

    return render_template('transfer_status.html', task=task)


@app.route('/graph', methods=['GET', 'POST'])
@authenticated
def graph():
    """
    Make a request to the "resource server" (service app) API to
    do the graph processing.
    """
    if request.method == 'GET':
        return render_template('graph.html', datasets=datasets)

    selected_ids = request.form.getlist('dataset')
    selected_year = request.form.get('year')

    if not (selected_ids and selected_year):
        flash("Please select at least one dataset and a year to graph.")
        return redirect(url_for('graph'))

    tokens = get_portal_tokens()
    service_token = tokens.get('GlobusWorld Resource Server')['token']

    service_url = '{}/{}'.format(app.config['SERVICE_URL_BASE'], 'api/doit')
    req_headers = dict(Authorization='Bearer {}'.format(service_token))

    req_data = dict(datasets=selected_ids,
                    year=selected_year,
                    user_identity_id=session.get('primary_identity'),
                    user_identity_name=session.get('primary_username'))

    resp = requests.post(service_url, headers=req_headers, data=req_data,
                         verify=False)

    resp.raise_for_status()

    resp_data = resp.json()
    dest_ep = resp_data.get('dest_ep')
    dest_path = resp_data.get('dest_path')
    dest_name = resp_data.get('dest_name')
    graph_count = resp_data.get('graph_count')

    flash("%d-file SVG upload to %s on %s completed!" %
          (graph_count, dest_path, dest_name))

    return redirect(url_for('browse', endpoint_id=dest_ep,
                            endpoint_path=dest_path.lstrip('/')))


@app.route('/graph/clean-up', methods=['POST'])
@authenticated
def graph_cleanup():
    """Make a request to the service app API to do the graph processing."""
    tokens = get_portal_tokens()
    service_token = tokens.get('GlobusWorld Resource Server')['token']

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
