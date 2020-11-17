from portal.decorators import authenticated
from portal import app, slate_api_token, slate_api_endpoint, minislate_user
import json
import requests
from flask import (flash, redirect, render_template,
                   request, session, url_for, jsonify)
from portal.connect_api import (list_applications_request,
                        list_incubator_applications_request,
                        list_instances_request, list_user_groups, 
                        get_user_access_token, list_clusters_request,
                        get_app_config, get_incubator_app_config,
                        cluster_allowed_groups)
import os

@app.route('/applications', methods=['GET'])
@authenticated
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
@authenticated
def view_application(name):
    """
    - View Known Applications Detail Page on SLATE
    """
    if request.method == 'GET':
        applications = list_applications_request()
        app_version = None
        chart_version = None
        for application in applications:
            if application['metadata']['name'] == name:
                app_version = application['metadata']['app_version']
                chart_version = application['metadata']['chart_version']

        return render_template('applications_stable_profile.html', name=name,
                                app_version=app_version, chart_version=chart_version,
                                minislate_user=minislate_user)


@app.route('/applications/incubator/<name>', methods=['GET'])
def view_incubator_application(name):
    """
    - View Incubator Applications Detail Page on SLATE
    """
    if request.method == 'GET':
        applications = list_incubator_applications_request()
        app_version = None
        chart_version = None

        for application in applications:
            if application['metadata']['name'] == name:
                app_version = application['metadata']['app_version']
                chart_version = application['metadata']['chart_version']

        return render_template('applications_incubator_profile.html', name=name,
                                app_version=app_version, chart_version=chart_version)


@app.route('/applications/<name>/new', methods=['GET', 'POST'])
@authenticated
def create_application_group(name):
    """ View form to install new application """
    if request.method == 'GET':
        return render_template('applications_create.html', name=name, minislate_user=minislate_user)

    elif request.method == 'POST':
        group = request.form["group"]
        return redirect(url_for('create_application', name=name, group_name=group))

# /applications-create-xhr
@app.route('/applications-create-xhr', methods=['GET'])
@authenticated
def applications_create_xhr():
    """ View form to install new application """
    if request.method == 'GET':
        # Get groups that user belongs to
        groups = list_user_groups(session)
        return jsonify(groups)


@app.route('/applications-create-final-xhr/<group_name>/<app_name>', methods=['GET'])
@authenticated
def applications_create_final_xhr(group_name, app_name):
    """ View form to install new application """
    if request.method == 'GET':
        # Get groups that user belongs to
        app_config = get_app_config(app_name)
        if app_config['kind'] == 'Error':
            app_config = get_incubator_app_config(app_name)
        app_config = app_config['spec']['body']
        # print(app_config)
        clusters_list = list_clusters_request()
        accessible_clusters = []

        for cluster in clusters_list:
            cluster_name = cluster['metadata']['name']
            if cluster_allowed_groups(cluster_name, group_name):
                accessible_clusters.append(cluster)
        # print(accessible_clusters)
        return jsonify(app_config, accessible_clusters)


@app.route('/applications/<name>/new/<group_name>', methods=['GET', 'POST'])
@authenticated
def create_application(name, group_name):
    """ View form to install new application """
    if request.method == 'GET':
        return render_template('applications_create_final.html', name=name, group_name=group_name, minislate_user=minislate_user)

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