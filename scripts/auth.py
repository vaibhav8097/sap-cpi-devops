import requests
from requests.auth import HTTPBasicAuth
from config.config import *

response = requests.post(
    TOKEN_URL,
    data={"grant_type": "client_credentials"},
    auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
)

response.raise_for_status()

token = response.json()["access_token"]

print(token)