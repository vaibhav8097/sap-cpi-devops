import os
import requests

from scripts.common.auth import get_access_token
from scripts.common.api import get_api_url
from scripts.common.logger import log


def main():

    token = get_access_token()

    api_url = get_api_url()

    iflow = os.environ["IFLOW_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    url = (
        f"{api_url}/api/v1/"
        f"IntegrationDesigntimeArtifacts"
        f"(Id='{iflow}',Version='active')"
    )

    response = requests.get(url, headers=headers)

    response.raise_for_status()

    data = response.json()["d"]

    print("\n========== iFlow Information ==========")

    print(f"ID          : {data.get('Id')}")
    print(f"Name        : {data.get('Name')}")
    print(f"Version     : {data.get('Version')}")
    print(f"Package     : {data.get('PackageId')}")
    print(f"Type        : {data.get('ArtifactType')}")

    print("=======================================")


if __name__ == "__main__":
    main()