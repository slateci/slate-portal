from portal.utils import (
    load_portal_client, get_safe_redirect)
from portal.decorators import authenticated, group_authenticated
from portal import app, slate_api_token, slate_api_endpoint, minislate_user
from datetime import datetime
import json
import requests
import time
import base64
from flask import (flash, redirect, render_template,
                   request, session, url_for, jsonify)
from portal.connect_api import (list_applications_request,
                        list_incubator_applications_request,
                        list_instances_request,
                        list_public_groups_request,
                        list_user_groups,
                        list_users_instances_request,
                        list_clusters_request, coordsConversion,
                        get_user_access_token, get_user_id,
                        get_user_info, delete_user)
import sys
import os
sys.path.insert(0, '/etc/slate/secrets')
# Set sys path and import view routes
sys.path.insert(1, 'portal/views')
import portal.views
import views_applications
import views_clusters
import views_instances
# import views_webhooks
import views_error_handling
import views_groups

try:
    # Read endpoint and token from VM
    j = open("/etc/slate/secrets/mailgun_api_token.txt", "r")
    mailgun_api_token = j.read().split()[0]
except:
    # Do not want mailgun spam on local/mini-slate
    mailgun_api_token = None

try:
    # Python 2
    from urllib.parse import urlparse, urlencode, parse_qs
    # print("Using Python 2")
except ImportError:
    # Python 3
    from urlparse import urlparse, parse_qs
    from urllib import urlencode
    # print("Using Python 3")


@app.route('/applications_ajax', methods=['GET'])
def applications_ajax():
    applications = list_applications_request()
    return jsonify(applications)


@app.route('/apps_readme_ajax/<name>', methods=['GET'])
def apps_readme_ajax(name):
    apps_readme = apps_readme_request(name)
    return jsonify(apps_readme)


def apps_readme_request(name):
    try:
        access_token = get_user_access_token(session)
        query = {'token': access_token}
    except:
        query = {'token': slate_api_token}

    apps_readme = requests.get(
        slate_api_endpoint + '/v1alpha3/apps/' + name + '/info', params=query)
    apps_readme = apps_readme.json()
    # app_config_query = '/v1alpha3/apps/' + name + '?token=' + query['token']
    return apps_readme


@app.route('/apps_config_ajax/<name>', methods=['GET'])
def apps_config_ajax(name):
    apps_config = apps_config_request(name)
    return jsonify(apps_config)


def apps_config_request(name):
    try:
        access_token = get_user_access_token(session)
        query = {'token': access_token}
    except:
        query = {'token': slate_api_token}

    apps_config = requests.get(
        slate_api_endpoint + '/v1alpha3/apps/' + name, params=query)
    apps_config = apps_config.json()

    return apps_config


@app.route('/apps_incubator_readme_ajax/<name>', methods=['GET'])
def apps_incubator_readme_ajax(name):
    apps_readme = apps_incubator_readme_request(name)
    return jsonify(apps_readme)


def apps_incubator_readme_request(name):
    try:
        access_token = get_user_access_token(session)
        query = {'token': access_token, 'dev': 'true'}
    except:
        query = {'token': slate_api_token, 'dev': 'true'}

    apps_readme = requests.get(
        slate_api_endpoint + '/v1alpha3/apps/' + name + '/info', params=query)
    apps_readme = apps_readme.json()

    return apps_readme


@app.route('/apps_incubator_config_ajax/<name>', methods=['GET'])
def apps_incubator_config_ajax(name):
    apps_config = apps_incubator_config_request(name)
    return jsonify(apps_config)


def apps_incubator_config_request(name):
    try:
        access_token = get_user_access_token(session)
        query = {'token': access_token, 'dev': 'true'}
    except:
        query = {'token': slate_api_token, 'dev': 'true'}

    apps_config = requests.get(
        slate_api_endpoint + '/v1alpha3/apps/' + name, params=query)
    apps_config = apps_config.json()

    return apps_config


@app.route('/', methods=['GET'])
def home():
    """Home page - play with it if you must!"""
    return redirect(url_for('dashboard'))


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
    next_url = get_safe_redirect()
    return redirect(url_for('authcallback', next=next_url))


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
    ga_logout_url.append('&redirect_name=Slate Portal')

    # Redirect the user to the Globus Auth logout page
    return redirect(''.join(ga_logout_url))


@app.route('/slate_portal', methods=['GET'])
def dashboard():
    """Send the user to dashboard"""
    try:
        # Check location of slate_portal_user file on minislate
        f = open("/slate_portal_user", "r")
        slate_portal_user = f.read().split()

        session['user_id'] = slate_portal_user[0]
        session['name'] = slate_portal_user[1]
        session['email'] = slate_portal_user[2]
        session['phone'] = slate_portal_user[3]
        session['institution'] = slate_portal_user[4]
        session['access_token'] = slate_portal_user[5]
        session['primary_identity'] = slate_portal_user[5]
        # session['slate_token'] = slate_portal_user[5]
        session['is_authenticated'] = True
        session['slate_portal_user'] = True

    except:
        session['slate_portal_user'] = False

    if request.method == 'GET':
        print("Session from dashboard: {}".format(session))
        if session["slate_portal_user"]:
            # single-user mode
            clusters = ["my-cluster"]
        else:
            clusters = ["uutah-prod", "uchicago-prod", "umich-prod"]

        with open('portal/static/news.md', "r") as file:
            news = file.read()
        # This json conversion is for JS to read on the frontend
        clusters_list = json.dumps(clusters)

        return render_template('dashboard.html', clusters=clusters,
                                news=news, clusters_list=clusters_list)


