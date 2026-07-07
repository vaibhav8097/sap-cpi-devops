import json
import os
import requests

from scripts.common.auth import get_access_token
from scripts.common.api import get_api_url
from scripts.common.logger import log


def call(url, headers):
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    return r.json()["d"]


def main():

    token = get_access_token()
    api_url = get_api_url()

    iflow = os.environ["IFLOW_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    log(f"Discovering {iflow}")

    artifact = call(
        f"{api_url}/api/v1/IntegrationDesigntimeArtifacts(Id='{iflow}',Version='active')",
        headers
    )

    report = {}

    report["Id"] = artifact.get("Id")
    report["Name"] = artifact.get("Name")
    report["Version"] = artifact.get("Version")
    report["Package"] = artifact.get("PackageId")
    report["Type"] = artifact.get("ArtifactType")
    report["ModifiedBy"] = artifact.get("ModifiedBy")
    report["ModifiedAt"] = artifact.get("ModifiedAt")

    os.makedirs("reports/inventory", exist_ok=True)

    file = f"reports/inventory/{iflow}.json"

    with open(file, "w") as f:
        json.dump(report, f, indent=4)

    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    main()