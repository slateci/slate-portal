from flask import g, request

from resource_server import app
from resource_server.decorators import authenticated
from resource_server.utils import get_dependent_tokens


@app.route('/api/doit', methods=['POST'])
@authenticated
def doit():
    get_dependent_tokens(g.req_token)

    return request.headers.get('Authorization', '')


@app.route('/api/cleanup', methods=['POST'])
@authenticated
def cleanup():
    return request.headers.get('Authorization', '')
