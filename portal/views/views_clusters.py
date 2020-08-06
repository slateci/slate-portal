from portal.decorators import authenticated
from portal import app, slate_api_token, slate_api_endpoint
import json
import requests
import time
from flask import (render_template, request, session, jsonify, redirect, flash, url_for)
from connect_api import (list_clusters_request, coordsConversion, 
                         get_user_access_token, get_cluster_info, 
                         get_group_members, list_cluster_whitelist)


@app.route('/clusters', methods=['GET'])
@authenticated
def list_clusters():
    """
    - List Clusters Registered on SLATE
    """
    if request.method == 'GET':
        return render_template('clusters.html')


@app.route('/clusters-xhr', methods=['GET'])
@authenticated
def list_clusters_xhr():
    """
    - List Clusters Registered on SLATE (json response)
    """
    if request.method == 'GET':
        slate_clusters, cluster_status_dict = list_clusters_dict_request(session)
        return jsonify(slate_clusters, cluster_status_dict)


def list_clusters_dict_request(session):
    """
    - Get Clusters and Status on SLATE
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token}
    # Sorted ordered list of clusters on slate
    slate_clusters = list_clusters_request()
    slate_clusters.sort(key=lambda e: e['metadata']['name'])

    multiplexJson = {}
    for cluster in slate_clusters:
        cluster_name = cluster['metadata']['name']
        cluster_status_query = "/v1alpha3/clusters/"+cluster_name+"/ping?token="+query['token']+"&cache"
        multiplexJson[cluster_status_query] = {"method":"GET"}
    # POST request for multiplex return
    multiplex = requests.post(
        slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
    multiplex = multiplex.json()

    cluster_status_dict = {}
    for cluster in multiplex:
        cluster_name = cluster.split('/')[3]
        cluster_status_dict[cluster_name] = json.loads(multiplex[cluster]['body'])['reachable']
    return slate_clusters, cluster_status_dict


@app.route('/clusters/<name>', methods=['GET'])
@authenticated
def view_public_cluster(name):
    """
    - List Clusters Registered on SLATE
    """
    if request.method == 'GET':
        return render_template('cluster_public_profile.html', name=name)


@app.route('/public-clusters-xhr/<name>', methods=['GET'])
@authenticated
def list_public_clusters_xhr(name):
    """
    - List User's Instances Registered on SLATE (json response)
    """
    if request.method == 'GET':
        cluster, owningGroupEmail, allowed_groups, cluster_status, storageClasses, priorityClasses = list_public_clusters_request(session, name)
        return jsonify(cluster, owningGroupEmail, allowed_groups, cluster_status, storageClasses, priorityClasses)


def list_public_clusters_request(session, name):
    """
    Request query to get public cluster's information
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token}
    # Get cluster whitelist and parse allowed groups
    whitelist = list_cluster_whitelist(name)
    allowed_groups = [item for item in whitelist['items']]

    # Get cluster info and parse below
    cluster = get_cluster_info(name, nodes=True)
    # print("Cluster Info: {}".format(cluster))

    # Get owning group information for contact info
    owningGroupName = cluster['metadata']['owningGroup']
    owningGroup = requests.get(
        slate_api_endpoint + '/v1alpha3/groups/' + owningGroupName, params=query)
    owningGroup = owningGroup.json()
    owningGroupEmail = owningGroup['metadata']['email']

    storageClasses = cluster['metadata']['storageClasses']
    priorityClasses = cluster['metadata']['priorityClasses']

    # Get Cluster status and return as string for flask template
    cluster_status = get_cluster_status(name)
    cluster_status = str(cluster_status)

    return cluster, owningGroupEmail, allowed_groups, cluster_status, storageClasses, priorityClasses


@app.route('/clusters/<cluster_name>/<node_name>', methods=['GET'])
@authenticated
def view_node_details(cluster_name, node_name):
    return render_template('cluster_node_details.html', cluster_name=cluster_name, node_name=node_name)


@app.route('/cluster-status-xhr/<cluster_name>', methods=['GET'])
@authenticated
def get_cluster_status_xhr(cluster_name):
    """
    - List Clusters Registered on SLATE (json response)
    """
    if request.method == 'GET':
        cluster_status = get_cluster_status(cluster_name)
        # print(cluster_status)
        return jsonify(cluster_status)


def get_cluster_status(cluster_name):
    """
    - Get Clusters and Status on SLATE
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token, 'cache': 'cache'}

    cluster_status_query = requests.get(
            slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/ping', params=query)
    cluster_status_query = cluster_status_query.json()
    cluster_status = cluster_status_query['reachable']
    
    return cluster_status


@app.route('/get-cluster-info-xhr/<cluster_name>', methods=['GET'])
@authenticated
def get_cluster_info_xhr(cluster_name):
    cluster_info = get_cluster_info(cluster_name)
    cluster_status = get_cluster_status(cluster_name)
    # print(cluster_info, cluster_status)
    return jsonify(cluster_info, cluster_status)