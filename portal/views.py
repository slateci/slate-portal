from portal.utils import (
    load_portal_client, get_portal_tokens, get_safe_redirect)
from portal.decorators import authenticated
from portal import app, database
import textwrap
import uuid
import sqlite3
import requests
from flask import (abort, flash, redirect, render_template,
                   request, session, url_for, jsonify)
# Use these four lines on container
import sys
sys.path.insert(0, '/etc/slate/secrets')
f = open("/etc/slate/secrets/slate_api_token.txt", "r")
g = open("slate_api_endpoint.txt", "r")

# Use these two lines below on local
# f = open("/Users/JeremyVan/Documents/Programming/UChicago/Slate/secrets/slate_api_token.txt", "r")
# g = open("/Users/JeremyVan/Documents/Programming/UChicago/Slate/secrets/slate_api_endpoint.txt", "r")

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
            slate_api_endpoint + '/v1alpha3/find_user', params=query)
        user_info = r.json()

        return render_template('cli_access.html', user_info=user_info, slate_api_endpoint=slate_api_endpoint)


@app.route('/groups', methods=['GET', 'POST'])
@authenticated
def list_groups():
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=token_query)

        s_info = s.json()
        group_list = s_info['items']

        return render_template('groups.html', group_list=group_list)


@app.route('/groups/new', methods=['GET', 'POST'])
@authenticated
def create_group():
    if request.method == 'GET':
        sciences = ["Resource Provider", "Astronomy", "Astrophysics",
                            "Biology", "Biochemistry", "Bioinformatics",
                            "Biomedical research", "Biophysics", "Botany",
                            "Cellular Biology", "Ecology", "Evolutionary Biology",
                            "Microbiology", "Molecular Biology", "Neuroscience",
                            "Physiology", "Structural Biology", "Zoology",
                            "Chemistry", "Biochemistry", "Physical Chemistry",
                            "Earth Sciences", "Economics", "Education",
                            "Educational Psychology", "Engineering",
                            "Electronic Engineering", "Nanoelectronics",
                            "Mathematics & Computer Science", "Computer Science",
                            "Geographic Information Science", "Information Theory",
                            "Mathematics", "Medicine", "Medical Imaging",
                            "Neuroscience", "Physiology", "Logic", "Statistics",
                            "Physics", "Accelerator Physics", "Astro-particle Physics",
                            "Astrophysics", "Biophysics",
                            "Computational Condensed Matter Physics",
                            "Gravitational Physics", "High Energy Physics",
                            "Neutrino Physics", "Nuclear Physics", "Physical Chemistry",
                            "Psychology", "Child Psychology", "Educational Psychology",
                            "Materials Science", "Multidisciplinary",
                            "Network Science", "Technology"]
        return render_template('groups_create.html', sciences=sciences)

    elif request.method == 'POST':
        """Route method to handle query to create a new Group"""

        name = request.form['name']
        token_query = {'token': session['slate_token']}
        add_group = {"apiVersion": 'v1alpha3',
                  'metadata': {'name': name}}

        requests.post(
            slate_api_endpoint + '/v1alpha3/groups', params=token_query, json=add_group)

        return redirect(url_for('view_group', name=name))


