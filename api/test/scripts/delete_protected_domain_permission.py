import os
import re
import sys
from functools import reduce
from typing import Dict, List, Optional, Any

import boto3
from boto3.dynamodb.conditions import Key, Attr, Or
from botocore.exceptions import ClientError

AWS_REGION = os.environ["AWS_REGION"]
RESOURCE_PREFIX = os.environ["RESOURCE_PREFIX"]
DATA_BUCKET = os.environ["DATA_BUCKET"]
DYNAMO_PERMISSIONS_TABLE_NAME = f"{RESOURCE_PREFIX}_users_permissions"
PROTECTED_PATH = "data/schemas/PROTECTED/"
PROTECTED_DOMAIN_PERMISSIONS_PARAMETER_NAME = (
    f"{RESOURCE_PREFIX}_protected_domain_permissions"
)

db_table = boto3.resource("dynamodb", region_name=AWS_REGION).Table(
    DYNAMO_PERMISSIONS_TABLE_NAME
)
s3_client = boto3.client("s3")
glue_client = boto3.client("glue", region_name=AWS_REGION)


def delete_protected_domain(domain: str):
    delete_dataset_files(domain)
    delete_protected_domain_permission_from_db(domain)


def delete_dataset_files(domain: str):
    print("Deleting files...")
    # Check protected domain exists
    metadatas = find_protected_datasets(domain)
    if not metadatas:
        print(f"No protected domain '{domain}' found")
    else:
        # Delete all files and raw files for each domain/dataset
        for metadata in metadatas:
            try:
                # Delete crawler
                glue_client.delete_crawler(
                    Name=f'{RESOURCE_PREFIX}_crawler/{metadata["domain"]}/{metadata["dataset"]}'
                )

                # List of related files
                data_files = get_file_paths(
                    domain=metadata["domain"], dataset=metadata["dataset"], path="data"
                )
                raw_data_files = get_file_paths(
                    domain=metadata["domain"],
                    dataset=metadata["dataset"],
                    path="raw_data",
                )

                # Delete raw files
                if raw_data_files:
                    delete_s3_files(raw_data_files)

                # Delete files and related tables
                if data_files:
                    delete_s3_files(data_files)
                    # Delete table
                    glue_client.delete_table(
                        DatabaseName=f"{RESOURCE_PREFIX}_catalogue_db",
                        Name=f'{metadata["domain"]}_{metadata["dataset"]}',
                    )
                # Delete schema
                delete_s3_files(
                    [
                        {
                            "Key": f'{PROTECTED_PATH}{metadata["domain"]}-{metadata["dataset"]}.json'
                        }
                    ]
                )
            except ClientError as error:
                print(
                    f'Unable to delete data related to {metadata["domain"]}-{metadata["dataset"]}'
                )
                print(error)
            print(f'Deleting files in {metadata["domain"]}/{metadata["dataset"]}')


def find_protected_datasets(domain: str) -> Optional[List[Dict[str, str]]]:
    response = s3_client.list_objects(
        Bucket=DATA_BUCKET,
        Prefix=PROTECTED_PATH,
    )
    if response.get("Contents") is not None:
        protected_datasets = [
            path["Key"]
            for path in response["Contents"]
            if path["Key"].startswith(f"{PROTECTED_PATH}{domain}")
        ]
        data = []
        for path in protected_datasets:
            result = re.search(f"{PROTECTED_PATH}{domain}-([a-z_]+).json", path)
            if result:
                dataset = result.group(1)
                data.append({"domain": domain, "dataset": dataset})
        return data
    else:
        return None


def get_file_paths(domain: str, dataset: str, path: str) -> List[Dict[str, str]]:
    response = s3_client.list_objects(
        Bucket=DATA_BUCKET,
        Prefix=f"{path}/{domain}/{dataset}",
    )
    if response.get("Contents") is not None:
        return [{"Key": path["Key"]} for path in response["Contents"]]


def delete_s3_files(file_paths: List[Dict[str, str]]) -> None:
    s3_client.delete_objects(
        Bucket=DATA_BUCKET,
        Delete={"Objects": file_paths},
    )


def delete_protected_domain_permission_from_db(domain: str) -> None:
    print("Deleting permissions...")
    # Get permission ids
    protected_permissions = get_protected_permissions(domain)

    if not protected_permissions:
        print(f"No protected domain permissions for domain '{domain}' found")
    else:
        # Check subjects with permission
        subjects_with_protected_permissions = get_users_with_protected_permissions(
            protected_permissions
        )

        # Delete permissions for users with protected domain and protected domain
        remove_protected_permissions_from_db(
            protected_permissions, subjects_with_protected_permissions
        )


def get_protected_permissions(domain: str) -> List[str]:
    response = db_table.query(
        KeyConditionExpression=Key("PK").eq("PERMISSION"),
        FilterExpression=Attr("Domain").eq(domain.upper()),
    )
    protected_permissions = [item["SK"] for item in response["Items"]]
    return protected_permissions


def get_users_with_protected_permissions(
    protected_permissions: List[str],
) -> List[Dict]:
    subjects_with_protected_permissions = db_table.query(
        KeyConditionExpression=Key("PK").eq("SUBJECT"),
        FilterExpression=reduce(
            Or,
            ([Attr("Permissions").contains(value) for value in protected_permissions]),
        ),
    )["Items"]
    return subjects_with_protected_permissions


def remove_protected_permissions_from_db(
    protected_permissions: List[str],
    subjects_with_protected_permissions: List[Dict[str, Any]],
):
    try:
        with db_table.batch_writer() as batch:
            # Remove protected domain permissions from subjects
            for subject in subjects_with_protected_permissions:
                subject["Permissions"].difference_update(protected_permissions)

                if len(subject["Permissions"]) == 0:
                    subject["Permissions"] = {}

                batch.put_item(Item=subject)

            # Remove protected domain permissions from database
            for permission in protected_permissions:
                batch.delete_item(
                    Key={
                        "PK": "PERMISSION",
                        "SK": permission,
                    }
                )
    except ClientError as error:
        print(f"Unable to delete {protected_permissions} from db")
        print(error)


if __name__ == "__main__":
    if len(sys.argv) == 2:
        delete_protected_domain(sys.argv[1])
    else:
        print("This method requires the domain for the protected domain to be deleted.")
        print(f"E.g. python {os.path.basename(__file__)} <domain>")
