from flask import session
import requests
import sys

sys.path.insert(0, '/etc/slate/secrets')

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

try:
    query = {'token': session['slate_token']}
except:
    query = {'token': slate_api_token}


def connect_name(group_name):
    """
    Returns string of root connect name, i.e. cms, osg, atlas, spt, etc.
    :param group_name: unix string name of group
    :return: string of connect name
    """
    connect_name = '.'.join(group_name.split('.')[:2])
    return connect_name


def query_status_code(query_response):
    if query_response.status_code == requests.codes.ok:
        query_return = query_response.json()['items']
    else:
        query_return = []
    return query_return


def list_applications_request():
    """
    Returns list of all applications on slate
    :return: list of slate applications
    """
    applications = requests.get(
        slate_api_endpoint + '/v1alpha3/apps')
    applications = query_status_code(applications)
    return applications


def list_incubator_applications_request():
    """
    Request query to list incubator applications information
    """
    incubator_apps = requests.get(
        slate_api_endpoint + '/v1alpha3/apps?dev=true')
    # incubator_apps = incubator_apps.json()['items']
    incubator_apps = query_status_code(incubator_apps)
    return incubator_apps


def list_public_groups_request():
    """
    Returns list of all public groups on slate
    :return: list of public groups
    """
    public_groups = requests.get(
        slate_api_endpoint + '/v1alpha3/groups', params=query)
    public_groups = public_groups.json()['items']
    return public_groups


def list_clusters_request():
    """
    Returns list of all clusters on slate
    :return: list of slate clusters
    """
    clusters = requests.get(
        slate_api_endpoint + '/v1alpha3/clusters', params=query)
    clusters = clusters.json()['items']
    return clusters


def list_instances_request():
    """
    Returns list of all instances on slate
    :return: list of slate instances
    """
    instances = requests.get(
        slate_api_endpoint + '/v1alpha3/instances', params=query)
    instances = instances.json()['items']
    return instances


def list_user_groups(session):
    """
    Returns list of groups that user belongs in

    :param session: session from User accessing information
    :return: list of user's groups
    """
    # Get groups to which the user belongs
    slate_user_id = session['slate_id']
    user_groups = requests.get(
        slate_api_endpoint + '/v1alpha3/users/'
        + slate_user_id + '/groups', params=query)
    user_groups = user_groups.json()['items']
    return user_groups


def list_users_instances_request(session):
    """
    Returns sorted list of instances associated with specific user

    :param session: session from User accessing information
    :return: list of instances belonging to a specific user
    """
    # Get list of all instances
    instances = list_instances_request()
    # Get groups to which the user belongs
    user_groups_list = list_user_groups(session)
    user_groups = []
    # Set up nice list of user group's name
    for groups in user_groups_list:
        user_groups.append(groups['metadata']['name'].encode('utf-8'))
    # Logic to isolate instances belonging to specific user
    user_instances = []
    for instance in instances:
        if instance['metadata']['group'] in user_groups:
            user_instances.append(instance)
    # Return list of instances in sorted order
    sorted_instances = sorted(
                        user_instances, key=lambda i: i['metadata']['name'])
    return sorted_instances


def list_connect_admins(group_name):
    """
    Return list of admins of connect group
    Return list of nested dictionaries with state, user_name, and state_set_by
    """
    query = {'token': slate_api_token}
    group_members = requests.get(
            slate_api_endpoint + '/v1alpha1/groups/'
            + connect_name(group_name) + '/members', params=query)
    memberships = group_members.json()['memberships']
    memberships = [member for member in memberships if member['state'] == 'admin']

    return memberships
