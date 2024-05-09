from http import HTTPStatus

import requests
import pytest

from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)


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
    def test_uploads_when_authorised(self):
        files = {"file": (self.filename, open("./test/e2e/" + self.filename, "rb"))}
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

    def test_queries_existing_dataset_as_csv_when_authorised(self):
        url = self.query_dataset_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset="query", version=1
        )

        headers = {
            "Accept": "text/csv",
            **self.generate_auth_headers(),
        }
        response = requests.post(url, headers=headers)
        assert response.status_code == HTTPStatus.NO_CONTENT

    @pytest.mark.order(2)
    def test_fails_to_query_and_sql_injection_attempted(self):
        url = self.query_dataset_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset="query"
        )
        body = {"filter": "';DROP TABLE test_e2e--"}
        response = requests.post(url, headers=(self.generate_auth_headers()), json=body)
        assert response.status_code == HTTPStatus.FORBIDDEN

    @pytest.mark.order(3)
    def test_lists_raw_datasets_and_deletes_existing_data(self):

        # Get available raw dataset names
        list_raw_files_url = self.list_dataset_raw_files_url(
            layer=self.layer, domain=self.e2e_test_domain, dataset=self.dataset
        )
        available_datasets_response = requests.get(
            list_raw_files_url, headers=self.generate_auth_headers()
        )
        assert available_datasets_response.status_code == HTTPStatus.OK
        filenames = available_datasets_response.json()
        assert len(filenames) == 1

        # Delete dataset
        file_name = filenames[0]
        delete_raw_data_url = self.delete_data_url(
            layer=self.layer,
            domain=self.e2e_test_domain,
            dataset=self.dataset,
            raw_filename=file_name,
        )

        response2 = requests.delete(
            delete_raw_data_url, headers=self.generate_auth_headers()
        )

        assert response2.status_code == HTTPStatus.OK


# TODO: Test the upload of a parquet file
