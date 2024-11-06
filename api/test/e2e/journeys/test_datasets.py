from http import HTTPStatus

import requests
import pytest
import csv
import json
import os
from io import StringIO
from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)
from test.e2e.utils import get_secret

RESOURCE_PREFIX = os.environ["RESOURCE_PREFIX"]

class TestDataJourneys(BaseAuthenticatedJourneyTest):
    dataset = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_READ_ALL_WRITE_ALL"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.create_schema("dataset")

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    @pytest.mark.order(1)
    def test_uploads_csv_when_authorised(self):
        files = {
            "file": (self.csv_filename, open("./test/e2e/" + self.csv_filename, "rb"))
        }
        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )
        response = requests.post(
            upload_url, headers=self.generate_auth_headers(), files=files
        )

        assert response.status_code == HTTPStatus.ACCEPTED

    @pytest.mark.order(1)
    def test_uploads_parquet_when_authorised(self):
        files = {
            "file": (
                self.parquet_filename,
                open("./test/e2e/" + self.parquet_filename, "rb"),
            )
        }
        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )
        response = requests.post(
            upload_url, headers=self.generate_auth_headers(), files=files
        )

        assert response.status_code == HTTPStatus.ACCEPTED

    @pytest.mark.order(2)
    def test_list_when_authorised(self):
        response = requests.post(
            self.datasets_endpoint,
            headers=self.generate_auth_headers(),
            json={"tags": {"test": "e2e"}},
        )
        expected = {
            "layer": self.layer,
            "domain": self.e2e_test_domain,
            "dataset": self.dataset,
        }
        assert response.status_code == HTTPStatus.OK
        # Asserts that the expected dataset fields are within the listed response
        assert any([expected.items() <= dataset.items() for dataset in response.json()])

    @pytest.mark.order(2)
    def test_gets_existing_dataset_info_when_authorised(self):
        url = self.info_dataset_url(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset=self.dataset,
            version=1,
        )

        response = requests.get(url, headers=(self.generate_auth_headers()))
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.order(2)
    def test_queries_non_existing_dataset_when_authorised(self):
        url = self.query_dataset_url(self.layer, "mydomain", "unknowndataset")
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.order(2)
    def test_queries_existing_dataset_as_csv_when_authorised(self):
        url = self.query_dataset_url(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset=self.dataset,
            version=1,
        )
        headers = {
            "Accept": "text/csv",
            **self.generate_auth_headers(),
        }
        response = requests.post(url, headers=headers)
        assert response.status_code == HTTPStatus.OK
        csv_content = response.text
        csv_reader = csv.DictReader(StringIO(csv_content))
        csv_data = [row for row in csv_reader]

        assert csv_data == [
            {
                "year": "2017",
                "month": "7",
                "destination": "Leeds",
                "arrival": "London",
                "type": "regular",
                "status": "completed",
            },
            {
                "year": "2017",
                "month": "7",
                "destination": "Darlington",
                "arrival": "Durham",
                "type": "regular",
                "status": "completed",
            },
        ]

    @pytest.mark.order(2)
    def test_queries_existing_dataset_as_json_when_authorised(self):
        url = self.query_dataset_url(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset=self.dataset,
            version=1,
        )
        headers = {
            **self.generate_auth_headers(),
        }
        response = requests.post(url, headers=headers)
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

    @pytest.mark.order(2)
    def test_fails_to_query_and_sql_injection_attempted(self):
        url = self.query_dataset_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset="query"
        )
        body = {"filter": "';DROP TABLE test_e2e--"}
        response = requests.post(url, headers=(self.generate_auth_headers()), json=body)
        assert response.status_code == HTTPStatus.FORBIDDEN

    @pytest.mark.order(2)
    def test_get_dataset_info(self):
        """
        This test should ensure that the dataset info can be retrieved with the right permissions
        """
        # Get dataset info
        info_url = self.info_dataset_url(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset=self.dataset,
        )

        response = requests.get(
            info_url,
            headers=self.generate_auth_headers("E2E_TEST_CLIENT_BASE_PERMISSIONS"),
        )

        assert response.status_code == HTTPStatus.OK

    @pytest.mark.order(2)
    def test_lists_raw_datasets(self):
        # Get available raw dataset names
        list_raw_files_url = self.list_dataset_raw_files_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset=self.dataset
        )
        available_datasets_response = requests.get(
            list_raw_files_url, headers=self.generate_auth_headers()
        )
        assert available_datasets_response.status_code == HTTPStatus.OK
        filenames = available_datasets_response.json()
        assert len(filenames) == 2 # 2 files uploaded csv and parquet

    @pytest.mark.order(2)
    def test_upload_to_invalid_location(self):
        """
        This test should ensure that invalid data cannot be uploaded to a schema.
        """
        files = {
            "file": (self.csv_filename, open("./test/e2e/" + self.csv_filename, "rb"))
        }

        invalid_params = {
            "layer": "invalid-layer",
            "domain": "invalid-domain",
            "dataset": "invalid-dataset"
        }

        invalid_response_codes = []
        for k,v in invalid_params.items():
            if k == "layer":
                upload_url = self.upload_dataset_url(
                    v, self.e2e_test_domain, self.dataset
                )
                assert self.return_status_code_for_invalid_url(upload_url) == HTTPStatus.BAD_REQUEST
            elif k == "domain":
                upload_url = self.upload_dataset_url(
                    self.layer, v, self.dataset
                )
                assert self.return_status_code_for_invalid_url(upload_url) == HTTPStatus.NOT_FOUND
            elif k == "dataset":
                upload_url = self.upload_dataset_url(
                    self.layer, self.e2e_test_domain, v
                )
                assert self.return_status_code_for_invalid_url(upload_url) == HTTPStatus.NOT_FOUND

    def return_status_code_for_invalid_url(self, url: str):
        response = requests.post(url, headers=self.generate_auth_headers())
        return response.status_code

    @pytest.mark.order(2)
    def test_large_data_endpoint(self):
        large_dataset_url = f"{self.query_dataset_url_large(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset=self.dataset,
            version=1
        )}"

        response = requests.post(large_dataset_url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.ACCEPTED
        job_id = response.json()['details']["job_id"]
        job_id_url = f"{self.jobs_url()}/{job_id}"

        response = requests.get(job_id_url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.OK

    def test_always_list_layers(self):
        response = requests.get(
            self.layers_url(),
            headers=self.generate_auth_headers(),
        )
        print(response.content)
        assert response.status_code == HTTPStatus.OK

    @pytest.mark.order(3)
    def delete_existing_dataset(self):
        # Delete dataset
        delete_raw_data_url = self.delete_data_url(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset=self.dataset,
            raw_filename=self.csv_filename,
        )

        response = requests.delete(
            delete_raw_data_url, headers=self.generate_auth_headers()
        )

        assert response.status_code == HTTPStatus.OK