@app.route('/groups/<name>', methods=['GET', 'POST'])
@authenticated
def view_group(name):
    slate_user_id = session['slate_id']
    token_query = {'token': session['slate_token']}

    if request.method == 'GET':
        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=token_query)
        s_info = s.json()
        group_list = s_info['items']
        group_id = None
        for group in group_list:
            if group['metadata']['name'] == name:
                group_id = group['metadata']['id']
                group_name = group['metadata']['name']

        # List all members
        users = requests.get(
            slate_api_endpoint + '/v1alpha3/users', params=token_query)
        users = users.json()['items']

        # Check if user is Admin of Group
        user = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=token_query)
        user_admin = user.json()['metadata']['admin']
        admin = False
        if user_admin:
            admin = True

        group_members = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + group_id + '/members', params=token_query)
        group_members = group_members.json()['items']

        # List of group members by their unique user ID
        group_member_ids = [members['metadata']['id'] for members in group_members]
        non_members = [user['metadata']
                       for user in users if user['metadata']['id'] not in group_member_ids]

        # Remove slate client accounts from user lists
        account_names = ['WebPortal', 'GitHub Webhook Account']
        for non_member in non_members:
            if non_member['name'] in account_names:
                non_members.remove(non_member)

        # Grab/list all Clusters in DB for now
        listclusters = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters', params=token_query)
        list_clusters = listclusters.json()['items']

        # Get clusters owned by group
        group_clusters = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + group_id + '/clusters', params=token_query)
        group_clusters = group_clusters.json()['items']

        # Get clusters this group has access to
        group_access = []
        for clusters in list_clusters:
            cluster_name = clusters['metadata']['name']
            cluster_allowed_groups = requests.get(
                slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups', params=token_query)
            allowed_groups = cluster_allowed_groups.json()['items']
            for group in allowed_groups:
                if group['metadata']['name'] == name:
                    group_access.append(clusters)

        # Get Group Secrets
        secrets_content = []

        secrets_query = {'token': session['slate_token'], 'group': name}
        secrets = requests.get(
            slate_api_endpoint + '/v1alpha3/secrets', params=secrets_query)
        secrets = secrets.json()['items']

        for secret in secrets:
            secret_id = secret['metadata']['id']
            secret_details = requests.get(
                slate_api_endpoint + '/v1alpha3/secrets/' + secret_id, params=token_query)
            secret_details = secret_details.json()
            secrets_content.append(secret_details)

        return render_template('groups_profile.html', group_list=group_list,
                               users=users, name=name, group_members=group_members,
                               non_members=non_members, clusters=list_clusters,
                               group_clusters=group_clusters, admin=admin,
                               group_access=group_access, secrets=secrets, secrets_content=secrets_content)
    elif request.method == 'POST':
        secret_id = request.form['secret_id']
        secrets_query = {'token': session['slate_token'], 'group': name}
        requests.delete(slate_api_endpoint + '/v1alpha3/secrets/' + secret_id, params=secrets_query)

        return redirect(url_for('view_group', name=name))


@app.route('/groups/<name>/new_secret', methods=['GET', 'POST'])
@authenticated
def create_secret(name):
    slate_user_id = session['slate_id']
    token_query = {'token': session['slate_token']}
    if request.method == 'GET':
        group_id = name
        # Get clusters owned by group
        clusters = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + group_id + '/clusters', params=token_query)
        clusters = clusters.json()['items']

        return render_template('secrets_create.html', name=name, clusters=clusters)
    elif request.method == 'POST':
        # Initialize empty contents dict
        contents = {}

        cluster = request.form['cluster']
        secret_name = request.form['secret_name']
        key_name = request.form['key_name']
        key_contents = request.form['key_contents']

        # Add secret contents key-value to dict
        contents[key_name] = key_contents

        add_secret = {"apiVersion": 'v1alpha3',
                    'metadata': {'name': secret_name, 'group': name, 'cluster': cluster},
                    'contents': contents}

        # Add secret to Group
        requests.post(
            slate_api_endpoint + '/v1alpha3/secrets', params=token_query, json=add_secret)

        return redirect(url_for('view_group', name=name))


@app.route('/groups/<name>/add_member', methods=['POST'])
@authenticated
def group_add_member(name):
    if request.method == 'POST':
        new_user_id = request.form['newuser']
        token_query = {'token': session['slate_token']}
        group_id = name

        # Add member to Group
        requests.put(
            slate_api_endpoint + '/v1alpha3/users/' + new_user_id + '/groups/' + group_id, params=token_query)

        return redirect(url_for('view_group', name=name))


@app.route('/groups/<name>/remove_member', methods=['POST'])
@authenticated
def group_remove_member(name):
    if request.method == 'POST':
        remove_user_id = request.form['remove_member']
        token_query = {'token': session['slate_token']}
        group_id = name

        s = requests.delete(
            slate_api_endpoint + '/v1alpha3/users/' + remove_user_id + '/groups/' + group_id, params=token_query)

        return redirect(url_for('view_group', name=name))


@app.route('/groups/<project_name>/clusters/<name>', methods=['GET', 'POST', 'DELETE'])
@authenticated
def view_cluster(project_name, name):
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}
        cluster_name = name
        group_name = project_name
        # list_clusters = []

        list_groups = requests.get(
            slate_api_endpoint + '/v1alpha3/groups', params=token_query)
        list_groups = list_groups.json()['items']
        list_groups = [group['metadata']['name'] for group in list_groups]

        cluster_groups = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups', params=token_query)
        cluster_groups = cluster_groups.json()['items']

        for group in cluster_groups:
            if group['metadata']['name'] in list_groups:
                list_groups.remove(group['metadata']['name'])

        non_access_groups = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups', params=token_query)
        non_access_groups = non_access_groups.json()['items']

        applications = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups/' + group_name + '/applications', params=token_query)
        applications = applications.json()['items']

        return render_template('cluster_profile.html', cluster_groups=cluster_groups,
                               project_name=project_name, name=name,
                               applications=applications, non_access_groups=list_groups)

    elif request.method == 'POST':
        """Members of group may give other groups access to this cluster"""

        new_group = request.form['new_group']
        token_query = {'token': session['slate_token']}
        cluster_name = name

        # Add group to cluster whitelist
        add_group = requests.put(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups/' + new_group, params=token_query)

        return redirect(url_for('view_cluster', name=name, project_name=project_name))

    elif request.method == 'DELETE':
        """Members of group may give other groups access to this cluster"""

        remove_group = request.form['remove_group']
        token_query = {'token': session['slate_token']}

        # print(remove_group)
        # delete group from cluster whitelist
        requests.delete(
            slate_api_endpoint + '/v1alpha3/clusters/' + name + '/allowed_groups/' + remove_group, params=token_query)

        return redirect(url_for('view_group', name=project_name))


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
            slate_api_endpoint + '/v1alpha3/users?token=' + user_id)
        response = requests.get(cat_url)
        user_info = response.json()

        return render_template('testing_user.html', user_info=user_info)


