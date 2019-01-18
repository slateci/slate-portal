from portal.utils import (
    load_portal_client, get_portal_tokens, get_safe_redirect)
from portal.decorators import authenticated
from portal import app, database
import textwrap
import uuid
import sqlite3
import requests
from flask import (abort, flash, redirect, render_template,
                   request, session, url_for)
# Use these four lines on container
import sys
sys.path.insert(0, '/etc/slate/secrets')
f = open("/etc/slate/secrets/slate_api_token.txt", "r")
g = open("slate_api_endpoint.txt", "r")

# Use these two lines below on local
# f = open("/Users/JeremyVan/Documents/Programming/UChicago/Slate/secrets/slate_api_token.txt", "r")
# g = open("/Users/JeremyVan/Documents/Programming/UChicago/Slate/secrets/slate_api_endpoint.txt", "r")
#
slate_api_token = f.read().split()[0]
slate_api_endpoint = g.read().split()[0]


try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


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
            slate_api_endpoint + '/v1alpha2/find_user', params=query)
        user_info = r.json()

        return render_template('cli_access.html', user_info=user_info, slate_api_endpoint=slate_api_endpoint)


@app.route('/vos', methods=['GET', 'POST'])
@authenticated
def list_vos():
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        s = requests.get(
            slate_api_endpoint + '/v1alpha2/users/' + slate_user_id + '/vos', params=token_query)

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
        add_vo = {"apiVersion": 'v1alpha2',
                  'metadata': {'name': name}}

        requests.post(
            slate_api_endpoint + '/v1alpha2/vos', params=token_query, json=add_vo)

        return redirect(url_for('view_vo', name=name))


@app.route('/vos/<name>', methods=['GET', 'POST'])
@authenticated
def view_vo(name):
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        s = requests.get(
            slate_api_endpoint + '/v1alpha2/users/' + slate_user_id + '/vos', params=token_query)
        s_info = s.json()
        vo_list = s_info['items']
        vo_id = None
        for vo in vo_list:
            if vo['metadata']['name'] == name:
                vo_id = vo['metadata']['id']
                vo_name = vo['metadata']['name']

        # List all members
        users = requests.get(
            slate_api_endpoint + '/v1alpha2/users', params=token_query)
        users = users.json()['items']

        # Check if user is Admin of VO
        user = requests.get(
            slate_api_endpoint + '/v1alpha2/users/' + slate_user_id, params=token_query)
        user_admin = user.json()['metadata']['admin']
        admin = False
        if user_admin:
            admin = True

        vo_members = requests.get(
            slate_api_endpoint + '/v1alpha2/vos/' + vo_id + '/members', params=token_query)
        vo_members = vo_members.json()['items']

        # List of vo members by their unique user ID
        vo_member_ids = [members['metadata']['id'] for members in vo_members]
        non_members = [user['metadata']
                       for user in users if user['metadata']['id'] not in vo_member_ids]

        # Remove slate client accounts from user lists
        account_names = ['WebPortal', 'GitHub Webhook Account']
        for non_member in non_members:
            if non_member['name'] in account_names:
                non_members.remove(non_member)

        # Grab/list all Clusters in DB for now
        listclusters = requests.get(
            slate_api_endpoint + '/v1alpha2/clusters', params=token_query)
        list_clusters = listclusters.json()['items']

        # Get clusters owned by VO
        vo_clusters = requests.get(
            slate_api_endpoint + '/v1alpha2/vos/' + vo_id + '/clusters', params=token_query)
        vo_clusters = vo_clusters.json()['items']

        # Get clusters this VO has access to
        vo_access = []
        for clusters in list_clusters:
            cluster_name = clusters['metadata']['name']
            cluster_allowed_vos = requests.get(
                slate_api_endpoint + '/v1alpha2/clusters/' + cluster_name + '/allowed_vos', params=token_query)
            allowed_vos = cluster_allowed_vos.json()['items']
            for vo in allowed_vos:
                if vo['metadata']['name'] == name:
                    vo_access.append(clusters)

        # Get VO Secrets
        secrets_content = []

        secrets_query = {'token': session['slate_token'], 'vo': name}
        secrets = requests.get(
            slate_api_endpoint + '/v1alpha2/secrets', params=secrets_query)
        secrets = secrets.json()['items']

        for secret in secrets:
            secret_id = secret['metadata']['id']
            secret_details = requests.get(
                slate_api_endpoint + '/v1alpha2/secrets/' + secret_id, params=token_query)
            secret_details = secret_details.json()
            secrets_content.append(secret_details)

        return render_template('vos_profile.html', vo_list=vo_list,
                               users=users, name=name, vo_members=vo_members,
                               non_members=non_members, clusters=list_clusters,
                               vo_clusters=vo_clusters, admin=admin,
                               vo_access=vo_access, secrets=secrets, secrets_content=secrets_content)


