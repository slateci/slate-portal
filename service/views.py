from flask import g, request

from service import app
from service.decorators import authenticated
from service.utils import get_dependent_tokens


@app.route('/api/doit', methods=['POST'])
@authenticated
def doit():
    get_dependent_tokens(g.req_token)

    return request.headers.get('Authorization', '')


@app.route('/api/cleanup', methods=['POST'])
@authenticated
def cleanup():
    return request.headers.get('Authorization', '')