@app.route('/admin', methods=['GET', 'POST'])
@authenticated
def view_admin():
    if request.method == 'GET':
        access_token = get_user_access_token(session)
        query = {'token': access_token}

        users = requests.get(
            slate_api_endpoint + '/v1alpha3/users', params=query)
        users = users.json()['items']

        return render_template('admin.html', users=users)


@app.route('/cli', methods=['GET', 'POST'])
@authenticated
def cli_access():
    if request.method == 'GET':
        # access_token = session['tokens']['auth.globus.org']['access_token']
        # access_token = textwrap.fill(access_token, 60)
        try:
            # Schema and query for getting user info and access token from Slate DB
            globus_id = session['primary_identity']
            query = {'token': slate_api_token,
                     'globus_id': globus_id}

            r = requests.get(
                slate_api_endpoint + '/v1alpha3/find_user', params=query)
            user_info = r.json()
            access_token = user_info['metadata']['access_token']
        except:
            access_token = get_user_access_token(session)

        return render_template('cli_access.html', access_token=access_token, slate_api_endpoint=slate_api_endpoint)


@app.route('/mailgun/<group_name>/<user_name>/<user_email>', methods=['GET', 'POST'])
@authenticated
def mailgun(group_name, user_name, user_email):
    admin_email = request.form['admin_email']

    r = requests.post("https://api.mailgun.net/v3/slateci.io/messages",
                auth=('api', mailgun_api_token),
                data={
                    "from": "SLATE <donotreply@slateci.io>",
                    "to": [admin_email],
                    "cc": "{} <{}>".format(user_name, user_email),
                    "subject": "Request to Join Group: {}".format(group_name),
                    "text": "Hello! User, {}, is CC'd on this email {}, and has requested to join your group, {} on SLATE. You may choose to add them from your groups detailed page through the SLATE portal.".format(user_name, user_email,group_name)
                })
    if r.status_code == requests.codes.ok:
        flash("Successfully requested group membership", 'success')
        return redirect(url_for('view_public_group', name=group_name))
    else:
        flash("Unable to send request", 'warning')
        return redirect(url_for('view_public_group', name=group_name))


@app.route('/secret-select-group', methods=['GET', 'POST'])
@authenticated
def secret_select_group():
    if request.method == 'GET':
        access_token, slate_user_id = get_user_info(session)
        query = {'token': access_token}

        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=query)

        s_info = s.json()
        group_list = s_info['items']

        return render_template('secret-select-group.html', group_list=group_list, minislate_user=minislate_user)


@app.route('/groups/new', methods=['GET', 'POST'])
@authenticated
def create_group():
    access_token, slate_user_id = get_user_info(session)
    query = {'token': access_token}
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
        user = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=query)
        user = user.json()

        return render_template('groups_create.html', sciences=sciences, user=user, minislate_user=minislate_user)

    elif request.method == 'POST':
        """Route method to handle query to create a new Group"""

        name = request.form['name']
        # Sanitize white space in name
        name = name.replace(" ", "-")
        # Lower case group name
        name = name.lower()
        phone = request.form['phone-number']
        email = request.form['email']
        scienceField = request.form['field-of-science']
        try:
            description = request.form['description']
        except:
            description = "Currently no description"

        access_token = get_user_access_token(session)
        query = {'token': access_token}
        add_group = {"apiVersion": 'v1alpha3',
                  'metadata': {'name': name, 'scienceField': scienceField, 'email': email, 'phone': phone, 'description': description}}

        r = requests.post(
            slate_api_endpoint + '/v1alpha3/groups', params=query, json=add_group)
        if r.status_code == requests.codes.ok:
            flash("Successfully created group", 'success')
            return redirect(url_for('view_group', name=name))
        else:
            # print(name, phone, email, scienceField, description)
            err_message = r.json()['message']
            flash('Failed to create group: {}'.format(err_message), 'warning')
            # return redirect(url_for('list_groups', name=name))
            return redirect(url_for('create_group'))


@app.route('/groups/<name>', methods=['GET', 'POST'])
@authenticated
@group_authenticated
def view_group(name):
    if request.method == 'GET':
        return render_template('groups_profile_overview.html', name=name, minislate_user=minislate_user)

    elif request.method == 'POST':
        access_token, slate_user_id = get_user_info(session)
        query = {'token': access_token}
        
        cluster_name = request.form['delete_cluster']
        r = requests.delete(
                    slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name,
                    params=query)

        if r.status_code == requests.codes.ok:
            flash("Successfully deleted cluster", 'success')
        else:
            err_message = r.json()['message']
            flash('Failed to destroy cluster: {}'.format(err_message), 'warning')

        return redirect(url_for('view_group', name=name))