@app.route('/profile', methods=['GET', 'POST'])
@authenticated
def profile():
    """User profile information. Assocated with a Globus Auth identity."""
    if request.method == 'GET':
        identity_id = session.get('primary_identity')
        institution = session.get('institution')
        globus_id = identity_id
        query = {'token': slate_api_token,
                 'globus_id': globus_id}

        profile = requests.get(
            slate_api_endpoint + '/v1alpha3/find_user', params=query)

        if profile:
            profile = requests.get(slate_api_endpoint + '/v1alpha3/users/' + session['slate_id'], params=query)
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
        phone = session['phone'] = request.form['phone-number']
        # Chris should maybe add institution into user info within DB?
        institution = session['institution'] = request.form['institution']
        globus_id = session['primary_identity']
        admin = False
        # Schema and query for adding users to Slate DB
        add_user = {"apiVersion": 'v1alpha3',
                    'metadata': {'name': name, 'email': email,
                                 'phone': phone, 'institution': institution}}
        query = {'token': slate_api_token}

        r = requests.put(slate_api_endpoint + '/v1alpha3/users/' + session['slate_id'], params=query, json=add_user)
        print(r)
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
        print("Session: ", session)
        session.update(
            tokens=tokens.by_resource_server,
            is_authenticated=True,
            name=id_token.get('name', ''),
            email=id_token.get('email', ''),
            institution=id_token.get('institution', ''),
            primary_username=id_token.get('preferred_username'),
            primary_identity=id_token.get('sub'),
            identity_provider=id_token.get('identity_provider')
        )
        # profile = database.load_profile(session['primary_identity'])
        # Need to query a request to view all users in Slate DB, then iterate
        # to see if profile exists by matching globus_id ideally. Get rid of
        # database.load_profile line above this once done
        globus_id = session['primary_identity']
        query = {'token': slate_api_token,
                 'globus_id': globus_id}

        profile = requests.get(
            slate_api_endpoint + '/v1alpha3/find_user', params=query)
        # print("GLOBUS ID:", globus_id)
        # print("QUERY:", query)
        # print("Profile:", profile)

        if profile:
            # name, email, institution = profile

            # session['name'] = name
            # session['email'] = email
            # session['institution'] = institution
            print("Institution:", session['institution'])
            globus_id = session['primary_identity']
            query = {'token': slate_api_token,
                     'globus_id': globus_id}

            profile = requests.get(
                slate_api_endpoint + '/v1alpha3/find_user', params=query)
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
            slate_api_endpoint + '/v1alpha3/find_user', params=query)
        user_info = r.json()
        slate_user_id = user_info['metadata']['id']
        # group_url = 'https://api-dev.slateci.io:18080/v1alpha3/users/' + slate_user_id + '/groups'

        token_query = {'token': slate_api_token}
        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=token_query)

        s_info = s.json()
        group_list = s_info['items']

        return render_template('register.html', user_info=user_info,
                               group_list=group_list, slate_user_id=slate_user_id)
    elif request.method == 'POST':
        name = request.form['name']
        group = request.form['group']
        return render_template('clusters.html', name=name, group=group, slate_api_endpoint=slate_api_endpoint)


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
            slate_api_endpoint + '/v1alpha3/clusters', params=token_query)
        slate_clusters = slate_clusters.json()['items']

        return render_template('clusters.html', slate_clusters=slate_clusters)


