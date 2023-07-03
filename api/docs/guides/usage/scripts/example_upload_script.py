import json
import os

import requests
from requests.auth import HTTPBasicAuth


CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
BASE_URL = os.environ["BASE_URL"]
DOMAIN = os.environ["DOMAIN"]
DATASET = os.environ["DATASET"]
LOCAL_FILEPATH = os.environ["LOCAL_FILEPATH"]


def fetch_token():
    auth = HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    payload = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
    }

    response = requests.post(
        BASE_URL + "/oauth2/token", auth=auth, headers=headers, json=payload
    )

    return json.loads(response.content.decode("utf-8"))["access_token"]


def upload_dataset(token: str, domain: str, dataset: str):
    post_url = f"{BASE_URL}/datasets/{domain}/{dataset}"
    headers = {"Authorization": "Bearer " + token}
    filename = os.path.basename(LOCAL_FILEPATH)
    files = {"file": (filename, open(LOCAL_FILEPATH, "rb"))}
    response = requests.post(post_url, headers=headers, files=files)
    return response.status_code, json.loads(response.content.decode("utf-8"))


token = fetch_token()
upload_dataset(token, DOMAIN, DATASET)