@app.route('/group-admin-clusters-xhr/<group_name>', methods=['GET'])
def group_admin_clusters_ajax(group_name):
    administering_clusters, accessible_clusters_diff = group_admin_clusters_request(group_name)
    return jsonify(administering_clusters, accessible_clusters_diff)


def group_admin_clusters_request(group_name):
    access_token, slate_user_id = get_user_info(session)
    query = {'token': access_token}

    # Get clusters owned by group
    administering_clusters = requests.get(
        slate_api_endpoint + '/v1alpha3/groups/' + group_name + '/clusters', params=query)
    administering_clusters = administering_clusters.json()['items']
    administering_clusters_names = [administering_cluster['metadata']['name'] for administering_cluster in administering_clusters]
    # print(administering_clusters_names)

    # Grab/list all Clusters in DB for now
    list_clusters = requests.get(
        slate_api_endpoint + '/v1alpha3/clusters', params=query)
    list_clusters = list_clusters.json()['items']

    # Create list of group's accesible clusters
    accessible_clusters = []
    # /groups/groupsID/clusters
    for clusters in list_clusters:
        cluster_name = clusters['metadata']['name']
        cluster_allowed_groups = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups/' + group_name, params=query)
        cluster_allowed_groups = cluster_allowed_groups.json()['accessAllowed']
        if cluster_allowed_groups:
            accessible_clusters.append(clusters)

    # Create accessible clusters list without duplicate names of administering clusters
    accessible_clusters_names = [accessible_cluster['metadata']['name'] for accessible_cluster in accessible_clusters]
    accessible_clusters_diff = list(set(accessible_clusters_names) - set(administering_clusters_names))
    # print(accessible_clusters_diff)
    return administering_clusters, accessible_clusters_diff


@app.route('/groups/<name>/members', methods=['GET', 'POST'])
@authenticated
@group_authenticated
def view_group_members(name):
    access_token, slate_user_id = get_user_info(session)
    query = {'token': access_token}

    if request.method == 'GET':
        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=query)
        s_info = s.json()
        group_list = s_info['items']
        group_id = None
        for group in group_list:
            if group['metadata']['name'] == name:
                group_id = group['metadata']['id']
                group_name = group['metadata']['name']

        # List all members
        users = requests.get(
            slate_api_endpoint + '/v1alpha3/users', params=query)
        users = users.json()['items']

        # Check if user is Admin of Group
        user = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=query)
        user_admin = user.json()['metadata']['admin']
        admin = False
        if user_admin:
            admin = True

        group_members = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + name + '/members', params=query)
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

        # Get Group Info
        group_info = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + name, params=query)
        group_info = group_info.json()

        return render_template('groups_profile_members.html',
                                group_list=group_list, users=users, name=name,
                                group_members=group_members, group_info=group_info,
                                non_members=non_members, admin=admin, minislate_user=minislate_user)


@app.route('/groups/<name>/add_members', methods=['GET', 'POST'])
@authenticated
@group_authenticated
def view_group_add_members(name):
    access_token, slate_user_id = get_user_info(session)
    query = {'token': access_token}

    if request.method == 'GET':
        s = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=query)
        s_info = s.json()
        group_list = s_info['items']
        group_id = None
        for group in group_list:
            if group['metadata']['name'] == name:
                group_id = group['metadata']['id']
                group_name = group['metadata']['name']

        # List all members
        users = requests.get(
            slate_api_endpoint + '/v1alpha3/users', params=query)
        users = users.json()['items']

        # Check if user is Admin of Group
        user = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=query)
        user_admin = user.json()['metadata']['admin']
        admin = False
        if user_admin:
            admin = True

        group_members = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + name + '/members', params=query)
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

        # Get Group Info
        group_info = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + name, params=query)
        group_info = group_info.json()

        return render_template('groups_profile_add_members.html', users=users,
                                name=name, group_info=group_info,
                                non_members=non_members, minislate_user=minislate_user)


@app.route('/groups/<name>/secrets', methods=['GET', 'POST'])
@authenticated
@group_authenticated
def view_group_secrets(name):
    if request.method == 'GET':
        return render_template('groups_profile_secrets.html', name=name, minislate_user=minislate_user)
    elif request.method == 'POST':
        """ Method to delete secret from group """
        secret_id = request.form['secret_id']
        access_token = get_user_access_token(session)
        secrets_query = {'token': access_token, 'group': name}
        r = requests.delete(slate_api_endpoint + '/v1alpha3/secrets/' + secret_id, params=secrets_query)
        # print(name, secret_id)
        if r.status_code == requests.codes.ok:
            flash("Successfully deleted secret", 'success')
        else:
            err_message = r.json()['message']
            flash('Failed to delete secret info: {}'.format(err_message), 'warning')

        return redirect(url_for('view_group_secrets', name=name))


@app.route('/group-secrets-xhr/<name>', methods=['GET'])
def group_secrets_ajax(name):
    secrets = group_secrets_ajax_request(name)
    return jsonify(secrets)


def group_secrets_ajax_request(name):
    access_token = get_user_access_token(session)
    secrets_query = {'token': access_token, 'group': name}
    secrets = requests.get(
        slate_api_endpoint + '/v1alpha3/secrets', params=secrets_query)
    secrets = secrets.json()['items']

    return secrets


