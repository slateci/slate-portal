import globus_sdk

from service import app


def load_auth_client():
    """Create a Globus Auth client from config info"""
    return globus_sdk.ConfidentialAppAuthClient(
        app.config['CLIENT_ID'], app.config['CLIENT_SECRET'])


def get_token(header):
    return header.split(' ')[1].strip()