@app.route('/vos/<name>/add_member', methods=['POST'])
@authenticated
def vo_add_member(name):
    if request.method == 'POST':
        new_user_id = request.form['newuser']
        token_query = {'token': session['slate_token']}
        vo_id = name

        # Add member to VO
        requests.put(
            slate_api_endpoint + '/v1alpha2/users/' + new_user_id + '/vos/' + vo_id, params=token_query)

        return redirect(url_for('view_vo', name=name))


@app.route('/vos/<name>/remove_member', methods=['POST'])
@authenticated
def vo_remove_member(name):
    if request.method == 'POST':
        remove_user_id = request.form['remove_member']
        token_query = {'token': session['slate_token']}
        vo_id = name

        s = requests.delete(
            slate_api_endpoint + '/v1alpha2/users/' + remove_user_id + '/vos/' + vo_id, params=token_query)

        return redirect(url_for('view_vo', name=name))


@app.route('/vos/<project_name>/clusters/<name>', methods=['GET', 'POST', 'DELETE'])
@authenticated
def view_cluster(project_name, name):
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}
        cluster_name = name
        vo_name = project_name
        # list_clusters = []

        list_vos = requests.get(
            slate_api_endpoint + '/v1alpha2/vos', params=token_query)
        list_vos = list_vos.json()['items']
        list_vos = [vo['metadata']['name'] for vo in list_vos]

        cluster_vos = requests.get(
            slate_api_endpoint + '/v1alpha2/clusters/' + cluster_name + '/allowed_vos', params=token_query)
        cluster_vos = cluster_vos.json()['items']

        for vo in cluster_vos:
            if vo['metadata']['name'] in list_vos:
                list_vos.remove(vo['metadata']['name'])

        non_access_vos = requests.get(
            slate_api_endpoint + '/v1alpha2/clusters/' + cluster_name + '/allowed_vos', params=token_query)
        non_access_vos = non_access_vos.json()['items']

        applications = requests.get(
            slate_api_endpoint + '/v1alpha2/clusters/' + cluster_name + '/allowed_vos/' + vo_name + '/applications', params=token_query)
        applications = applications.json()['items']

        return render_template('cluster_profile.html', cluster_vos=cluster_vos,
                               project_name=project_name, name=name,
                               applications=applications, non_access_vos=list_vos)

    elif request.method == 'POST':
        """Members of VO may give other VOs access to this cluster"""

        new_vo = request.form['new_vo']
        token_query = {'token': session['slate_token']}
        cluster_name = name

        # Add VO to cluster whitelist
        add_vo = requests.put(
            slate_api_endpoint + '/v1alpha2/clusters/' + cluster_name + '/allowed_vos/' + new_vo, params=token_query)

        return redirect(url_for('view_cluster', name=name, project_name=project_name))

    elif request.method == 'DELETE':
        """Members of VO may give other VOs access to this cluster"""

        remove_vo = request.form['remove_vo']
        token_query = {'token': session['slate_token']}

        # print(remove_vo)
        # delete VO from cluster whitelist
        requests.delete(
            slate_api_endpoint + '/v1alpha2/clusters/' + name + '/allowed_vos/' + remove_vo, params=token_query)

        return redirect(url_for('view_vo', name=project_name))


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
            slate_api_endpoint + '/v1alpha2/users?token=' + user_id)
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
            slate_api_endpoint + '/v1alpha2/find_user', params=query)

        if profile:
            profile = profile.json()['metadata']
            session['slate_token'] = profile['access_token']
            session['slate_id'] = profile['id']
        else:
            flash(
                'Please complete any missing profile fields and press Save.')

        if request.args.get('next'):
            session['next'] = get_safe_redirect()

        return render_template('profile.html', slate_api_token=slate_api_token, profile=profile)
    elif request.method == 'POST':
        name = session['name'] = request.form['name']
        email = session['email'] = request.form['email']
        # Chris should maybe add institution into user info within DB?
        # institution = session['institution'] = request.form['institution']
        globus_id = session['primary_identity']
        admin = False
        # Schema and query for adding users to Slate DB
        add_user = {"apiVersion": 'v1alpha2',
                    'metadata': {'globusID': globus_id,
                                 'name': name, 'email': email, 'admin': admin}}
        query = {'token': slate_api_token}

        requests.post(
            slate_api_endpoint + '/v1alpha2/users', params=query, json=add_user)

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
        flash("You could not be logged into the portal: "
              + request.args.get('error_description', request.args['error']))
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
            slate_api_endpoint + '/v1alpha2/find_user', params=query)

        if profile:
            # name, email, institution = profile

            # session['name'] = name
            # session['email'] = email
            # session['institution'] = institution
            globus_id = session['primary_identity']
            query = {'token': slate_api_token,
                     'globus_id': globus_id}

            profile = requests.get(
                slate_api_endpoint + '/v1alpha2/find_user', params=query)
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
            slate_api_endpoint + '/v1alpha2/find_user', params=query)
        user_info = r.json()
        slate_user_id = user_info['metadata']['id']
        # vo_url = 'https://api-dev.slateci.io:18080/v1alpha2/users/' + slate_user_id + '/vos'

        token_query = {'token': slate_api_token}
        s = requests.get(
            slate_api_endpoint + '/v1alpha2/users/' + slate_user_id + '/vos', params=token_query)

        s_info = s.json()
        vo_list = s_info['items']

        return render_template('register.html', user_info=user_info,
                               vo_list=vo_list, slate_user_id=slate_user_id)
    elif request.method == 'POST':
        name = request.form['name']
        vo = request.form['vo']
        return render_template('clusters.html', name=name, vo=vo, slate_api_endpoint=slate_api_endpoint)


