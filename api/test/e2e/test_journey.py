import json
from abc import ABC
from http import HTTPStatus
from typing import List

import boto3
import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from api.common.config.aws import (
    DATA_BUCKET,
    DOMAIN_NAME,
    AWS_REGION,
    AWS_ACCOUNT,
    RESOURCE_PREFIX,
)
from api.common.config.constants import CONTENT_ENCODING
from test.e2e.e2e_test_utils import get_secret, AuthenticationFailedError
from test.scripts.delete_protected_domain_permission import (
    delete_protected_domain_permission_from_db,
)


class BaseJourneyTest(ABC):
    base_url = f"https://{DOMAIN_NAME}"
    datasets_endpoint = f"{base_url}/datasets"
    schema_endpoint = f"{base_url}/schema"

    e2e_test_domain = "test_e2e"
    layer = "default"
    schemas_directory = "schemas"
    data_directory = f"data/{layer}/{e2e_test_domain}"
    raw_data_directory = f"raw_data/{layer}/{e2e_test_domain}"

    filename = "test_journey_file.csv"

    def upload_dataset_url(self, layer: str, domain: str, dataset: str) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}"

    def query_dataset_url(
        self, layer: str, domain: str, dataset: str, version: int = 0
    ) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/query?version={version}"

    def info_dataset_url(
        self, layer: str, domain: str, dataset: str, version: int = 0
    ) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/info?version={version}"

    def list_dataset_raw_files_url(self, layer: str, domain: str, dataset: str) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/1/files"

    def create_protected_domain_url(self, domain: str) -> str:
        return f"{self.base_url}/protected_domains/{domain}"

    def list_protected_domain_url(self) -> str:
        return f"{self.base_url}/protected_domains"

    def modify_subjects_permissions_url(self) -> str:
        return f"{self.base_url}/subjects/permissions"

    def delete_data_url(
        self, layer: str, domain: str, dataset: str, raw_filename: str
    ) -> str:
        return f"{self.datasets_endpoint}/{layer}/{domain}/{dataset}/1/{raw_filename}"

    def permissions_url(self) -> str:
        return f"{self.base_url}/permissions"

    def subjects_url(self) -> str:
        return f"{self.base_url}/subjects"

    def status_url(self) -> str:
        return f"{self.base_url}/status"


class TestGeneralBehaviour(BaseJourneyTest):
    def test_http_request_is_redirected_to_https(self):
        response = requests.get(self.status_url())
        assert f"https://{DOMAIN_NAME}" in response.url

    def test_status_always_accessible(self):
        api_url = self.status_url()
        response = requests.get(api_url)
        assert response.status_code == HTTPStatus.OK


class TestUnauthenticatedJourneys(BaseJourneyTest):
    def test_query_is_forbidden_when_no_token_provided(self):
        url = self.query_dataset_url(self.layer, "mydomain", "unknowndataset")
        response = requests.post(url)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_upload_is_forbidden_when_no_token_provided(self):
        files = {"file": (self.filename, open("./test/e2e/" + self.filename, "rb"))}
        url = self.upload_dataset_url(self.layer, self.e2e_test_domain, "upload")
        response = requests.post(url, files=files)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_list_is_forbidden_when_no_token_provided(self):
        response = requests.post(self.datasets_endpoint)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_list_permissions_is_forbidden_when_no_token_provided(self):
        response = requests.get(self.permissions_url())
        assert response.status_code == HTTPStatus.FORBIDDEN


