from unittest.mock import Mock, call, patch

import pytest
from boto3.dynamodb.conditions import Key, Attr, Or
from botocore.exceptions import ClientError

from api.adapter.dynamodb_adapter import DynamoDBAdapter
from api.common.config.auth import SubjectType
from api.common.custom_exceptions import (
    AWSServiceError,
    UserError,
)
from api.domain.Jobs.Job import JobStatus
from api.domain.Jobs.QueryJob import QueryJob, QueryStep
from api.domain.Jobs.UploadJob import UploadJob, UploadStep
from api.domain.dataset_filters import DatasetFilters
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.permission_item import PermissionItem
from api.domain.subject_permissions import SubjectPermissions
from api.domain.schema import Column, Schema
from api.domain.schema_metadata import SchemaMetadata, Owner


class TestDynamoDBAdapterGeneric:
    def setup_method(self):
        self.dynamo_data_source = Mock()

        self.dynamo_data_source.Table.side_effect = [
            Mock(),
            Mock(),
            Mock(),
        ]

        self.dynamo_adapter = DynamoDBAdapter(self.dynamo_data_source)

    def test_collect_all_items(self):
        mock_call = Mock()
        mock_call.side_effect = [
            {"Items": ["item1", "item2"], "LastEvaluatedKey": "last_evaluated_key"},
            {"Items": ["item3", "item4"]},
        ]

        actual_items = self.dynamo_adapter.collect_all_items(mock_call, key="arg")

        assert actual_items == ["item1", "item2", "item3", "item4"]
        mock_call.assert_has_calls(
            [call(key="arg"), call(ExclusiveStartKey="last_evaluated_key", key="arg")]
        )


