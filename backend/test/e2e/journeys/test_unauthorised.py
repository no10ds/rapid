from http import HTTPStatus

import requests

from test.e2e.journeys.base_journey import (
    BaseAuthenticatedJourneyTest,
)


class TestUnauthorisedJourney(BaseAuthenticatedJourneyTest):
    dataset = None

    def client_name(self) -> str:
        return "E2E_TEST_CLIENT_WRITE_ALL"

    @classmethod
    def setup_class(cls):
        cls.dataset = cls.create_schema("unauthorised")

    @classmethod
    def teardown_class(cls):
        cls.delete_dataset(cls.dataset)

    def test_query_existing_dataset_when_not_authorised_to_read(self):

        url = self.query_dataset_url(self.layer, self.e2e_test_domain, self.dataset)
        response = requests.post(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_existing_dataset_info_when_not_authorised_to_read(self):
        url = self.info_dataset_url(self.layer, self.e2e_test_domain, self.dataset)
        response = requests.get(url, headers=self.generate_auth_headers())
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_list_permissions_when_not_user_admin(self):
        response = requests.get(
            self.permissions_url(), headers=self.generate_auth_headers()
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
