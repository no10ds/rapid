from unittest.mock import patch

from api.adapter.aws_resource_adapter import AWSResourceAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.application.services.dataset_service import DatasetService
from api.common.config.auth import Action


class TestWriteDatasets:
    upload_service = DatasetService()

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.WRITE
        subject_id = "1234adsfasd8234kj"
        permissions = ["READ_PRIVATE", "WRITE_PUBLIC", "WRITE_PRIVATE"]
        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_1", domain="test_domain_1", version=1
        )
        enriched_dataset_metadata_2 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_2", domain="test_domain_2", version=2
        )

        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.side_effect = [
            [enriched_dataset_metadata_1],
            [enriched_dataset_metadata_2],
        ]

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 2
        assert enriched_dataset_metadata_1 in result
        assert enriched_dataset_metadata_2 in result
        assert mock_get_datasets_metadata.call_count == 2
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets_with_write_all_permission(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.WRITE
        subject_id = "1234adsfasd8234kj"
        permissions = ["READ_PRIVATE", "WRITE_ALL", "WRITE_PRIVATE"]
        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_public_dataset", domain="test_domain_1"
        )
        enriched_dataset_metadata_2 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_private_dataset", domain="test_domain_2", version=2
        )

        enriched_dataset_metadata_3 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_protected_dataset", domain="test_domain_3", version=3
        )

        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.side_effect = [
            [enriched_dataset_metadata_1],
            [enriched_dataset_metadata_2],
            [enriched_dataset_metadata_3],
        ]

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 3
        assert enriched_dataset_metadata_1 in result
        assert enriched_dataset_metadata_2 in result
        assert enriched_dataset_metadata_3 in result
        assert mock_get_datasets_metadata.call_count == 3
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets_for_write_public(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.WRITE
        subject_id = "1234adsfasd8234kj"
        permissions = ["READ_ALL", "WRITE_PUBLIC"]
        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_1", domain="test_domain_1", version=3
        )
        enriched_dataset_metadata_list = [
            enriched_dataset_metadata_1,
        ]
        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.return_value = enriched_dataset_metadata_list

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 1
        assert enriched_dataset_metadata_1 in result
        assert mock_get_datasets_metadata.call_count == 1
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets_for_write_protected_domain(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.WRITE
        subject_id = "1234adsfasd8234kj"
        permissions = ["READ_ALL", "WRITE_PUBLIC", "WRITE_PROTECTED_TEST2DOMAIN"]
        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_1", domain="some_domain"
        )
        enriched_dataset_metadata_protected_domain = (
            AWSResourceAdapter.EnrichedDatasetMetaData(
                dataset="test_dataset_2", domain="test2domain"
            )
        )

        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.side_effect = [
            [enriched_dataset_metadata_1],
            [enriched_dataset_metadata_protected_domain],
        ]

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 2
        assert enriched_dataset_metadata_1 in result
        assert enriched_dataset_metadata_protected_domain in result
        assert mock_get_datasets_metadata.call_count == 2
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)


class TestReadDatasets:
    upload_service = DatasetService()

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.READ
        subject_id = "1234adsfasd8234kj"
        permissions = ["READ_PRIVATE", "READ_PUBLIC", "WRITE_PRIVATE"]
        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_1", domain="test_domain_1"
        )
        enriched_dataset_metadata_2 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_2", domain="test_domain_2", version=2
        )

        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.side_effect = [
            [enriched_dataset_metadata_1],
            [enriched_dataset_metadata_2],
        ]

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 2
        assert enriched_dataset_metadata_1 in result
        assert enriched_dataset_metadata_2 in result
        assert mock_get_datasets_metadata.call_count == 2
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets_with_read_all_permission(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.READ
        subject_id = "1234adsfasd8234kj"
        permissions = ["READ_PRIVATE", "READ_ALL", "WRITE_PRIVATE"]

        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_public_dataset", domain="test_domain_1", version=2
        )
        enriched_dataset_metadata_2 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_private_dataset", domain="test_domain_2", version=2
        )
        enriched_dataset_metadata_3 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_protected_dataset", domain="test_domain_3", version=2
        )

        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.side_effect = [
            [enriched_dataset_metadata_1],
            [enriched_dataset_metadata_2],
            [enriched_dataset_metadata_3],
        ]

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 3
        assert enriched_dataset_metadata_1 in result
        assert enriched_dataset_metadata_2 in result
        assert enriched_dataset_metadata_3 in result
        assert mock_get_datasets_metadata.call_count == 3
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets_for_read_public(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.READ
        subject_id = "1234adsfasd8234kj"
        permissions = ["WRITE_ALL", "READ_PUBLIC"]
        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_1", domain="test_domain_1", version=100
        )
        enriched_dataset_metadata_list = [
            enriched_dataset_metadata_1,
        ]
        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.return_value = enriched_dataset_metadata_list

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 1
        assert enriched_dataset_metadata_1 in result
        assert mock_get_datasets_metadata.call_count == 1
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)

    @patch.object(AWSResourceAdapter, "get_datasets_metadata")
    @patch.object(DynamoDBAdapter, "get_permissions_for_subject")
    def test_get_authorised_datasets_for_read_protected_domain(
        self, mock_get_permissions_for_subject, mock_get_datasets_metadata
    ):
        action = Action.READ
        subject_id = "1234adsfasd8234kj"
        permissions = ["WRITE_ALL", "READ_PUBLIC", "READ_PROTECTED_TEST2DOMAIN"]
        enriched_dataset_metadata_1 = AWSResourceAdapter.EnrichedDatasetMetaData(
            dataset="test_dataset_1", domain="some_domain", version=2
        )
        enriched_dataset_metadata_protected_domain = (
            AWSResourceAdapter.EnrichedDatasetMetaData(
                dataset="test_dataset_2", domain="test2domain", version=1
            )
        )

        mock_get_permissions_for_subject.return_value = permissions
        mock_get_datasets_metadata.side_effect = [
            [enriched_dataset_metadata_1],
            [enriched_dataset_metadata_protected_domain],
        ]

        result = self.upload_service.get_authorised_datasets(subject_id, action)

        assert len(result) == 2
        assert enriched_dataset_metadata_1 in result
        assert enriched_dataset_metadata_protected_domain in result
        assert mock_get_datasets_metadata.call_count == 2
        mock_get_permissions_for_subject.assert_called_once_with(subject_id)
