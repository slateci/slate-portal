
import flask

from portal import app
from portal.decorators import authenticated

# http://128.135.158.222:18080/v1alpha1/users?token=3acc9bdc-1243-40ea-96df-373c8a616a16

# https://api-dev.slateci.io:18080/v1alpha2/vos/slate-dev/clusters?token=user_epmivg01IoM

@app.route('/vo_clusters/slate-dev', methods=['GET', 'POST'])
@authenticated
def get_vo_clusters():
    """
    Get information for a specified user and return
    it in as json or jsonp

    :return: json or jsonp status of user information
    """

    slate_user_id = session['slate_id']
    token_query = {'token': 'user_epmivg01IoM'}

    # url = "https://api-dev.slateci.io:18080/v1alpha2/vos/" + name + "/clusters?token=" + session['slate_id']
    result = {}
    testData = requests.get("https://api-dev.slateci.io:18080/v1alpha2/vos/slate-dev/clusters", params=token_query)
    testData = testData.json()['items']
    for item in testData:
        cluster = item['metadata']
        sanitized_obj = {'name': cluster.name,
                            'id': cluster.id,
                            'owningVO': cluster.owningVO}
        return flask.jsonify(sanitized_obj)
    return flask.jsonify(result), 404
