import os
import requests
from requests.auth import HTTPBasicAuth

CLIENT_ID = os.environ["BTP_CLIENT_ID"]
CLIENT_SECRET = os.environ["BTP_CLIENT_SECRET"]
TOKEN_URL = os.environ["BTP_TOKEN_URL"]
API_URL = os.environ["BTP_API_URL"].rstrip("/")

print("Getting OAuth Token...")

response = requests.post(
    TOKEN_URL,
    data={"grant_type": "client_credentials"},
    auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
)

response.raise_for_status()

token = response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

print("Fetching Packages...")

packages = requests.get(
    f"{API_URL}/api/v1/IntegrationPackages",
    headers=headers,
)

packages.raise_for_status()

package_list = packages.json()["d"]["results"]

print(f"Packages Found : {len(package_list)}")

os.makedirs("backup/artifacts", exist_ok=True)

for package in package_list:

    package_id = package["Id"]

    print(f"\nPackage : {package_id}")

    url = f"{API_URL}/api/v1/IntegrationPackages('{package_id}')/IntegrationDesigntimeArtifacts"

    artifacts = requests.get(url, headers=headers)

    if artifacts.status_code != 200:
        continue

    artifact_list = artifacts.json()["d"]["results"]

    for artifact in artifact_list:

        artifact_id = artifact["Id"]

        print(f"Downloading : {artifact_id}")

        download = f"{API_URL}/api/v1/IntegrationDesigntimeArtifacts(Id='{artifact_id}',Version='active')/$value"

        zipfile = requests.get(
            download,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        if zipfile.status_code == 200:

            with open(
                f"backup/artifacts/{artifact_id}.zip",
                "wb"
            ) as f:

                f.write(zipfile.content)

print("\nBackup Completed Successfully")