import os
import time
import requests

from scripts.common.auth import get_access_token
from scripts.common.api import get_api_url
from scripts.common.logger import log


MAX_RETRIES = 12
WAIT_TIME = 5


def main():

    token = get_access_token()
    api_url = get_api_url()

    task_id = os.environ["TASK_ID"]

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }

    status_url = (
        f"{api_url}/api/v1/"
        f"BuildAndDeployStatus(TaskId='{task_id}')"
    )

    log(f"Checking Deployment Status...")
    log(f"Task ID : {task_id}")

    for attempt in range(MAX_RETRIES):

        response = requests.get(status_url, headers=headers)

        if response.status_code != 200:

            log(f"Attempt {attempt+1} : Status API not ready")

            time.sleep(WAIT_TIME)
            continue

        result = response.json()["d"]

        status = result.get("Status", "UNKNOWN")

        log(f"Current Status : {status}")

        if status.upper() == "SUCCESS":

            log("Deployment Completed Successfully")

            return

        if status.upper() == "FAILED":

            raise Exception("Deployment Failed")

        time.sleep(WAIT_TIME)

    raise Exception("Deployment Timeout")


if __name__ == "__main__":
    main()