@app.route('/group-secrets-key-xhr/<secret_id>', methods=['GET'])
def group_secrets_key_ajax(secret_id):
    secret_details = group_secrets_key_ajax_request(secret_id)
    return jsonify(secret_details)


def group_secrets_key_ajax_request(secret_id):
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    secret_details = requests.get(
        slate_api_endpoint + '/v1alpha3/secrets/' + secret_id, params=query)
    secret_details = secret_details.json()
    # Base64 decode secret contents
    for key, value in list(secret_details['contents'].items()):
        try:
            value_decoded = base64.b64decode(value).decode('utf-8')
            secret_details['contents'][key] = value_decoded
        except UnicodeError:
            secret_details['contents'][key] = value

    return secret_details


@app.route('/groups/<name>/new_secret', methods=['GET', 'POST'])
@authenticated
def create_secret(name):
    access_token = get_user_access_token(session)
    query = {'token': access_token, 'group': name}
    if request.method == 'GET':
        # Get clusters owned by group
        clusters = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters', params=query)
        clusters = clusters.json()['items']

        return render_template('secrets_create.html', name=name, clusters=clusters, minislate_user=minislate_user)
    elif request.method == 'POST':
        # Initialize empty contents dict
        contents = {}

        cluster = request.form['cluster']
        secret_name = request.form['secret_name']
        key_name = request.form['key_name']
        key_contents = request.form['key_contents']
        # Add secret contents key-value to dict
        for key_name, key_contents in zip (request.form.getlist('key_name'), request.form.getlist('key_contents')):
            contents[key_name] = base64.b64encode(key_contents)
        # contents[key_name] = base64.b64encode(key_contents)

        add_secret = {"apiVersion": 'v1alpha3',
                    'metadata': {'name': secret_name, 'group': name, 'cluster': cluster},
                    'contents': contents}

        # Add secret to Group
        r = requests.post(
            slate_api_endpoint + '/v1alpha3/secrets', params=query, json=add_secret)
        if r.status_code == requests.codes.ok:
            flash("Successfully added secret", 'success')
        else:
            err_message = r.json()['message']
            flash('Unable to add secret: {}'.format(err_message), 'warning')

        return redirect(url_for('view_group_secrets', name=name))


@app.route('/groups/<name>/add_member', methods=['POST'])
@authenticated
def group_add_member(name):
    if request.method == 'POST':
        new_user_id = request.form['add_member']
        access_token = get_user_access_token(session)
        query = {'token': access_token}
        group_id = name
        # Add member to Group
        r = requests.put(
            slate_api_endpoint + '/v1alpha3/users/'
            + new_user_id + '/groups/' + group_id, params=query)
        if r.status_code == requests.codes.ok:
            flash("Successfully added member", 'success')
        else:
            err_message = r.json()['message']
            flash('Failed to add {}: {}'.format(new_user_id, err_message), 'warning')

        return redirect(url_for('view_group_members', name=name))


@app.route('/groups/<name>/remove_member', methods=['POST'])
@authenticated
def group_remove_member(name):
    if request.method == 'POST':
        remove_user_id = request.form['remove_member']
        access_token = get_user_access_token(session)
        query = {'token': access_token}
        group_id = name

        r = requests.delete(
            slate_api_endpoint + '/v1alpha3/users/' + remove_user_id + '/groups/' + group_id, params=query)
        if r.status_code == requests.codes.ok:
            flash("Successfully removed member from group", 'success')
        else:
            err_message = r.json()['message']
            flash('Failed to remove member: {}'.format(err_message), 'warning')

        return redirect(url_for('view_group_members', name=name))


@app.route('/groups/<project_name>/clusters/<name>', methods=['GET', 'POST', 'DELETE'])
@authenticated
def view_cluster(project_name, name):
    if request.method == 'GET':
        access_token = get_user_access_token(session)
        query = {'token': access_token}
        cluster_name = name
        group_name = project_name

        # Get list of groups
        list_groups = requests.get(
            slate_api_endpoint + '/v1alpha3/groups', params=query)
        list_groups = list_groups.json()['items']
        list_groups_names = [group['metadata']['name'] for group in list_groups]

        # Get list of groups allowed to access this cluster
        allowed_groups = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups', params=query)
        allowed_groups = allowed_groups.json()['items']
        allowed_groups_names = [group['metadata']['name'] for group in allowed_groups]

        for group in allowed_groups:
            if group['metadata']['name'] == '<all>':
                allowed_groups_names = list_groups_names
            elif group['metadata']['name'] in list_groups_names:
                list_groups_names.remove(group['metadata']['name'])

        # Getting Cluster information
        cluster = requests.get(slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name, params=query)
        cluster = cluster.json()

        # Get clusters owned by group
        group_clusters = requests.get(
            slate_api_endpoint + '/v1alpha3/groups/' + group_name + '/clusters', params=query)
        group_clusters = group_clusters.json()['items']
        administering = False

        for group in group_clusters:
            if group['metadata']['name'] == cluster_name:
                administering = True

        # Groups that do not have access to this cluster, populated in drop-down form to 'add group'
        # print("LIST GROUPS: {}".format(list_groups))
        # print("ALLOWED GROUPS: {}".format(allowed_groups))
        non_access_groups = list(set(list_groups_names) - set(allowed_groups_names))
        sorted_non_access_groups = sorted(non_access_groups)
        # print("NON ACCESS GROUPS: {}".format(non_access_groups))

        return render_template('cluster_profile.html', allowed_groups=allowed_groups,
                               project_name=project_name, name=name,
                               non_access_groups=sorted_non_access_groups,
                               cluster=cluster, administering=administering,
                               group_clusters=group_clusters, minislate_user=minislate_user)

    elif request.method == 'POST':
        """Members of group may give other groups access to this cluster"""

        new_group = request.form['new_group']
        access_token = get_user_access_token(session)
        query = {'token': access_token}
        cluster_name = name

        # Add group to cluster whitelist
        requests.put(
            slate_api_endpoint + '/v1alpha3/clusters/'
            + cluster_name + '/allowed_groups/' + new_group, params=query)

        return redirect(url_for('view_cluster', name=name, project_name=project_name))


