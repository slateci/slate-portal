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

@app.route('/about', methods=['GET'])
@authenticated
def about_portal():
    """
    - Display Portal About information
    """
    if request.method == 'GET':
        return render_template('about.html')
