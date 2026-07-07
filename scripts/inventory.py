import os
import json
import csv
import requests

from scripts.common.auth import get_access_token
from scripts.common.api import get_api_url
from scripts.common.logger import log


def main():

    token = get_access_token()
    api_url = get_api_url()

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    os.makedirs("reports/inventory", exist_ok=True)

    log("Reading Integration Packages...")

    packages = requests.get(
        f"{api_url}/api/v1/IntegrationPackages",
        headers=headers
    )

    packages.raise_for_status()

    packages = packages.json()["d"]["results"]

    inventory = []

    for package in packages:

        package_id = package["Id"]

        log(f"Package : {package_id}")

        artifacts = requests.get(
            f"{api_url}/api/v1/IntegrationPackages('{package_id}')/IntegrationDesigntimeArtifacts",
            headers=headers
        )

        artifacts.raise_for_status()

        artifacts = artifacts.json()["d"]["results"]

        for artifact in artifacts:

            inventory.append({

                "Package": package_id,

                "Artifact": artifact["Id"],

                "Name": artifact.get("Name"),

                "Version": artifact.get("Version"),

                "Type": artifact.get("ArtifactType")
            })

    with open("reports/inventory/inventory.json","w") as file:
        json.dump(inventory,file,indent=4)

    with open("reports/inventory/inventory.csv","w",newline="") as file:

        writer=csv.DictWriter(
            file,
            fieldnames=[
                "Package",
                "Artifact",
                "Name",
                "Version",
                "Type"
            ])

        writer.writeheader()

        writer.writerows(inventory)

    log(f"Total Packages : {len(packages)}")
    log(f"Total Artifacts : {len(inventory)}")

    log("Inventory Report Generated Successfully")


if __name__=="__main__":
    main()