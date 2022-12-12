from portal import app
from flask import session
import requests
import sys
from geopy.geocoders import Nominatim
from portal import slate_api_token, slate_api_endpoint, minislate_user

#  Users
def check_user_exists():
    identity_id = session.get('primary_identity')
    query = {'token': slate_api_token,
             'globus_id': identity_id}
    response = requests.get(
            slate_api_endpoint + '/v1alpha3/find_user', params=query)
    return response


def get_user_info(session):
    if minislate_user:
        check_minislate_user()

    query = {'token': slate_api_token,
             'globus_id': session['primary_identity']}

    profile = requests.get(
        slate_api_endpoint + '/v1alpha3/find_user', params=query)

    profile = profile.json()
    app.logger.debug('Trying to get user info from method: {}'.format(profile))
    if minislate_user:
        access_token = session['access_token']
        user_id = session['user_id']
    else:
        user_id = profile['metadata']['id']
        access_token = profile['metadata']['access_token']
    return access_token, user_id


def get_user_id(session):

    query = {'token': slate_api_token,
             'globus_id': session['primary_identity']}

    profile = requests.get(
        slate_api_endpoint + '/v1alpha3/find_user', params=query)

    profile = profile.json()
    if minislate_user:
        user_id = session['user_id']
    else:
        user_id = profile['metadata']['id']
    return user_id


def get_user_access_token(session):

    if minislate_user:
        check_minislate_user()

    query = {'token': slate_api_token,
             'globus_id': session['primary_identity']}
    app.logger.debug("Querying user information using: {}".format(query))
    profile = requests.get(
        slate_api_endpoint + '/v1alpha3/find_user', params=query)
    app.logger.debug("RESPONSE from getting user profile: {}".format(profile))
    profile = profile.json()
    app.logger.debug("JSONIFY Response: {}".format(profile))
    if minislate_user:
        access_token = session['access_token']
    else:
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
    app.logger.debug(res)
    res = res.json()
    app.logger.debug(res)
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
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    response = requests.get(
        slate_api_endpoint + '/v1alpha3/apps/' + app_name, params=query)
    app_config = response.json()

    return app_config


def get_incubator_app_config(app_name):
    try:
        access_token = get_user_access_token(session)
        query = {'token': access_token, 'dev': 'true'}
    except:
        query = {'token': slate_api_token, 'dev': 'true'}

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
    access_token = get_user_access_token(session)
    query = {'token': access_token}

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
    access_token = get_user_access_token(session)
    query = {'token': access_token}

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
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    app.logger.debug("Querying to get public groups...")
    public_groups = requests.get(
        slate_api_endpoint + '/v1alpha3/groups', params=query)
    app.logger.debug("Response: {}".format(public_groups))

    public_groups = public_groups.json()['items']
    app.logger.debug("Public Group items: {}".format(public_groups))
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
    access_token = get_user_access_token(session)
    query = {'token': access_token}

    clusters = requests.get(
        slate_api_endpoint + '/v1alpha3/clusters', params=query)
    clusters = clusters.json()['items']
    return clusters


def list_instances_request():
    """
    Returns list of all instances on slate
    :return: list of slate instances
    """
    access_token = get_user_access_token(session)
    query = {'token': access_token}
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
    access_token = get_user_access_token(session)
    query = {'token': access_token}
    # Get groups to which the user belongs
    slate_user_id = get_user_id(session)
    app.logger.debug("Querying to get user groups with user id: {}".format(slate_user_id))
    user_groups = requests.get(
        slate_api_endpoint + '/v1alpha3/users/'
        + slate_user_id + '/groups', params=query)
    app.logger.debug("Response: {}".format(user_groups))
    user_groups = user_groups.json()['items']
    app.logger.debug("User group items: {}".format(user_groups))
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
    app.logger.debug("Querying cluster info...")
    try:
        cluster = requests.get(slate_api_endpoint + '/v1alpha3/clusters/' + cluster_name, params=query, timeout=10)
    except:
        app.logger.debug("Got past query...")
        cluster = 504
    # except Exception as ex:
    #     print("Timedout: {}".format(ex.__dict__))
    app.logger.debug("Response from querying cluster info: {}".format(cluster))

    if cluster == 504:
        app.logger.debug("At least we found the error response: {}".format(cluster))
        return 504
    else:
        cluster = cluster.json()
        app.logger.debug("Response JSON: {}".format(cluster))
        return cluster

def cluster_exists(cluster_name):
    app.logger.debug("Querying list of existing clusters...")
    clusters = list_clusters_request()
    app.logger.debug("Checking if cluster {} exists in current clusters...".format(cluster_name))
    cluster_names = []
    for cluster in clusters:
        cluster_names.append(cluster['metadata']['name'])
    if cluster_name not in cluster_names:
        app.logger.debug("Returning False because did not find {} in {}".format(cluster_name, cluster_names))
        return False
    else:
        app.logger.debug("Found {} in current existing clusters".format(cluster_name))
        return True

def get_instance_details(instance_id):
    access_token = get_user_access_token(session)
    query = {'token': access_token, 'detailed': True}

    app.logger.debug("Querying instance details...")
    response = requests.get(slate_api_endpoint + '/v1alpha3/instances/' + instance_id, params=query)
    app.logger.debug("Query response: {}".format(response))

    if response.status_code == 504:
        return 504
    else:
        instance_details = response.json()

    return instance_details


def get_instance_logs(instance_id):
    access_token = get_user_access_token(session)
    query = {'token': access_token}
    app.logger.debug("Querying instance logs...")
    response = requests.get(slate_api_endpoint + '/v1alpha3/instances/' + instance_id + '/logs', params=query)
    app.logger.debug("Query response: {}".format(response))
    if response.status_code == 500:
        return 500
    elif response.status_code == requests.codes.ok:
        instance_logs = response.json()
        return instance_logs


def check_minislate_user():
    try:
        # Check location of slate_portal_user file on minislate
        f = open("/slate_portal_user", "r")
        slate_portal_user = f.read().split()

        session['user_id'] = slate_portal_user[0]
        session['name'] = slate_portal_user[1]
        session['email'] = slate_portal_user[2]
        session['phone'] = slate_portal_user[3]
        session['institution'] = slate_portal_user[4]
        session['primary_identity'] = slate_portal_user[5]
        session['access_token'] = slate_portal_user[5]
        session['is_authenticated'] = True
        session['slate_portal_user'] = True

    except:
        session['slate_portal_user'] = False
