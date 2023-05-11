import json

import requests
from flask import flash, jsonify, redirect, render_template, request, session, url_for

from portal import app, minislate_user, slate_api_endpoint, slate_api_token
from portal.connect_api import (
    coordsConversion,
    delete_user,
    get_group_clusters,
    get_group_info,
    get_group_members,
    get_user_access_token,
    get_user_id,
    get_user_info,
    list_applications_request,
    list_clusters_request,
    list_incubator_applications_request,
    list_instances_request,
    list_public_groups_request,
    list_user_groups,
    list_users_instances_request,
)
from portal.decorators import authenticated, group_authenticated


@app.route("/groups", methods=["GET", "POST"])
@authenticated
def list_groups():
    if request.method == "GET":
        return render_template("groups.html")


@app.route("/groups-xhr", methods=["GET"])
@authenticated
def view_user_groups():
    if request.method == "GET":
        user_groups = list_user_groups(session)
        return jsonify(user_groups)


@app.route("/get-group-info-xhr/<group_name>", methods=["GET"])
@authenticated
def get_group_info_xhr(group_name):
    if request.method == "GET":
        group_info = get_group_info(group_name)
        app.logger.debug(group_info)
        return jsonify(group_info)


@app.route("/groups-profile-members-xhr/<group_name>", methods=["GET"])
@authenticated
def groups_profile_members_xhr(group_name):
    if request.method == "GET":
        group_members = get_group_members(group_name)
        return jsonify(group_members)


@app.route("/public-groups", methods=["GET", "POST"])
@authenticated
def list_public_groups():
    if request.method == "GET":
        return render_template("groups_public.html")


@app.route("/public-groups-xhr", methods=["GET"])
def public_groups_ajax():
    public_groups = list_public_groups_request()
    return jsonify(public_groups)


@app.route("/public-groups/<name>", methods=["GET", "POST"])
@authenticated
def view_public_group(name):
    access_token = get_user_access_token(session)
    if request.method == "GET":
        return render_template(
            "groups_public_profile.html", name=name, minislate_user=minislate_user
        )


@app.route("/public-groups-xhr/<name>", methods=["GET"])
def view_public_group_ajax(name):
    group_info = get_group_info(name)
    group_clusters = get_group_clusters(name)
    try:
        group_clusters = group_clusters["items"]
    except:
        group_clusters = []
    return jsonify(group_info, group_clusters)
