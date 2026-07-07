import os
import requests

from scripts.common.auth import get_access_token
from scripts.common.api import get_api_url
from scripts.common.logger import log

def main():

    token = get_access_token()
    api_url = get_api_url()

    iflow_id = os.environ["IFLOW_ID"]
    version = os.environ.get("IFLOW_VERSION", "active")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    deploy_url = (
        f"{api_url}/api/v1/"
        f"DeployIntegrationDesigntimeArtifact"
        f"?Id='{iflow_id}'&Version='{version}'"
    )

    log(f"Deploying {iflow_id}...")

    response = requests.post(deploy_url, headers=headers)

    print(response.status_code)
    print(response.text)

    response.raise_for_status()
    task_id = response.text.strip()

    log(f"Task ID : {task_id}")

    with open(os.environ["GITHUB_ENV"], "a") as env:
    env.write(f"TASK_ID={task_id}\n")

    log("Deployment request submitted successfully.")

if __name__ == "__main__":
    main()