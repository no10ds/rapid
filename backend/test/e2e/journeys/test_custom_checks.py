from http import HTTPStatus

import requests
from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)


class TestCustomChecksJourney(BaseAuthenticatedJourneyTest):
    dataset = None

    valid_csv_filename = "test_journey_file_custom_checks_valid.csv"
    invalid_csv_filename = "test_journey_file_custom_checks_invalid.csv"

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_READ_ALL_WRITE_ALL"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.create_schema("custom_checks")

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    def test_upload_invalid_data(self):
        files = {
            "file": (self.invalid_csv_filename, open("./test/e2e/" + self.invalid_csv_filename, "rb"))
        }

        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )

        response = requests.post(
            upload_url,
            headers=self.generate_auth_headers(),
            files=files
        )

        assert response.status_code == HTTPStatus.ACCEPTED

        job_id = response.json()["details"]["job_id"]
        job_url = f"{self.jobs_url()}/{job_id}"

        job_response = requests.get(job_url, headers=self.generate_auth_headers())
        assert job_response.status_code == HTTPStatus.OK
        assert job_response.json()["status"] == "FAILED"
        assert "validator" in str(job_response.json().get("errors", "")).lower()

    def test_upload_valid_data(self):
        files = {"file": (self.valid_csv_filename, open("./test/e2e/" + self.valid_csv_filename, "rb"))}

        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )

        upload_response = requests.post(
            upload_url,
            headers=self.generate_auth_headers(),
            files=files
        )

        assert upload_response.status_code == HTTPStatus.ACCEPTED

        job_id = upload_response.json()["details"]["job_id"]
        dataset_version = upload_response.json()["details"]["dataset_version"]
        job_url = f"{self.jobs_url()}/{job_id}"

        job_response = requests.get(job_url, headers=self.generate_auth_headers())
        assert job_response.status_code == HTTPStatus.OK
        assert job_response.json()["status"] == "SUCCESS"

        query_url = self.query_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset, version=dataset_version
        )

        query_response = requests.post(
            query_url,
            headers=self.generate_auth_headers(),
            json={}
        )

        assert query_response.status_code == HTTPStatus.OK
        assert len(query_response.json()) >= 2
