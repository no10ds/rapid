from http import HTTPStatus
import requests
import pytest
import pandas as pd
from io import StringIO
from test.e2e.journeys.base_journey import BaseAuthenticatedJourneyTest


class TestCustomChecksJourney(BaseAuthenticatedJourneyTest):
    dataset = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_DATA_ADMIN"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.generate_schema_name("custom_checks")
        cls.create_schema_with_custom_checks(cls.dataset)

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    @classmethod
    def create_schema_with_custom_checks(cls, dataset_name: str) -> str:
        """Create a schema with custom pandera checks"""
        schema = {
            "metadata": {
                "layer": cls.layer,
                "domain": cls.e2e_test_domain,
                "dataset": dataset_name,
                "sensitivity": "PUBLIC",
                "description": "A test dataset with custom checks",
                "key_value_tags": {
                    "test": "custom_checks"
                },
                "key_only_tags": [],
                "owners": [
                    {
                        "name": "test",
                        "email": "test@example.com"
                    }
                ],
                "update_behaviour": "APPEND"
            },
            "columns": {
                "id": {
                    "partition_index": None,
                    "data_type": "int",
                    "nullable": False,
                    "unique": True
                },
                "value": {
                    "partition_index": None,
                    "data_type": "float",
                    "nullable": True,
                    "checks": [
                        {
                            "name": "value_range_check",
                            "check_fn": "greater_than_or_equal_to",
                            "check_kwargs": {"min_value": 0},
                            "error": "Value must be greater than or equal to 0"
                        },
                        {
                            "name": "value_max_check",
                            "check_fn": "less_than",
                            "check_kwargs": {"max_value": 100},
                            "error": "Value must be less than 100"
                        }
                    ]
                },
                "category": {
                    "partition_index": None,
                    "data_type": "string",
                    "nullable": False,
                    "checks": [
                        {
                            "name": "category_check",
                            "check_fn": "isin",
                            "check_kwargs": {"allowed_values": ["A", "B", "C"]},
                            "error": "Category must be one of: A, B, C"
                        }
                    ]
                }
            }
        }

        response = requests.post(
            cls.schema_endpoint,
            headers=cls.generate_auth_headers(cls, "E2E_TEST_CLIENT_DATA_ADMIN"),
            json=schema,
        )

        assert response.status_code == HTTPStatus.CREATED
        return dataset_name

    def create_valid_data_csv(self):
        """Create a CSV file with valid data that passes all checks"""
        data = pd.DataFrame({
            "id": [1, 2, 3, 4, 5],
            "value": [10.5, 25.0, 50.0, 75.5, 99.9],
            "category": ["A", "B", "C", "A", "B"]
        })
        csv_buffer = StringIO()
        data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        return csv_buffer

    def create_invalid_data_csv(self, invalid_type):
        """Create a CSV file with invalid data that fails checks"""
        if invalid_type == "value_range":
            # Value less than 0
            data = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "value": [-10.5, 25.0, 50.0, 75.5, 99.9],
                "category": ["A", "B", "C", "A", "B"]
            })
        elif invalid_type == "value_max":
            # Value greater than 100
            data = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "value": [10.5, 25.0, 150.0, 75.5, 99.9],
                "category": ["A", "B", "C", "A", "B"]
            })
        elif invalid_type == "category":
            # Invalid category
            data = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "value": [10.5, 25.0, 50.0, 75.5, 99.9],
                "category": ["A", "B", "D", "A", "B"]
            })
        else:
            # Multiple errors
            data = pd.DataFrame({
                "id": [1, 2, 3, 4, 5],
                "value": [-10.5, 25.0, 150.0, 75.5, 99.9],
                "category": ["A", "B", "D", "A", "E"]
            })

        csv_buffer = StringIO()
        data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        return csv_buffer

    def test_upload_valid_data(self):
        """Test that valid data passes all custom checks"""
        csv_buffer = self.create_valid_data_csv()
        files = {"file": ("valid_data.csv", csv_buffer)}

        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )

        response = requests.post(
            upload_url,
            headers=self.generate_auth_headers(),
            files=files
        )

        assert response.status_code == HTTPStatus.ACCEPTED

    @pytest.mark.parametrize(
        "invalid_type,expected_error",
        [
            ("value_range", "Column [value] failed check 'value_range_check'"),
            ("value_max", "Column [value] failed check 'value_max_check'"),
            ("category", "Column [category] failed check 'category_check'"),
            ("multiple", "Column [value] failed check")
        ],
    )
    def test_upload_invalid_data(self, invalid_type, expected_error):
        """Test that invalid data fails custom checks with appropriate error messages"""
        csv_buffer = self.create_invalid_data_csv(invalid_type)
        files = {"file": (f"invalid_data_{invalid_type}.csv", csv_buffer)}

        upload_url = self.upload_dataset_url(
            self.layer, self.e2e_test_domain, self.dataset
        )

        response = requests.post(
            upload_url,
            headers=self.generate_auth_headers(),
            files=files
        )

        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert expected_error in response.text