class TestUnauthorisedJourney(BaseJourneyTest):
    def setup_class(self):
        token_url = f"https://{DOMAIN_NAME}/oauth2/token"
        write_all_credentials = get_secret(
            secret_name=f"{RESOURCE_PREFIX}_E2E_TEST_CLIENT_WRITE_ALL"
        )

        cognito_client_id = write_all_credentials["CLIENT_ID"]
        cognito_client_secret = write_all_credentials[
            "CLIENT_SECRET"
        ]  # pragma: allowlist secret

        auth = HTTPBasicAuth(cognito_client_id, cognito_client_secret)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        payload = {"grant_type": "client_credentials", "client_id": cognito_client_id}

        response = requests.post(token_url, auth=auth, headers=headers, json=payload)
        res = json.loads(response.content.decode(CONTENT_ENCODING))

        if response.status_code != HTTPStatus.OK:
            raise AuthenticationFailedError(f"{response.status_code}")

        res = json.loads(response.content.decode(CONTENT_ENCODING))
        self.token = res["access_token"]

    # Utils -------------

    def generate_auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    # Tests -------------
    def test_query_existing_dataset_when_not_authorised_to_read(self):
        url = self.query_dataset_url(self.layer, self.e2e_test_domain, "query")
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_existing_dataset_info_when_not_authorised_to_read(self):
        url = self.info_dataset_url(self.layer, self.e2e_test_domain, "query")
        response = requests.get(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_list_permissions_when_not_user_admin(self):
        response = requests.get(
            self.permissions_url(), headers=self.generate_auth_headers()
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


class TestAuthenticatedDataJourneys(BaseJourneyTest):
    s3_client = boto3.client("s3")

    def setup_class(self):
        token_url = f"https://{DOMAIN_NAME}/oauth2/token"

        read_and_write_credentials = get_secret(
            secret_name=f"{RESOURCE_PREFIX}_E2E_TEST_CLIENT_READ_ALL_WRITE_ALL"  # pragma: allowlist secret
        )

        cognito_client_id = read_and_write_credentials["CLIENT_ID"]
        cognito_client_secret = read_and_write_credentials[
            "CLIENT_SECRET"
        ]  # pragma: allowlist secret

        auth = HTTPBasicAuth(cognito_client_id, cognito_client_secret)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        payload = {
            "grant_type": "client_credentials",
            "client_id": cognito_client_id,
        }

        response = requests.post(token_url, auth=auth, headers=headers, json=payload)

        if response.status_code != HTTPStatus.OK:
            raise AuthenticationFailedError(f"{response.status_code}")

        self.token = json.loads(response.content.decode(CONTENT_ENCODING))[
            "access_token"
        ]

    # Utils -------------

    def generate_auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def upload_test_file_to_(self, data_directory: str, dataset: str, filename: str):
        self.s3_client.put_object(
            Bucket=DATA_BUCKET,
            Key=f"{data_directory}/{dataset}/1/{filename}",
            Body=open("./test/e2e/" + self.filename, "rb"),
        )

    # Tests -------------
    def test_list_when_authorised(self):
        response = requests.post(
            self.datasets_endpoint,
            headers=self.generate_auth_headers(),
            json={"tags": {"test": "e2e"}},
        )
        assert response.status_code == HTTPStatus.OK

    def test_uploads_when_authorised(self):
        files = {"file": (self.filename, open("./test/e2e/" + self.filename, "rb"))}
        upload_url = self.upload_dataset_url(self.layer, self.e2e_test_domain, "upload")
        response = requests.post(
            upload_url, headers=self.generate_auth_headers(), files=files
        )

        assert response.status_code == HTTPStatus.ACCEPTED

        raw_filename = json.loads(response.text)["details"]["raw_filename"]
        delete_url = self.delete_data_url(
            self.layer, self.e2e_test_domain, "upload", raw_filename
        )
        requests.delete(delete_url, headers=self.generate_auth_headers())

    def test_gets_existing_dataset_info_when_authorised(self):
        url = self.info_dataset_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset="query", version=1
        )

        response = requests.get(url, headers=(self.generate_auth_headers()))
        assert response.status_code == HTTPStatus.OK

    def test_queries_non_existing_dataset_when_authorised(self):
        url = self.query_dataset_url(self.layer, "mydomain", "unknowndataset")
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_queries_existing_dataset_as_csv_when_authorised(self):
        url = self.query_dataset_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset="query", version=1
        )
        headers = {
            "Accept": "text/csv",
            "Authorization": "Bearer " + self.token,
        }
        response = requests.post(url, headers=headers)
        assert response.status_code == HTTPStatus.OK

    def test_fails_to_query_when_authorised_and_sql_injection_attempted(self):
        url = self.query_dataset_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset="query"
        )
        body = {"filter": "';DROP TABLE test_e2e--"}
        response = requests.post(url, headers=(self.generate_auth_headers()), json=body)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_deletes_existing_data_when_authorised(self):
        # Upload files directly to relevant directories in S3
        self.upload_test_file_to_(
            self.raw_data_directory,
            dataset="delete",
            filename="test_journey_file.csv",
        )
        self.upload_test_file_to_(
            self.data_directory,
            dataset="delete",
            filename="test_journey_file.parquet",
        )

        # Get available raw dataset names
        list_raw_files_url = self.list_dataset_raw_files_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset="delete"
        )
        available_datasets_response = requests.get(
            list_raw_files_url, headers=(self.generate_auth_headers())
        )
        assert available_datasets_response.status_code == HTTPStatus.OK

        response_list = json.loads(available_datasets_response.text)
        assert self.filename in response_list

        # Delete chosen dataset file (raw file and actual data file)
        first_dataset_file = response_list[0]
        delete_raw_data_url = self.delete_data_url(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset="delete",
            raw_filename=first_dataset_file,
        )

        response2 = requests.delete(
            delete_raw_data_url, headers=(self.generate_auth_headers())
        )
        assert response2.status_code == HTTPStatus.NO_CONTENT


