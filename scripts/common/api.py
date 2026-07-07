import os


def get_api_url():
    """
    Returns SAP Integration Suite API URL
    """

    return os.environ["BTP_API_URL"].rstrip("/")