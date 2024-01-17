from abc import ABC
from unittest.mock import Mock
from unittest import mock
import pytest
from botocore.exceptions import ClientError
import os

from api.adapter.cognito_adapter import CognitoAdapter
from api.common.config.auth import COGNITO_USER_POOL_ID, COGNITO_RESOURCE_SERVER_ID
from api.common.config.aws import DOMAIN_NAME
from api.common.custom_exceptions import AWSServiceError, UserError
from api.domain.client import ClientRequest, ClientResponse
from api.domain.user import UserResponse, UserRequest


class BaseCognitoAdapter(ABC):
    cognito_boto_client = None
    cognito_adapter = None

    @classmethod
    def setup_method(cls):
        cls.cognito_boto_client = Mock()
        cls.cognito_adapter = CognitoAdapter(cls.cognito_boto_client)


class TestCognitoAdapterClientApps(BaseCognitoAdapter):
    def test_create_client_app(self):
        self.cognito_boto_client.list_user_pool_clients.return_value = {
            "UserPoolClients": []
        }

        self.cognito_boto_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "UserPoolClients": [],
            }
        ]

        client_request = ClientRequest(
            client_name="my_client", permissions=["WRITE_PUBLIC", "READ_PRIVATE"]
        )
        expected_response = ClientResponse(
            client_name="my_client",
            client_id="some_client",
            client_secret="some_secret",  # pragma: allowlist secret
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        cognito_response = {
            "UserPoolClient": {
                "UserPoolId": COGNITO_USER_POOL_ID,
                "ClientName": "my_client",
                "ClientId": "some_client",
                "ClientSecret": "some_secret",  # pragma: allowlist secret
                "LastModifiedDate": "datetime.datetime(2022, 2, 15, 16, 52, 17, 627000",
                "CreationDate": "datetime.datetime(2022, 2, 15, 16, 52, 17, 627000",
                "RefreshTokenValidity": 30,
                "TokenValidityUnits": {},
                "ExplicitAuthFlows": [
                    "ALLOW_CUSTOM_AUTH",
                    "ALLOW_USER_SRP_AUTH",
                    "ALLOW_REFRESH_TOKEN_AUTH",
                ],
                "AllowedOAuthFlows": ["client_credentials"],
                "AllowedOAuthScopes": [f"https://{DOMAIN_NAME}/read"],
                "AllowedOAuthFlowsUserPoolClient": True,
                "EnableTokenRevocation": True,
            },
            "ResponseMetadata": {
                "RequestId": "7e5b5c39-8bf8-4082-a335-fe435a8014c6",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "date": "Tue, 15 Feb 2022 16:52:17 GMT",
                    "content-type": "application/x-amz-json-1.1",
                    "content-length": "568",
                    "connection": "keep-alive",
                    "x-amzn-requestid": "7e5b5c39-8bf8-4082-a335-fe435a8014c6",
                },
                "RetryAttempts": 0,
            },
        }

        self.cognito_boto_client.create_user_pool_client.return_value = cognito_response

        actual_response = self.cognito_adapter.create_client_app(client_request)

        self.cognito_boto_client.create_user_pool_client.assert_called_once_with(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientName="my_client",
            GenerateSecret=True,
            ExplicitAuthFlows=[
                "ALLOW_REFRESH_TOKEN_AUTH",
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_USER_SRP_AUTH",
            ],
            AllowedOAuthFlows=["client_credentials"],
            AllowedOAuthScopes=[f"https://{DOMAIN_NAME}/CLIENT_APP"],
            AllowedOAuthFlowsUserPoolClient=True,
        )
        assert actual_response == expected_response

    def test_creates_client_app_with_default_allowed_oauth_scope(self):
        self.cognito_boto_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "UserPoolClients": [],
            }
        ]

        client_request = ClientRequest(
            client_name="my_client", permissions=["WRITE_PUBLIC", "READ_PRIVATE"]
        )

        self.cognito_boto_client.create_user_pool_client.return_value = {
            "UserPoolClient": {
                "UserPoolId": COGNITO_USER_POOL_ID,
                "ClientName": "my_client",
                "ClientId": "some_client",
                "ClientSecret": "some_secret",  # pragma: allowlist secret
            }
        }

        self.cognito_adapter.create_client_app(client_request)

        self.cognito_boto_client.create_user_pool_client.assert_called_once_with(
            UserPoolId=COGNITO_USER_POOL_ID,
            ClientName="my_client",
            GenerateSecret=True,
            ExplicitAuthFlows=[
                "ALLOW_REFRESH_TOKEN_AUTH",
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_USER_SRP_AUTH",
            ],
            AllowedOAuthFlows=["client_credentials"],
            AllowedOAuthScopes=[f"https://{DOMAIN_NAME}/CLIENT_APP"],
            AllowedOAuthFlowsUserPoolClient=True,
        )

    def test_delete_client_app(self):
        self.cognito_adapter.delete_client_app("client_id")
        self.cognito_boto_client.delete_user_pool_client.assert_called_once_with(
            UserPoolId=COGNITO_USER_POOL_ID, ClientId="client_id"
        )

    def test_delete_client_app_fails_when_client_does_not_exist(self):
        self.cognito_boto_client.delete_user_pool_client.side_effect = ClientError(
            error_response={"Error": {"Code": "ResourceNotFoundException"}},
            operation_name="AdminDeleteUser",
        )

        with pytest.raises(
            UserError,
            match="The client 'my_client' does not exist cognito",
        ):
            self.cognito_adapter.delete_client_app("my_client")

    def test_delete_client_app_throws_user_error_when_client_id_is_not_valid(self):
        self.cognito_boto_client.delete_user_pool_client.side_effect = ClientError(
            error_response={"Error": {"Code": "InvalidParameterException"}},
            operation_name="AdminDeleteUser",
        )

        with pytest.raises(
            UserError,
            match="The client ID is not valid",
        ):
            self.cognito_adapter.delete_client_app("hello-there")

    def test_delete_client_app_throws_service_error_when_fails_for_any_other_error(
        self,
    ):
        self.cognito_boto_client.delete_user_pool_client.side_effect = ClientError(
            error_response={"Error": {"Code": "AnyOtherError"}},
            operation_name="AdminDeleteUser",
        )

        with pytest.raises(
            AWSServiceError,
            match="Something went wrong. Please Contact your administrator.",
        ):
            self.cognito_adapter.delete_client_app("my_client")

    def test_raises_error_when_the_client_fails_to_create_in_aws(self):
        self.cognito_boto_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "UserPoolClients": [],
            }
        ]

        client_request = ClientRequest(
            client_name="my_client", permissions=["NOT_VALID"]
        )

        self.cognito_boto_client.create_user_pool_client.side_effect = ClientError(
            error_response={"Error": {"Code": "InvalidParameterException"}},
            operation_name="CreateUserPoolClient",
        )

        with pytest.raises(
            AWSServiceError, match="The client 'my_client' could not be created"
        ):
            self.cognito_adapter.create_client_app(client_request)

    def test_throws_error_when_client_app_has_duplicate_name(self):
        client_request = ClientRequest(
            client_name="existing_name_2", permissions=["VALID"]
        )

        self.cognito_boto_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "UserPoolClients": [
                    {"ClientName": "existing_name_1"},
                    {"ClientName": "existing_name_2"},
                ],
            }
        ]

        with pytest.raises(
            UserError, match="Client name 'existing_name_2' already exists"
        ):
            self.cognito_adapter.create_client_app(client_request)

    def test_throws_error_when_client_app_name_has_not_been_changed_from_placeholder_value(
        self,
    ):
        placeholder_client_name = "string"

        client_request = ClientRequest(
            client_name=placeholder_client_name, permissions=["VALID"]
        )

        self.cognito_boto_client.get_paginator.return_value.paginate.return_value = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "UserPoolClients": [],
            }
        ]

        with pytest.raises(UserError, match="You must specify a valid client name"):
            self.cognito_adapter.create_client_app(client_request)


