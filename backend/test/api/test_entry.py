from unittest.mock import patch

import pytest
from api.application.services.authorisation.dataset_access_evaluator import (
    DatasetAccessEvaluator,
)
from api.common.config.auth import Action
from api.common.config.constants import BASE_API_PATH
from api.common.custom_exceptions import AWSServiceError, UserError
from api.domain.dataset_metadata import DatasetMetadata
from api.entry import _determine_user_ui_actions

from test.api.common.controller_test_utils import BaseClientTest


@pytest.fixture(scope="session", autouse=True)
def get_subject_id_mock():
    with patch("api.entry.get_subject_id", return_value=None) as client_token_mock:
        yield client_token_mock


class TestStatus(BaseClientTest):
    def test_http_status_response_is_200_status(self):
        response = self.client.get(f"{BASE_API_PATH}/status")
        assert response.status_code == 200

    def test_returns_no_metadata_for_api(self):
        response = self.client.get(f"{BASE_API_PATH}/apis")
        assert response.status_code == 404

    @patch("api.entry.permissions_service")
    def test_gets_permissions_for_ui(self, mock_permissions_service):
        expected_permission_object = {"any-key": "any-value"}

        mock_permissions_service.get_all_permissions_ui.return_value = (
            expected_permission_object
        )

        response = self.client.get(
            f"{BASE_API_PATH}/permissions_ui", cookies={"rat": "user_token"}
        )

        mock_permissions_service.get_all_permissions_ui.assert_called_once()
        assert response.status_code == 200


class TestDatasetsUI(BaseClientTest):
    @patch("api.entry.get_subject_id")
    @patch.object(DatasetAccessEvaluator, "get_authorised_datasets")
    def test_gets_datasets_for_ui_write(
        self, mock_get_authorised_datasets, mock_get_subject_id
    ):
        subject_id = "123abc"
        mock_get_subject_id.return_value = subject_id

        mock_get_authorised_datasets.return_value = [
            DatasetMetadata("layer", "domain1", "datset1", 1),
            DatasetMetadata("layer", "domain1", "datset2", 1),
            DatasetMetadata("layer", "domain2", "dataset3", 1),
        ]

        response = self.client.get(
            f"{BASE_API_PATH}/datasets_ui/WRITE", cookies={"rat": "user_token"}
        )

        mock_get_authorised_datasets.assert_called_once_with(subject_id, Action.WRITE)
        assert response.status_code == 200

    @patch("api.entry.get_subject_id")
    @patch.object(DatasetAccessEvaluator, "get_authorised_datasets")
    def test_gets_datasets_for_ui_read(
        self, mock_get_authorised_datasets, mock_get_subject_id
    ):
        subject_id = "123abc"
        mock_get_subject_id.return_value = subject_id

        mock_get_authorised_datasets.return_value = [
            DatasetMetadata("layer", "domain1", "datset1", 1),
            DatasetMetadata("layer", "domain1", "datset2", 1),
            DatasetMetadata("layer", "domain2", "dataset3", 1),
        ]

        response = self.client.get(
            f"{BASE_API_PATH}/datasets_ui/READ", cookies={"rat": "user_token"}
        )

        mock_get_authorised_datasets.assert_called_once_with(subject_id, Action.READ)
        assert response.status_code == 200


class TestMethodsUI(BaseClientTest):
    @pytest.mark.parametrize(
        "permissions,can_manage_users,can_upload,can_download,can_create_schema,can_search_catalog",
        [
            ([], False, False, False, False, False),
            (["READ_ALL"], False, False, True, False, True),
            (["WRITE_ALL"], False, True, False, False, False),
            (["DATA_ADMIN"], False, False, False, True, False),
            (["USER_ADMIN"], True, False, False, False, False),
            (["READ_ALL", "WRITE_ALL"], False, True, True, False, True),
            (["USER_ADMIN", "READ_ALL", "WRITE_ALL"], True, True, True, False, True),
            (["READ_PRIVATE", "WRITE_PUBLIC"], False, True, True, False, True),
            (
                ["READ_PROTECTED_domain1", "WRITE_PROTECTED_domain2"],
                False,
                True,
                True,
                False,
                True,
            ),
        ],
    )
    def test_determines_user_allowed_ui_actions(
        self,
        permissions,
        can_manage_users,
        can_upload,
        can_download,
        can_create_schema,
        can_search_catalog,
    ):
        allowed_actions = _determine_user_ui_actions(permissions)

        assert allowed_actions["can_manage_users"] is can_manage_users
        assert allowed_actions["can_upload"] is can_upload
        assert allowed_actions["can_download"] is can_download
        assert allowed_actions["can_create_schema"] is can_create_schema
        assert allowed_actions["can_search_catalog"] is can_search_catalog

    @patch("api.entry.get_subject_id")
    @patch("api.entry.permissions_service")
    def test_calls_methods_with_expected_arguments(
        self, mock_permissions_service, mock_get_subject_id
    ):
        mock_get_subject_id.return_value = "123abc"

        mock_permissions_service.get_subject_permission_keys.return_value = [
            "READ_ALL",
            "WRITE_ALL",
            "USER_ADMIN",
            "DATA_ADMIN",
        ]

        response = self.client.get(
            f"{BASE_API_PATH}/methods", cookies={"rat": "user_token"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "error_message": None,
            "can_manage_users": True,
            "can_upload": True,
            "can_download": True,
            "can_create_schema": True,
            "can_search_catalog": True,
        }

    @patch("api.entry.get_subject_id")
    @patch("api.entry.permissions_service")
    def test_calls_methods_with_expected_arguments_when_user_error(
        self, mock_permissions_service, mock_get_subject_id
    ):
        mock_get_subject_id.return_value = "123abc"

        mock_permissions_service.get_subject_permission_keys.side_effect = UserError(
            "a message"
        )

        response = self.client.get(
            f"{BASE_API_PATH}/methods", cookies={"rat": "user_token"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "error_message": "You have not been granted relevant permissions. Please speak to your system administrator.",
        }

    @patch("api.entry.get_subject_id")
    @patch("api.entry.permissions_service")
    def test_calls_methods_with_expected_arguments_when_aws_error(
        self, mock_permissions_service, mock_get_subject_id
    ):
        mock_get_subject_id.return_value = "123abc"

        mock_permissions_service.get_subject_permission_keys.side_effect = (
            AWSServiceError("a custom message")
        )

        response = self.client.get(
            f"{BASE_API_PATH}/methods", cookies={"rat": "user_token"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "error_message": "a custom message",
        }

    @patch("api.entry.get_subject_id")
    @patch("api.entry.permissions_service")
    @patch("api.entry._determine_user_ui_actions")
    def test_calls_methods_with_expected_arguments_when_no_permissions(
        self, mock_ui_actions, mock_permissions_service, mock_get_subject_id
    ):

        mock_get_subject_id.return_value = "123abc"

        mock_ui_actions.return_value = {}

        response = self.client.get(
            f"{BASE_API_PATH}/methods", cookies={"rat": "user_token"}
        )

        assert response.status_code == 200
        assert response.json() == {
            "error_message": "You have not been granted relevant permissions. Please speak to your system administrator.",
        }
