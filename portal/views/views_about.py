import json
import os

import requests
from flask import flash, jsonify, redirect, render_template, request, session, url_for

from portal import app, minislate_user, slate_api_endpoint, slate_api_token
from portal.connect_api import (
    cluster_allowed_groups,
    get_app_config,
    get_incubator_app_config,
    get_user_access_token,
    list_applications_request,
    list_clusters_request,
    list_incubator_applications_request,
    list_instances_request,
    list_user_groups,
)
from portal.decorators import authenticated


@app.route("/about", methods=["GET"])
@authenticated
def about_portal():
    """
    - Display Portal About information
    """
    if request.method == "GET":
        return render_template("about.html")
