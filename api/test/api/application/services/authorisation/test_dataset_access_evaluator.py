from itertools import compress
from unittest.mock import Mock
import pytest

from api.application.services.authorisation.dataset_access_evaluator import (
    DatasetAccessEvaluator,
    LayerPermissionConverter,
)
from api.common.config.auth import Action
from api.common.custom_exceptions import AuthorisationError
from api.domain.dataset_filters import DatasetFilters
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.permission_item import PermissionItem
from api.domain.schema import Schema


class TestDatasetAccessEvaluator:
    def setup_method(self):
        self.schema_service = Mock()
        self.permission_service = Mock()
        self.evaluator = DatasetAccessEvaluator(
            schema_service=self.schema_service,
            permission_service=self.permission_service,
        )

    def test_layer_permission_converter(self):
        expected = {"RAW": ["raw"], "LAYER": ["layer"], "ALL": ["raw", "layer"]}
        actual = {i.name: i.value for i in LayerPermissionConverter}
        assert actual == expected

    @pytest.mark.parametrize(
        "permission, input_filters, expected_filters",
        [
            (
                PermissionItem(
                    id="READ_ALL_ALL", layer="ALL", sensitivity="ALL", type="READ"
                ),
                DatasetFilters(),
                DatasetFilters(
                    sensitivity=["PUBLIC", "PRIVATE", "PROTECTED"],
                    layer=["raw", "layer"],
                ),
            ),
            (
                PermissionItem(
                    id="WRITE_RAW_ALL",
                    layer="RAW",
                    sensitivity="ALL",
                    type="WRITE",
                ),
                DatasetFilters(),
                DatasetFilters(
                    sensitivity=["PUBLIC", "PRIVATE", "PROTECTED"], layer=["raw"]
                ),
            ),
            (
                PermissionItem(
                    id="WRITE_ALL_PUBLIC",
                    layer="ALL",
                    sensitivity="PUBLIC",
                    type="WRITE",
                ),
                DatasetFilters(),
                DatasetFilters(sensitivity=["PUBLIC"], layer=["raw", "layer"]),
            ),
            (
                PermissionItem(
                    id="READ_RAW_PROTECTED_TEST",
                    layer="RAW",
                    sensitivity="PROTECTED",
                    type="READ",
                    domain="TEST",
                ),
                DatasetFilters(),
                DatasetFilters(sensitivity=["PROTECTED"], layer=["raw"], domain="TEST"),
            ),
            (
                PermissionItem(
                    id="READ_ALL_ALL", layer="ALL", sensitivity="ALL", type="READ"
                ),
                DatasetFilters(key_only_tags=["tag1"]),
                DatasetFilters(
                    sensitivity=["PUBLIC", "PRIVATE", "PROTECTED"],
                    layer=["raw", "layer"],
                    key_only_tags=["tag1"],
                ),
            ),
            (
                PermissionItem(
                    id="WRITE_ALL_PUBLIC",
                    layer="ALL",
                    sensitivity="PUBLIC",
                    type="WRITE",
                ),
                DatasetFilters(sensitivity="ALL"),
                DatasetFilters(sensitivity=["PUBLIC"], layer=["raw", "layer"]),
            ),
        ],
    )
    def test_extract_datasets_from_permission(
        self, permission, input_filters, expected_filters
    ):
        self.schema_service.get_schema_metadatas = Mock()
        self.schema_service.get_schema_metadatas.return_value = "dataset"

        res = self.evaluator.extract_datasets_from_permission(permission, input_filters)

        self.schema_service.get_schema_metadatas.assert_called_once_with(
            expected_filters
        )
        assert res == "dataset"

    def test_fetch_datasets(self):
        permissions = [
            PermissionItem(
                id="READ_ALL",
                layer="ALL",
                sensitivity="ALL",
                type="READ",
            ),
            PermissionItem(
                id="READ_RAW_PROTECTED_TEST",
                layer="RAW",
                sensitivity="PROTECTED",
                type="READ",
                domain="TEST",
            ),
        ]

        self.evaluator.extract_datasets_from_permission = Mock(
            side_effect=[
                [
                    DatasetMetadata(layer="raw", domain="domain", dataset="dataset"),
                    DatasetMetadata(layer="raw", domain="domain_1", dataset="dataset"),
                ],
                [
                    DatasetMetadata(layer="raw", domain="domain", dataset="dataset"),
                    DatasetMetadata(layer="raw", domain="domain_2", dataset="dataset"),
                ],
            ]
        )

        expected = [
            DatasetMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                version=None,
            ),
            DatasetMetadata(
                layer="raw",
                domain="domain_1",
                dataset="dataset",
                version=None,
            ),
            DatasetMetadata(
                layer="raw",
                domain="domain_2",
                dataset="dataset",
                version=None,
            ),
        ]

        res = self.evaluator.fetch_datasets(permissions)

        assert res == expected

    @pytest.mark.parametrize(
        "metadata, permission, expected",
        [
            # 0. Success: All criteria overlap directly
            (
                Schema(
                    layer="raw",
                    domain="test",
                    dataset="dataset",
                    sensitivity="PUBLIC",
                ),
                PermissionItem(
                    id="READ_RAW_PUBLIC", type="READ", layer="RAW", sensitivity="PUBLIC"
                ),
                True,
            ),
            # 1. Success: All criteria overlap directly with protected domain
            (
                Schema(
                    layer="raw",
                    domain="test",
                    dataset="dataset",
                    sensitivity="PROTECTED",
                ),
                PermissionItem(
                    id="WRITE_RAW_PROTECTED_TEST",
                    type="WRITE",
                    layer="RAW",
                    sensitivity="PROTECTED",
                    domain="TEST",
                ),
                True,
            ),
            # 2. Success: All criteria inherit overlaps
            (
                Schema(
                    layer="raw",
                    domain="test",
                    dataset="dataset",
                    sensitivity="PUBLIC",
                ),
                PermissionItem(
                    id="WRITE_ALL_PRIVATE",
                    type="WRITE",
                    layer="ALL",
                    sensitivity="PRIVATE",
                ),
                True,
            ),
            # 3. Failure: Sensitivity does not overlap
            (
                Schema(
                    layer="raw",
                    domain="test",
                    dataset="dataset",
                    sensitivity="PRIVATE",
                ),
                PermissionItem(
                    id="READ_RAW_PUBLIC", type="READ", layer="RAW", sensitivity="PUBLIC"
                ),
                False,
            ),
            # 4. Failure: Layer does not overlap
            (
                Schema(
                    layer="raw",
                    domain="test",
                    dataset="dataset",
                    sensitivity="PRIVATE",
                ),
                PermissionItem(
                    id="READ_LAYER_PRIVATE",
                    type="READ",
                    layer="LAYER",
                    sensitivity="PRIVATE",
                ),
                False,
            ),
            # 5. Failure: Is protected and domain does not overlap
            (
                Schema(
                    layer="raw",
                    domain="test_fail",
                    dataset="dataset",
                    sensitivity="PROTECTED",
                ),
                PermissionItem(
                    id="READ_ANY_PROTECTED_TEST",
                    type="READ",
                    layer="ALL",
                    sensitivity="PROTECTED",
                    domain="TEST",
                ),
                False,
            ),
        ],
    )
    def test_schema_metadata_overlaps_with_permission(
        self, schema: Schema, permission: PermissionItem, expected: bool
    ):
        res = self.evaluator.schema_metadata_overlaps_with_permission(
            schema, permission
        )
        assert res == expected

    @pytest.mark.parametrize(
        "action, permission_mask",
        [(Action.READ, [True, False, False]), (Action.WRITE, [False, True, True])],
    )
    def test_get_authorised_datasets(self, action: Action, permission_mask: list[bool]):
        subject_id = "abc-123"
        permissions = [
            PermissionItem(
                id="READ_ALL_PUBLIC", layer="ALL", type="READ", sensitivity="PUBLIC"
            ),
            PermissionItem(
                id="WRITE_ALL_PUBLIC", layer="ALL", type="WRITE", sensitivity="PUBLIC"
            ),
            PermissionItem(
                id="WRITE_ALL_PRIVATE", layer="ALL", type="WRITE", sensitivity="PRIVATE"
            ),
        ]

        self.permission_service.get_subject_permissions = Mock(return_value=permissions)
        self.evaluator.fetch_datasets = Mock(return_value=["dataset"])

        res = self.evaluator.get_authorised_datasets(
            subject_id, action, "dataset_filter"
        )
        assert res == ["dataset"]
        self.permission_service.get_subject_permissions.assert_called_once_with(
            subject_id
        )
        self.evaluator.fetch_datasets.assert_called_once_with(
            list(compress(permissions, permission_mask)), "dataset_filter"
        )

    def test_can_access_dataset_success(self):
        subject_id = "abc-123"
        dataset = "dataset"
        read_permissions = [
            PermissionItem(
                id="READ_ALL_PUBLIC", layer="ALL", type="READ", sensitivity="PUBLIC"
            )
        ]
        write_permissions = [
            PermissionItem(
                id="WRITE_ALL_PUBLIC", layer="ALL", type="WRITE", sensitivity="PUBLIC"
            ),
            PermissionItem(
                id="WRITE_ALL_PRIVATE", layer="ALL", type="WRITE", sensitivity="PRIVATE"
            ),
        ]
        schema = Schema(
            dataset_metadata=DatasetMetadata(
                layer="raw",
                domain="test_fail",
                dataset="dataset",
            ),
            sensitivity="PRIVATE",
            columns={},
        )

        self.permission_service.get_subject_permissions = Mock(
            return_value=read_permissions + write_permissions
        )
        self.schema_service.get_schema = Mock(return_value=schema)

        res = self.evaluator.can_access_dataset(
            dataset, subject_id, [Action.WRITE, Action.READ]
        )

        self.permission_service.get_subject_permissions.assert_called_once_with(
            subject_id
        )
        self.schema_service.get_schema.assert_called_once_with(dataset)
        assert res is True

    def test_can_access_dataset_failure(self):
        subject_id = "abc-123"
        dataset = DatasetMetadata("layer", "domain", "dataset")
        read_permissions = [
            PermissionItem(
                id="READ_ALL_PUBLIC", layer="ALL", type="READ", sensitivity="PUBLIC"
            )
        ]
        write_permissions = [
            PermissionItem(
                id="WRITE_ALL_PUBLIC", layer="ALL", type="WRITE", sensitivity="PUBLIC"
            ),
            PermissionItem(
                id="WRITE_ALL_PRIVATE", layer="ALL", type="WRITE", sensitivity="PRIVATE"
            ),
        ]
        schema = Schema(
            dataset_metadata=DatasetMetadata(
                layer="raw",
                domain="test_fail",
                dataset="dataset",
            ),
            sensitivity="PRIVATE",
            columns={},
        )

        self.permission_service.get_subject_permissions = Mock(
            return_value=read_permissions + write_permissions
        )
        self.schema_service.get_schema = Mock(return_value=schema)

        with pytest.raises(
            AuthorisationError,
            match="User abc-123 does not have enough permissions to access the dataset layer \\[layer\\], domain \\[domain\\] and dataset \\[dataset\\]",
        ):
            self.evaluator.can_access_dataset(dataset, subject_id, [Action.READ])

            self.permission_service.get_subject_permissions.assert_called_once_with(
                subject_id
            )
            self.schema_service.get_schema.assert_called_once_with(dataset)
