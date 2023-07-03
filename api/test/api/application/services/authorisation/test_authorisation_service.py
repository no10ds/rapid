from typing import List
from unittest.mock import patch, Mock

import pytest
from fastapi import HTTPException
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError

from api.application.services.authorisation.authorisation_service import (
    secure_dataset_endpoint,
    check_credentials_availability,
    check_permissions,
    retrieve_permissions,
    match_permissions,
    secure_endpoint,
    have_credentials,
)
from api.common.config.auth import SensitivityLevel
from api.common.custom_exceptions import (
    AuthorisationError,
    UserCredentialsUnavailableError,
    UserError,
    NotAuthorisedToViewPageError,
    AuthenticationError,
)
from api.domain.token import Token


class TestSecureEndpoint:
    @patch(
        "api.application.services.authorisation.authorisation_service.secure_dataset_endpoint"
    )
    def test_calls_secure_dataset_endpoint_function_without_domain_and_dataset(
        self, mock_secure_dataset_endpoint
    ):
        endpoint_scopes = SecurityScopes(scopes=["READ"])
        browser_request = False
        client_token = "the-client-token"
        user_token = None

        secure_endpoint(
            security_scopes=endpoint_scopes,
            browser_request=browser_request,
            client_token=client_token,
            user_token=user_token,
        )

        mock_secure_dataset_endpoint.assert_called_once_with(
            endpoint_scopes, browser_request, client_token, user_token
        )


class TestSecureDatasetEndpoint:
    def test_raises_error_when_no_user_credentials_provided(self):
        client_token = None
        user_token = None
        browser_request = True

        with pytest.raises(UserCredentialsUnavailableError):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=user_token,
                domain="mydomain",
                dataset="mydataset",
            )

    def test_raises_forbidden_exception_when_invalid_token(self):
        user_token = None
        client_token = None
        browser_request = False
        with pytest.raises(AuthenticationError):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=user_token,
                domain="mydomain",
                dataset="mydataset",
            )

    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_raises_unauthorised_exception_when_invalid_token_provided(
        self, mock_parse_token
    ):
        client_token = "invalid-token"
        browser_request = False

        mock_parse_token.side_effect = InvalidTokenError()

        with pytest.raises(HTTPException):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=None,
                domain="mydomain",
                dataset="mydataset",
            )

    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    def test_raises_authorisation_error_when_client_unauthorised(
        self, mock_check_permissions, mock_parse_token
    ):
        client_token = "unauthorised-token"
        browser_request = False

        mock_parse_token.return_value = client_token
        mock_check_permissions.side_effect = AuthorisationError("the message")

        with pytest.raises(AuthorisationError):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=None,
                domain="mydomain",
                dataset="mydataset",
            )

    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    def test_raises_not_authorised_to_see_page_error_when_user_unauthorised(
        self, mock_check_permissions, mock_parse_token
    ):
        user_token = "unauthorised-token"

        mock_parse_token.return_value = user_token
        mock_check_permissions.side_effect = AuthorisationError("the message")

        with pytest.raises(NotAuthorisedToViewPageError):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=True,
                client_token=None,
                user_token=user_token,
                domain="mydomain",
                dataset="mydataset",
            )

    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_parses_token_and_checks_permissions_when_user_token_available(
        self, mock_parse_token, mock_check_permissions
    ):
        user_token = "user-token"
        token = Token({"sub": "the-user-id", "cognito:groups": ["group1", "group2"]})

        mock_parse_token.return_value = token

        secure_dataset_endpoint(
            security_scopes=SecurityScopes(scopes=["READ"]),
            browser_request=True,
            client_token=None,
            user_token=user_token,
            domain="mydomain",
            dataset="mydataset",
        )

        mock_parse_token.assert_called_once_with("user-token")
        mock_check_permissions.assert_called_once_with(
            token, ["READ"], "mydomain", "mydataset"
        )

    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_favours_client_token_when_both_tokens_available(
        self, mock_parse_token, mock_check_permissions
    ):
        user_token = "user-token"
        client_token = "client-token"
        token = Token(
            {
                "sub": "the-client-id",
            }
        )

        mock_parse_token.return_value = token

        secure_dataset_endpoint(
            security_scopes=SecurityScopes(scopes=["READ"]),
            browser_request=False,
            client_token=client_token,
            user_token=user_token,
            domain="mydomain",
            dataset=None,
        )

        mock_parse_token.assert_called_once_with("client-token")
        mock_check_permissions.assert_called_once_with(
            token, ["READ"], "mydomain", None
        )

    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_parses_token_and_checks_permissions_when_client_token_available(
        self, mock_parse_token, mock_check_permissions
    ):
        client_token = "client-token"
        token = Token(
            {
                "sub": "the-user-id",
            }
        )

        mock_parse_token.return_value = token

        secure_dataset_endpoint(
            security_scopes=SecurityScopes(scopes=["READ"]),
            browser_request=False,
            client_token=client_token,
            user_token=None,
            domain="mydomain",
            dataset=None,
        )

        mock_parse_token.assert_called_once_with("client-token")
        mock_check_permissions.assert_called_once_with(
            token, ["READ"], "mydomain", None
        )

    @patch(
        "api.application.services.authorisation.authorisation_service.match_permissions"
    )
    @patch(
        "api.application.services.authorisation.authorisation_service.retrieve_permissions"
    )
    @patch("api.application.services.authorisation.authorisation_service.Token")
    def test_check_permission_for_subject_token(
        self, mock_token, mock_retrieve_permissions, mock_match_permissions
    ):
        endpoint_scopes = ["READ"]
        domain = "test-domain"
        dataset = "test-dataset"

        subject_permissions = ["Permission1", "Permission2"]
        mock_retrieve_permissions.return_value = subject_permissions

        check_permissions(mock_token, endpoint_scopes, domain, dataset)

        mock_match_permissions.assert_called_once_with(
            subject_permissions, endpoint_scopes, domain, dataset
        )


