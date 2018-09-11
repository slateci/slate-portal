import sys
sys.path.insert(0, '/etc/slate/secrets')
# f = open("/Users/JeremyVan/Documents/Programming/UChicago/Slate/secrets/slate_api_token.txt", "r")
f = open("/etc/slate/secrets/slate_api_token.txt", "r")
slate_api_token = f.read().split()[0]

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
        query = {'token': slate_api_token,
                 'globus_id': globus_id}

        r = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/find_user', params=query)
        user_info = r.json()

        return render_template('cli_access.html', user_info=user_info)


@app.route('/vos', methods=['GET', 'POST'])
@authenticated
def list_vos():
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        s = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/users/' + slate_user_id + '/vos', params=token_query)

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
            'https://api-dev.slateci.io:18081/v1alpha1/vos', params=token_query, json=add_vo)

        return redirect(url_for('view_vo', name=name))


@app.route('/vos/<name>', methods=['GET', 'POST'])
@authenticated
def view_vo(name):
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        s = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/users/' + slate_user_id + '/vos', params=token_query)
        s_info = s.json()
        vo_list = s_info['items']
        vo_id = None
        for vo in vo_list:
            if vo['metadata']['name'] == name:
                vo_id = vo['metadata']['id']

        users = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/users', params=token_query)
        users = users.json()['items']

        vo_members = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/vos/' + vo_id + '/members', params=token_query)
        vo_members = vo_members.json()['items']
        # print(type(users))
        # print(type(vo_members))

        vo_nonmembers = [u for u in users if u['metadata']['id']
                         not in set([u['metadata']['id'] for u in vo_members])]

        return render_template('vos_profile.html', vo_list=vo_list, users=vo_nonmembers, name=name, vo_members=vo_members)


@app.route('/vos/<name>/add_member', methods=['POST'])
@authenticated
def vo_add_member(name):
    if request.method == 'POST':
        new_user_id = request.form['newuser']
        token_query = {'token': session['slate_token']}
        vo_id = name

        s = requests.put(
            'https://api-dev.slateci.io:18081/v1alpha1/users/' + new_user_id + '/vos/' + vo_id, params=token_query)

        return redirect(url_for('view_vo', name=name))


@app.route('/vos/<name>/remove_member', methods=['POST'])
@authenticated
def vo_remove_member(name):
    if request.method == 'POST':
        remove_user_id = request.form['remove_member']
        token_query = {'token': session['slate_token']}
        vo_id = name

        s = requests.delete(
            'https://api-dev.slateci.io:18081/v1alpha1/users/' + remove_user_id + '/vos/' + vo_id, params=token_query)

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
            'https://api-dev.slateci.io:18081/v1alpha1/users?token=' + user_id)
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
        query = {'token': slate_api_token,
                 'globus_id': globus_id}

        profile = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/find_user', params=query)

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

        return render_template('profile.html', slate_api_token=slate_api_token)
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
        query = {'token': slate_api_token}

        requests.post(
            'https://api-dev.slateci.io:18081/v1alpha1/users', params=query, json=add_user)

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
        query = {'token': slate_api_token,
                 'globus_id': globus_id}

        profile = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/find_user', params=query)

        if profile:
            # name, email, institution = profile

            # session['name'] = name
            # session['email'] = email
            # session['institution'] = institution
            globus_id = session['primary_identity']
            query = {'token': slate_api_token,
                     'globus_id': globus_id}

            profile = requests.get(
                'https://api-dev.slateci.io:18081/v1alpha1/find_user', params=query)
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
        query = {'token': slate_api_token,
                 'globus_id': globus_id}

        r = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/find_user', params=query)
        user_info = r.json()
        slate_user_id = user_info['metadata']['id']
        # vo_url = 'https://api-dev.slateci.io:18080/v1alpha1/users/' + slate_user_id + '/vos'

        token_query = {'token': slate_api_token}
        s = requests.get(
            'https://api-dev.slateci.io:18081/v1alpha1/users/' + slate_user_id + '/vos', params=token_query)

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
