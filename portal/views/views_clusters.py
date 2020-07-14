from portal.decorators import authenticated
from portal import app
import json
import requests
import time
from flask import (render_template, request, session, jsonify)
from connect_api import (list_clusters_request, coordsConversion, get_user_access_token)

try:
    # Read endpoint and token from VM
    f = open("/etc/slate/secrets/slate_api_token.txt", "r")
    g = open("slate_api_endpoint.txt", "r")
except:
    # Read endpoint and token local
    f = open("secrets/slate_api_token.txt", "r")
    g = open("secrets/slate_api_endpoint.txt", "r")

slate_api_token = f.read().split()[0]
slate_api_endpoint = g.read().split()[0]


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
        # print(slate_clusters)
        # for cluster in slate_clusters:
        #     lat = cluster['metadata']['location'][0]['lat']
        #     lon = cluster['metadata']['location'][0]['lon']
        #     readable_address = coordsConversion(lat, lon)
        #     cluster['metadata']['coordsConversion'] = readable_address
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
        access_token = get_user_access_token(session)
        query = {'token': access_token}

        cluster_query = "/v1alpha3/clusters/"+name+"?token="+query['token']
        # Set up multiplex JSON
        multiplexJson = {cluster_query: {"method":"GET"}}
        # POST request for multiplex return
        multiplex = requests.post(
            slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
        multiplex = multiplex.json()

        # cluster = ast.literal_eval(multiplex[cluster_query]['body'])
        cluster = json.loads(multiplex[cluster_query]['body'])
        try:
            lat = cluster['metadata']['location'][0]['lat']
            lon = cluster['metadata']['location'][0]['lon']
        except:
            lat = 0
            lon = 0
        address = coordsConversion(lat, lon)

        return render_template('cluster_public_profile.html', name=name, address=address)


@app.route('/public-clusters-xhr/<name>', methods=['GET'])
@authenticated
def list_public_clusters_xhr(name):
    """
    - List User's Instances Registered on SLATE (json response)
    """
    if request.method == 'GET':
        cluster, owningGroupEmail, allowed_groups, cluster_status = list_public_clusters_request(session, name)
        return jsonify(cluster, owningGroupEmail, allowed_groups, cluster_status)


def list_public_clusters_request(session, name):
    """
    Request query to get public cluster's information
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    cluster_query = "/v1alpha3/clusters/"+name+"?token="+query['token']
    allowed_groups_query = "/v1alpha3/clusters/"+name+"/allowed_groups?token="+query['token']
    cluster_status_query = "/v1alpha3/clusters/"+name+"/ping?token="+query['token']+"&cache"

    # Set up multiplex JSON
    multiplexJson = {cluster_query: {"method":"GET"},
                        allowed_groups_query: {"method":"GET"},
                        cluster_status_query: {"method":"GET"}}
    # POST request for multiplex return
    multiplex = requests.post(
        slate_api_endpoint + '/v1alpha3/multiplex', params=query, json=multiplexJson)
    multiplex = multiplex.json()

    # Parse post return for apps, clusters, and pub groups
    allowed_groups_json = json.loads(multiplex[allowed_groups_query]['body'])
    allowed_groups = [item for item in allowed_groups_json['items']]
    cluster = json.loads(multiplex[cluster_query]['body'])

    # Get owning group information for contact info
    owningGroupName = cluster['metadata']['owningGroup']
    owningGroup = requests.get(
        slate_api_endpoint + '/v1alpha3/groups/' + owningGroupName, params=query)
    owningGroup = owningGroup.json()
    owningGroupEmail = owningGroup['metadata']['email']
    
    # Get Cluster status from multiplex
    cluster_status = json.loads(multiplex[cluster_status_query]['body'])
    cluster_status = str(cluster_status['reachable'])

    return cluster, owningGroupEmail, allowed_groups, cluster_status