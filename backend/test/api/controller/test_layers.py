from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestLayersList(BaseClientTest):
    def test_returns_expected_layers(self):

        response = self.client.get(
            f"{BASE_API_PATH}/layers",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        assert response.json() == ["raw", "layer"]