@app.route('/groups/<project_name>/clusters/<name>/<group_name>', methods=['GET', 'POST'])
@authenticated
def group_cluster_apps(project_name, name, group_name):
    access_token = get_user_access_token(session)
    query = {'token': access_token}
    if request.method == 'GET':
        cluster_name = name
        # set up multiplex JSON
        group_apps_query =  '/v1alpha3/clusters/' + cluster_name + '/allowed_groups/' + group_name + '/applications' + '?token='+query['token']
        applications_query = '/v1alpha3/apps'
        multiplex_JSON = {group_apps_query: {"method": "GET"}, applications_query: {"method": "GET"}}
        # POST request for multiplex return
        multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplex_JSON)
        multiplex = multiplex.json()
        # Parse multiplex json into applications and group allowed apps
        group_allowed_apps = json.loads(multiplex[group_apps_query]['body'])['items']
        applications = json.loads(multiplex[applications_query]['body'])['items']

        return render_template('group_cluster_apps.html', project_name=project_name,
                                name=name, group_name=group_name, applications=applications,
                                group_allowed_apps=group_allowed_apps, minislate_user=minislate_user)

    elif request.method == 'POST':
        cluster_id = name
        group_id = group_name
        # Get list of apps on SLATE to cross reference
        slate_apps = requests.get(slate_api_endpoint + '/v1alpha3/apps', params=query)
        slate_apps = slate_apps.json()['items']
        slate_app_names = [app['metadata']['name'] for app in slate_apps]
        # Grab list of app names selected from form checkbox
        allowed_apps = request.form.getlist('new_app')

        remove_apps = list(set(slate_app_names) - set(allowed_apps))
        # Individually add each app to group's accessible apps
        r = None

        if allowed_apps:
            for app_name in allowed_apps:
                add_app_query = '/v1alpha3/clusters/' + cluster_id + '/allowed_groups/' + group_id + '/applications/' + app_name
                r = requests.put(slate_api_endpoint + add_app_query, params=query)
        if remove_apps:
            for app_name in remove_apps:
                remove_app_query = '/v1alpha3/clusters/' + cluster_id + '/allowed_groups/' + group_id + '/applications/' + app_name
                r = requests.delete(slate_api_endpoint + remove_app_query, params=query)
        #         print(app_name, r)

        if r.status_code == requests.codes.ok:
            flash("Successfully updated {}'s allowed apps".format(group_id), 'success')
        else:
            err_message = r.json()['message']
            flash('Failed to add applications to group: {}'.format(err_message), 'warning')
        return redirect(url_for('view_cluster', project_name=project_name, name=name))


@app.route('/groups/<project_name>/clusters/<name>/remove_group_from_cluster', methods=['POST'])
@authenticated
def remove_group_from_cluster(project_name, name):
    if request.method == 'POST':
        """Members of group may revoke other groups access to this cluster"""
        group_id = request.form['remove_group']
        print(group_id)
        cluster_id = name
        access_token = get_user_access_token(session)
        query = {'token': access_token}
        # print(cluster_id, group_id)
        # delete group from cluster whitelist
        r=requests.delete(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_id + '/allowed_groups/' + group_id, params=query)
        print("Remove from Whitelist: ", r)
        return redirect(url_for('view_cluster', project_name=project_name, name=name))


