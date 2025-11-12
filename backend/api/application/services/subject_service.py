from typing import List, Dict, Optional

from api.adapter.cognito_adapter import CognitoAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.common.config.auth import SubjectType
from api.common.custom_exceptions import UserError
from api.common.logger import AppLogger
from api.domain.client import ClientResponse, ClientRequest
from api.domain.subject_permissions import SubjectPermissions
from api.domain.user import UserRequest, UserResponse, UserDeleteRequest


class SubjectService:
    def __init__(
        self, cognito_adapter=CognitoAdapter(), dynamodb_adapter=DynamoDBAdapter()
    ):
        self.cognito_adapter = cognito_adapter
        self.dynamodb_adapter = dynamodb_adapter

    def create_client(self, client_request: ClientRequest) -> ClientResponse:
        self.dynamodb_adapter.validate_permissions(client_request.get_permissions())
        client_response = self.cognito_adapter.create_client_app(client_request)
        self._store_client_permissions(client_request, client_response)

        return client_response

    def create_user(self, user_request: UserRequest) -> UserResponse:
        self.dynamodb_adapter.validate_permissions(user_request.get_permissions())
        user_response = self.cognito_adapter.create_user(user_request)
        self._store_user_permissions(user_request, user_response)

        return user_response

    def delete_user(self, delete_request: UserDeleteRequest) -> None:
        self.dynamodb_adapter.delete_subject(delete_request.user_id)
        self.cognito_adapter.delete_user(delete_request.username)

    def delete_client(self, client_id: str) -> None:
        self.dynamodb_adapter.delete_subject(client_id)
        self.cognito_adapter.delete_client_app(client_id)

    def _store_client_permissions(
        self, client_request: ClientRequest, client_response: ClientResponse
    ):
        try:
            self.dynamodb_adapter.store_subject_permissions(
                SubjectType.CLIENT,
                client_response.client_id,
                client_request.get_permissions(),
            )
        except Exception as error:
            self.cognito_adapter.delete_client_app(client_response.client_id)
            raise error

    def _store_user_permissions(
        self, user_request: UserRequest, user_response: UserResponse
    ):
        try:
            self.dynamodb_adapter.store_subject_permissions(
                SubjectType.USER, user_response.user_id, user_request.get_permissions()
            )
        except Exception as error:
            self.cognito_adapter.delete_user(user_response.username)
            raise error

    def set_subject_permissions(
        self, subject_permissions: SubjectPermissions
    ) -> SubjectPermissions:
        self.dynamodb_adapter.validate_permissions(subject_permissions.permissions)
        self.dynamodb_adapter.update_subject_permissions(subject_permissions)
        return subject_permissions

    def get_subject_name_by_id(self, subject_id: str) -> str:
        result = [
            subject["subject_name"]
            for subject in self.cognito_adapter.get_all_subjects()
            if subject["subject_id"] == subject_id
        ]
        if result:
            return result[0]
        raise UserError(f"Subject with ID {subject_id} does not exist")

    def list_subjects(self) -> List[Dict[str, Optional[str]]]:
        return self.cognito_adapter.get_all_subjects()
