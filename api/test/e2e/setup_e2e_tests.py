import json
import os
from dotenv import load_dotenv

import requests
from requests.auth import HTTPBasicAuth

load_dotenv()


PATH = os.path.dirname(os.path.realpath(__file__))
SCHEMA_PATH = os.path.join(PATH, "test_files/schemas")
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
BASE_URL = os.environ["BASE_URL"]


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

    print(response.content)

    return json.loads(response.content.decode("utf-8"))["access_token"]


def upload_schema(token: str, schema: dict):
    post_url = f"{BASE_URL}/schema"
    headers = {"Authorization": "Bearer " + token}
    response = requests.post(post_url, headers=headers, json=schema)
    return response.status_code, json.loads(response.content.decode("utf-8"))


def create_protected_domain(token: str, domain: str):
    post_url = f"{BASE_URL}/protected_domains/{domain}"
    headers = {"Authorization": "Bearer " + token}
    response = requests.post(post_url, headers=headers)
    return response.status_code, json.loads(response.content.decode("utf-8"))


def upload_dataset(token: str, file_path: str, domain: str, dataset: str):
    post_url = f"{BASE_URL}/datasets/{domain}/{dataset}"
    headers = {"Authorization": "Bearer " + token}
    filename = os.path.basename(file_path)
    files = {"file": (filename, open(file_path, "rb"))}
    response = requests.post(post_url, headers=headers, files=files)
    return response.status_code, json.loads(response.content.decode("utf-8"))


print("Script starting")
token = fetch_token()

files = os.listdir(SCHEMA_PATH)
print(create_protected_domain(token, "test_e2e_protected"))
for file in files:
    with open(os.path.join(SCHEMA_PATH, file), "r") as f:
        schema = json.load(f)
        print(f)
        res = upload_schema(token, schema)
        print(res)

print(
    upload_dataset(
        token, os.path.join(PATH, "test_journey_file.csv"), "test_e2e", "query"
    )
)

print(
    upload_dataset(
        token,
        os.path.join(PATH, "test_journey_file.csv"),
        "test_e2e_protected",
        "do_not_delete",
    )
)
print("Script finished successfuly")
