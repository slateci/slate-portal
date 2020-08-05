from portal.decorators import authenticated
from portal import app, csrf, slate_api_token, slate_api_endpoint
import json
import requests
from flask import (flash, redirect, render_template,
                   request, session, url_for, jsonify)
from connect_api import (list_applications_request,
                        list_incubator_applications_request,
                        list_instances_request, list_user_groups, 
                        get_user_access_token)
import os

@app.route('/applications', methods=['GET'])
def list_applications():
    """
    - List Known Applications on SLATE
    """
    if request.method == 'GET':
        return render_template('applications.html')


@app.route('/applications-xhr', methods=['GET'])
def list_applications_xhr():
    """
    - List Applications Registered on SLATE (json response)
    """
    if request.method == 'GET':
        applications = list_applications_request()
        return jsonify(applications)


@app.route('/incubator-applications-xhr', methods=['GET'])
def list_incubator_applications_xhr():
    """
    - List Incubator Applications Registered on SLATE (json response)
    """
    if request.method == 'GET':
        incubator_apps = list_incubator_applications_request()
        return jsonify(incubator_apps)


@app.route('/applications/<name>', methods=['GET'])
def view_application(name):
    """
    - View Known Applications Detail Page on SLATE
    """
    if request.method == 'GET':
        try:
            access_token = get_user_access_token(session)
            query = {'token': access_token}
        except:
            query = {'token': slate_api_token}

        app_config_query = '/v1alpha3/apps/' + name + '?token=' + query['token']
        app_read_query = '/v1alpha3/apps/' + name + '/info?token=' + query['token']
        applications_query = '/v1alpha3/apps?token=' + query['token']

        multiplexJson = {app_config_query: {"method":"GET"},
                            app_read_query: {"method":"GET"},
                            applications_query: {"method": "GET"}}

        multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
        multiplex = multiplex.json()
        app_config = json.loads(multiplex[app_config_query]['body'])
        app_readme = json.loads(multiplex[app_read_query]['body'])
        applications = json.loads(multiplex[applications_query]['body'])
        applications = applications['items']

        app_version = None
        chart_version = None
        for application in applications:
            if application['metadata']['name'] == name:
                app_version = application['metadata']['app_version']
                chart_version = application['metadata']['chart_version']

        if app_config['kind'] == 'Error':
            error = True
            return redirect(url_for('not_found', e=error))
        else:
            error = False

        return render_template('applications_stable_profile.html', name=name,
                                app_config=app_config, app_readme=app_readme,
                                app_version=app_version,
                                chart_version=chart_version, error=error)


@app.route('/applications/incubator/<name>', methods=['GET'])
def view_incubator_application(name):
    """
    - View Incubator Applications Detail Page on SLATE
    """
    if request.method == 'GET':
        try:
            access_token = get_user_access_token(session)
            query = {'token': access_token}
        except:
            query = {'token': slate_api_token}

        app_config_query = '/v1alpha3/apps/' + name + '?dev=true?token=' + query['token']
        app_read_query = '/v1alpha3/apps/' + name + '/info?dev=true?token=' + query['token']
        applications_query = '/v1alpha3/apps?dev=true?token=' + query['token']

        multiplexJson = {app_config_query: {"method":"GET"},
                            app_read_query: {"method":"GET"},
                            applications_query: {"method": "GET"}}

        multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
        multiplex = multiplex.json()
        app_config = json.loads(multiplex[app_config_query]['body'])
        app_readme = json.loads(multiplex[app_read_query]['body'])
        applications = json.loads(multiplex[applications_query]['body'])
        applications = applications['items']

        if app_config['kind'] == 'Error':
            error = True
        else:
            error = False

        try:
            app_config = app_config['spec']['body']
            app_readme = app_readme['spec']['body']
        except:
            app_config = None
            app_readme = None

        app_version = None
        chart_version = None

        for application in applications:
            if application['metadata']['name'] == name:
                app_version = application['metadata']['app_version']
                chart_version = application['metadata']['chart_version']

        return render_template('applications_incubator_profile.html', name=name,
                                app_config=app_config, app_readme=app_readme,
                                app_version=app_version,
                                chart_version=chart_version, error=error)


@app.route('/applications/<name>/new', methods=['GET', 'POST'])
@authenticated
def create_application_group(name):
    """ View form to install new application """
    if request.method == 'GET':
        # Get groups that user belongs to
        groups = list_user_groups(session)
        return render_template('applications_create.html', name=name, groups=groups)

    elif request.method == 'POST':
        group = request.form["group"]
        return redirect(url_for('create_application', name=name, group_name=group))


@app.route('/applications/<name>/new/<group_name>', methods=['GET', 'POST'])
@authenticated
def create_application(name, group_name):
    """ View form to install new application """
    if request.method == 'GET':
        access_token = get_user_access_token(session)
        query = {'token': access_token}

        # Get configuration of app <name> selected
        app_config_query = '/v1alpha3/apps/' + name + '?token=' + query['token']
        # Grab/list all Clusters in DB for now
        clusters_query = '/v1alpha3/clusters?token=' + query['token']
        # Set up multiplex JSON
        multiplexJson = {app_config_query: {"method":"GET"},
                            clusters_query: {"method":"GET"}}
        # POST request for multiplex return
        multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
        multiplex = multiplex.json()
        # Parse post return for instance, instance details, and instance logs
        app_config = json.loads(multiplex[app_config_query]['body'])
        clusters_json = json.loads(multiplex[clusters_query]['body'])
        list_clusters = clusters_json['items']

        # Create list of group's accesible clusters
        accessible_clusters = []
        cluster_allowed_groups_multiplexJson = {}

        for clusters in list_clusters:
            cluster_name = clusters['metadata']['name']

            cluster_allowed_groups_query = '/v1alpha3/clusters/' + cluster_name + '/allowed_groups' + '?token=' + query['token']
            cluster_allowed_groups_multiplexJson[cluster_allowed_groups_query] = {"method":"GET"}

        cluster_multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=cluster_allowed_groups_multiplexJson)
        cluster_multiplex = cluster_multiplex.json()

        for query, value in list(cluster_multiplex.items()):
            a = json.loads(value['body'])
            items = a['items']
            for item in items:
                if item['metadata']['name'] == group_name:
                    cluster_name = query.split('/')[3]
                    accessible_clusters.append(cluster_name)

        cluster_list = sorted(accessible_clusters)
        return render_template('applications_create_final.html', name=name,
                                app_config=app_config,
                                cluster_list=cluster_list,
                                group_name=group_name)

    elif request.method == 'POST':
        access_token = get_user_access_token(session)
        query = {'token': access_token}

        group = group_name
        cluster = request.form["cluster"]
        configuration = request.form["config"]

        install_app = {"apiVersion": 'v1alpha3', "group": group, "cluster": cluster, "configuration": configuration}

        # Post query to install application config
        app_install = requests.post(
            slate_api_endpoint + '/v1alpha3/apps/' + name, params=query, json=install_app)

        print("APP INSTALL STATUS: {}".format(app_install))
        print("APP NAME: {}".format(name))

        if app_install.status_code == 200:
            app_id = app_install.json()['metadata']['id']
            flash('You have successfully installed an application instance', 'success')
            return redirect(url_for('view_instance', name=app_id))
        else:
            err_message = app_install.json()['message']
            flash('Failed to install application instance: {}'.format(err_message), 'warning')
            return redirect(url_for('view_application', name=name))