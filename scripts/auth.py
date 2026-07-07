import os
import requests
from requests.auth import HTTPBasicAuth

CLIENT_ID = os.environ["BTP_CLIENT_ID"]
CLIENT_SECRET = os.environ["BTP_CLIENT_SECRET"]
TOKEN_URL = os.environ["BTP_TOKEN_URL"]

response = requests.post(
    TOKEN_URL,
    data={"grant_type": "client_credentials"},
    auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
)

response.raise_for_status()

print("Authentication Successful")
print(response.json())