@app.route('/groups/<project_name>/clusters/<name>/edit', methods=['GET','POST'])
@authenticated
def edit_cluster(project_name, name):
    access_token = get_user_access_token(session)
    query = {'token': access_token}
    cluster_id = name
    cluster = requests.get(slate_api_endpoint + '/v1alpha3/clusters/' + cluster_id, params=query)
    cluster = cluster.json()

    if request.method == 'GET':
        """Members of group may edit information about cluster"""
        # Setting lat/lon coordinates for edit fields to autofill
        try:
            latitude = cluster['metadata']['location'][0]['lat']
            longitude = cluster['metadata']['location'][0]['lon']
        except:
            latitude = cluster['metadata']['location']
            longitude = cluster['metadata']['location']
        
        try:
            address = cluster['metadata']['location'][0]['desc']
        except:
            address = ''

        return render_template('cluster_edit.html', cluster=cluster,
                                project_name=project_name, name=name,
                                latitude=latitude, longitude=longitude,
                                address=address, minislate_user=minislate_user)

    elif request.method == 'POST':
        # locations param is a list of coordinates, initialized as empty list
        locations = []
        owningOrganization = request.form['owningOrganization']
        # grab one or many location coordinates from dynamic form fields
        for latitude, longitude in zip (request.form.getlist('latitude'), request.form.getlist('longitude')):
            try:
                address = coordsConversion(latitude, longitude)
                locations.append({'lat': float(latitude), 'lon': float(longitude), 'desc': address})
            except:
                locations.append({'lat': float(latitude), 'lon': float(longitude)})
        # print("Locations: ", locations)
        # Set up JSON and request query
        add_cluster = {"apiVersion": 'v1alpha3',
                  'metadata': {'owningOrganization': owningOrganization, 'location': locations}}
        # print("Updating cluster info: {}".format(add_cluster))
        r = requests.put(slate_api_endpoint + '/v1alpha3/clusters/' + cluster_id, params=query, json=add_cluster)
        # print("Response for update query: {}".format(r.json()))
        if r.status_code == requests.codes.ok:
            flash("Successfully updated cluster information", 'success')
        else:
            err_message = r.json()['message']
            flash('Failed to update cluster info: {}'.format(err_message), 'warning')
        return redirect(url_for('view_cluster', project_name=project_name, name=name))


@app.route('/groups/<name>/delete', methods=['POST'])
@authenticated
def delete_group(name):
    if request.method == 'POST':
        access_token = get_user_access_token(session)
        query = {'token': access_token}
        # group_id = name

        try:
            print("Querying deletion of group: {}".format(name))
            r = requests.delete(
                slate_api_endpoint + '/v1alpha3/groups/' + name, params=query, timeout=1)
            print("Query to delete group {} RESPONSE: {}".format(name, r))
        except requests.exceptions.ReadTimeout:
            print("Timedout, but force to next page")

        flash("Successfully deleted group", 'success')
        return redirect(url_for('list_groups'))


@app.route('/groups/<name>/edit', methods=['GET', 'POST'])
@authenticated
def edit_group(name):
    access_token = get_user_access_token(session)
    query = {'token': access_token}
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

        group = requests.get(slate_api_endpoint + '/v1alpha3/groups/' + name,
                                params=query)
        group = group.json()

        return render_template('groups_edit.html', sciences=sciences, group=group, name=name, minislate_user=minislate_user)

    elif request.method == 'POST':
        """Route method to handle query to edit Group inro"""

        phone = request.form['phone-number']
        email = request.form['email']
        scienceField = request.form['field-of-science']
        try:
            description = request.form['description']
        except:
            description = "Currently no description"

        access_token = get_user_access_token(session)
        query = {'token': access_token}
        add_group = {"apiVersion": 'v1alpha3',
                  'metadata': {'email': email, 'phone': phone, 'scienceField': scienceField, 'description': description}}

        r = requests.put(
            slate_api_endpoint + '/v1alpha3/groups/' + name, params=query, json=add_group)

        if r.status_code == requests.codes.ok:
            flash("Successfully updated group", 'success')
            return redirect(url_for('view_group', name=name))
        else:
            err_message = r.json()['message']
            flash('Failed to update group information: {}'.format(err_message), 'warning')
            return redirect(url_for('list_groups'))


@app.route('/profile/new', methods=['GET', 'POST'])
@authenticated
def create_profile():
    identity_id = session.get('primary_identity')
    institution = session.get('institution')
    globus_id = identity_id
    query = {'token': slate_api_token,
             'globus_id': globus_id}

    if request.method == 'GET':
        try:
            access_token, user_id = get_user_info(session)
            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
        except:
            with open('portal/static/AUP.md', 'r') as f:
                aup = f.read()

            return render_template('profile_create.html', aup=aup)

    elif request.method == 'POST':
        # Check for AUP agreement from form
        try:
            aup_check = request.form['aup-check']
        except:
            aup_check = None

        # If checked, proceed to store user
        if aup_check:
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone-number']
            institution = request.form['institution']
            globus_id = session['primary_identity']
            admin = False
            # Schema and query for adding users to Slate DB
            post_user = {"apiVersion": 'v1alpha3',
                        'metadata': {'globusID': globus_id, 'name': name, 'email': email,
                                    'phone': phone, 'institution': institution, 'admin': admin}}

            query = {'token': slate_api_token}

            r = requests.post(slate_api_endpoint + '/v1alpha3/users', params=query, json=post_user)
            if r.status_code == requests.codes.ok:
                user = r.json()
                session['user_id'] = user['metadata']['id']
                flash("Successfully created your profile", 'success')
                return redirect(url_for('profile'))
            else:
                # err_message = r.json()['message']
                flash('Please complete any missing profile fields and press Save.')
                return redirect(url_for('create_profile'))
        else:
            flash('Please complete any missing profile fields and press Save.')
            return redirect(url_for('create_profile'))