class TestAuthenticatedSchemaJourney(BaseJourneyTest):
    glue_client = boto3.client("glue")
    s3_client = boto3.client("s3")

    def generate_auth_headers(self):
        token_url = f"https://{DOMAIN_NAME}/oauth2/token"
        data_admin_credentials = get_secret(
            secret_name=f"{RESOURCE_PREFIX}_E2E_TEST_CLIENT_DATA_ADMIN"  # pragma: allowlist secret
        )
        cognito_client_id = data_admin_credentials["CLIENT_ID"]
        cognito_client_secret = data_admin_credentials[
            "CLIENT_SECRET"
        ]  # pragma: allowlist secret

        auth = HTTPBasicAuth(cognito_client_id, cognito_client_secret)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {
            "grant_type": "client_credentials",
            "client_id": cognito_client_id,
        }
        response = requests.post(token_url, auth=auth, headers=headers, json=payload)
        print(response.content)
        if response.status_code != HTTPStatus.OK:
            raise AuthenticationFailedError(f"{response.status_code}")

        token = json.loads(response.content.decode(CONTENT_ENCODING))["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def upload_schema_version1(self) -> Response:
        with open("./test/e2e/test_files/schemas/test_e2e-update_v1.json") as f:
            schema_v1_json = json.load(f)

        return requests.post(
            self.schema_endpoint,
            headers=self.generate_auth_headers(),
            json=schema_v1_json,
        )

    def upload_schema_version2(self) -> Response:
        with open("./test/e2e/test_files/schemas/test_e2e-update_v2.json") as f:
            schema_v2_json = json.load(f)

        return requests.put(
            self.schema_endpoint,
            headers=self.generate_auth_headers(),
            json=schema_v2_json,
        )

    def test_uploads_new_schema_version(self):
        response1 = self.upload_schema_version1()
        assert response1.status_code in [HTTPStatus.CREATED, HTTPStatus.CONFLICT]

        response2 = self.upload_schema_version2()
        assert response2.status_code == HTTPStatus.OK

        glue_crawler_arn = (
            "arn:aws:glue:{region}:{account_id}:crawler/{glue_crawler}".format(
                region=AWS_REGION,
                account_id=AWS_ACCOUNT,
                glue_crawler=f"{RESOURCE_PREFIX}_crawler/default/test_e2e/update",
            )
        )

        try:
            current_tags = self.glue_client.get_tags(ResourceArn=glue_crawler_arn)[
                "Tags"
            ]
            assert current_tags["no_of_versions"] == "2"
            assert current_tags["sensitivity"] == "PUBLIC"
            assert "new_tag" not in current_tags.keys()
        finally:
            self.s3_client.delete_objects(
                Bucket=DATA_BUCKET,
                Delete={
                    "Objects": [
                        {
                            "Key": f"{self.schemas_directory}/default/PUBLIC/test_e2e/update/1/schema.json"
                        },
                        {
                            "Key": f"{self.schemas_directory}/default/PUBLIC/test_e2e/update/2/schema.json"
                        },
                    ]
                },
            )
            self.glue_client.delete_crawler(
                Name=f"{RESOURCE_PREFIX}_crawler/default/test_e2e/update"
            )


class TestAuthenticatedSubjectJourneys(BaseJourneyTest):
    s3_client = boto3.client("s3")
    cognito_client_id = None

    def setup_class(self):
        token_url = f"https://{DOMAIN_NAME}/oauth2/token"

        read_and_write_credentials = get_secret(
            secret_name=f"{RESOURCE_PREFIX}_E2E_TEST_CLIENT_USER_ADMIN"  # pragma: allowlist secret
        )

        self.cognito_client_id = read_and_write_credentials["CLIENT_ID"]
        cognito_client_secret = read_and_write_credentials[
            "CLIENT_SECRET"
        ]  # pragma: allowlist secret

        auth = HTTPBasicAuth(self.cognito_client_id, cognito_client_secret)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.cognito_client_id,
        }

        response = requests.post(token_url, auth=auth, headers=headers, json=payload)

        if response.status_code != HTTPStatus.OK:
            raise AuthenticationFailedError(f"{response.status_code}")

        self.token = json.loads(response.content.decode(CONTENT_ENCODING))[
            "access_token"
        ]

    # Utils -------------

    def generate_auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def test_lists_all_permissions_contains_all_default_permissions(self):
        response = requests.get(
            self.permissions_url(), headers=self.generate_auth_headers()
        )

        expected_permissions = [
            "READ_ALL",
            "WRITE_ALL",
            "READ_ALL_PUBLIC",
            "WRITE_ALL_PUBLIC",
            "READ_ALL_PRIVATE",
            "WRITE_ALL_PRIVATE",
            "READ_DEFAULT_PUBLIC",
            "WRITE_DEFAULT_PUBLIC",
            "READ_DEFAULT_PRIVATE",
            "WRITE_DEFAULT_PRIVATE",
            "DATA_ADMIN",
            "USER_ADMIN",
        ]

        response_json = response.json()
        assert response.status_code == HTTPStatus.OK
        for permission in expected_permissions:
            assert permission in response_json

    def test_lists_subject_permissions(self):
        response = requests.get(
            f"{self.permissions_url()}/{self.cognito_client_id}",
            headers=self.generate_auth_headers(),
        )

        assert response.status_code == HTTPStatus.OK
        assert response.json() == ["USER_ADMIN"]

    def test_list_all_subjects(self):
        response = requests.get(
            self.subjects_url(),
            headers=self.generate_auth_headers(),
        )

        minimum_expected_names = [
            f"{RESOURCE_PREFIX}_ui_test_user",
            f"{RESOURCE_PREFIX}_e2e_test_client_read_and_write",
            f"{RESOURCE_PREFIX}_e2e_test_client_data_admin",
            f"{RESOURCE_PREFIX}_e2e_test_client_write_all",
            f"{RESOURCE_PREFIX}_e2e_test_client_user_admin",
        ]

        assert response.status_code == HTTPStatus.OK
        returned_subject_names = [
            subject["subject_name"] for subject in response.json()
        ]
        assert all(
            [
                expected_name in returned_subject_names
                for expected_name in minimum_expected_names
            ]
        )


