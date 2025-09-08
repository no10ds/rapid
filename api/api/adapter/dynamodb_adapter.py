import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from typing import Any, Callable, Dict, List, Optional, Type

import boto3
from boto3.dynamodb.conditions import Attr, Key, Or
from botocore.exceptions import ClientError

from api.common.config.auth import (
    PermissionsTableItem,
    Sensitivity,
    ServiceTableItem,
    SubjectType,
)
from api.common.config.aws import (
    AWS_REGION,
    DYNAMO_PERMISSIONS_TABLE_NAME,
    SCHEMA_TABLE_NAME,
    SERVICE_TABLE_NAME,
)
from api.common.custom_exceptions import AWSServiceError, UserError
from api.common.logger import AppLogger
from api.domain.dataset_filters import DatasetFilters
from api.domain.dataset_metadata import DatasetMetadata
from api.domain.Jobs.Job import Job
from api.domain.Jobs.QueryJob import QueryJob
from api.domain.Jobs.UploadJob import UploadJob
from api.domain.permission_item import PermissionItem
from api.domain.schema import Schema, COLUMNS
from api.domain.schema_metadata import IS_LATEST_VERSION
from api.domain.subject_permissions import SubjectPermissions


class DatabaseAdapter(ABC):
    @abstractmethod
    def store_subject_permissions(
        self, subject_type: SubjectType, subject_id: str, permissions: List[str]
    ) -> None:
        pass

    @abstractmethod
    def store_protected_permissions(
        self, permissions: List[PermissionItem], domain: str
    ) -> None:
        pass

    @abstractmethod
    def validate_permissions(self, subject_permissions: List[str]):
        pass

    @abstractmethod
    def get_all_permissions(self) -> List[dict]:
        pass

    @abstractmethod
    def get_permission_keys_for_subject(self, subject_id: str) -> List[str]:
        pass

    @abstractmethod
    def update_subject_permissions(
        self, subject_permissions: SubjectPermissions
    ) -> None:
        pass

    @abstractmethod
    def delete_subject(self, subject_id: str) -> None:
        pass

    @abstractmethod
    def store_upload_job(self, upload_job: UploadJob) -> None:
        pass

    @abstractmethod
    def get_jobs(self) -> List[Job]:
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Dict:
        pass

    @abstractmethod
    def update_job(self, job: Job) -> None:
        pass

    @abstractmethod
    def store_schema(self, schema: Schema) -> None:
        pass

    @abstractmethod
    def get_latest_schemas(self, dataset: Type[DatasetMetadata]) -> List[dict]:
        pass

    @abstractmethod
    def get_schema(self, dataset: Type[DatasetMetadata]) -> Dict:
        pass

    @abstractmethod
    def delete_schema(self, metadata: Type[DatasetMetadata]) -> None:
        pass

    @abstractmethod
    def deprecate_schema(self, metadata: Type[DatasetMetadata]) -> None:
        pass


@dataclass
class ExpressionAttribute:
    name: str
    _alias: str

    @property
    def alias(self) -> str:
        return f"#{self._alias}"

    @alias.setter
    def alias(self, value: str) -> None:
        self._alias = value


