import requests

from arrow import utcnow
from base64 import urlsafe_b64encode
from flask import request
from threading import Lock

try:
    from urllib.parse import urlparse, urljoin
except:
    from urlparse import urlparse, urljoin

from portal import app


def basic_auth_header():
    """Generate a Globus Auth compatible basic auth header."""
    auth_config = app.config['GLOBUS_AUTH']
    cid = auth_config['client_id']
    csecret = auth_config['client_secret']

    creds = '{}:{}'.format(cid, csecret)
    basic_auth = urlsafe_b64encode(creds.encode(encoding='UTF-8'))

    return 'Basic ' + basic_auth.decode(encoding='UTF-8')


def is_safe_redirect_url(target):
    """https://security.openstack.org/guidelines/dg_avoid-unvalidated-redirects.html"""  # noqa
    host_url = urlparse(request.host_url)
    redirect_url = urlparse(urljoin(request.host_url, target))

    return redirect_url.scheme in ('http', 'https') and \
        host_url.netloc == redirect_url.netloc


def get_safe_redirect():
    """https://security.openstack.org/guidelines/dg_avoid-unvalidated-redirects.html"""  # noqa
    url = request.args.get('next')
    if url and is_safe_redirect_url(url):
        return url

    url = request.referrer
    if url and is_safe_redirect_url(url):
        return url

    return '/'


def get_portal_tokens(
        scopes=['openid', 'urn:globus:auth:scope:demo-resource-server:all']):
    """
    Uses the client_credentials grant to get access tokens on the
    Portal's "client identity."
    """
    with get_portal_tokens.lock:
        if not get_portal_tokens.access_tokens:
            get_portal_tokens.access_tokens = {}

        client_id = app.config['GLOBUS_AUTH']['client_id']
        secret = app.config['GLOBUS_AUTH']['client_secret']
        url = app.config['GLOBUS_AUTH']['token_uri']
        data = {
            'grant_type': 'client_credentials',
            'scope': ' '.join(scopes)
        }

        resp = requests.post(url, auth=(client_id, secret), data=data)
        resp = resp.json()

        get_portal_tokens.access_tokens.update({
            resp['resource_server']: {
                'token': resp['access_token'],
                'scope': resp['scope'],
                'expires_at': utcnow().replace(
                    seconds=+resp['expires_in'])
            }
        })

        for token in resp['other_tokens']:
            get_portal_tokens.access_tokens.update({
                token['resource_server']: {
                    'token': token['access_token'],
                    'scope': token['scope'],
                    'expires_at': utcnow().replace(
                        seconds=+resp['expires_in'])
                }
            })

        return get_portal_tokens.access_tokens

get_portal_tokens.lock = Lock()
get_portal_tokens.access_tokens = None
