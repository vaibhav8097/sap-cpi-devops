import json
import os
import shutil
from datetime import datetime

import requests

from scripts.common.auth import get_access_token
from scripts.common.api import get_api_url
from scripts.common.logger import log
from scripts.common.utils import create_folder


def main():

    # ==========================================================
    # Create Backup Folders
    # ==========================================================

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    history_folder = os.path.join("backup", "history", timestamp)
    latest_folder = os.path.join("backup", "latest")
    reports_folder = "reports"

    create_folder(history_folder)
    create_folder(latest_folder)
    create_folder(reports_folder)

    log("=" * 60)
    log("SAP CPI Enterprise Backup Started")
    log("=" * 60)

    # ==========================================================
    # Authentication
    # ==========================================================

    log("[1/4] Authenticating...")

    token = get_access_token()
    api_url = get_api_url()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }

    log("Authentication Successful")

    # ==========================================================
    # Fetch Packages
    # ==========================================================

    log("[2/4] Fetching Integration Packages...")

    response = requests.get(
        f"{api_url}/api/v1/IntegrationPackages",
        headers=headers,
    )

    response.raise_for_status()

    packages = response.json()["d"]["results"]

    log(f"Packages Found : {len(packages)}")

    package_count = 0
    artifact_count = 0
    failed_downloads = 0

    # ==========================================================
    # Download Packages
    # ==========================================================

    log("[3/4] Downloading Integration Artifacts...")

    for package in packages:

        package_count += 1

        package_id = package["Id"]

        log("")
        log(f"Processing Package : {package_id}")

        package_history = os.path.join(history_folder, package_id)
        package_latest = os.path.join(latest_folder, package_id)

        create_folder(package_history)
        create_folder(package_latest)

        artifacts_downloaded = []

        artifacts_response = requests.get(
            f"{api_url}/api/v1/IntegrationPackages('{package_id}')/IntegrationDesigntimeArtifacts",
            headers=headers,
        )

        if artifacts_response.status_code != 200:

            log(f"Unable to fetch artifacts for {package_id}")
            continue

        artifacts = artifacts_response.json()["d"]["results"]

        log(f"Artifacts Found : {len(artifacts)}")

        for artifact in artifacts:

            artifact_id = artifact["Id"]

            log(f"Downloading : {artifact_id}")

            download_url = (
                f"{api_url}/api/v1/"
                f"IntegrationDesigntimeArtifacts"
                f"(Id='{artifact_id}',Version='active')/$value"
            )

            zip_response = requests.get(
                download_url,
                headers={
                    "Authorization": f"Bearer {token}"
                },
            )

            if zip_response.status_code == 200:

                history_zip = os.path.join(
                    package_history,
                    f"{artifact_id}.zip",
                )

                with open(history_zip, "wb") as file:
                    file.write(zip_response.content)

                shutil.copy2(
                    history_zip,
                    os.path.join(
                        package_latest,
                        f"{artifact_id}.zip",
                    ),
                )

                artifact_count += 1

                artifacts_downloaded.append(
                    {
                        "artifact": artifact_id,
                        "type": artifact.get("ArtifactType"),
                        "version": artifact.get("Version"),
                    }
                )

            else:

                failed_downloads += 1

                log(f"Failed : {artifact_id}")

        # ======================================================
        # Package Metadata
        # ======================================================

        metadata = {

            "package": package_id,

            "backup_time": timestamp,

            "artifact_count": len(artifacts_downloaded),

            "artifacts": artifacts_downloaded,

            "github": {

                "repository": os.getenv(
                    "GITHUB_REPOSITORY",
                    "Local"
                ),

                "run_id": os.getenv(
                    "GITHUB_RUN_ID",
                    "Manual"
                ),

                "commit": os.getenv(
                    "GITHUB_SHA",
                    "Local"
                )
            }
        }

        with open(
            os.path.join(
                package_history,
                "metadata.json",
            ),
            "w",
        ) as file:

            json.dump(
                metadata,
                file,
                indent=4,
            )

    # ==========================================================
    # Backup Summary
    # ==========================================================

    log("[4/4] Generating Backup Summary...")

    summary = {

        "backup_time": timestamp,

        "packages_processed": package_count,

        "artifacts_downloaded": artifact_count,

        "failed_downloads": failed_downloads,

        "history_folder": history_folder,

        "latest_folder": latest_folder,

        "status": "SUCCESS"
    }

    with open(
        os.path.join(
            reports_folder,
            "backup-summary.json",
        ),
        "w",
    ) as file:

        json.dump(
            summary,
            file,
            indent=4,
        )

    # ==========================================================
    # Console Summary
    # ==========================================================

    log("")
    log("=" * 60)
    log("SAP CPI Backup Completed")
    log("=" * 60)

    log(f"Packages Processed    : {package_count}")
    log(f"Artifacts Downloaded  : {artifact_count}")
    log(f"Failed Downloads      : {failed_downloads}")

    log("")
    log(f"History Folder : {history_folder}")
    log(f"Latest Folder  : {latest_folder}")

    log("")
    log("Backup Summary Generated")
    log("reports/backup-summary.json")

    log("=" * 60)


if __name__ == "__main__":
    main()