from unittest.mock import patch

from api.adapter.aws_resource_adapter import AWSResourceAdapter
from api.common.custom_exceptions import AWSServiceError
from api.common.utilities import handle_version_retrieval, build_error_message_list


class TestHandleVersionRetrieval:
    @patch.object(AWSResourceAdapter, "get_version_from_crawler_tags")
    def test_retrieve_version_from_crawler_when_version_is_none(
        self, mock_get_version_from_crawler_tags
    ):
        expected_version = 3

        mock_get_version_from_crawler_tags.return_value = expected_version

        actual_version = handle_version_retrieval("domain1", "dataset1", None)

        mock_get_version_from_crawler_tags.assert_called_once_with(
            "domain1", "dataset1"
        )

        assert actual_version == expected_version

    def test_return_user_input_version_when_version_is_defined(self):
        expected_version = 4

        actual_version = handle_version_retrieval("domain1", "dataset1", 4)

        assert actual_version == expected_version


class TestBuildErrorList:
    def test_build_list_when_message_is_list(self):
        result = build_error_message_list(AWSServiceError(["error1", "error2"]))

        assert result == ["error1", "error2"]

    def test_build_list_when_message_is_string(self):
        result = build_error_message_list(AWSServiceError("error1"))

        assert result == ["error1"]

    def test_build_list_when_exception_has_no_message(self):
        result = build_error_message_list(ValueError("error1"))

        assert result == ["error1"]
