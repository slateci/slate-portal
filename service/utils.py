from base64 import urlsafe_b64encode
import requests

from service import app


def basic_auth_header():
    """Generate a Globus Auth compatible basic auth header."""
    cid = app.config['GA_CLIENT_ID']
    csecret = app.config['GA_CLIENT_SECRET']

    creds = '{}:{}'.format(cid, csecret)
    basic_auth = urlsafe_b64encode(creds.encode(encoding='UTF-8'))

    return 'Basic ' + basic_auth.decode(encoding='UTF-8')


def get_token(header):
    return header.split(' ')[1].strip()


# Move get_dependent_tokens into views.py
def get_dependent_tokens(token):
    # Call Globus Auth dependent token grant
    # Exercise 2 begin
    url = app.config['GA_TOKEN_URI']
    data = {
        'grant_type': 'urn:globus:auth:grant_type:dependent_token',
        'token': token
    }

    tokens = requests.post(url,
                           headers=dict(Authorization=basic_auth_header()),
                           data=data)
    # Exercise 2 end

    return tokens.json()