@app.route('/profile', methods=['GET', 'POST'])
@authenticated
def profile():
    """User profile information. Assocated with a Globus Auth identity."""
    if request.method == 'GET':
        globus_id = session.get('primary_identity')
        query = {'token': slate_api_token,
                 'globus_id': globus_id}

        user = requests.get(
            slate_api_endpoint + '/v1alpha3/find_user', params=query)

        if user:
            slate_id = user.json()['metadata']['id']
            profile = requests.get(slate_api_endpoint + '/v1alpha3/users/' + slate_id, params=query)
            profile = profile.json()['metadata']
            session['name'] = profile['name']
            session['email'] = profile['email']
            session['institution'] = profile['institution']
            session['user_id'] = slate_id
        else:
            flash('Please complete any missing profile fields and press Save.')
            return redirect(url_for('create_profile', next=url_for('dashboard')))

        if request.args.get('next'):
            session['next'] = get_safe_redirect()

        return render_template('profile.html', profile=profile)


@app.route('/profile/edit', methods=['GET', 'POST'])
@authenticated
def edit_profile():
    if request.method == 'GET':
        identity_id = session.get('primary_identity')
        access_token = get_user_access_token(session)
        query = {'token': slate_api_token,
                 'globus_id': identity_id}
        print("Querying for user profile...")
        profile = requests.get(
            slate_api_endpoint + '/v1alpha3/find_user', params=query)
        print("Response from querying profile: {}".format(profile.json()))

        if profile:
            print("Found profile: {}".format(profile))
            query = {'token': access_token,
                     'globus_id': identity_id}
            slate_user_id = get_user_id(session)

            print("Querying profile details...")
            profile = requests.get(slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=query)

            print("Response from querying profile details: {}".format(profile))
            profile = profile.json()['metadata']
        else:
            flash('Please complete any missing profile fields and press Save.')
            return redirect('create_profile')

        if request.args.get('next'):
            session['next'] = get_safe_redirect()
        return render_template('profile_edit.html', profile=profile)
    elif request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone-number']
        institution = request.form['institution']
        # Schema and query for adding users to Slate DB
        put_user = {"apiVersion": 'v1alpha3',
                    'metadata': {'name': name, 'email': email,
                                 'phone': phone, 'institution': institution}}

        query = {'token': slate_api_token}
        slate_user_id = get_user_id(session)

        requests.put(slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=query, json=put_user)

        if 'next' in session:
            redirect_to = session['next']
            session.pop('next')
        else:
            redirect_to = url_for('profile')

        return redirect(redirect_to)


@app.route('/authcallback', methods=['GET'])
def authcallback():
    """Handles the interaction with Globus Auth."""
    print("Entering Authcallback Route")
    # Check if single user instance on minislate
    try:
        # Change to location of slate_portal_user file
        print("Trying to read slate portal user file")
        f = open("/slate_portal_user", "r")
        slate_portal_user = f.read().split()
    except:
        slate_portal_user = None
    print("Slate Portal User: {}".format(slate_portal_user))
    if slate_portal_user:
        print("Found slate portal user on minislate")
        user_id = session['user_id'] = slate_portal_user[0]
        name = session['name'] = slate_portal_user[1]
        email = session['email'] = slate_portal_user[2]
        phone = session['phone'] = slate_portal_user[3]
        institution = session['institution'] = slate_portal_user[4]
        session['access_token'] = slate_portal_user[5]
        session['is_authenticated'] = True
        session['slate_portal_user'] = True
        globus_id = session['primary_identity'] = slate_portal_user[5]
        admin = False

        # Schema and query for adding users to Slate DB
        post_user = {"apiVersion": 'v1alpha3',
                     'metadata': {'globusID': globus_id, 'name': name, 'email': email,
                                  'phone': phone, 'institution': institution, 'admin': admin}}

        query = {'token': slate_api_token}
        print("Query to post new user")
        r = requests.post(slate_api_endpoint + '/v1alpha3/users', params=query, json=post_user)
        print("Response: {}".format(r))

        print("Redirecting to dashboard in single user mode with the following session {}".format(session))
        return redirect(url_for('dashboard'))

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
        next_url = get_safe_redirect()
        additional_authorize_params = (
            {'signup': 1} if request.args.get('signup') else {'next': next_url})

        auth_uri = client.oauth2_get_authorize_url(
            additional_params=additional_authorize_params)
        # print("AUTH URI: {}".format(auth_uri))

        return redirect(auth_uri)
    else:
        # If we do have a "code" param, we're coming back from Globus Auth
        # and can start the process of exchanging an auth code for a token.
        next_url = get_safe_redirect()
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
            identity_provider=id_token.get('identity_provider')
        )
        #  Grab user's access token in order to find their identity set
        access_token = session['tokens']['auth.globus.org']['access_token']
        token_introspect = client.oauth2_token_introspect(
            token=access_token, include='identity_set')
        identity_set = token_introspect.data['identity_set']
        # Initialize profile variable to None
        profile = None
        # Need to query a request to view all users in Slate DB, then iterate
        # to see if profile exists by matching globus_id ideally.
        for identity in identity_set:
            query = {'token': slate_api_token,
                    'globus_id': identity}
            try:
                # print("Trying this query: {}".format(query))
                # Query response to find user profile
                r = requests.get(
                    slate_api_endpoint + '/v1alpha3/find_user', params=query)
                if r.status_code == requests.codes.ok:
                    # Set profile and check for admin status
                    print('Found profile with globus_id: {}'.format(identity))
                    profile = r.json()
                    print('Profile Information: {}'.format(profile))

                    slate_user_id = profile['metadata']['id']
                    session['user_id'] = slate_user_id
                    session['primary_identity'] = identity
                    user_info = requests.get(slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=query)
                    user_info = user_info.json()['metadata']
                    if user_info['admin']:
                        session['admin'] = True
            except:
                print("User identity not found: {}".format(identity))
        
        try:
            referrer = urlparse(request.referrer)
            # print("REFERRER: {}".format(referrer))
            queries = parse_qs(referrer.query)
            # print("QUERIES: {}".format(queries))
            redirect_uri = queries['redirect_uri']
            next_url = queries['next'][0]
            # print("AFTER QUERIES NEXT URL: {}".format(next_url))
        except:
            next_url = '/'

        if profile:
            print('Logging in with profile: {}'.format(profile))
            # Check for admin status
            slate_user_id = profile['metadata']['id']
            session['user_id'] = slate_user_id
            user_info = requests.get(slate_api_endpoint + '/v1alpha3/users/' + slate_user_id, params=query)
            user_info = user_info.json()['metadata']
            if user_info['admin']:
                session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('create_profile',
                                    next=url_for('dashboard')))
        # print("FINAL NEXT URL {}".format(next_url))

        if next_url == '/':
            return redirect(url_for('dashboard'))
        else:
            return redirect(next_url)