class TestCognitoAdapterUsers(BaseCognitoAdapter):
    @mock.patch.dict(
        os.environ, {"CUSTOM_USERNAME_REGEX": "[a-zA-Z][a-zA-Z0-9@._-]{2,127}"}
    )
    def test_create_user(self):
        CUSTOM_USERNAME_REGEX = "[a-zA-Z][a-zA-Z0-9@._-]{2,127}"
        cognito_response = {
            "User": {
                "Username": "user-name",
                "Attributes": [
                    {"Name": "sub", "Value": "some-uu-id-b226-e5fd18c59b85"},
                    {"Name": "email_verified", "Value": "True"},
                    {"Name": "email", "Value": "user-name@example1.com"},
                ],
            },
            "ResponseMetadata": {
                "RequestId": "the-request-id-b368-fae5cebb746f",
                "HTTPStatusCode": 200,
            },
        }
        expected_response = UserResponse(
            username="user-name",
            email="user-name@example1.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
            user_id="some-uu-id-b226-e5fd18c59b85",
        )
        request = UserRequest(
            username="user-name",
            email="user-name@example1.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )
        self.cognito_boto_client.admin_create_user.return_value = cognito_response

        actual_response = self.cognito_adapter.create_user(request)
        self.cognito_boto_client.admin_create_user.assert_called_once_with(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username="user-name",
            UserAttributes=[
                {"Name": "email", "Value": "user-name@example1.com"},
                {"Name": "email_verified", "Value": "True"},
            ],
            DesiredDeliveryMediums=[
                "EMAIL",
            ],
        )

        assert actual_response == expected_response

    def test_delete_user(self):
        self.cognito_adapter.delete_user("username")
        self.cognito_boto_client.admin_delete_user.assert_called_once_with(
            UserPoolId=COGNITO_USER_POOL_ID, Username="username"
        )

    def test_delete_user_fails(self):
        self.cognito_boto_client.admin_delete_user.side_effect = ClientError(
            error_response={"Error": {"Code": "ResourceNotFoundException"}},
            operation_name="AdminDeleteUser",
        )

        with pytest.raises(
            AWSServiceError,
            match="Something went wrong. Please Contact your administrator.",
        ):
            self.cognito_adapter.delete_user("username")

    def test_delete_user_fails_when_user_does_not_exist(self):
        self.cognito_boto_client.admin_delete_user.side_effect = ClientError(
            error_response={"Error": {"Code": "UserNotFoundException"}},
            operation_name="AdminDeleteUser",
        )

        with pytest.raises(
            UserError,
            match="The user 'my_user' does not exist cognito",
        ):
            self.cognito_adapter.delete_user("my_user")

    @mock.patch.dict(
        os.environ, {"CUSTOM_USERNAME_REGEX": "[a-zA-Z][a-zA-Z0-9@._-]{2,127}"}
    )
    def test_create_user_fails_in_aws(self):
        request = UserRequest(
            username="user-name",
            email="user-name@example1.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        self.cognito_boto_client.admin_create_user.side_effect = ClientError(
            error_response={"Error": {"Code": "InvalidParameterException"}},
            operation_name="AdminCreateUser",
        )

        with pytest.raises(
            AWSServiceError, match="The user 'user-name' could not be created"
        ):
            self.cognito_adapter.create_user(request)

    @mock.patch.dict(
        os.environ, {"CUSTOM_USERNAME_REGEX": "[a-zA-Z][a-zA-Z0-9@._-]{2,127}"}
    )
    def test_create_user_fails_when_the_user_already_exist(self):
        request = UserRequest(
            username="user-name",
            email="user-name@example1.com",
            permissions=["WRITE_PUBLIC", "READ_PRIVATE"],
        )

        self.cognito_boto_client.admin_create_user.side_effect = ClientError(
            error_response={"Error": {"Code": "UsernameExistsException"}},
            operation_name="AdminCreateUser",
        )

        with pytest.raises(
            UserError,
            match="The user 'user-name' or email 'user-name@example1.com' already exist",
        ):
            self.cognito_adapter.create_user(request)


class TestGetSubjects(BaseCognitoAdapter):
    def test_gets_all_subjects(self):
        list_clients_response = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "UserPoolClients": [
                    {"ClientId": "the-client-id-1", "ClientName": "the_client_name_1"},
                    {"ClientId": "the-client-id-2", "ClientName": "the_client_name_2"},
                ],
            }
        ]

        list_users_response = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key": "value"},
                "Users": [
                    {
                        "Username": "user-name-1",
                        "Attributes": [
                            {"Name": "sub", "Value": "the-user-id-1"},
                            {"Name": "email_verified", "Value": "True"},
                            {"Name": "email", "Value": "fake@test.com"},
                        ],
                    },
                    {
                        "Username": "user-name-2",
                        "Attributes": [
                            {"Name": "sub", "Value": "the-user-id-2"},
                        ],
                    },
                ],
            }
        ]

        self.cognito_boto_client.get_paginator.return_value.paginate.side_effect = [
            list_clients_response,
            list_users_response,
        ]

        expected = [
            {
                "subject_id": "the-client-id-1",
                "subject_name": "the_client_name_1",
                "type": "CLIENT",
            },
            {
                "subject_id": "the-client-id-2",
                "subject_name": "the_client_name_2",
                "type": "CLIENT",
            },
            {
                "subject_id": "the-user-id-1",
                "subject_name": "user-name-1",
                "email": "fake@test.com",
                "type": "USER",
            },
            {
                "subject_id": "the-user-id-2",
                "subject_name": "user-name-2",
                "email": None,
                "type": "USER",
            },
        ]

        result = self.cognito_adapter.get_all_subjects()

        assert result == expected

    def test_raises_error_when_listing_clients_fails(self):
        self.cognito_boto_client.get_paginator.return_value.paginate.side_effect = (
            ClientError(
                error_response={"Error": {"Code": "SomeException"}},
                operation_name="ListUserPoolClients",
            )
        )

        with pytest.raises(
            AWSServiceError,
            match="The list of client apps and users could not be retrieved",
        ):
            self.cognito_adapter.get_all_subjects()

    def test_raises_error_when_listing_users_fails(self):
        list_clients_response = [
            {
                "NextToken": "xxx",
                "ResponseMetadata": {"key", "value"},
                "UserPoolClients": [
                    {"ClientId": "the-client-id-1", "ClientName": "the_client_name_1"},
                    {"ClientId": "the-client-id-2", "ClientName": "the_client_name_2"},
                ],
            }
        ]

        self.cognito_boto_client.get_paginator.return_value.paginate.side_effect = [
            list_clients_response,
            ClientError(
                error_response={"Error": {"Code": "SomeException"}},
                operation_name="ListUsers",
            ),
        ]

        with pytest.raises(
            AWSServiceError,
            match="The list of client apps and users could not be retrieved",
        ):
            self.cognito_adapter.get_all_subjects()


