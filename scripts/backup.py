import os
import shutil
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

# ======================================================
# Configuration
# ======================================================

CLIENT_ID = os.environ["BTP_CLIENT_ID"]
CLIENT_SECRET = os.environ["BTP_CLIENT_SECRET"]
TOKEN_URL = os.environ["BTP_TOKEN_URL"]
API_URL = os.environ["BTP_API_URL"].rstrip("/")

# ======================================================
# Create Backup Folders
# ======================================================

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

history_folder = f"backup/history/{timestamp}"
latest_folder = "backup/latest"

os.makedirs(history_folder, exist_ok=True)
os.makedirs(latest_folder, exist_ok=True)

print("=" * 60)
print("SAP CPI Backup Started")
print("=" * 60)

# ======================================================
# OAuth Authentication
# ======================================================

print("\n[1/4] Getting OAuth Token...")

response = requests.post(
    TOKEN_URL,
    data={"grant_type": "client_credentials"},
    auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET),
)

response.raise_for_status()

token = response.json()["access_token"]

headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json",
}

print("Authentication Successful")

# ======================================================
# Fetch Packages
# ======================================================

print("\n[2/4] Fetching Integration Packages...")

packages_response = requests.get(
    f"{API_URL}/api/v1/IntegrationPackages",
    headers=headers,
)

packages_response.raise_for_status()

packages = packages_response.json()["d"]["results"]

print(f"Packages Found : {len(packages)}")

download_count = 0

# ======================================================
# Download Artifacts
# ======================================================

print("\n[3/4] Downloading Artifacts...\n")

for package in packages:

    package_id = package["Id"]

    print(f"Package : {package_id}")

    artifacts_response = requests.get(
        f"{API_URL}/api/v1/IntegrationPackages('{package_id}')/IntegrationDesigntimeArtifacts",
        headers=headers,
    )

    if artifacts_response.status_code != 200:
        print("Unable to fetch artifacts")
        continue

    artifacts = artifacts_response.json()["d"]["results"]

    for artifact in artifacts:

        artifact_id = artifact["Id"]

        print(f"   Downloading -> {artifact_id}")

        download_url = (
            f"{API_URL}/api/v1/"
            f"IntegrationDesigntimeArtifacts(Id='{artifact_id}',Version='active')/$value"
        )

        zip_response = requests.get(
            download_url,
            headers={"Authorization": f"Bearer {token}"},
        )

        if zip_response.status_code == 200:

            history_file = os.path.join(
                history_folder,
                f"{artifact_id}.zip",
            )

            with open(history_file, "wb") as file:
                file.write(zip_response.content)

            shutil.copy2(
                history_file,
                os.path.join(latest_folder, f"{artifact_id}.zip"),
            )

            download_count += 1

# ======================================================
# Summary
# ======================================================

print("\n[4/4] Backup Summary")

print("-" * 60)

print(f"Packages Processed : {len(packages)}")
print(f"Artifacts Downloaded : {download_count}")

print(f"History Folder : {history_folder}")
print(f"Latest Folder  : {latest_folder}")

print("\nBackup Completed Successfully")

print("=" * 60)