class TestDynamoDBAdapterPermissionsTable:
    expected_db_query_response = {
        "Items": [
            {
                "PK": "PERMISSION",
                "SK": "USER_ADMIN",
                "Id": "USER_ADMIN",
                "Type": "USER_ADMIN",
            },
            {
                "PK": "PERMISSION",
                "SK": "READ_ALL",
                "Id": "READ_ALL",
                "Sensitivity": "ALL",
                "Type": "READ",
            },
            {
                "PK": "PERMISSION",
                "SK": "WRITE_ALL",
                "Id": "WRITE_ALL",
                "Sensitivity": "ALL",
                "Type": "WRITE",
            },
            {
                "PK": "PERMISSION",
                "SK": "READ_PRIVATE",
                "Id": "READ_PRIVATE",
                "Sensitivity": "PRIVATE",
                "Type": "READ",
            },
        ],
        "Count": 4,
    }

    def setup_method(self):
        self.dynamo_data_source = Mock()

        self.permissions_table = Mock()
        self.service_table = Mock()
        self.schema_table = Mock()

        self.dynamo_data_source.Table.side_effect = [
            self.permissions_table,
            self.service_table,
            self.schema_table,
        ]

        self.dynamo_adapter = DynamoDBAdapter(self.dynamo_data_source)

    def test_store_subject_permissions(self):
        client_id = "123456789"
        client_permissions = ["READ_ALL", "WRITE_ALL", "READ_PRIVATE", "USER_ADMIN"]
        expected_client_permissions = {
            "READ_ALL",
            "WRITE_ALL",
            "READ_PRIVATE",
            "USER_ADMIN",
        }
        self.permissions_table.query.return_value = self.expected_db_query_response

        self.dynamo_adapter.store_subject_permissions(
            SubjectType.CLIENT, client_id, client_permissions
        )

        self.permissions_table.put_item.assert_called_once_with(
            Item={
                "PK": "SUBJECT",
                "SK": client_id,
                "Id": client_id,
                "Type": "CLIENT",
                "Permissions": expected_client_permissions,
            },
        )
        self.service_table.assert_not_called()

    def test_store_subject_permissions_throws_error_when_database_call_fails(self):
        subject_id = "123456789"
        permissions = ["READ_ALL", "WRITE_ALL", "READ_PRIVATE", "USER_ADMIN"]
        subject_type = SubjectType.CLIENT
        self.permissions_table.query.return_value = self.expected_db_query_response

        self.permissions_table.put_item.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
            operation_name="PutItem",
        )

        with pytest.raises(
            AWSServiceError,
            match=f"Error storing the {subject_type}: {subject_id}",
        ):
            self.dynamo_adapter.store_subject_permissions(
                subject_type, subject_id, permissions
            )
        self.service_table.assert_not_called()

    def test_store_protected_permission(self):
        domain = "TRAIN"
        mock_batch_writer = Mock()
        mock_batch_writer.__enter__ = Mock(return_value=mock_batch_writer)
        mock_batch_writer.__exit__ = Mock(return_value=None)
        self.permissions_table.batch_writer.return_value = mock_batch_writer

        permissions = [
            PermissionItem(
                id="READ_PROTECTED_TRAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain=domain,
                layer="LAYER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_TRAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain=domain,
                layer="LAYER",
            ),
        ]

        self.dynamo_adapter.store_protected_permissions(permissions, domain)

        mock_batch_writer.put_item.assert_has_calls(
            (
                call(
                    Item={
                        "PK": "PERMISSION",
                        "SK": "WRITE_PROTECTED_TRAIN",
                        "Id": "WRITE_PROTECTED_TRAIN",
                        "Type": "WRITE",
                        "Sensitivity": "PROTECTED",
                        "Domain": "TRAIN",
                        "Layer": "LAYER",
                    }
                ),
                call(
                    Item={
                        "PK": "PERMISSION",
                        "SK": "READ_PROTECTED_TRAIN",
                        "Id": "READ_PROTECTED_TRAIN",
                        "Type": "READ",
                        "Sensitivity": "PROTECTED",
                        "Domain": "TRAIN",
                        "Layer": "LAYER",
                    }
                ),
            ),
            any_order=True,
        )

        self.service_table.assert_not_called()

    def test_store_protected_permission_throws_error_when_database_call_fails(self):
        domain = "TRAIN"
        mock_batch_writer = Mock()
        mock_batch_writer.__enter__ = Mock(return_value=mock_batch_writer)
        mock_batch_writer.__exit__ = Mock(return_value=None)
        self.permissions_table.batch_writer.return_value = mock_batch_writer

        mock_batch_writer.put_item.side_effect = ClientError(
            error_response={"Error": {"Code": "ResourceNotFoundException"}},
            operation_name="PutItem",
        )

        permissions = [
            PermissionItem(
                id="READ_PROTECTED_TRAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain=domain,
                layer="LAYER",
            ),
            PermissionItem(
                id="WRITE_PROTECTED_TRAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain=domain,
                layer="LAYER",
            ),
        ]
        with pytest.raises(
            AWSServiceError,
            match=f"Error storing the protected domain permission for {domain}",
        ):
            self.dynamo_adapter.store_protected_permissions(permissions, domain)

        self.service_table.assert_not_called()

    def test_validate_permission_throws_error_when_query_fails(self):
        permissions = ["READ_ALL", "WRITE_ALL", "READ_PRIVATE", "USER_ADMIN"]

        self.permissions_table.query.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
            operation_name="Query",
        )

        with pytest.raises(
            AWSServiceError,
            match="Error fetching permissions from the database",
        ):
            self.dynamo_adapter.validate_permissions(permissions)

        self.service_table.assert_not_called()

    def test_validate_permission_throws_error_when_no_permissions_provided(self):
        permissions = []

        with pytest.raises(
            UserError,
            match="At least one permission must be provided",
        ):
            self.dynamo_adapter.validate_permissions(permissions)

        self.service_table.assert_not_called()

    def test_validates_permissions_exist_in_the_database(self):
        test_user_permissions = ["READ_PRIVATE", "WRITE_ALL"]
        self.permissions_table.query.return_value = {
            "Items": [
                {
                    "PK": "PERMISSION",
                    "SK": "WRITE_ALL",
                    "Id": "WRITE_ALL",
                    "Sensitivity": "ALL",
                    "Type": "WRITE",
                },
                {
                    "PK": "PERMISSION",
                    "SK": "READ_PRIVATE",
                    "Id": "READ_PRIVATE",
                    "Sensitivity": "PRIVATE",
                    "Type": "READ",
                },
            ],
            "Count": 2,
        }

        try:
            self.dynamo_adapter.validate_permissions(test_user_permissions)
        except UserError:
            pytest.fail("Unexpected UserError was thrown")

        self.permissions_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("PERMISSION"),
            FilterExpression=Or(
                *[(Attr("Id").eq(value)) for value in test_user_permissions]
            ),
        )

        self.service_table.assert_not_called()

    def test_raises_error_when_attempting_to_validate_at_least_one_invalid_permission(
        self,
    ):
        self.permissions_table.query.return_value = {
            "Items": [
                {
                    "PK": "PERMISSION",
                    "SK": "WRITE_ALL",
                    "Id": "WRITE_ALL",
                    "Sensitivity": "ALL",
                    "Type": "WRITE",
                }
            ],
            "Count": 1,
        }

        invalid_permissions = ["READ_SENSITIVE", "ACCESS_ALL", "ADMIN", "FAKE_ADMIN"]
        test_user_permissions = ["WRITE_ALL", *invalid_permissions]

        with pytest.raises(
            UserError,
            match="One or more of the provided permissions is invalid or duplicated",
        ):
            self.dynamo_adapter.validate_permissions(test_user_permissions)

        self.service_table.assert_not_called()

    def test_get_all_permissions(self):
        expected_response = [
            PermissionItem(
                id="USER_ADMIN",
                type="USER_ADMIN",
            ),
            PermissionItem(
                id="READ_ALL",
                sensitivity="ALL",
                type="READ",
            ),
            PermissionItem(
                id="WRITE_ALL",
                sensitivity="ALL",
                type="WRITE",
            ),
            PermissionItem(
                id="READ_PRIVATE",
                sensitivity="PRIVATE",
                type="READ",
            ),
        ]
        self.permissions_table.query.return_value = self.expected_db_query_response
        actual_response = self.dynamo_adapter.get_all_permissions()

        self.permissions_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("PERMISSION"),
        )
        assert actual_response == expected_response
        self.service_table.assert_not_called()

    def test_get_all_permissions_throws_aws_service_error(self):
        self.permissions_table.query.side_effect = ClientError(
            error_response={
                "Error": {"Code": "QueryFailedException"},
                "Message": "Failed to execute query: The error message",
            },
            operation_name="Query",
        )

        with pytest.raises(
            AWSServiceError,
            match="Error fetching permissions, please contact your system administrator",
        ):
            self.dynamo_adapter.get_all_permissions()

        self.service_table.assert_not_called()

    def test_get_permission_keys_for_subject(self):
        subject_id = "test-subject-id"
        self.permissions_table.query.return_value = {
            "Items": [
                {
                    "PK": "SUBJECT",
                    "SK": subject_id,
                    "Id": subject_id,
                    "Type": "CLIENT",
                    "Permissions": {
                        "DATA_ADMIN",
                        "READ_ALL",
                        "USER_ADMIN",
                        "WRITE_ALL",
                    },
                }
            ],
            "Count": 1,
        }

        expected_permissions = ["DATA_ADMIN", "READ_ALL", "USER_ADMIN", "WRITE_ALL"]

        response = self.dynamo_adapter.get_permission_keys_for_subject(subject_id)

        assert sorted(response) == sorted(expected_permissions)

        self.permissions_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("SUBJECT"),
            FilterExpression=Attr("Id").eq(subject_id),
        )

        self.service_table.assert_not_called()

    def test_get_permissions_for_non_existent_subject(self):
        subject_id = "fake-subject-id"
        self.permissions_table.query.return_value = {
            "Items": [],
            "Count": 0,
        }

        with pytest.raises(
            UserError,
            match="Subject fake-subject-id not found in database",
        ):
            self.dynamo_adapter.get_permission_keys_for_subject(subject_id)

        self.service_table.assert_not_called()

    def test_get_permissions_for_subject_with_no_permissions(self):
        subject_id = "test-subject-id"
        self.permissions_table.query.return_value = {
            "Items": [
                {
                    "PK": "SUBJECT",
                    "SK": subject_id,
                    "Id": subject_id,
                    "Type": "CLIENT",
                }
            ],
            "Count": 1,
        }

        response = self.dynamo_adapter.get_permission_keys_for_subject(subject_id)

        assert response == []
        self.service_table.assert_not_called()

    def test_get_permissions_for_subject_with_blank_permission(self):
        subject_id = "test-subject-id"
        self.permissions_table.query.return_value = {
            "Items": [
                {
                    "PK": "SUBJECT",
                    "SK": subject_id,
                    "Id": subject_id,
                    "Type": "CLIENT",
                    "Permissions": {""},
                }
            ],
            "Count": 1,
        }

        response = self.dynamo_adapter.get_permission_keys_for_subject(subject_id)

        assert response == []
        self.service_table.assert_not_called()

    def test_get_permissions_for_subject_throws_aws_service_error(self):
        subject_id = "test-subject-id"
        self.permissions_table.query.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
            operation_name="Query",
        )

        with pytest.raises(
            AWSServiceError,
            match="Error fetching permissions, please contact your system administrator",
        ):
            self.dynamo_adapter.get_permission_keys_for_subject(subject_id)

        self.service_table.assert_not_called()

    def test_get_all_protected_permissions(self):
        expected_db_query_response = {
            "Items": [
                {
                    "PK": "PERMISSION",
                    "SK": "WRITE_PROTECTED_DOMAIN",
                    "Id": "WRITE_PROTECTED_DOMAIN",
                    "Sensitivity": "PROTECTED",
                    "Type": "WRITE",
                    "Domain": "DOMAIN",
                    "Layer": "ALL",
                },
                {
                    "PK": "PERMISSION",
                    "SK": "READ_PROTECTED_DOMAIN",
                    "Id": "READ_PROTECTED_DOMAIN",
                    "Sensitivity": "PROTECTED",
                    "Type": "READ",
                    "Domain": "DOMAIN",
                    "Layer": "ALL",
                },
            ],
            "Count": 2,
        }

        expected_permission_item_list = [
            PermissionItem(
                id="WRITE_PROTECTED_DOMAIN",
                type="WRITE",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
            PermissionItem(
                id="READ_PROTECTED_DOMAIN",
                type="READ",
                sensitivity="PROTECTED",
                domain="DOMAIN",
                layer="ALL",
            ),
        ]

        self.permissions_table.query.return_value = expected_db_query_response
        response = self.dynamo_adapter.get_all_protected_permissions()
        assert len(response) == 2
        self.permissions_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("PERMISSION"),
            FilterExpression=Attr("Sensitivity").eq("PROTECTED"),
        )

        assert response == expected_permission_item_list
        self.service_table.assert_not_called()

    def test_get_all_protected_permissions_throws_aws_service_error(self):
        self.permissions_table.query.side_effect = ClientError(
            error_response={"Error": {"Code": "SomeOtherError"}},
            operation_name="UpdateItem",
        )
        with pytest.raises(
            AWSServiceError,
            match="Error fetching protected permissions, please contact your system administrator",
        ):
            self.dynamo_adapter.get_all_protected_permissions()

        self.service_table.assert_not_called()

    def test_update_subject_permissions(self):
        subject_permissions = SubjectPermissions(
            subject_id="asdf1234678sd", permissions=["READ_ALL"]
        )

        self.dynamo_adapter.update_subject_permissions(subject_permissions)

        self.permissions_table.update_item.assert_called_once_with(
            Key={"PK": "SUBJECT", "SK": subject_permissions.subject_id},
            ConditionExpression="SK = :sid",
            UpdateExpression="set #P = :r",
            ExpressionAttributeValues={
                ":r": set(subject_permissions.permissions),
                ":sid": subject_permissions.subject_id,
            },
            ExpressionAttributeNames={"#P": "Permissions"},
        )

        self.service_table.assert_not_called()

    def test_update_subject_permissions_on_service_error(self):
        subject_permissions = SubjectPermissions(
            subject_id="asdf1234678sd", permissions=["READ_ALL"]
        )
        self.permissions_table.update_item.side_effect = ClientError(
            error_response={"Error": {"Code": "SomeOtherError"}},
            operation_name="UpdateItem",
        )

        with pytest.raises(
            AWSServiceError,
            match=f"Error updating permissions for {subject_permissions.subject_id}",
        ):
            self.dynamo_adapter.update_subject_permissions(subject_permissions)

        self.service_table.assert_not_called()

    def test_user_error_when_user_does_not_exist_in_database(self):
        subject_permissions = SubjectPermissions(
            subject_id="asdf1234678sd", permissions=["READ_ALL"]
        )
        self.permissions_table.update_item.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
            operation_name="UpdateItem",
        )

        with pytest.raises(
            UserError, match="Subject with ID asdf1234678sd does not exist"
        ):
            self.dynamo_adapter.update_subject_permissions(subject_permissions)

        self.service_table.assert_not_called()

    def test_delete_subject(self):
        self.dynamo_adapter.delete_subject("some_id")
        self.permissions_table.delete_item.assert_called_once_with(
            Key={"PK": "SUBJECT", "SK": "some_id"}
        )
        self.service_table.assert_not_called()

    def test_delete_permission(self):
        self.dynamo_adapter.delete_permission("some_id")
        self.permissions_table.delete_item.assert_called_once_with(
            Key={"PK": "PERMISSION", "SK": "some_id"}
        )
        self.service_table.assert_not_called()