class TestCognitoScopes(BaseCognitoAdapter):
    def test_get_existing_scopes(self):
        resource_server_response = {
            "ResourceServer": {
                "UserPoolId": "user_pool",
                "Identifier": "identifier",
                "Name": "name",
                "Scopes": [
                    {
                        "ScopeName": "READ_PUBLIC",
                        "ScopeDescription": "READ_PUBLIC description",
                    },
                    {
                        "ScopeName": "USER-ADMIN",
                        "ScopeDescription": "USER-ADMIN description",
                    },
                    {
                        "ScopeName": "READ_PROTECTED_DOMAIN",
                        "ScopeDescription": "READ_PROTECTED_DOMAIN description",
                    },
                    {
                        "ScopeName": "READ_PROTECTED_TRUCK",
                        "ScopeDescription": "READ_PROTECTED_TRUCK description",
                    },
                ],
            }
        }
        expected_response = ["READ_PROTECTED_DOMAIN", "READ_PROTECTED_TRUCK"]

        self.cognito_boto_client.describe_resource_server.return_value = (
            resource_server_response
        )

        actual_response = self.cognito_adapter.get_protected_scopes()

        self.cognito_boto_client.describe_resource_server.assert_called_once_with(
            UserPoolId=COGNITO_USER_POOL_ID, Identifier=COGNITO_RESOURCE_SERVER_ID
        )

        assert actual_response == expected_response

    def test_get_scopes_fails(self):
        self.cognito_boto_client.describe_resource_server.side_effect = ClientError(
            error_response={"Error": {"Code": "SomeException"}},
            operation_name="DescribeResourceServer",
        )

        with pytest.raises(
            AWSServiceError,
            match="Internal server error, please contact system administrator",
        ):
            self.cognito_adapter.get_protected_scopes()