class TestCheckCredentialsAvailability:
    def test_succeeds_when_at_least_user_credential_type_available(self):
        try:
            check_credentials_availability(
                browser_request=True, user_token="user-token", client_token=None
            )
        except UserCredentialsUnavailableError:
            pytest.fail("Unexpected UserCredentialsUnavailableError raised")
        except HTTPException:
            pytest.fail("Unexpected HTTPException raised")

    def test_succeeds_when_at_least_client_credential_type_available(self):
        try:
            check_credentials_availability(
                browser_request=True, user_token=None, client_token="client-token"
            )
        except UserCredentialsUnavailableError:
            pytest.fail("Unexpected UserCredentialsUnavailableError raised")
        except HTTPException:
            pytest.fail("Unexpected HTTPException raised")

    def test_raises_user_credentials_error_when_is_browser_request_with_no_credentials(
        self,
    ):
        with pytest.raises(UserCredentialsUnavailableError):
            check_credentials_availability(
                browser_request=True, user_token=None, client_token=None
            )

    def test_raises_http_error_when_is_not_browser_request_with_no_credentials(self):
        with pytest.raises(AuthenticationError):
            check_credentials_availability(
                browser_request=False, user_token=None, client_token=None
            )

    @pytest.mark.parametrize(
        "user_token, client_token, expected",
        [
            # Credentials DO exist
            ("the-user-token", None, True),
            (None, "the-client-token", True),
            # Credentials do NOT exist
            (None, None, False),
            (None, None, False),
        ],
    )
    def test_returns_expected_outcome(self, user_token, client_token, expected):
        result = have_credentials(
            user_token=user_token,
            client_token=client_token,
        )
        assert result is expected


class TestRetrievePermissions:
    @patch("api.application.services.authorisation.authorisation_service.db_adapter")
    def test_get_subject_permissions_from_database_when_they_exist(
        self, mock_db_adapter
    ):
        token_with_only_db_permissions = Token({"sub": "the-subject-id"})

        mock_db_adapter.get_permissions_for_subject.return_value = [
            "READ_ALL",
            "WRITE_PUBLIC",
        ]

        result = retrieve_permissions(token_with_only_db_permissions)

        assert result == [
            "READ_ALL",
            "WRITE_PUBLIC",
        ]

    @patch("api.application.services.authorisation.authorisation_service.db_adapter")
    def test_returns_no_permissions_when_subject_not_found_error(self, mock_db_adapter):
        token_with_no_db_permissions = Token(
            {
                "sub": "the-subject-id",
            }
        )

        mock_db_adapter.get_permissions_for_subject.side_effect = UserError(
            message="the message"
        )

        result = retrieve_permissions(token_with_no_db_permissions)

        assert result == []

    @patch("api.application.services.authorisation.authorisation_service.db_adapter")
    def test_return_empty_permissions_list_when_no_permissions_found(
        self, mock_db_adapter
    ):
        token_with_no_permissions = Token(
            {
                "sub": "the-subject-id",
                "scope": "",
            }
        )

        mock_db_adapter.get_permissions_for_subject.return_value = []

        result = retrieve_permissions(token_with_no_permissions)

        assert result == []