@app.route('/clusters', methods=['GET'])
@authenticated
def list_clusters():
    """
    - List Clusters Registered on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        slate_clusters = requests.get(
            slate_api_endpoint + '/v1alpha2/clusters', params=token_query)
        slate_clusters = slate_clusters.json()['items']

        return render_template('clusters.html', slate_clusters=slate_clusters)


@app.route('/applications', methods=['GET'])
@authenticated
def list_applications():
    """
    - List Known Applications on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        applications = requests.get(
            slate_api_endpoint + '/v1alpha2/apps', params=token_query)
        applications = applications.json()['items']
        return render_template('applications.html', applications=applications)


@app.route('/applications/<name>', methods=['GET'])
@authenticated
def view_application(name):
    """
    - View Known Applications Detail Page on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        app_config = requests.get(
            slate_api_endpoint + '/v1alpha2/apps/' + name, params=token_query)
        app_config = app_config.json()
        return render_template('applications_profile.html', name=name, app_config=app_config)


@app.route('/applications/<name>/new', methods=['GET', 'POST'])
@authenticated
def create_application(name):
    """ View form to install new application """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        # Get configuration of app <name> selected
        app_config = requests.get(
            slate_api_endpoint + '/v1alpha2/apps/' + name, params=token_query)
        app_config = app_config.json()

        # Get VOs that user belongs to
        vos = requests.get(
            slate_api_endpoint + '/v1alpha2/users/' + slate_user_id + '/vos', params=token_query)
        vos = vos.json()
        vos = vos['items']

        vo_clusters_dict = {}
        cluster_list = []

        for vo in vos:
            vo_clusters = requests.get(
                slate_api_endpoint + '/v1alpha2/vos/' + vo['metadata']['id'] + '/clusters', params=token_query)
            vo_clusters = vo_clusters.json()['items']

            # cluster_list = []
            for cluster in vo_clusters:
                if cluster['metadata']['name']:
                    cluster_list.append(cluster['metadata']['name'])

            # vo_name = vo['metadata']['name']
            # vo_clusters_dict[vo_name] = cluster_list


        return render_template('applications_create.html', name=name,
                                app_config=app_config, vos=vos,
                                vo_clusters_dict=vo_clusters_dict,
                                cluster_list=cluster_list)

    elif request.method == 'POST':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        vo = request.form["vo"]
        cluster = request.form["cluster"]
        configuration = request.form["config"]

        install_app = {"apiVersion": 'v1alpha2', "vo": vo, "cluster": cluster, "configuration": configuration}

        # Post query to install application config
        app_install = requests.post(
            slate_api_endpoint + '/v1alpha2/apps/' + name, params=token_query, json=install_app)

        if app_install.status_code == 200:
            flash('You have successfully installed an application instance', 'success')
        else:
            flash('Failed to install application instance', 'warning')

        return redirect(url_for('view_application', name=name))


@app.route('/instances', methods=['GET'])
@authenticated
def list_instances():
    """
    - List deployed application instances on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        instances = requests.get(
            slate_api_endpoint + '/v1alpha2/instances', params=token_query)
        instances = instances.json()['items']
        return render_template('instances.html', instances=instances)


@app.route('/instances/<name>', methods=['GET'])
@authenticated
def view_instance(name):
    """
    - View detailed instance information on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        instance_detail = requests.get(
            slate_api_endpoint + '/v1alpha2/instances/' + name + '?token=' + session['slate_token'] + '&detailed')
        instance_detail = instance_detail.json()
        instance_status = "Not Error"

        instance_log = requests.get(
            slate_api_endpoint + '/v1alpha2/instances/' + name + '/logs', params=token_query)
        instance_log = instance_log.json()

        if instance_detail['kind'] == 'Error':
            instance_status = "BIG ERROR"

        return render_template('instance_profile.html', name=name,
                                instance_detail=instance_detail,
                                instance_status=instance_status,
                                instance_log=instance_log)
