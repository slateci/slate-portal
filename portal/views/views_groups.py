from portal.decorators import authenticated, group_authenticated
from portal import app
import json
import requests
from flask import (flash, redirect, render_template,
                   request, session, url_for, jsonify)
from connect_api import (list_applications_request,
                        list_incubator_applications_request,
                        list_instances_request,
                        list_public_groups_request,
                        list_user_groups,
                        list_users_instances_request,
                        list_clusters_request, coordsConversion,
                        get_user_access_token, get_user_id,
                        get_user_info, delete_user)
# Read endpoint and token from config file
slate_api_token = app.config['SLATE_API_TOKEN']
slate_api_endpoint = app.config['SLATE_API_ENDPOINT']


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

        group_info_query = '/v1alpha3/groups/' + name + '?token=' +query['token']
        group_clusters_query = '/v1alpha3/groups/' + name + '/clusters?token=' +query['token']
        # Set up multiplex JSON
        multiplexJson = {group_info_query: {"method":"GET"},
                            group_clusters_query: {"method":"GET"}}
        # POST request for multiplex return
        multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
        multiplex = multiplex.json()

        # Parse post return for apps, clusters, and pub groups
        try:
            group_info_json = json.loads(multiplex[group_info_query]['body'])
            group_clusters_json = json.loads(multiplex[group_clusters_query]['body'])
            group_clusters_json = group_clusters_json['items']
        except:
            return render_template('404.html')

        return render_template('groups_public_profile.html', group_info=group_info_json, group_clusters=group_clusters_json, name=name)

