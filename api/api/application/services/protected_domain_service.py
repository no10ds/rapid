from typing import List, Set

from api.adapter.aws_resource_adapter import AWSResourceAdapter
from api.adapter.cognito_adapter import CognitoAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.adapter.s3_adapter import S3Adapter
from api.application.services.schema_validation import valid_domain_name
from api.common.config.auth import (
    SensitivityLevel,
    Action,
)
from api.common.custom_exceptions import ConflictError, UserError, DomainNotEmptyError
from api.common.logger import AppLogger
from api.domain.permission_item import PermissionItem
from api.domain.dataset_filters import DatasetFilters
from api.domain.subject_permissions import SubjectPermissions


class ProtectedDomainService:
    def __init__(
        self,
        cognito_adapter=CognitoAdapter(),
        dynamodb_adapter=DynamoDBAdapter(),
        resource_adapter=AWSResourceAdapter(),
        s3_adapter=S3Adapter(),
    ):
        self.cognito_adapter = cognito_adapter
        self.dynamodb_adapter = dynamodb_adapter
        self.resource_adapter = resource_adapter
        self.s3_adapter = s3_adapter

    def create_protected_domain_permission(self, domain: str) -> None:
        AppLogger.info(f"Creating protected domain permission {domain}")
        domain = domain.upper().strip()

        if not valid_domain_name(domain):
            raise UserError(
                f"The value set for domain [{domain}] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character"
            )

        self._verify_protected_domain_does_not_exist(domain)

        generated_permissions = self._generate_protected_permission_items(domain)

        self.dynamodb_adapter.store_protected_permissions(generated_permissions, domain)

    def list_protected_domains(self) -> Set[str]:
        return self._list_protected_permission_domains()

    def delete_protected_domain_permission(
        self, domain: str, user_subjects_list: List[str | None]
    ) -> None:
        AppLogger.info(f"Deleting protected domain permission {domain}")
        domain = domain.lower().strip()

        # Ensure the domain they want to delete exists in the list of protected domains
        self._verify_protected_domain_does_exist(domain)

        # Ensure the domain is currently empty of any datasets
        self._verify_protected_domain_is_empty(domain)

        # Delete the read and write protected permissions from the table
        read_protected_id = (
            f"{Action.READ.value}_{SensitivityLevel.PROTECTED.value}_{domain.upper()}"
        )
        write_protected_id = (
            f"{Action.WRITE.value}_{SensitivityLevel.PROTECTED.value}_{domain.upper()}"
        )
        self.dynamodb_adapter.delete_permission(read_protected_id)
        self.dynamodb_adapter.delete_permission(write_protected_id)

        for user in user_subjects_list:
            user_permissions = self.dynamodb_adapter.get_permissions_for_subject(user)
            # Drop the read protected permission from the user
            if read_protected_id in user_permissions:
                user_permissions.remove(read_protected_id)
            # Drop the write protected permission from the user
            if write_protected_id in user_permissions:
                user_permissions.remove(write_protected_id)

            # Push changes back for updated user
            self.dynamodb_adapter.update_subject_permissions(
                subject_permissions=SubjectPermissions(
                    subject_id=user, permissions=user_permissions
                )
            )

    def _list_protected_permission_domains(self):
        permission_items = self.dynamodb_adapter.get_all_protected_permissions()
        return set([item.domain.lower() for item in permission_items])

    def _verify_protected_domain_does_not_exist(self, domain):
        if domain.lower() in self._list_protected_permission_domains():
            AppLogger.info(f"The protected domain, [{domain}] already exists")
            raise ConflictError(f"The protected domain, [{domain}] already exists")

    def _verify_protected_domain_does_exist(self, domain):
        if domain.lower() not in self._list_protected_permission_domains():
            AppLogger.info(f"The protected domain, [{domain}] does not exist")
            raise UserError(f"The protected domain, [{domain}] does not exist.")

    def _verify_protected_domain_is_empty(self, domain):
        query = DatasetFilters(sensitivity=SensitivityLevel.PROTECTED.value)
        datasets_metadata = self.resource_adapter.get_datasets_metadata(
            s3_adapter=self.s3_adapter, query=query
        )
        datasets = [data.dataset for data in datasets_metadata if data.domain == domain]
        if datasets:
            # Prompt to the user that datasets still exist and tell them to delete them
            raise DomainNotEmptyError(
                f"Cannot delete protected domain [{domain}] as it is not empty. Please delete the datasets {datasets}."
            )

    def _generate_protected_permission_items(self, domain) -> List[PermissionItem]:
        read_permission_item = PermissionItem(
            id=f"{Action.READ.value}_{SensitivityLevel.PROTECTED.value}_{domain}",
            type=Action.READ.value,
            sensitivity=SensitivityLevel.PROTECTED.value,
            domain=domain,
        )
        write_permission_item = PermissionItem(
            id=f"{Action.WRITE.value}_{SensitivityLevel.PROTECTED.value}_{domain}",
            type=Action.WRITE.value,
            sensitivity=SensitivityLevel.PROTECTED.value,
            domain=domain,
        )

        return [read_permission_item, write_permission_item]
