from http import HTTPStatus

import requests
from test.e2e.journeys.base_journey import (
    BaseJourneyTest,
)


class TestUnauthenticatedJourneys(BaseJourneyTest):
    def test_query_is_forbidden_when_no_token_provided(self):
        url = self.query_dataset_url(self.layer, "mydomain", "unknowndataset")
        response = requests.post(url)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_upload_is_forbidden_when_no_token_provided(self):
        files = {"file": (self.filename, open("./test/e2e/" + self.filename, "rb"))}
        url = self.upload_dataset_url(self.layer, self.e2e_test_domain, "anything")
        response = requests.post(url, files=files)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_list_is_forbidden_when_no_token_provided(self):
        response = requests.post(self.datasets_endpoint)
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_list_permissions_is_forbidden_when_no_token_provided(self):
        response = requests.get(self.permissions_url())
        assert response.status_code == HTTPStatus.FORBIDDEN
