from flask import session
import requests
import sys
from geopy.geocoders import Nominatim
# from portal import slate_api_token, slate_api_token

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
    access_token = get_user_access_token(session)
    query = {'token': access_token}
except:
    query = {'token': slate_api_token}

#  Users
def get_user_info(session):
    # test_new_id = 'user_oXa_2vOeAHw'
    # test_original_id = 'user_XYiA5LV1SdA'
    query = {'token': slate_api_token,
             'globus_id': session['primary_identity']}

    profile = requests.get(
        slate_api_endpoint + '/v1alpha3/find_user', params=query)

    profile = profile.json()
    print('Trying to get using info from method: {}'.format(profile))
    user_id = profile['metadata']['id']
    access_token = profile['metadata']['access_token']
    return access_token, user_id


def get_user_id(session):

    query = {'token': slate_api_token,
             'globus_id': session['primary_identity']}

    profile = requests.get(
        slate_api_endpoint + '/v1alpha3/find_user', params=query)

    profile = profile.json()
    user_id = profile['metadata']['id']
    return user_id


def get_user_access_token(session):

    query = {'token': slate_api_token,
             'globus_id': session['primary_identity']}

    profile = requests.get(
        slate_api_endpoint + '/v1alpha3/find_user', params=query)

    profile = profile.json()
    access_token = profile['metadata']['access_token']
    return access_token


def get_user_details(user_id):
    query = {'token': slate_api_token,
             'globus_id': session['primary_identity']}

    user_details = requests.get(
        slate_api_endpoint + '/v1alpha3/users/' + user_id, params=query)

    user_details = user_details.json()
    return user_details


def delete_user(userID, query):
    res = requests.delete(slate_api_endpoint + '/v1alpha3/' + userID, params=query)
    print(res)
    res = res.json()
    print(res)
    return res

def coordsConversion(lat, lon):
    geolocator = Nominatim()
    location = geolocator.reverse("{}, {}".format(lat, lon), timeout=None)
    location_raw = location.raw

    try:
        city = location_raw['address']['city']
    except:
        city = None
    try:
        state = location_raw['address']['state']
    except:
        state = None
    try:
        country = location_raw['address']['country']
    except:
        country = None

    address = [city, state, country]
    readable_address = []
    for i in address:
        if i:
            readable_address.append(i)
    readable_address = ', '.join(readable_address)

    return readable_address


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
    

def get_app_config(app_name):
    response = requests.get(
        slate_api_endpoint + '/v1alpha3/apps/' + app_name, params=query)
    app_config = response.json()

    return app_config


def cluster_allowed_groups(cluster_name, group_name):
    """
    Request query check if a group has access to a cluster
    :cluster_name: str cluster name
    :group_name: str group name
    :return: bool
    """
    response = requests.get(
        slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups/' + group_name, params=query)
    cluster_allowed = response.json()
    accessAllowed = cluster_allowed['accessAllowed']
    return accessAllowed
    

def list_cluster_whitelist(cluster_name):
    """
    Request cluster whitelist
    :cluster_name: str cluster name
    :group_name: str group name
    :return: bool
    """
    response = requests.get(
        slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name + '/allowed_groups', params=query)
    cluster_whitelist = response.json()
    # print("WHITE LIST {}".format(cluster_whitelist))
    return cluster_whitelist


def list_public_groups_request():
    """
    Returns list of all public groups on slate
    :return: list of public groups
    """
    public_groups = requests.get(
        slate_api_endpoint + '/v1alpha3/groups', params=query)
    public_groups = public_groups.json()['items']
    return public_groups


def get_group_info(group_name):
    """
    Returns group info
    :return:
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    group_info = requests.get(
        slate_api_endpoint + '/v1alpha3/groups/' + group_name, params=query)
    group_info = group_info.json()
    return group_info


def get_group_clusters(group_name):
    """
    Returns list of clusters administered by group
    :return: list
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    group_clusters = requests.get(
        slate_api_endpoint + '/v1alpha3/groups/' + group_name + '/clusters', params=query)
    group_clusters = group_clusters.json()
    return group_clusters


def get_group_members(group_name):
    """
    Returns list of members of group
    :return: list of members belonging to group
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    group_members = requests.get(
        slate_api_endpoint + '/v1alpha3/groups/' + group_name + '/members', params=query)
    group_members = group_members.json()
    return group_members


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
    slate_user_id = get_user_id(session)
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
        user_groups.append(groups['metadata']['name'])
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
            slate_api_endpoint + '/v1alpha3/groups/'
            + connect_name(group_name) + '/members', params=query)
    memberships = group_members.json()['memberships']
    memberships = [member for member in memberships if member['state'] == 'admin']

    return memberships


def get_cluster_info(cluster_name, nodes=False):
    access_token = get_user_access_token(session)
    if nodes:
        query = {'token': access_token, 'nodes': nodes}
    else:
        query = {'token': access_token}
    # try:
    print("Querying cluster info...")
    try:
        cluster = requests.get(slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name, params=query, timeout=10)
    except:
        print("Got past query...")
        cluster = 504
    # except Exception as ex:
    #     print("Timedout: {}".format(ex.__dict__))
    print("Response from querying cluter info: {}".format(cluster))

    if cluster == 504:
        print("At least we found the error response: {}".format(cluster))
        return 504
    else:
        cluster = cluster.json()
        print("Response JSON: {}".format(cluster))
        return cluster

def cluster_exists(cluster_name):
    print("Querying list of existing clusters...")
    clusters = list_clusters_request()
    print("Checking if cluster {} exists in current clusters...".format(cluster_name))
    cluster_names = []
    for cluster in clusters:
        cluster_names.append(cluster['metadata']['name'])
    if cluster_name not in cluster_names:
        print("Returning False because did not find {} in {}".format(cluster_name, cluster_names))
        return False
    else:
        print("Found {} in current exisint clusters".format(cluster_name))
        return True

def get_instance_details(instance_id):
    access_token = get_user_access_token(session)
    query = {'token': access_token, 'detailed': True}
    instance_details = requests.get(slate_api_endpoint + '/v1alpha3/instances/' + instance_id, params=query)
    instance_details = instance_details.json()
    return instance_details