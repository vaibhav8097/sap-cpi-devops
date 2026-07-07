import os
import requests
from requests.auth import HTTPBasicAuth


def get_access_token():
    """
    Returns OAuth Access Token
    """

    client_id = os.environ["BTP_CLIENT_ID"]
    client_secret = os.environ["BTP_CLIENT_SECRET"]
    token_url = os.environ["BTP_TOKEN_URL"]

    response = requests.post(
        token_url,
        data={"grant_type": "client_credentials"},
        auth=HTTPBasicAuth(client_id, client_secret),
    )

    response.raise_for_status()

    return response.json()["access_token"]