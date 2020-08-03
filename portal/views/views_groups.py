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