class TestDynamoDBAdapterServiceTable:
    def setup_method(self):
        self.dynamo_data_source = Mock()

        self.permissions_table = Mock()
        self.service_table = Mock()
        self.schema_table = Mock()

        self.dynamo_data_source.Table.side_effect = [
            self.permissions_table,
            self.service_table,
            self.schema_table,
        ]

        self.test_service_table_name = "TEST SERVICE TABLE"
        self.dynamo_adapter = DynamoDBAdapter(self.dynamo_data_source)

    @patch("api.domain.Jobs.UploadJob.time")
    def test_store_async_upload_job(self, mock_time):
        mock_time.time.return_value = 1000

        self.dynamo_adapter.store_upload_job(
            UploadJob(
                "subject-123",
                "abc-123",
                "filename.csv",
                "111-222-333",
                DatasetMetadata("layer", "domain1", "dataset2", 4),
            )
        )

        self.service_table.put_item.assert_called_once_with(
            Item={
                "PK": "JOB",
                "SK": "abc-123",
                "SK2": "subject-123",
                "Type": "UPLOAD",
                "Status": "IN PROGRESS",
                "Step": "VALIDATION",
                "Errors": None,
                "Filename": "filename.csv",
                "RawFileIdentifier": "111-222-333",
                "Layer": "layer",
                "Domain": "domain1",
                "Dataset": "dataset2",
                "Version": 4,
                "TTL": 605800,
            },
        )

        self.permissions_table.assert_not_called()

    @patch("api.domain.Jobs.Job.uuid")
    @patch("api.domain.Jobs.QueryJob.time")
    def test_store_async_query_job(self, mock_time, mock_uuid):
        mock_time.time.return_value = 2000
        mock_uuid.uuid4.return_value = "abc-123"
        version = 5

        self.dynamo_adapter.store_query_job(
            QueryJob(
                "subject-123", DatasetMetadata("layer", "domain1", "dataset1", version)
            )
        )

        self.service_table.put_item.assert_called_once_with(
            Item={
                "PK": "JOB",
                "SK": "abc-123",
                "SK2": "subject-123",
                "Type": "QUERY",
                "Status": "IN PROGRESS",
                "Step": "INITIALISATION",
                "Errors": None,
                "Layer": "layer",
                "Domain": "domain1",
                "Dataset": "dataset1",
                "Version": 5,
                "ResultsURL": None,
                "TTL": 88400,
            },
        )

        self.permissions_table.assert_not_called()

    @patch("api.adapter.dynamodb_adapter.time")
    def test_get_jobs(self, mock_time):
        mock_time.time.return_value = 19821
        self.service_table.query.return_value = {
            "Items": [
                {
                    "Step": "VALIDATION",
                    "SK": "113e0baf-5302-4b79-9902-ad620e8e531b",
                    "Status": "IN PROGRESS",
                    "Type": "UPLOAD",
                    "Filename": "file1.csv",
                    "Errors": None,
                    "PK": "JOB",
                },
                {
                    "Step": "VALIDATION",
                    "SK": "3f0baed7-8618-4517-97bd-d5a384053ca4",
                    "Status": "FAILED",
                    "Type": "UPLOAD",
                    "Filename": "file2.csv",
                    "Errors": {"error2", "error1"},
                    "PK": "JOB",
                },
            ],
            "Count": 2,
        }
        expected = [
            {
                "step": "VALIDATION",
                "job_id": "113e0baf-5302-4b79-9902-ad620e8e531b",
                "status": "IN PROGRESS",
                "filename": "file1.csv",
                "errors": None,
                "type": "UPLOAD",
            },
            {
                "step": "VALIDATION",
                "job_id": "3f0baed7-8618-4517-97bd-d5a384053ca4",
                "status": "FAILED",
                "filename": "file2.csv",
                "errors": {"error2", "error1"},
                "type": "UPLOAD",
            },
        ]

        result = self.dynamo_adapter.get_jobs("subject-123")

        assert result == expected
        self.permissions_table.assert_not_called()
        self.service_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("JOB") & Key("SK2").eq("subject-123"),
            FilterExpression=Attr("TTL").gt(19821),
            IndexName="JOB_SUBJECT_ID",
        )

    @patch("api.adapter.dynamodb_adapter.time")
    def test_get_jobs_for_no_jobs_returned(self, mock_time):
        mock_time.time.return_value = 19821
        self.service_table.query.return_value = {
            "Items": [],
            "Count": 0,
            "ScannedCount": 18,
        }
        expected = []

        result = self.dynamo_adapter.get_jobs("subject-123")

        assert result == expected
        self.permissions_table.assert_not_called()
        self.service_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("JOB") & Key("SK2").eq("subject-123"),
            FilterExpression=Attr("TTL").gt(19821),
            IndexName="JOB_SUBJECT_ID",
        )

    def test_get_job(self):
        self.service_table.query.return_value = {
            "Items": [
                {
                    "Step": "VALIDATION",
                    "SK": "113e0baf-5302-4b79-9902-ad620e8e531b",
                    "Status": "IN PROGRESS",
                    "Type": "UPLOAD",
                    "Filename": "file1.csv",
                    "Errors": None,
                    "PK": "JOB",
                }
            ],
            "Count": 1,
        }

        expected = {
            "step": "VALIDATION",
            "job_id": "113e0baf-5302-4b79-9902-ad620e8e531b",
            "status": "IN PROGRESS",
            "filename": "file1.csv",
            "errors": None,
            "type": "UPLOAD",
        }

        result = self.dynamo_adapter.get_job("113e0baf-5302-4b79-9902-ad620e8e531b")

        assert result == expected
        self.service_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("JOB")
            & Key("SK").eq("113e0baf-5302-4b79-9902-ad620e8e531b")
        )

        self.permissions_table.assert_not_called()

    def test_get_job_fails_if_no_job_found(self):
        self.service_table.query.return_value = {
            "Items": [],
            "Count": 0,
        }

        with pytest.raises(
            UserError,
            match="Could not find job with id 113e0baf-5302-4b79-9902-ad620e8e531b",
        ):
            self.dynamo_adapter.get_job("113e0baf-5302-4b79-9902-ad620e8e531b")

        self.permissions_table.assert_not_called()

    def test_get_job_fails_if_aws_fails(self):
        self.service_table.query.side_effect = ClientError(
            error_response={"Error": {"Code": "DatabaseConnectionError"}},
            operation_name="Query",
        )

        with pytest.raises(
            AWSServiceError, match="Error fetching job from the database"
        ):
            self.dynamo_adapter.get_job("113e0baf-5302-4b79-9902-ad620e8e531b")

        self.permissions_table.assert_not_called()

    def test_raises_error_when_get_jobs_fails(self):
        self.service_table.query.side_effect = ClientError(
            error_response={"Error": {"Code": "DatabaseConnectionError"}},
            operation_name="Scan",
        )

        with pytest.raises(
            AWSServiceError, match="Error fetching jobs from the database"
        ):
            self.dynamo_adapter.get_jobs("subject-123")

    def test_update_job(self):
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            DatasetMetadata("layer", "domain1", "dataset2", 4),
        )
        job.set_step(UploadStep.VALIDATION)
        job.set_status(JobStatus.FAILED)
        job.set_errors({"error1", "error2"})

        self.dynamo_adapter.update_job(job)

        self.service_table.update_item.assert_called_once_with(
            Key={
                "PK": "JOB",
                "SK": "abc-123",
            },
            ConditionExpression="SK = :jid",
            UpdateExpression="set #A = :a, #B = :b, #C = :c",
            ExpressionAttributeNames={
                "#A": "Step",
                "#B": "Status",
                "#C": "Errors",
            },
            ExpressionAttributeValues={
                ":a": "VALIDATION",
                ":b": "FAILED",
                ":c": {"error1", "error2"},
                ":jid": "abc-123",
            },
        )

    def test_update_job_without_errors(self):
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            DatasetMetadata("layer", "domain1", "dataset2", 4),
        )
        job.set_step(UploadStep.VALIDATION)
        job.set_status(JobStatus.FAILED)

        self.dynamo_adapter.update_job(job)

        self.service_table.update_item.assert_called_once_with(
            Key={
                "PK": "JOB",
                "SK": "abc-123",
            },
            ConditionExpression="SK = :jid",
            UpdateExpression="set #A = :a, #B = :b, #C = :c",
            ExpressionAttributeNames={
                "#A": "Step",
                "#B": "Status",
                "#C": "Errors",
            },
            ExpressionAttributeValues={
                ":a": "VALIDATION",
                ":b": "FAILED",
                ":c": None,
                ":jid": "abc-123",
            },
        )

    def test_update_job_raises_error_when_fails(self):
        job = UploadJob(
            "subject-123",
            "abc-123",
            "file1.csv",
            "111-222-333",
            DatasetMetadata("layer", "domain1", "dataset2", 4),
        )

        self.service_table.update_item.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
            operation_name="UpdateItem",
        )

        with pytest.raises(
            AWSServiceError, match="There was an error updating job status"
        ):
            self.dynamo_adapter.update_job(job)

    @patch("api.domain.Jobs.Job.uuid")
    def test_update_query_job(self, mock_uuid):
        mock_uuid.uuid4.return_value = "abc-123"

        job = QueryJob(
            "subject-123", DatasetMetadata("layer", "domain1", "dataset2", 4)
        )
        job.set_results_url("https://some-url.com")
        job.set_status(JobStatus.SUCCESS)
        job.set_step(QueryStep.NONE)

        self.dynamo_adapter.update_query_job(job)

        self.service_table.update_item.assert_called_once_with(
            Key={
                "PK": "JOB",
                "SK": job.job_id,
            },
            ConditionExpression="SK = :jid",
            UpdateExpression="set #A = :a, #B = :b, #C = :c, #D = :d",
            ExpressionAttributeNames={
                "#A": "Step",
                "#B": "Status",
                "#C": "Errors",
                "#D": "ResultsURL",
            },
            ExpressionAttributeValues={
                ":a": "-",
                ":b": "SUCCESS",
                ":c": None,
                ":d": "https://some-url.com",
                ":jid": "abc-123",
            },
        )

    @patch("api.domain.Jobs.Job.uuid")
    def test_update_query_job_raises_error_when_fails(self, mock_uuid):
        mock_uuid.uuid4.return_value = "abc-123"

        job = QueryJob(
            "subject-123", DatasetMetadata("layer", "domain1", "dataset2", 4)
        )

        self.service_table.update_item.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
            operation_name="UpdateItem",
        )

        with pytest.raises(
            AWSServiceError, match="There was an error updating job status"
        ):
            self.dynamo_adapter.update_query_job(job)


