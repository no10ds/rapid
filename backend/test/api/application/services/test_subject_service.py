from unittest.mock import Mock

import pytest

from api.application.services.subject_service import SubjectService
from api.common.config.auth import SubjectType
from api.common.custom_exceptions import AWSServiceError, UserError
from api.domain.client import ClientRequest, ClientResponse
from api.domain.subject_permissions import SubjectPermissions
from api.domain.user import UserResponse, UserRequest, UserDeleteRequest


class TestClientCreation:
    def setup_method(self):
        self.cognito_adapter = Mock()
        self.dynamo_adapter = Mock()
        self.subject_service = SubjectService(self.cognito_adapter, self.dynamo_adapter)

    def test_create_client(self):
        expected_response = ClientResponse(
            client_name="my_client",
            client_id="some-client-id",
            client_secret="some-client-secret",  # pragma: allowlist secret
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        client_request = ClientRequest(
            client_name="my_client", permissions=["WRITE_PUBLIC", "READ_PRIVATE"]
        )

        self.cognito_adapter.create_client_app.return_value = expected_response

        client_response = self.subject_service.create_client(client_request)

        self.cognito_adapter.create_client_app.assert_called_once_with(client_request)

        self.dynamo_adapter.validate_permissions.assert_called_once_with(
            client_request.permissions
        )

        self.dynamo_adapter.store_subject_permissions.assert_called_once_with(
            SubjectType.CLIENT, expected_response.client_id, client_request.permissions
        )

        assert client_response == expected_response

    def test_do_not_create_client_when_validate_permissions_fails(self):
        client_request = ClientRequest(
            client_name="my_client", permissions=["WRITE_PUBLIC", "READ_PRIVATE"]
        )
        self.dynamo_adapter.validate_permissions.side_effect = AWSServiceError(
            "The client could not be created, please contact your system administrator"
        )

        with pytest.raises(
            AWSServiceError,
            match="The client could not be created, please contact your system administrator",
        ):
            self.subject_service.create_client(client_request)

        self.dynamo_adapter.store_subject_permissions.assert_not_called()
        self.cognito_adapter.create_client_app.assert_not_called()

    def test_do_not_create_client_when_invalid_permissions(self):
        client_request = ClientRequest(
            client_name="my_client", permissions=["WRITE_PUBLIC", "READ_PRIVATE"]
        )
        self.dynamo_adapter.validate_permissions.side_effect = UserError(
            "One or more of the provided permissions do not exist"
        )

        with pytest.raises(
            UserError,
            match="One or more of the provided permissions do not exist",
        ):
            self.subject_service.create_client(client_request)

        self.dynamo_adapter.store_subject_permissions.assert_not_called()
        self.cognito_adapter.create_client_app.assert_not_called()

    def test_delete_existing_client_when_db_fails(self):
        expected_response = ClientResponse(
            client_name="my_client",
            client_id="some-client-id",
            client_secret="some-client-secret",  # pragma: allowlist secret
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        client_request = ClientRequest(
            client_name="my_client", permissions=["WRITE_PUBLIC", "READ_PRIVATE"]
        )
        self.cognito_adapter.create_client_app.return_value = expected_response
        self.dynamo_adapter.store_subject_permissions.side_effect = AWSServiceError(
            "The client could not be created, please contact your system administrator"
        )

        with pytest.raises(
            AWSServiceError,
            match="The client could not be created, please contact your system administrator",
        ):
            self.subject_service.create_client(client_request)

        self.cognito_adapter.create_client_app.assert_called_once_with(client_request)
        self.cognito_adapter.delete_client_app.assert_called_once_with("some-client-id")


class TestUserCreation:
    def setup_method(self):
        self.cognito_adapter = Mock()
        self.dynamo_adapter = Mock()
        self.subject_service = SubjectService(self.cognito_adapter, self.dynamo_adapter)

    def test_create_subject(self):
        expected_response = UserResponse(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
            user_id="some-uu-id-b226-e5fd18c59b85",
        )
        subject_request = UserRequest(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        self.cognito_adapter.create_user.return_value = expected_response

        actual_response = self.subject_service.create_user(subject_request)

        self.dynamo_adapter.validate_permissions.assert_called_once_with(
            subject_request.permissions
        )

        self.cognito_adapter.create_user.assert_called_once_with(subject_request)

        self.dynamo_adapter.store_subject_permissions.assert_called_once_with(
            SubjectType.USER, expected_response.user_id, subject_request.permissions
        )

        assert actual_response == expected_response

    def test_do_not_create_user_when_validate_permissions_fails(self):
        subject_request = UserRequest(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )
        self.dynamo_adapter.validate_permissions.side_effect = AWSServiceError(
            "The user could not be created, please contact your system administrator"
        )

        with pytest.raises(
            AWSServiceError,
            match="The user could not be created, please contact your system administrator",
        ):
            self.subject_service.create_user(subject_request)

        self.dynamo_adapter.store_subject_permissions.assert_not_called()
        self.cognito_adapter.create_user.assert_not_called()

    def test_do_not_create_user_when_invalid_permissions(self):
        subject_request = UserRequest(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["FAKE_NAME"],
        )
        self.dynamo_adapter.validate_permissions.side_effect = UserError(
            "One or more of the provided permissions do not exist"
        )

        with pytest.raises(
            UserError,
            match="One or more of the provided permissions do not exist",
        ):
            self.subject_service.create_user(subject_request)

        self.dynamo_adapter.store_subject_permissions.assert_not_called()
        self.cognito_adapter.create_user.assert_not_called()

    def test_delete_existing_user_when_update_fails(self):
        subject_response = UserResponse(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
            user_id="some-uu-id-b226-e5fd18c59b85",
        )
        subject_request = UserRequest(
            username="user-name",
            email="user-name@some-email.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )
        self.cognito_adapter.create_user.return_value = subject_response
        self.dynamo_adapter.store_subject_permissions.side_effect = AWSServiceError(
            "The user could not be created, please contact your system administrator"
        )

        with pytest.raises(
            AWSServiceError,
            match="The user could not be created, please contact your system administrator",
        ):
            self.subject_service.create_user(subject_request)

        self.cognito_adapter.create_user.assert_called_once_with(subject_request)
        self.cognito_adapter.delete_user.assert_called_once_with("user-name")


class TestSetSubjectPermissions:
    def setup_method(self):
        self.cognito_adapter = Mock()
        self.dynamo_adapter = Mock()
        self.subject_service = SubjectService(self.cognito_adapter, self.dynamo_adapter)

    def test_set_subject_permissions(self):
        subject_permissions = SubjectPermissions(
            subject_id="123asdf67gd", permissions=["READ_ALL", "WRITE_PUBLIC"]
        )

        self.subject_service.set_subject_permissions(subject_permissions)

        self.dynamo_adapter.validate_permissions.assert_called_once_with(
            subject_permissions.permissions
        )
        self.dynamo_adapter.update_subject_permissions.assert_called_once_with(
            subject_permissions
        )

    def test_set_subject_permissions_when_validation_raises_errors(self):
        subject_permissions = SubjectPermissions(
            subject_id="123asdf67gd", permissions=["READ_ALL", "WRITE_PUBLIC"]
        )
        self.dynamo_adapter.validate_permissions.side_effect = UserError(
            "One or more of the provided permissions is invalid or duplicated"
        )

        with pytest.raises(
            UserError,
            match="One or more of the provided permissions is invalid or duplicated",
        ):
            self.subject_service.set_subject_permissions(subject_permissions)

        self.dynamo_adapter.update_subject_permissions.assert_not_called()

    def test_set_subject_permissions_when_db_update_raises_error(self):
        subject_permissions = SubjectPermissions(
            subject_id="123asdf67gd", permissions=["READ_ALL", "WRITE_PUBLIC"]
        )
        self.dynamo_adapter.update_subject_permissions.side_effect = AWSServiceError(
            f"Error updating permissions for {subject_permissions.subject_id}"
        )

        with pytest.raises(
            AWSServiceError,
            match=f"Error updating permissions for {subject_permissions.subject_id}",
        ):
            self.subject_service.set_subject_permissions(subject_permissions)

        self.dynamo_adapter.validate_permissions.assert_called_once_with(
            subject_permissions.permissions
        )


class TestGetSubjectNameById:
    def setup_method(self):
        self.cognito_adapter = Mock()
        self.dynamo_adapter = Mock()
        self.subject_service = SubjectService(self.cognito_adapter, self.dynamo_adapter)

    def test_gets_subjects_name_by_id(self):
        self.cognito_adapter.get_all_subjects.return_value = [
            {
                "subject_id": "the-client-id",
                "subject_name": "the_client_name",
                "type": "CLIENT",
            },
            {
                "subject_id": "the-user-id",
                "subject_name": "the_user_name",
                "type": "USER",
            },
        ]

        result = self.subject_service.get_subject_name_by_id("the-user-id")

        assert result == "the_user_name"

    def test_raises_error_if_no_subject_found(self):
        unknown_id = "unknown-id"

        self.cognito_adapter.get_all_subjects.return_value = [
            {
                "subject_id": "the-client-id",
                "subject_name": "the_client_name",
                "type": "CLIENT",
            },
            {
                "subject_id": "the-user-id",
                "subject_name": "the_user_name",
                "type": "USER",
            },
        ]

        with pytest.raises(
            UserError, match="Subject with ID unknown-id does not exist"
        ):
            self.subject_service.get_subject_name_by_id(unknown_id)


class TestSubjectDeletion:
    def setup_method(self):
        self.cognito_adapter = Mock()
        self.dynamo_adapter = Mock()
        self.subject_service = SubjectService(self.cognito_adapter, self.dynamo_adapter)

    def test_delete_user(self):
        delete_request = UserDeleteRequest(
            username="my_user", user_id="some-uu-id-b226-e5fd18c59b85"
        )
        self.subject_service.delete_user(delete_request)

        self.cognito_adapter.delete_user.assert_called_once_with("my_user")
        self.dynamo_adapter.delete_subject.assert_called_once_with(
            "some-uu-id-b226-e5fd18c59b85"
        )

    def test_delete_client(self):
        self.subject_service.delete_client("my_client_id")

        self.cognito_adapter.delete_client_app.assert_called_once_with("my_client_id")
        self.dynamo_adapter.delete_subject.assert_called_once_with("my_client_id")


class TestListSubjects:
    def setup_method(self):
        self.cognito_adapter = Mock()
        self.dynamo_adapter = Mock()
        self.subject_service = SubjectService(self.cognito_adapter, self.dynamo_adapter)

    def test_list_subjects(self):
        expected = [{"key": "value"}]

        self.cognito_adapter.get_all_subjects.return_value = expected

        result = self.subject_service.list_subjects()

        assert result == expected
