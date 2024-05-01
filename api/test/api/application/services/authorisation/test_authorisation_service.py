from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from fastapi import HTTPException
from fastapi.security import SecurityScopes
from jwt.exceptions import InvalidTokenError
import pytest

from api.application.services.authorisation.authorisation_service import (
    secure_dataset_endpoint,
    check_credentials_availability,
    check_permissions,
    secure_endpoint,
    have_credentials,
    validate_token,
    get_user_token,
    get_client_token,
    get_token,
    get_subject_id,
)
from api.application.services.authorisation.dataset_access_evaluator import (
    DatasetAccessEvaluator,
)
from api.application.services.permissions_service import PermissionsService
from api.common.config.auth import Action, RAPID_ACCESS_TOKEN
from api.common.custom_exceptions import (
    AuthorisationError,
    UserCredentialsUnavailableError,
    NotAuthorisedToViewPageError,
    AuthenticationError,
)
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.permission_item import PermissionItem
from api.domain.token import Token


@dataclass
class MockToken:
    subject: str


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


class TestValidateToken:
    @patch(
        "api.application.services.authorisation.authorisation_service.check_credentials_availability"
    )
    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_validate_token_with_client_token(
        self,
        mock_parse_token: MagicMock,
        mock_check_credentials_availability: MagicMock,
    ):
        mock_token = MockToken("subject-abc")
        mock_parse_token.return_value = mock_token

        res = validate_token(True, None, "user_token")

        mock_check_credentials_availability.assert_called_once_with(
            True, None, "user_token"
        )
        mock_parse_token.assert_called_once_with("user_token")
        assert res == mock_token

    @patch(
        "api.application.services.authorisation.authorisation_service.check_credentials_availability"
    )
    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_validate_token_with_user_token(
        self,
        mock_parse_token: MagicMock,
        mock_check_credentials_availability: MagicMock,
    ):
        token = "token"
        mock_parse_token.return_value = token

        res = validate_token(True, "client_token", None)

        mock_check_credentials_availability.assert_called_once_with(
            True,
            "client_token",
            None,
        )
        mock_parse_token.assert_called_once_with("client_token")
        assert res == token

    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_favours_client_token_when_both_tokens_available(self, mock_parse_token):
        user_token = "user-token"
        client_token = "client-token"
        token = Token(
            {
                "sub": "the-client-id",
            }
        )

        mock_parse_token.return_value = token
        validate_token(
            browser_request=False,
            client_token=client_token,
            user_token=user_token,
        )
        mock_parse_token.assert_called_once_with("client-token")


class TestGetToken:
    def test_get_user_token(self):
        request = MagicMock()
        expected = "1234567890"
        request.cookies.get.return_value = expected

        res = get_user_token(request)
        request.cookies.get.assert_called_once_with(RAPID_ACCESS_TOKEN, None)
        assert res == expected

    def test_get_client_token(self):
        request = MagicMock()
        expected = "1234567890"
        token = f"Bearer {expected}"
        request.headers.get.return_value = token

        res = get_client_token(request)
        assert res == expected

    @pytest.mark.parametrize(
        "client_token, user_token, response",
        [
            ("1234", "5678", "1234"),
            (None, '"5678', "5678"),
            ("1234", None, "1234"),
        ],
    )
    def get_token(self, client_token: str, user_token: str, expected: str):
        request = MagicMock()

        if client_token:
            request.headers.get.return_value = f"Bearer {client_token}"

        if user_token:
            request.cookies.get.return_value = user_token

        res = get_token(request)
        assert res == expected


class TestGetSubject:
    @patch("api.application.services.authorisation.authorisation_service.get_token")
    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_get_subject_id(
        self, mock_parse_token: MagicMock, mock_get_token: MagicMock
    ):
        @dataclass
        class MockToken:
            subject: str

        request = MagicMock()
        expected_user = "abc-123"
        expected_token = "token"

        mock_get_token.return_value = expected_token
        mock_parse_token.return_value = MockToken(subject=expected_user)

        res = get_subject_id(request)

        mock_get_token.assert_called_once_with(request)
        mock_parse_token.assert_called_once_with(expected_token)
        assert res == expected_user


class TestCheckPermissions:
    @patch.object(PermissionsService, "get_subject_permissions")
    def test_check_permissions_success(self, mock_get_subject_permissions: MagicMock):
        subject_id = "subject123"
        permissions = [
            PermissionItem(id="READ_ALL", type="READ", layer="ALL", sensitivity="ALL"),
            PermissionItem(id="DATA_ADMIN", type="DATA_ADMIN"),
            PermissionItem(id="USER_ADMIN", type="USER_ADMIN"),
        ]

        mock_get_subject_permissions.return_value = permissions

        res = check_permissions(subject_id, [Action.WRITE, Action.DATA_ADMIN])

        mock_get_subject_permissions.assert_called_once_with(subject_id)
        assert res is True

    @patch.object(PermissionsService, "get_subject_permissions")
    def test_check_permissions_raises_error(
        self, mock_get_subject_permissions: MagicMock
    ):
        subject_id = "subject123"
        permissions = [
            PermissionItem(id="READ_ALL", type="READ", layer="ALL", sensitivity="ALL"),
            PermissionItem(id="DATA_ADMIN", type="DATA_ADMIN"),
            PermissionItem(id="USER_ADMIN", type="USER_ADMIN"),
        ]

        mock_get_subject_permissions.return_value = permissions

        with pytest.raises(
            AuthorisationError,
            match="User subject123 does not have permissions that grant access to the endpoint scopes",
        ):
            check_permissions(subject_id, [Action.WRITE])
            mock_get_subject_permissions.assert_called_once_with(subject_id)