@app.route('/clusters/new', methods=['GET'])
@authenticated
def create_cluster():
    """
    - Create Cluster on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        # Get groups to which the user belongs
        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=token_query)

        s_info = s.json()
        group_list = s_info['items']

        return render_template('clusters_create.html', group_list=group_list)



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
            slate_api_endpoint + '/v1alpha3/apps', params=token_query)
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
            slate_api_endpoint + '/v1alpha3/apps/' + name, params=token_query)
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
            slate_api_endpoint + '/v1alpha3/apps/' + name, params=token_query)
        app_config = app_config.json()

        # Get groups that user belongs to
        groups = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=token_query)
        groups = groups.json()
        groups = groups['items']

        group_clusters_dict = {}
        cluster_list = []

        for group in groups:
            group_clusters = requests.get(
                slate_api_endpoint + '/v1alpha3/groups/' + group['metadata']['id'] + '/clusters', params=token_query)
            group_clusters = group_clusters.json()['items']

            # cluster_list = []
            for cluster in group_clusters:
                if cluster['metadata']['name']:
                    cluster_list.append(cluster['metadata']['name'])

            # group_name = group['metadata']['name']
            # group_clusters_dict[group_name] = cluster_list

        # testData = requests.get("https://api-dev.slateci.io:18080/v1alpha3/groups/slate-dev/clusters", params=token_query)
        # testData = testData.json()['items']


        return render_template('applications_create.html', name=name,
                                app_config=app_config, groups=groups,
                                group_clusters_dict=group_clusters_dict,
                                cluster_list=cluster_list)

    elif request.method == 'POST':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        group = request.form["group"]
        cluster = request.form["cluster"]
        configuration = request.form["config"]

        install_app = {"apiVersion": 'v1alpha3', "group": group, "cluster": cluster, "configuration": configuration}

        # Post query to install application config
        app_install = requests.post(
            slate_api_endpoint + '/v1alpha3/apps/' + name, params=token_query, json=install_app)

        if app_install.status_code == 200:
            flash('You have successfully installed an application instance', 'success')
        else:
            flash('Failed to install application instance', 'warning')

        return redirect(url_for('view_application', name=name))

@app.route('/_get_data', methods=["GET", "POST"])
def _get_data():
    myList = ['elements1', 'elements2', 'elements3']

    return jsonify({'data': render_template('response.html', mylist=myList)})

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
            slate_api_endpoint + '/v1alpha3/instances', params=token_query)
        instances = instances.json()['items']
        # Get groups to which the user belongs
        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=token_query)

        s_info = s.json()
        group_list = s_info['items']
        user_groups = []

        for groups in group_list:
            user_groups.append(groups['metadata']['name'].encode('utf-8'))

        return render_template('instances.html', instances=instances, user_groups=user_groups)


@app.route('/instances/<name>', methods=['GET'])
@authenticated
def view_instance(name):
    """
    - View detailed instance information on SLATE
    """
    slate_user_id = session['slate_id']
    token_query = {'token': session['slate_token']}
    if request.method == 'GET':

        instance_detail = requests.get(
            slate_api_endpoint + '/v1alpha3/instances/' + name + '?token=' + session['slate_token'] + '&detailed')
        instance_detail = instance_detail.json()
        instance_status = "Not Error"

        instance_log = requests.get(
            slate_api_endpoint + '/v1alpha3/instances/' + name + '/logs', params=token_query)
        instance_log = instance_log.json()

        if instance_detail['kind'] == 'Error':
            instance_status = "BIG ERROR"

        return render_template('instance_profile.html', name=name,
                                instance_detail=instance_detail,
                                instance_status=instance_status,
                                instance_log=instance_log)


@app.route('/instances/<name>/delete_instance', methods=['GET'])
@authenticated
def delete_instance(name):
    slate_user_id = session['slate_id']
    token_query = {'token': session['slate_token']}

    requests.delete(slate_api_endpoint + '/v1alpha3/instances/' + name, params=token_query)

    return redirect(url_for('list_instances'))

@app.route('/provisioning', methods=['GET'])
@authenticated
def list_provisionings():
    """
     List cluster node provisionings on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        # instances = requests.get(
        #     slate_api_endpoint + '/v1alpha3/instances', params=token_query)
        # instances = instances.json()['items']
        return render_template('provisionings.html')


@app.route('/provisioning/new', methods=['GET'])
@authenticated
def create_provisionings():
    """
     List cluster node provisionings on SLATE
    """
    if request.method == 'GET':
        slate_user_id = session['slate_id']
        token_query = {'token': session['slate_token']}

        # https://api-dev.slateci.io:18080/v1alpha3/clusters?token=9b3bff41-dc76-405b-9a84-5cbea43afaf2

        clusters = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters', params=token_query)
        clusters = clusters.json()['items']
        return render_template('provisionings_create.html', clusters=clusters)
