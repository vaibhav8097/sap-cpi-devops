import os
import shutil
from datetime import datetime

import requests

from scripts.common.auth import get_access_token
from scripts.common.api import get_api_url
from scripts.common.logger import log
from scripts.common.utils import create_folder


def main():

    # ==========================================
    # Create Backup Folders
    # ==========================================

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    history_folder = os.path.join("backup", "history", timestamp)
    latest_folder = os.path.join("backup", "latest")

    create_folder(history_folder)
    create_folder(latest_folder)

    log("=" * 60)
    log("SAP CPI Backup Started")
    log("=" * 60)

    # ==========================================
    # Authentication
    # ==========================================

    log("[1/4] Authenticating with SAP Integration Suite...")

    token = get_access_token()
    api_url = get_api_url()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    log("Authentication Successful")

    # ==========================================
    # Fetch Packages
    # ==========================================

    log("[2/4] Fetching Integration Packages...")

    packages_response = requests.get(
        f"{api_url}/api/v1/IntegrationPackages",
        headers=headers,
    )

    packages_response.raise_for_status()

    packages = packages_response.json()["d"]["results"]

    log(f"Packages Found : {len(packages)}")

    download_count = 0

    # ==========================================
    # Download Artifacts
    # ==========================================

    log("[3/4] Downloading Integration Artifacts...")

    for package in packages:

        package_id = package["Id"]

        log(f"Processing Package : {package_id}")

        artifacts_response = requests.get(
            f"{api_url}/api/v1/IntegrationPackages('{package_id}')/IntegrationDesigntimeArtifacts",
            headers=headers,
        )

        if artifacts_response.status_code != 200:
            log(f"Unable to fetch artifacts for {package_id}")
            continue

        artifacts = artifacts_response.json()["d"]["results"]

        for artifact in artifacts:

            artifact_id = artifact["Id"]

            log(f"Downloading : {artifact_id}")

            download_url = (
                f"{api_url}/api/v1/"
                f"IntegrationDesigntimeArtifacts(Id='{artifact_id}',Version='active')/$value"
            )

            zip_response = requests.get(
                download_url,
                headers={
                    "Authorization": f"Bearer {token}"
                },
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
                    os.path.join(
                        latest_folder,
                        f"{artifact_id}.zip",
                    ),
                )

                download_count += 1

            else:
                log(f"Failed to download {artifact_id}")

    # ==========================================
    # Summary
    # ==========================================

    log("[4/4] Backup Summary")

    log("-" * 60)

    log(f"Packages Processed : {len(packages)}")
    log(f"Artifacts Downloaded : {download_count}")

    log(f"History Folder : {history_folder}")
    log(f"Latest Folder : {latest_folder}")

    log("Backup Completed Successfully")

    log("=" * 60)


if __name__ == "__main__":
    main()