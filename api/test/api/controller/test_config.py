from unittest.mock import patch

from api.application.services.data_service import DataService
from api.common.config.constants import BASE_API_PATH
from test.api.common.controller_test_utils import BaseClientTest


class TestUpdateTableConfig(BaseClientTest):
    @patch.object(DataService, "update_table_config")
    def test_updates_table_config(self, mock_update_table_config):
        response = self.client.post(
            f"{BASE_API_PATH}/table_config?domain=domain1&dataset=dataset1",
            headers={"Authorization": "Bearer test-token"},
        )

        mock_update_table_config.assert_called_once_with("domain1", "dataset1")

        assert response.status_code == 200