class TestPermissionsMatching:
    def setup_method(self):
        self.mock_s3_client = Mock()

    @patch("api.application.services.authorisation.authorisation_service.s3_adapter")
    @pytest.mark.parametrize(
        "domain, dataset, sensitivity, token_scopes, endpoint_scopes",
        [
            # No endpoint scopes allow anyone access
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["READ_PUBLIC"], []),
            # Token with correct action and sensitivity privilege
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["READ_PUBLIC"], ["READ"]),
            ("domain", "dataset", SensitivityLevel.PRIVATE, ["READ_PRIVATE"], ["READ"]),
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["WRITE_PUBLIC"], ["WRITE"]),
            (
                "domain",
                "dataset",
                SensitivityLevel.PRIVATE,
                ["WRITE_PRIVATE"],
                ["WRITE"],
            ),
            # Token with ALL permission
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["READ_ALL"], ["READ"]),
            ("domain", "dataset", SensitivityLevel.PRIVATE, ["READ_ALL"], ["READ"]),
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["WRITE_ALL"], ["WRITE"]),
            ("domain", "dataset", SensitivityLevel.PRIVATE, ["WRITE_ALL"], ["WRITE"]),
            # Higher sensitivity levels imply lower ones
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["READ_PRIVATE"], ["READ"]),
            (
                "domain",
                "dataset",
                SensitivityLevel.PUBLIC,
                ["WRITE_PRIVATE"],
                ["WRITE"],
            ),
            # Standalone scopes (no domain or dataset, different type of action)
            (None, None, None, ["USER_ADMIN"], ["USER_ADMIN"]),
            (None, None, None, ["DATA_ADMIN"], ["DATA_ADMIN"]),
        ],
    )
    def test_matches_permissions(
        self,
        mock_s3_adapter,
        domain: str,
        dataset: str,
        sensitivity: SensitivityLevel,
        token_scopes: List[str],
        endpoint_scopes: List[str],
    ):
        mock_s3_adapter.get_dataset_sensitivity.return_value = sensitivity
        try:
            match_permissions(token_scopes, endpoint_scopes, domain, dataset)
        except AuthorisationError:
            pytest.fail("Unexpected Unauthorised Error was thrown")

    @patch("api.application.services.authorisation.authorisation_service.s3_adapter")
    @pytest.mark.parametrize(
        "domain, dataset, sensitivity, token_scopes, endpoint_scopes",
        [
            # Token with no scopes is unauthorised
            ("domain", "dataset", SensitivityLevel.PUBLIC, [], ["READ"]),
            # Token does not have required action privilege
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["READ_PUBLIC"], ["WRITE"]),
            # Token does not have required sensitivity privilege
            ("domain", "dataset", SensitivityLevel.PRIVATE, ["READ_PUBLIC"], ["READ"]),
            (
                "domain",
                "dataset",
                SensitivityLevel.PRIVATE,
                ["WRITE_PUBLIC"],
                ["WRITE"],
            ),
            # Edge combinations
            # WRITE high sensitivity does not imply READ low sensitivity
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["WRITE_PRIVATE"], ["READ"]),
            # WRITE does not imply READ
            ("domain", "dataset", SensitivityLevel.PUBLIC, ["WRITE_ALL"], ["READ"]),
            ("domain", "dataset", SensitivityLevel.PRIVATE, ["WRITE_ALL"], ["READ"]),
        ],
    )
    def test_denies_permissions(
        self,
        mock_s3_adapter,
        domain: str,
        dataset: str,
        sensitivity: SensitivityLevel,
        token_scopes: List[str],
        endpoint_scopes: List[str],
    ):

        mock_s3_adapter.get_dataset_sensitivity.return_value = sensitivity

        with pytest.raises(
            AuthorisationError, match="Not enough permissions to access endpoint"
        ):
            match_permissions(token_scopes, endpoint_scopes, domain, dataset)