class TestDynamoDBAdapterSchemaTable:
    def setup_method(self):
        self.dynamo_data_source = Mock()

        self.permissions_table = Mock()
        self.service_table = Mock()
        self.schema_table = Mock()

        self.dynamo_data_source.Table.side_effect = [
            self.permissions_table,
            self.service_table,
            self.schema_table,
        ]

        self.test_service_table_name = "TEST SCHEMA TABLE"
        self.dynamo_adapter = DynamoDBAdapter(self.dynamo_data_source)

        self.schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                version=2,
                sensitivity="PUBLIC",
                description="This is a test schema",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_only_tags=["key"],
                key_value_tags={"key": "value"},
            ),
            columns=[
                Column(
                    name="colname1",
                    partition_index=0,
                    data_type="integer",
                    allow_null=False,
                ),
                Column(
                    name="colname2",
                    partition_index=None,
                    data_type="string",
                    allow_null=True,
                ),
            ],
        )

    def test_store_schema(self):
        self.dynamo_adapter.store_schema(self.schema)

        self.schema_table.put_item.assert_called_once_with(
            Item={
                "PK": "raw/some/other",
                "SK": 2,
                "Layer": "raw",
                "Domain": "some",
                "Dataset": "other",
                "Version": 2,
                "Sensitivity": "PUBLIC",
                "Description": "This is a test schema",
                "UpdateBehaviour": "APPEND",
                "KeyValueTags": {"key": "value"},
                "KeyOnlyTags": ["key"],
                "Owners": [{"name": "owner", "email": "owner@email.com"}],
                "IsLatestVersion": True,
                "Columns": [
                    {
                        "name": "colname1",
                        "partition_index": 0,
                        "data_type": "integer",
                        "allow_null": False,
                        "format": None,
                    },
                    {
                        "name": "colname2",
                        "partition_index": None,
                        "data_type": "string",
                        "allow_null": True,
                        "format": None,
                    },
                ],
            }
        )

    def test_store_schema_client_error(self):
        self.schema_table.put_item.side_effect = ClientError(
            error_response={"Error": {"Code": "TableDoesNotExist"}},
            operation_name="PutItems",
        )

        with pytest.raises(
            AWSServiceError,
            match=r"Error storing schema for layer \[raw\], domain \[some\], dataset \[other\] and version \[2\]",
        ):
            self.dynamo_adapter.store_schema(self.schema)

    @pytest.mark.parametrize("result, expected", [(["schema"], "schema"), ([], None)])
    def test_get_schema(self, result, expected):
        self.schema_table.query.return_value = {"Items": result}

        res = self.dynamo_adapter.get_schema(
            DatasetMetadata("raw", "domain", "dataset", 1)
        )

        self.schema_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("raw/domain/dataset") & Key("SK").eq(1)
        )
        assert res == expected

    def test_get_schema_client_error(self):
        self.schema_table.query.side_effect = ClientError(
            error_response={"Error": {"Code": "KeyDoesNotExist"}},
            operation_name="Query",
        )

        with pytest.raises(
            AWSServiceError,
            match="Error fetching schema from the database",
        ):
            self.dynamo_adapter.get_schema(
                DatasetMetadata("raw", "domain", "dataset", 1)
            )

    def test_get_latest_schemas_with_no_args(self):
        self.schema_table.scan.return_value = {"Items": ["schema", "schema_2"]}
        res = self.dynamo_adapter.get_latest_schemas(DatasetFilters())

        self.schema_table.scan.assert_called_once_with(
            FilterExpression=Attr("IsLatestVersion").eq(True)
        )
        assert res == ["schema", "schema_2"]

    @pytest.mark.parametrize(
        "result, expected",
        [({"Items": ["schema", "schema_2"]}, ["schema", "schema_2"]), ({}, None)],
    )
    def test_get_latest_schemas_with_args(self, result, expected):
        self.schema_table.scan.return_value = result

        mock_query = Attr("KeyOnlyTags").eq("2") & Attr("foo").is_in(["bar"])

        dataset_filters = Mock()
        dataset_filters.format_resource_query = Mock(return_value=mock_query)

        res = self.dynamo_adapter.get_latest_schemas(dataset_filters)

        self.schema_table.scan.assert_called_once_with(
            FilterExpression=Attr("IsLatestVersion").eq(True) & mock_query
        )
        dataset_filters.format_resource_query.assert_called_once()
        assert res == expected

    def test_get_latest_schemas_client_error(self):
        self.schema_table.scan.side_effect = ClientError(
            error_response={"Error": {"Code": "KeyDoesNotExist"}},
            operation_name="Query",
        )

        with pytest.raises(
            AWSServiceError,
            match="Error fetching the latest schemas from the database",
        ):
            self.dynamo_adapter.get_latest_schemas(DatasetFilters())

    @pytest.mark.parametrize("result, expected", [(["schema1"], "schema1"), ([], None)])
    def test_get_latest_schema(self, result, expected):
        self.schema_table.query.return_value = {"Items": result}

        res = self.dynamo_adapter.get_latest_schema(
            DatasetMetadata("raw", "domain", "dataset", 1)
        )

        self.schema_table.query.assert_called_once_with(
            KeyConditionExpression=Key("PK").eq("raw/domain/dataset"),
            FilterExpression=Attr("IsLatestVersion").eq(True),
        )

        assert res == expected

    def test_get_latest_schema_client_error(self):
        self.schema_table.query.side_effect = ClientError(
            error_response={"Error": {"Code": "KeyDoesNotExist"}},
            operation_name="Query",
        )

        with pytest.raises(
            AWSServiceError,
            match="Error fetching latest schema from the database",
        ):
            self.dynamo_adapter.get_latest_schema(
                DatasetMetadata("raw", "domain", "dataset", 1)
            )

    def test_deprecate_schema(self):
        self.dynamo_adapter.deprecate_schema(
            DatasetMetadata("raw", "domain", "dataset", 1)
        )

        self.schema_table.update_item.assert_called_once_with(
            Key={
                "PK": "raw/domain/dataset",
                "SK": 1,
            },
            UpdateExpression="set #A = :a",
            ExpressionAttributeNames={
                "#A": "IsLatestVersion",
            },
            ExpressionAttributeValues={
                ":a": False,
            },
        )

    def test_deprecate_schema_client_error(self):
        self.schema_table.update_item.side_effect = ClientError(
            error_response={"Error": {"Code": "ConditionalCheckFailedException"}},
            operation_name="UpdateItem",
        )

        with pytest.raises(
            AWSServiceError,
            match="There was an deprecating the schema",
        ):
            self.dynamo_adapter.deprecate_schema(
                DatasetMetadata("raw", "domain", "dataset", 1)
            )

    def test_delete_schema(self):
        self.dynamo_adapter.delete_schema(
            DatasetMetadata("raw", "domain", "dataset", 1)
        )

        self.schema_table.delete_item.assert_called_once_with(
            Key={
                "PK": "raw/domain/dataset",
                "SK": 1,
            },
        )

    def test_delete_schema_client_error(self):
        self.schema_table.delete_item.side_effect = ClientError(
            error_response={"Error": {"Code": "FailedToDelete"}},
            operation_name="DeleteItem",
        )

        with pytest.raises(
            AWSServiceError,
            match="Error deleting the schema ",
        ):
            self.dynamo_adapter.delete_schema(
                DatasetMetadata("raw", "domain", "dataset", 1)
            )
