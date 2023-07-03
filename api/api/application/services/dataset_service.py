from typing import Set, Dict, List

from api.common.config.auth import SensitivityLevel, Action
from api.adapter.aws_resource_adapter import AWSResourceAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.adapter.glue_adapter import GlueAdapter
from api.adapter.s3_adapter import S3Adapter
from api.domain.dataset_filters import DatasetFilters

WRITE_ALL = f"{Action.WRITE.value}_ALL"
WRITE_PRIVATE = f"{Action.WRITE.value}_{SensitivityLevel.PRIVATE.value}"
WRITE_PUBLIC = f"{Action.WRITE.value}_{SensitivityLevel.PUBLIC.value}"
READ_ALL = f"{Action.READ.value}_ALL"
READ_PRIVATE = f"{Action.READ.value}_{SensitivityLevel.PRIVATE.value}"
READ_PUBLIC = f"{Action.READ.value}_{SensitivityLevel.PUBLIC.value}"

sensitivities_dict = {
    WRITE_ALL: SensitivityLevel.get_all_values(),
    WRITE_PRIVATE: [SensitivityLevel.PRIVATE.value, SensitivityLevel.PUBLIC.value],
    WRITE_PUBLIC: [SensitivityLevel.PUBLIC.value],
    READ_ALL: SensitivityLevel.get_all_values(),
    READ_PRIVATE: [SensitivityLevel.PRIVATE.value, SensitivityLevel.PUBLIC.value],
    READ_PUBLIC: [SensitivityLevel.PUBLIC.value],
}


class DatasetService:
    def __init__(
        self,
        resource_adapter=AWSResourceAdapter(),
        dynamodb_adapter=DynamoDBAdapter(),
        glue_adapter=GlueAdapter(),
        s3_adapter=S3Adapter(),
    ):
        self.dynamodb_adapter = dynamodb_adapter
        self.resource_adapter = resource_adapter
        self.s3_adapter = s3_adapter
        self.glue_adapter = glue_adapter

    def get_authorised_datasets(
        self,
        subject_id: str,
        action: Action,
        tag_filters: DatasetFilters = DatasetFilters(),
    ) -> List[str]:
        permissions = self.dynamodb_adapter.get_permissions_for_subject(subject_id)
        sensitivities_and_domains = self._extract_sensitivities_and_domains(
            permissions, action
        )
        return self._fetch_datasets(sensitivities_and_domains, tag_filters)

    def _extract_sensitivities_and_domains(
        self, permissions: List[str], action: Action
    ) -> Dict[str, Set[str]]:
        sensitivities = set()
        protected_domains = set()

        relevant_permissions = [
            permission
            for permission in permissions
            if permission.startswith(action.value)
        ]
        for permission in relevant_permissions:
            if self._is_protected_permission(permission, action):
                slice_index = self._protected_index_map(action)
                protected_domains.add(permission[slice_index:])
            else:
                sensitivities.update(sensitivities_dict.get(permission))
        return {"protected_domains": protected_domains, "sensitivities": sensitivities}

    def _fetch_datasets(
        self, sensitivities_and_domains: Dict[str, Set[str]], tag_filters
    ):
        authorised_datasets = list()

        if len(sensitivities_and_domains.get("sensitivities")) > 0:
            self._extract_datasets_from_sensitivities(
                authorised_datasets, sensitivities_and_domains, tag_filters
            )
        if len(sensitivities_and_domains.get("protected_domains")) > 0:
            self._extract_datasets_from_protected_domains(
                authorised_datasets, sensitivities_and_domains, tag_filters
            )

        # Now filter the list to only get unique values
        # return the values of a new dictionary that use the unique upload_path as a key
        return sorted(
            list(
                {
                    dataset.get_ui_upload_path(): dataset
                    for dataset in authorised_datasets
                }.values()
            ),
            key=lambda d: d.domain,
        )

    def _extract_datasets_from_protected_domains(
        self, authorised_datasets, sensitivities_and_domains, tag_filters
    ):
        query = DatasetFilters(
            sensitivity=SensitivityLevel.PROTECTED.value,
            key_value_tags=tag_filters.key_value_tags,
            key_only_tags=tag_filters.key_only_tags,
        )
        datasets_metadata_list_protected_domains = (
            self.resource_adapter.get_datasets_metadata(
                self.s3_adapter, self.glue_adapter, query
            )
        )
        for protected_domain in sensitivities_and_domains.get("protected_domains"):
            for dataset in datasets_metadata_list_protected_domains:
                if dataset.domain == protected_domain.lower():
                    authorised_datasets.append(dataset)

    def _extract_datasets_from_sensitivities(
        self, authorised_datasets, sensitivities_and_domains, tag_filters
    ):
        datasets_metadata_list_sensitivities = []

        for sensitivity in sensitivities_and_domains.get("sensitivities"):
            query = DatasetFilters(
                sensitivity=sensitivity,
                key_value_tags=tag_filters.key_value_tags,
                key_only_tags=tag_filters.key_only_tags,
            )
            datasets_metadata_list_sensitivities.extend(
                self.resource_adapter.get_datasets_metadata(
                    self.s3_adapter, self.glue_adapter, query
                )
            )

            for datasets_metadata in datasets_metadata_list_sensitivities:
                authorised_datasets.append(datasets_metadata)

    def _is_protected_permission(self, permission: str, action: Action) -> bool:
        return permission.startswith(
            f"{action.value}_{SensitivityLevel.PROTECTED.value}_"
        )

    def _protected_index_map(self, action: Action) -> int:
        return {
            Action.WRITE.value: len(
                f"{Action.WRITE.value}_{SensitivityLevel.PROTECTED.value}_"
            ),
            Action.READ.value: len(
                f"{Action.READ.value}_{SensitivityLevel.PROTECTED.value}_"
            ),
        }[action.value]
