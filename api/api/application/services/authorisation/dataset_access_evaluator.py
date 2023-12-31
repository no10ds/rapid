from enum import Enum
from typing import List

from api.common.custom_exceptions import AuthorisationError
from api.common.config.auth import Action, Sensitivity, ALL, Layer
from api.application.services.permissions_service import PermissionsService
from api.application.services.schema_service import SchemaService
from api.domain.dataset_filters import DatasetFilters
from api.domain.dataset_metadata import DatasetMetadata, LAYER, DOMAIN
from api.domain.schema_metadata import SchemaMetadata, SENSITIVITY
from api.domain.permission_item import PermissionItem


class SensitivityPermissionConverter(Enum):
    ALL = list(Sensitivity)
    PRIVATE = [Sensitivity.PRIVATE, Sensitivity.PUBLIC]
    PUBLIC = [Sensitivity.PUBLIC]
    PROTECTED = [Sensitivity.PROTECTED]


LayerPermissionConverter = Enum(
    "LayerPermissionConverter",
    dict([(layer.upper(), [layer]) for layer in list(Layer)] + [(ALL, list(Layer))]),
)


class DatasetAccessEvaluator:
    def __init__(
        self,
        schema_service=SchemaService(),
        permission_service=PermissionsService(),
    ):
        self.schema_service = schema_service
        self.permission_service = permission_service

    def get_authorised_datasets(
        self,
        subject_id: str,
        action: Action,
        filters: DatasetFilters = DatasetFilters(),
    ) -> List[DatasetMetadata]:
        """
        This function does the following:
        1. Get the permissions of the subject
        2. Filters the permission by the relevant action e.g READ/WRITE
        3. Queries the datasets to find those that match these permissions and tags
        4. Returns them
        """
        permissions = self.permission_service.get_subject_permissions(subject_id)
        permissions = self.filter_permissions_by_action(permissions, action)
        return self.fetch_datasets(permissions, filters)

    def can_access_dataset(
        self, dataset: DatasetMetadata, subject_id: str, actions: List[Action]
    ):
        """
        This function does the following:
        1. Gets the permissions of the subject
        2. Gets the schema metadata of the dataset
        3. Loops through the dataset actions
        4. Filters the permission by the relevant action
        5. Assesses if the schema metadata overlaps with the permissions, returning True if they do
        6. Raise Authorisation if the loop is over and there was no permission overlap
        """
        permissions = self.permission_service.get_subject_permissions(subject_id)
        schema_metadata = self.schema_service.get_schema(dataset).metadata

        for action in actions:
            filtered_permissions = self.filter_permissions_by_action(
                permissions, action
            )
            if any(
                self.schema_metadata_overlaps_with_permission(
                    schema_metadata, permission
                )
                for permission in filtered_permissions
            ):
                return True
        raise AuthorisationError(
            f"User {subject_id} does not have enough permissions to access the dataset {dataset.string_representation()}"
        )

    def schema_metadata_overlaps_with_permission(
        self, schema_metadata: SchemaMetadata, permission: PermissionItem
    ) -> bool:
        return all(
            [
                schema_metadata.get_sensitivity()
                in SensitivityPermissionConverter[permission.sensitivity].value,
                schema_metadata.get_layer()
                in LayerPermissionConverter[permission.layer].value,
                schema_metadata.get_domain() == permission.get_domain()
                if permission.is_protected_permission()
                else True,
            ]
        )

    def filter_permissions_by_action(
        self, permissions: List[PermissionItem], action: Action
    ):
        return [permission for permission in permissions if permission.type == action]

    def fetch_datasets(
        self,
        permissions: List[PermissionItem],
        filters: DatasetFilters = DatasetFilters(),
    ) -> List[SchemaMetadata]:
        authorised_datasets = set()
        for permission in permissions:
            authorised_datasets.update(
                self.extract_datasets_from_permission(permission, filters)
            )
        return sorted(authorised_datasets)

    def extract_datasets_from_permission(
        self, permission: PermissionItem, filters: DatasetFilters = DatasetFilters()
    ) -> List[SchemaMetadata]:
        """
        Extracts the datasets from the permission, while combining with the filters argument.
        The permission filters overwrite the filters argument to stop any injection of permissions via the filters.
        """
        query = DatasetFilters(
            **(
                # If there are overlapping keys, the permission values will overwrite the others
                dict(filters)
                | {
                    SENSITIVITY: SensitivityPermissionConverter[
                        permission.sensitivity
                    ].value,
                    LAYER: LayerPermissionConverter[permission.layer].value,
                    DOMAIN: permission.domain,
                }
            )
        )
        return self.schema_service.get_schema_metadatas(query)
