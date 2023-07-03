import time
from abc import ABC, abstractmethod
from functools import reduce
from typing import List, Dict, Any

import boto3
from boto3.dynamodb.conditions import Key, Attr, Or
from botocore.exceptions import ClientError

from api.common.config.auth import (
    PermissionsTableItem,
    SubjectType,
    SensitivityLevel,
    ServiceTableItem,
)
from api.common.config.aws import (
    AWS_REGION,
    DYNAMO_PERMISSIONS_TABLE_NAME,
    SERVICE_TABLE_NAME,
)
from api.common.custom_exceptions import UserError, AWSServiceError
from api.common.logger import AppLogger
from api.domain.Jobs.Job import Job
from api.domain.Jobs.QueryJob import QueryJob
from api.domain.Jobs.UploadJob import UploadJob
from api.domain.permission_item import PermissionItem
from api.domain.subject_permissions import SubjectPermissions


class DatabaseAdapter(ABC):
    @abstractmethod
    def store_subject_permissions(
        self, subject_type: SubjectType, subject_id: str, permissions: List[str]
    ) -> None:
        pass

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
    def get_permissions_for_subject(self, subject_id: str) -> List[str]:
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


class DynamoDBAdapter(DatabaseAdapter):
    def __init__(self, data_source=boto3.resource("dynamodb", region_name=AWS_REGION)):
        self.permissions_table = data_source.Table(DYNAMO_PERMISSIONS_TABLE_NAME)
        self.service_table = data_source.Table(SERVICE_TABLE_NAME)

    def store_subject_permissions(
        self, subject_type: SubjectType, subject_id: str, permissions: List[str]
    ) -> None:
        subject_type = subject_type.value
        try:
            AppLogger.info(f"Storing permissions for {subject_type}: {subject_id}")
            self.permissions_table.put_item(
                Item={
                    "PK": PermissionsTableItem.SUBJECT.value,
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
                            "PK": PermissionsTableItem.PERMISSION.value,
                            "SK": permission.id,
                            "Id": permission.id,
                            "Type": permission.type,
                            "Sensitivity": permission.sensitivity,
                            "Domain": permission.domain,
                        }
                    )
        except ClientError as error:
            self._handle_client_error(
                f"Error storing the protected domain permission for {domain}", error
            )

    def validate_permissions(self, subject_permissions: List[str]) -> None:
        if not subject_permissions:
            raise UserError("At least one permission must be provided")
        permissions_response = self._find_permissions(subject_permissions)
        if not permissions_response["Count"] == len(subject_permissions):
            AppLogger.info(f"Invalid permission in {subject_permissions}")
            raise UserError(
                "One or more of the provided permissions is invalid or duplicated"
            )

    def get_all_permissions(self) -> List[str]:
        try:
            permissions = self.permissions_table.query(
                KeyConditionExpression=Key("PK").eq(
                    PermissionsTableItem.PERMISSION.value
                ),
            )
            return [permission["SK"] for permission in permissions["Items"]]

        except ClientError as error:
            AppLogger.info(f"Error retrieving all permissions: {error}")
            raise AWSServiceError(
                "Error fetching permissions, please contact your system administrator"
            )

    def get_all_protected_permissions(self) -> List[PermissionItem]:
        try:
            list_of_items = self.permissions_table.query(
                KeyConditionExpression=Key("PK").eq(
                    PermissionsTableItem.PERMISSION.value
                ),
                FilterExpression=Attr("Sensitivity").eq(
                    SensitivityLevel.PROTECTED.value
                ),
            )["Items"]
            return [
                self._generate_protected_permission_item(item) for item in list_of_items
            ]
        except ClientError as error:
            AppLogger.info(f"Error retrieving all protected permissions: {error}")
            raise AWSServiceError(
                "Error fetching protected permissions, please contact your system administrator"
            )

    def get_permissions_for_subject(self, subject_id: str) -> List[str]:
        AppLogger.info(f"Getting permissions for: {subject_id}")
        try:
            return [
                permission
                for permission in self.permissions_table.query(
                    KeyConditionExpression=Key("PK").eq(
                        PermissionsTableItem.SUBJECT.value
                    ),
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
                    "PK": PermissionsTableItem.SUBJECT.value,
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

    def store_upload_job(self, upload_job: UploadJob) -> None:
        item_config = {
            "PK": "JOB",
            "SK": upload_job.job_id,
            "SK2": upload_job.subject_id,
            "Type": upload_job.job_type.value,
            "Status": upload_job.status.value,
            "Step": upload_job.step.value,
            "Errors": upload_job.errors if upload_job.errors else None,
            "Filename": upload_job.filename,
            "RawFileIdentifier": upload_job.raw_file_identifier,
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
            "Type": query_job.job_type.value,
            "Status": query_job.status.value,
            "Step": query_job.step.value,
            "Errors": query_job.errors if query_job.errors else None,
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
                for job in self.service_table.query(
                    KeyConditionExpression=Key("PK").eq(ServiceTableItem.JOB.value)
                    & Key("SK2").eq(subject_id),
                    FilterExpression=Attr("TTL").gt(int(time.time())),
                    IndexName="JOB_SUBJECT_ID",
                )["Items"]
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
                    ":a": job.step.value,
                    ":b": job.status.value,
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
                    ":a": job.step.value,
                    ":b": job.status.value,
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
            return self.permissions_table.query(
                KeyConditionExpression=Key("PK").eq(
                    PermissionsTableItem.PERMISSION.value
                ),
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
        )