@app.route('/clusters/new', methods=['GET'])
@authenticated
def create_cluster():
    """
    - Create Cluster on SLATE
    """
    if request.method == 'GET':
        # Get groups to which the user belongs
        group_list = list_user_groups(session)
        return render_template('clusters_create.html', group_list=group_list, minislate_user=minislate_user)


@app.route('/_get_data', methods=["GET", "POST"])
def _get_data():
    myList = ['elements1', 'elements2', 'elements3']

    return jsonify({'data': render_template('response.html', mylist=myList)})


@app.route('/provisioning', methods=['GET'])
@authenticated
def list_provisionings():
    """
     List cluster node provisionings on SLATE
    """
    if request.method == 'GET':
        return render_template('provisionings.html')


@app.route('/provisioning/new', methods=['GET'])
@authenticated
def create_provisionings():
    """
     List cluster node provisionings on SLATE
    """
    if request.method == 'GET':
        access_token = get_user_access_token(session)
        query = {'token': access_token}

        clusters = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters', params=query)
        clusters = clusters.json()['items']
        return render_template('provisionings_create.html', clusters=clusters)


@app.route('/secrets', methods=['GET'])
@authenticated
def list_secrets():
    """
    - List User Related Secrets Registered on SLATE
    """
    if request.method == 'GET':
        # start_time = time.time()

        access_token, slate_user_id = get_user_info(session)
        query = {'token': access_token}

        # List groups to which the user belongs
        user_groups = requests.get(
            slate_api_endpoint + '/v1alpha3/users/' + slate_user_id + '/groups', params=query)
        user_groups = user_groups.json()['items']
        user_groups = [group['metadata']['name'] for group in user_groups]

        multiplexJson = {}
        # Set up secrets query multiplex for every group relating to the user
        for group_name in user_groups:
            secrets_query = "/v1alpha3/secrets?token="+query['token']+"&group="+group_name
            multiplexJson[secrets_query] = {"method":"GET"}

        multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
        multiplex = multiplex.json()

        # Parsing the multiplex result, returning a list of secret's contents/info
        secrets_content = []
        for query in multiplex:
            list_of_items = json.loads(multiplex[query]['body'])['items']
            for item in list_of_items:
                metadata = item['metadata']
                secrets_content.append(metadata)

        # end_time = time.time()
        # print(end_time-start_time)
        return render_template('secrets.html', secrets=secrets_content)
    
@app.route('/volumes', methods=['GET'])
@authenticated
def list_volumes():
    """
    - List Volumes Registered on SLATE
    """
    if request.method == 'GET':
        access_token, slate_user_id = get_user_info(session)
        query = {'token': access_token}               
        volumes = requests.get(
            slate_api_endpoint + '/v1alpha3/volumes', params=query)
        volumes = volumes.json()['items']
        return render_template('volumes.html', volumes=volumes)
    
@app.route('/volumes/<name>', methods=['GET'])
@authenticated
def volume_info(name):
    """
    - View detailed volume information on SLATE
    """
    if request.method == 'GET':
        access_token, slate_user_id = get_user_info(session)
        query = {'token': access_token}
        print("Querying volume details...")
        response = requests.get(slate_api_endpoint + '/v1alpha3/volumes/' + name, params=query)
        print("Query response: {}".format(response))
        if response.status_code == 504:
            flash('The connection to {} has timed out. Please try again later.'.format(name), 'warning')
            return redirect(url_for('list_volumes'))
        volume_details = response.json()
        return render_template('volume_profile.html', name=name,
                                volume_info=volume_details)
