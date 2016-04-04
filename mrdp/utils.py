from base64 import urlsafe_b64encode
from flask import request

try:
    from urllib.parse import urlparse, urljoin
except:
    from urlparse import urlparse, urljoin

from mrdp import app


def basic_auth_header():
    """Generate a Globus Auth compatible basic auth header."""
    cid = app.config['GA_CLIENT_ID']
    csecret = app.config['GA_CLIENT_SECRET']

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