class TestSecureEndpoint:
    @patch(
        "api.application.services.authorisation.authorisation_service.validate_token"
    )
    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    def test_secure_endpoint(self, mock_check_permissions, mock_validate_token):
        scopes = ["READ"]
        endpoint_scopes = SecurityScopes(scopes=scopes)
        browser_request = False
        client_token = "the-client-token"
        user_token = None
        mock_validate_token.return_value = MockToken(client_token)

        secure_endpoint(
            security_scopes=endpoint_scopes,
            browser_request=browser_request,
            client_token=client_token,
            user_token=user_token,
        )

        mock_check_permissions.assert_called_once_with(client_token, scopes)
        mock_validate_token.assert_called_once_with(
            browser_request, client_token, user_token
        )

    @patch("api.application.services.authorisation.authorisation_service.parse_token")
    def test_raises_unauthorised_exception_when_invalid_token_provided(
        self, mock_parse_token
    ):
        client_token = "invalid-token"
        browser_request = False

        mock_parse_token.side_effect = InvalidTokenError()

        with pytest.raises(HTTPException):
            secure_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=None,
            )

    @patch(
        "api.application.services.authorisation.authorisation_service.validate_token"
    )
    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    def test_raises_unauthorised_error_with_user_token(
        self, mock_check_permissions, mock_validate_token
    ):
        user_token = "token"
        browser_request = False
        mock_validate_token.return_value = MockToken("subject-abc")
        mock_check_permissions.side_effect = AuthorisationError("message")

        with pytest.raises(NotAuthorisedToViewPageError):
            secure_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=None,
                user_token=user_token,
            )

    @patch(
        "api.application.services.authorisation.authorisation_service.validate_token"
    )
    @patch(
        "api.application.services.authorisation.authorisation_service.check_permissions"
    )
    def test_raises_unauthorised_error_with_client_token(
        self, mock_check_permissions, mock_validate_token
    ):
        client_token = "token"
        browser_request = False
        mock_validate_token.return_value = MockToken("subject-abc")
        mock_check_permissions.side_effect = AuthorisationError("message")

        with pytest.raises(AuthorisationError, match="message"):
            secure_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=None,
            )


class TestSecureDatasetEndpoint:
    @patch.object(DatasetAccessEvaluator, "can_access_dataset")
    @patch(
        "api.application.services.authorisation.authorisation_service.validate_token"
    )
    @patch(
        "api.application.services.authorisation.authorisation_service.process_dataset_metadata"
    )
    def test_secure_dataset_endpoint_success(
        self,
        mock_process_dataset_metadata: MagicMock,
        mock_validate_token: MagicMock,
        mock_can_access_dataset: MagicMock,
    ):
        subject_id = "subject_id"
        browser_request = False
        client_token = "client_token"
        user_token = "user_token"
        layer = "layer"
        domain = "domain"
        dataset = "dataset"
        metadata = DatasetMetadata(layer, domain, dataset)

        mock_validate_token.return_value = MockToken(subject_id)
        mock_process_dataset_metadata.return_value = metadata

        secure_dataset_endpoint(
            security_scopes=SecurityScopes(scopes=["READ"]),
            browser_request=browser_request,
            client_token=client_token,
            user_token=user_token,
            layer=layer,
            domain=domain,
            dataset=dataset,
        )

        mock_validate_token.assert_called_once_with(
            browser_request, client_token, user_token
        )
        mock_process_dataset_metadata.assert_called_once_with(layer, domain, dataset)
        mock_can_access_dataset.assert_called_once_with(metadata, subject_id, ["READ"])

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
                layer="layer",
                domain="domain",
                dataset="dataset",
            )

    @patch(
        "api.application.services.authorisation.authorisation_service.validate_token"
    )
    @patch.object(DatasetAccessEvaluator, "can_access_dataset")
    def test_raises_unauthorised_error_with_user_token(
        self, mock_can_access_dataset, mock_validate_token
    ):
        user_token = "token"
        browser_request = False
        mock_validate_token.return_value = MockToken("subject-abc")
        mock_can_access_dataset.side_effect = AuthorisationError("message")

        with pytest.raises(NotAuthorisedToViewPageError):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=None,
                user_token=user_token,
                layer="layer",
                domain="domain",
                dataset="dataset",
            )

    @patch(
        "api.application.services.authorisation.authorisation_service.validate_token"
    )
    @patch.object(DatasetAccessEvaluator, "can_access_dataset")
    def test_raises_unauthorised_error_with_client_token(
        self, mock_can_access_dataset, mock_validate_token
    ):
        client_token = "token"
        browser_request = False
        mock_validate_token.return_value = MockToken("subject-abc")
        mock_can_access_dataset.side_effect = AuthorisationError("message")

        with pytest.raises(AuthorisationError, match="message"):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=None,
                layer="layer",
                domain="domain",
                dataset="dataset",
            )

    @pytest.mark.parametrize(
        "layer, domain, dataset",
        [
            ("layer", "domain", None),
            ("layer", None, "layer"),
            (None, "domain", "layer"),
        ],
    )
    @patch(
        "api.application.services.authorisation.authorisation_service.validate_token"
    )
    def test_raises_authentication_error_when_any_metadata_field_is_missing(
        self, mock_validate_token, layer, domain, dataset
    ):
        client_token = "token"
        browser_request = False
        mock_validate_token.return_value = MockToken("subject-abc")

        with pytest.raises(
            AuthenticationError, match="You are not authorised to perform this action"
        ):
            secure_dataset_endpoint(
                security_scopes=SecurityScopes(scopes=["READ"]),
                browser_request=browser_request,
                client_token=client_token,
                user_token=None,
                layer=layer,
                domain=domain,
                dataset=dataset,
            )
