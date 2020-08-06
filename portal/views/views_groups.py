from portal.decorators import authenticated, group_authenticated
from portal import app, slate_api_token, slate_api_endpoint
import json
import requests
from flask import (flash, redirect, render_template,
                   request, session, url_for, jsonify)
from connect_api import (list_applications_request,
                        list_incubator_applications_request,
                        list_instances_request,
                        list_public_groups_request,
                        list_user_groups, get_group_info,
                        get_group_clusters, 
                        list_users_instances_request,
                        list_clusters_request, coordsConversion,
                        get_user_access_token, get_user_id,
                        get_user_info, delete_user, get_group_members)


@app.route('/groups', methods=['GET', 'POST'])
@authenticated
def list_groups():
    if request.method == 'GET':
        return render_template('groups.html')


@app.route('/groups-xhr', methods=['GET'])
@authenticated
def view_user_groups():
    if request.method == 'GET':
        user_groups = list_user_groups(session)
        return jsonify(user_groups)


@app.route('/groups-profile-members-xhr/<group_name>', methods=['GET'])
@authenticated
def groups_profile_members_xhr(group_name):
    if request.method == 'GET':
        group_members = get_group_members(group_name)
        return jsonify(group_members)


@app.route('/public-groups', methods=['GET', 'POST'])
@authenticated
def list_public_groups():
    if request.method == 'GET':
        return render_template('groups_public.html')


@app.route('/public-groups-xhr', methods=['GET'])
def public_groups_ajax():
    public_groups = list_public_groups_request()
    return jsonify(public_groups)


@app.route('/public-groups/<name>', methods=['GET', 'POST'])
@authenticated
def view_public_group(name):
    access_token = get_user_access_token(session)
    query = {'token': access_token}
    if request.method == 'GET':
        return render_template('groups_public_profile.html', name=name)


@app.route('/public-groups-xhr/<name>', methods=['GET'])
def view_public_group_ajax(name):
    group_info = get_group_info(name)
    group_clusters = get_group_clusters(name)
    try:
        group_clusters = group_clusters['items']
    except:
        group_clusters = []
    return jsonify(group_info, group_clusters)