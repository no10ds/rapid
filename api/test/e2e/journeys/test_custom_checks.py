from http import HTTPStatus

import requests
import pytest
from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)


class TestCustomChecksJourney(BaseAuthenticatedJourneyTest):
    dataset = None
    
    # CSV file names for custom checks testing
    valid_csv_filename = "test_journey_file_custom_checks_valid.csv"
    invalid_csv_filename = "test_journey_file_custom_checks_invalid.csv"

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_DATA_ADMIN"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.create_schema("custom_checks")

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    def test_upload_valid_data(self):
        """Test that valid data passes all custom checks"""
        files = {
            "file": (self.valid_csv_filename, open("./test/e2e/" + self.valid_csv_filename, "rb"))
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

    def test_upload_invalid_data(self):
        """Test that invalid data fails custom checks with appropriate error messages"""
        files = {"file": (self.invalid_csv_filename, open("./test/e2e/" + self.invalid_csv_filename, "rb"))}

        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )

        response = requests.post(
            upload_url,
            headers=self.generate_auth_headers(),
            files=files
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        # Check that validation failed with custom check errors
        assert "failed check" in response.text

    def test_query_data_after_valid_upload(self):
        """Test that we can query data after a successful upload"""
        # First upload valid data
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

        # Now query the data
        query_url = self.query_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )

        query_response = requests.post(
            query_url,
            headers=self.generate_auth_headers(),
            json={}
        )

        assert query_response.status_code == HTTPStatus.OK
        
        # Verify the data structure
        data = query_response.json()
        assert len(data) == 2  # We uploaded 2 rows
        assert all(row["year"] >= 2000 and row["year"] <= 2030 for row in data)
        assert all(row["month"] >= 1 and row["month"] <= 12 for row in data)
        assert all(row["type"] in ["regular", "express", "priority"] for row in data)
        assert all(row["status"] in ["completed", "pending", "cancelled"] for row in data)

    def test_get_dataset_info(self):
        """Test that we can get dataset info including custom checks"""
        info_url = self.info_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )

        response = requests.get(
            info_url,
            headers=self.generate_auth_headers()
        )

        assert response.status_code == HTTPStatus.OK
        
        info = response.json()
        assert "columns" in info
        
        # Check that custom checks are present in the schema
        year_column = next((col for col in info["columns"] if col["name"] == "year"), None)
        assert year_column is not None
        assert "checks" in year_column
        assert len(year_column["checks"]) == 2

        month_column = next((col for col in info["columns"] if col["name"] == "month"), None)
        assert month_column is not None
        assert "checks" in month_column
        assert len(month_column["checks"]) == 1

        type_column = next((col for col in info["columns"] if col["name"] == "type"), None)
        assert type_column is not None
        assert "checks" in type_column
        assert len(type_column["checks"]) == 1

        status_column = next((col for col in info["columns"] if col["name"] == "status"), None)
        assert status_column is not None
        assert "checks" in status_column
        assert len(status_column["checks"]) == 1