class DynamoDBAdapter(DatabaseAdapter):
    def __init__(self, data_source=boto3.resource("dynamodb", region_name=AWS_REGION)):
        self.permissions_table = data_source.Table(DYNAMO_PERMISSIONS_TABLE_NAME)
        self.service_table = data_source.Table(SERVICE_TABLE_NAME)
        self.schema_table = data_source.Table(SCHEMA_TABLE_NAME)

    def store_subject_permissions(
        self, subject_type: SubjectType, subject_id: str, permissions: List[str]
    ) -> None:
        subject_type = subject_type
        try:
            AppLogger.info(f"Storing permissions for {subject_type}: {subject_id}")
            self.permissions_table.put_item(
                Item={
                    "PK": PermissionsTableItem.SUBJECT,
                    "SK": subject_id,
                    "Id": subject_id,
                    "Type": subject_type,
                    "Permissions": set(permissions),
                },
            )
        except ClientError as error:
            self._handle_client_error(
                f"Error storing the {subject_type}: {subject_id}", error
            )

    def store_protected_permissions(
        self, permissions: List[PermissionItem], domain: str
    ) -> None:
        try:
            AppLogger.info(f"Storing protected permissions for {domain}")
            with self.permissions_table.batch_writer() as batch:
                for permission in permissions:
                    batch.put_item(
                        Item={
                            "PK": PermissionsTableItem.PERMISSION,
                            "SK": permission.id,
                            "Id": permission.id,
                            "Type": permission.type,
                            "Sensitivity": permission.sensitivity,
                            "Domain": permission.domain,
                            "Layer": permission.layer,
                        }
                    )
        except ClientError as error:
            self._handle_client_error(
                f"Error storing the protected domain permission for {domain}", error
            )

    def store_schema(self, schema: Schema) -> None:
        try:
            AppLogger.info(
                f"Storing schema for {schema.metadata.string_representation()}"
            )

            metadata_dict = schema.metadata.dict()

            if 'layer' in metadata_dict:
                metadata_dict['layer'] = metadata_dict['layer'].value
            columns_dict = {}
            for name, col in schema.columns.items():
                col_dict = dict(col)
                columns_dict[name] = col_dict

            self.schema_table.put_item(
                Item={
                    "PK": schema.metadata.dataset_identifier(with_version=False),
                    "SK": schema.metadata.get_version(),
                    **metadata_dict,
                    COLUMNS: columns_dict,
                }
            )
        except ClientError as error:
            self._handle_client_error(
                f"Error storing schema for {schema.metadata.string_representation()}",
                error,
            )

    def validate_permissions(self, subject_permissions: List[str]) -> None:
        if not subject_permissions:
            raise UserError("At least one permission must be provided")
        permissions_response = self._find_permissions(subject_permissions)
        if not len(permissions_response) == len(subject_permissions):
            AppLogger.info(f"Invalid permission in {subject_permissions}")
            raise UserError(
                "One or more of the provided permissions is invalid or duplicated"
            )

    def get_all_permissions(self) -> List[PermissionItem]:
        try:
            permissions = self.collect_all_items(
                self.permissions_table.query,
                KeyConditionExpression=Key("PK").eq(PermissionsTableItem.PERMISSION),
            )
            return [
                PermissionItem(
                    id=permission["SK"],
                    type=permission["Type"],
                    layer=permission.get("Layer"),
                    sensitivity=permission.get("Sensitivity"),
                    domain=permission.get("Domain"),
                )
                for permission in permissions
            ]

        except KeyError as error:
            AppLogger.info(
                f"Error retrieving the permissions, one has an empty key: {error}"
            )
            raise AWSServiceError(
                "Error fetching permissions, one of them is incorrectly formatted, please contact your system administrator"
            )

        except ClientError as error:
            AppLogger.info(f"Error retrieving all permissions: {error}")
            raise AWSServiceError(
                "Error fetching permissions, please contact your system administrator"
            )

    def get_all_protected_permissions(self) -> List[PermissionItem]:
        try:
            items = self.collect_all_items(
                self.permissions_table.query,
                KeyConditionExpression=Key("PK").eq(PermissionsTableItem.PERMISSION),
                FilterExpression=Attr("Sensitivity").eq(Sensitivity.PROTECTED),
            )
            return [self._generate_protected_permission_item(item) for item in items]
        except ClientError as error:
            AppLogger.info(f"Error retrieving all protected permissions: {error}")
            raise AWSServiceError(
                "Error fetching protected permissions, please contact your system administrator"
            )

    def get_permission_keys_for_subject(self, subject_id: str) -> List[str]:
        AppLogger.info(f"Getting permissions for: {subject_id}")
        try:
            return [
                permission
                for permission in self.permissions_table.query(
                    KeyConditionExpression=Key("PK").eq(PermissionsTableItem.SUBJECT),
                    FilterExpression=Attr("Id").eq(subject_id),
                )["Items"][0]["Permissions"]
                if permission is not None and permission != ""
            ]
        except KeyError:
            return []
        except ClientError:
            AppLogger.info(f"Error retrieving permissions for subject {subject_id}")
            raise AWSServiceError(
                "Error fetching permissions, please contact your system administrator"
            )
        except IndexError:
            AppLogger.info(f"Subject {subject_id} not found")
            raise UserError(f"Subject {subject_id} not found in database")

    def update_subject_permissions(
        self, subject_permissions: SubjectPermissions
    ) -> SubjectPermissions:
        try:
            unique_permissions = set(subject_permissions.permissions)
            self.permissions_table.update_item(
                Key={
                    "PK": PermissionsTableItem.SUBJECT,
                    "SK": subject_permissions.subject_id,
                },
                ConditionExpression="SK = :sid",
                UpdateExpression="set #P = :r",
                ExpressionAttributeNames={"#P": "Permissions"},
                ExpressionAttributeValues={
                    ":r": unique_permissions,
                    ":sid": subject_permissions.subject_id,
                },
            )
            return SubjectPermissions(
                subject_id=subject_permissions.subject_id,
                permissions=list(unique_permissions),
            )
        except ClientError as error:
            if self._failed_conditions(error):
                message = (
                    f"Subject with ID {subject_permissions.subject_id} does not exist"
                )
                AppLogger.error(message)
                raise UserError(message)
            self._handle_client_error(
                f"Error updating permissions for {subject_permissions.subject_id}",
                error,
            )

    def delete_subject(self, subject_id: str) -> None:
        self.permissions_table.delete_item(Key={"PK": "SUBJECT", "SK": subject_id})

    def delete_permission(self, permission_id: str) -> None:
        self.permissions_table.delete_item(
            Key={"PK": "PERMISSION", "SK": permission_id}
        )

    def delete_schema(self, metadata: Type[DatasetMetadata]) -> None:
        try:
            self.schema_table.delete_item(
                Key={
                    "PK": metadata.dataset_identifier(with_version=False),
                    "SK": metadata.get_version(),
                }
            )
        except ClientError as error:
            self._handle_client_error(
                f"Error deleting the schema {metadata.string_representation()}", error
            )

    def store_upload_job(self, upload_job: UploadJob) -> None:
        item_config = {
            "PK": "JOB",
            "SK": upload_job.job_id,
            "SK2": upload_job.subject_id,
            "Type": upload_job.job_type,
            "Status": upload_job.status,
            "Step": upload_job.step,
            "Errors": upload_job.errors if upload_job.errors else None,
            "Filename": upload_job.filename,
            "RawFileIdentifier": upload_job.raw_file_identifier,
            "Layer": upload_job.layer,
            "Domain": upload_job.domain,
            "Dataset": upload_job.dataset,
            "Version": upload_job.version,
            "TTL": upload_job.expiry_time,
        }
        self._store_job(item_config)

    def store_query_job(self, query_job: QueryJob) -> None:
        item_config = {
            "PK": "JOB",
            "SK": query_job.job_id,
            "SK2": query_job.subject_id,
            "Type": query_job.job_type,
            "Status": query_job.status,
            "Step": query_job.step,
            "Errors": query_job.errors if query_job.errors else None,
            "Layer": query_job.layer,
            "Domain": query_job.domain,
            "Dataset": query_job.dataset,
            "Version": query_job.version,
            "ResultsURL": query_job.results_url,
            "TTL": query_job.expiry_time,
        }
        self._store_job(item_config)

    def get_jobs(self, subject_id: str) -> List[Dict]:
        try:
            return [
                self._map_job(job)
                for job in self.collect_all_items(
                    self.service_table.query,
                    KeyConditionExpression=Key("PK").eq(ServiceTableItem.JOB)
                    & Key("SK2").eq(subject_id),
                    FilterExpression=Attr("TTL").gt(int(time.time())),
                    IndexName="JOB_SUBJECT_ID",
                )
            ]
        except ClientError as error:
            self._handle_client_error("Error fetching jobs from the database", error)

    def get_job(self, job_id: str) -> Dict:
        try:
            return self._map_job(
                self.service_table.query(
                    KeyConditionExpression=Key("PK").eq("JOB") & Key("SK").eq(job_id)
                )["Items"][0]
            )
        except IndexError:
            raise UserError(f"Could not find job with id {job_id}")
        except ClientError as error:
            self._handle_client_error("Error fetching job from the database", error)

    def get_schema(self, dataset: Type[DatasetMetadata]) -> Optional[dict]:
        try:
            return self.schema_table.query(
                KeyConditionExpression=Key("PK").eq(
                    dataset.dataset_identifier(with_version=False)
                )
                & Key("SK").eq(dataset.get_version())
            )["Items"][0]
        except IndexError:
            return None
        except ClientError as error:
            self._handle_client_error("Error fetching schema from the database", error)

    def get_latest_schemas(
        self,
        query: DatasetFilters = DatasetFilters(),
        attributes: List[ExpressionAttribute] = None,
    ) -> List[dict]:
        try:
            query_arguments = query.format_resource_query()
            if query_arguments:
                filter_expression = Attr(IS_LATEST_VERSION).eq(True) & query_arguments
            else:
                filter_expression = Attr(IS_LATEST_VERSION).eq(True)

            additional_kwargs = {}
            if attributes:
                additional_kwargs["ProjectionExpression"] = ", ".join(
                    [attr.alias for attr in attributes]
                )
                additional_kwargs["ExpressionAttributeNames"] = {
                    attr.alias: attr.name for attr in attributes
                }

            return self.collect_all_items(
                self.schema_table.scan,
                FilterExpression=filter_expression,
                **additional_kwargs,
            )
        except KeyError:
            return []
        except ClientError as error:
            self._handle_client_error(
                "Error fetching the latest schemas from the database", error
            )

    def get_latest_schema(self, dataset: Type[DatasetMetadata]) -> Optional[dict]:
        try:
            return self.schema_table.query(
                KeyConditionExpression=Key("PK").eq(
                    dataset.dataset_identifier(with_version=False)
                ),
                # Sort by SK in descending order to get the latest version
                ScanIndexForward=False,
            )["Items"][0]
        except IndexError:
            return None
        except ClientError as error:
            self._handle_client_error(
                "Error fetching latest schema from the database", error
            )

    def deprecate_schema(self, dataset: Type[DatasetMetadata]) -> None:
        try:
            self.schema_table.update_item(
                Key={
                    "PK": dataset.dataset_identifier(with_version=False),
                    "SK": dataset.get_version(),
                },
                UpdateExpression="set #A = :a",
                ExpressionAttributeNames={
                    "#A": IS_LATEST_VERSION,
                },
                ExpressionAttributeValues={
                    ":a": False,
                },
            )
        except ClientError as error:
            self._handle_client_error("There was an deprecating the schema", error)

    def update_job(self, job: Job) -> None:
        try:
            self.service_table.update_item(
                Key={
                    "PK": "JOB",
                    "SK": job.job_id,
                },
                ConditionExpression="SK = :jid",
                UpdateExpression="set #A = :a, #B = :b, #C = :c",
                ExpressionAttributeNames={
                    "#A": "Step",
                    "#B": "Status",
                    "#C": "Errors",
                },
                ExpressionAttributeValues={
                    ":a": job.step,
                    ":b": job.status,
                    ":c": job.errors if job.errors else None,
                    ":jid": job.job_id,
                },
            )
        except ClientError as error:
            self._handle_client_error("There was an error updating job status", error)

    def update_query_job(self, job: QueryJob) -> None:
        try:
            self.service_table.update_item(
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
                    ":a": job.step,
                    ":b": job.status,
                    ":c": job.errors if job.errors else None,
                    ":d": job.results_url if job.results_url else None,
                    ":jid": job.job_id,
                },
            )
        except ClientError as error:
            self._handle_client_error("There was an error updating job status", error)

    def _map_job(self, job: Dict) -> Dict:
        name_map = {
            "SK": "job_id",
            "RawFileIdentifier": "raw_file_identifier",
            "ResultsURL": "result_url",
        }
        return {
            name_map.get(key, key.lower()): value
            for key, value in job.items()
            if key != "PK"
        }

    def _store_job(self, item: Dict):
        self.service_table.put_item(Item=item)

    def _find_permissions(self, permissions: List[str]) -> Dict[str, Any]:
        try:
            return self.collect_all_items(
                self.permissions_table.query,
                KeyConditionExpression=Key("PK").eq(PermissionsTableItem.PERMISSION),
                FilterExpression=reduce(
                    Or, ([Attr("Id").eq(value) for value in permissions])
                ),
            )
        except ClientError as error:
            self._handle_client_error(
                "Error fetching permissions from the database", error
            )

    def _failed_conditions(self, error):
        return (
            error.response.get("Error").get("Code") == "ConditionalCheckFailedException"
        )

    @staticmethod
    def _handle_client_error(message: str, error: Any) -> None:
        AppLogger.error(f"{message}: {error}")
        raise AWSServiceError(message)

    def _generate_protected_permission_item(self, item: dict) -> PermissionItem:
        return PermissionItem(
            id=item["Id"],
            sensitivity=item["Sensitivity"],
            type=item["Type"],
            domain=item["Domain"],
            layer=item["Layer"],
        )

    def collect_all_items(self, method: Callable, **kwargs) -> List[Dict]:
        response = method(**kwargs)
        items = response["Items"]
        while response.get("LastEvaluatedKey"):
            response = method(ExclusiveStartKey=response["LastEvaluatedKey"], **kwargs)
            items.extend(response["Items"])
        return items