class TestAuthenticatedProtectedDomainJourneys(BaseJourneyTest):
    s3_client = boto3.client("s3")
    cognito_client_id = None

    def setup_class(self):
        token_url = f"https://{DOMAIN_NAME}/oauth2/token"

        read_and_write_credentials = get_secret(
            secret_name=f"{RESOURCE_PREFIX}_E2E_TEST_CLIENT_DATA_ADMIN"  # pragma: allowlist secret
        )

        self.cognito_client_id = read_and_write_credentials["CLIENT_ID"]
        cognito_client_secret = read_and_write_credentials[
            "CLIENT_SECRET"
        ]  # pragma: allowlist secret

        auth = HTTPBasicAuth(self.cognito_client_id, cognito_client_secret)

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.cognito_client_id,
        }

        response = requests.post(token_url, auth=auth, headers=headers, json=payload)

        if response.status_code != HTTPStatus.OK:
            raise AuthenticationFailedError(f"{response.status_code}")

        self.token = json.loads(response.content.decode(CONTENT_ENCODING))[
            "access_token"
        ]

    @classmethod
    def teardown_class(cls):
        delete_protected_domain_permission_from_db("test_e2e")

    # Utils -------------
    def generate_auth_headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def assume_permissions(self, permissions: List[str]):
        modification_url = self.modify_subjects_permissions_url()
        payload = {
            "subject_id": self.cognito_client_id,
            "permissions": ["USER_ADMIN", "DATA_ADMIN", *permissions],
        }

        response = requests.put(
            modification_url, headers=self.generate_auth_headers(), json=payload
        )
        assert response.status_code == HTTPStatus.OK

    def reset_permissions(self):
        self.assume_permissions([])

    # Tests -------------
    def test_create_protected_domain(self):
        self.reset_permissions()
        # Create protected domain
        create_url = self.create_protected_domain_url("test_e2e")
        response = requests.post(create_url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.CREATED

        # Lists created protected domain
        list_url = self.list_protected_domain_url()
        response = requests.get(list_url, headers=self.generate_auth_headers())
        assert "test_e2e" in response.json()

        # Not authorised to access existing protected domain
        url = self.query_dataset_url(
            layer="default", domain="test_e2e_protected", dataset="do_not_delete"
        )
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_allows_access_to_protected_domain_when_granted_permission(self):
        self.assume_permissions(["READ_DEFAULT_PROTECTED_TEST_E2E_PROTECTED"])

        url = self.query_dataset_url("default", "test_e2e_protected", "do_not_delete")
        response = requests.post(url, headers=self.generate_auth_headers())

        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "0": {
                "year": "2017",
                "month": "7",
                "destination": "Leeds",
                "arrival": "London",
                "type": "regular",
                "status": "completed",
            },
            "1": {
                "year": "2017",
                "month": "7",
                "destination": "Darlington",
                "arrival": "Durham",
                "type": "regular",
                "status": "completed",
            },
        }

        self.reset_permissions()
