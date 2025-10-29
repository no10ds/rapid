from http import HTTPStatus

import requests

from test.e2e.journeys.base_journey import (
    BaseJourneyTest,
    DOMAIN_NAME,
)


class TestGeneralBehaviour(BaseJourneyTest):
    def test_http_request_is_redirected_to_https(self):
        response = requests.get(self.status_url())
        assert f"https://{DOMAIN_NAME}" in response.url

    def test_status_always_accessible(self):
        api_url = self.status_url()
        response = requests.get(api_url)
        assert response.status_code == HTTPStatus.OK
