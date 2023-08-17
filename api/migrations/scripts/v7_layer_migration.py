"""
This script migrates all of your current rAPId datasets to a given Layer, if none is given then it will just be the default layer.
It also migrates the schemas to dynamodb, removing the need for crawlers in the process.

The resources that get changed are the:
- The data folders in S3 are moved to reflect the layer that the datasets belong to.
- Schemas will be read from S3 and written to DynamoDB.
- Glue tables will be renamed to reflect the layer that the datasets belong to.
- Glue crawlers will be deleted.
- Permissions get updated
    1. Migrate old subjects have access to the migrated layer
    2. Alter the protected domain permissions to include the new possible layers

Please ensure that none of the crawlers are running when you start this script.
"""
import argparse
from copy import deepcopy
import json
import os
from typing import List
import re
from pprint import pprint

import boto3
import dotenv

dotenv.load_dotenv()


from api.domain.schema import Schema  # noqa: E402
from api.application.services.schema_service import SchemaService  # noqa: E402
from api.adapter.athena_adapter import AthenaAdapter  # noqa: E402


AWS_REGION = os.environ["AWS_REGION"]
DATA_BUCKET = os.environ["DATA_BUCKET"]
RESOURCE_PREFIX = os.environ["RESOURCE_PREFIX"]
DATA_PATH = "data"
SCHEMAS_PATH = "data/schemas"
RAW_DATA_PATH = "raw_data"
GLUE_DB = f"{RESOURCE_PREFIX}_catalogue_db"
DYNAMODB_PERMISSIONS_TABLE = f"{RESOURCE_PREFIX}_users_permissions"
GLUE_CATALOGUE_DB_NAME = RESOURCE_PREFIX + "_catalogue_db"


def main(
    layer: str,
    all_layers: List[str],
    s3_client,
    glue_client,
    resource_client,
    dynamodb_client,
    schema_service,
    athena_adapter,
):
    migrate_files(layer, s3_client)
    schema_errors = migrate_schemas(layer, schema_service, glue_client)
    migrate_tables(layer, glue_client, athena_adapter)
    migrate_crawlers(glue_client, resource_client)
    migrate_permissions(layer, all_layers, dynamodb_client)

    if schema_errors:
        print("- These were the schema errors that need to be addressed manually")
        pprint(schema_errors)


def migrate_permissions(layer, all_layers, dynamodb_client):
    print("- Migrating the permissions")
    migrate_protected_domain_permissions(layer, all_layers, dynamodb_client)
    migrate_subject_permissions(layer, dynamodb_client)
    print("- Finished migrating the permissions")


def migrate_subject_permissions(layer, dynamodb_client):
    print("-- Migrating the permissions of the subjects")

    PERMISSIONS_TO_REPLACE = [
        "READ_PUBLIC",
        "READ_PROTECTED",
        "READ_PRIVATE",
        "WRITE_PUBLIC",
        "WRITE_PRIVATE",
        "WRITE_PROTECTED",
    ]
    paginator = dynamodb_client.get_paginator("scan")
    page_iterator = paginator.paginate(
        TableName=DYNAMODB_PERMISSIONS_TABLE,
        ScanFilter={
            "PK": {
                "AttributeValueList": [
                    {
                        "S": "SUBJECT",
                    },
                ],
                "ComparisonOperator": "EQ",
            },
        },
    )
    items = [item for page in page_iterator for item in page["Items"]]
    for item in items:
        permissions = item["Permissions"]["SS"]
        to_replace = False
        for idx, permission in enumerate(permissions):
            for permission_to_change in PERMISSIONS_TO_REPLACE:
                # Amend the permission to include the layer
                if permission.startswith(permission_to_change):
                    to_replace = True
                    permissions[idx] = permission.replace(
                        permission_to_change,
                        permission_to_change.replace("_", f"_{layer.upper()}_"),
                    )

        if to_replace:
            print(f"--- Adding layer to the permissions for subject {item['SK']['S']}")
            dynamodb_client.update_item(
                TableName=DYNAMODB_PERMISSIONS_TABLE,
                Key={key: value for key, value in item.items() if key in ["PK", "SK"]},
                UpdateExpression="set #P = :r",
                ExpressionAttributeNames={"#P": "Permissions"},
                ExpressionAttributeValues={
                    ":r": {"SS": permissions},
                },
            )

    print("-- Finished migrating the permissions of the subjects")


def migrate_protected_domain_permissions(layer, all_layers, dynamodb_client):
    print("-- Migrating the protected domain permissions")
    layer_permissions = [layer.upper() for layer in all_layers] + ["ALL"]
    PROTECTED = "PROTECTED"
    actions = ["READ", "WRITE"]

    for action in actions:
        print(f"--- Migrating the {action} protected domain permissions")
        paginator = dynamodb_client.get_paginator("scan")
        page_iterator = paginator.paginate(
            TableName=DYNAMODB_PERMISSIONS_TABLE,
            ScanFilter={
                "PK": {
                    "AttributeValueList": [
                        {
                            "S": "PERMISSION",
                        },
                    ],
                    "ComparisonOperator": "EQ",
                },
                "SK": {
                    "AttributeValueList": [
                        {
                            "S": action,
                        },
                    ],
                    "ComparisonOperator": "BEGINS_WITH",
                },
                "Sensitivity": {
                    "AttributeValueList": [
                        {
                            "S": PROTECTED,
                        },
                    ],
                    "ComparisonOperator": "EQ",
                },
                "Layer": {
                    "ComparisonOperator": "NULL",
                },
            },
        )
        items = [item for page in page_iterator for item in page["Items"]]
        for item in items:
            print(f"---- Adding layer permissions to the permission {item['SK']['S']}")
            for layer in layer_permissions:
                new_item = deepcopy(item)
                current_prefix = f"{action}_{PROTECTED}"
                future_prefix = f"{action}_{layer}_{PROTECTED}"
                new_item["SK"]["S"] = future_prefix + new_item["SK"]["S"].removeprefix(
                    current_prefix
                )
                new_item["Id"]["S"] = future_prefix + new_item["Id"]["S"].removeprefix(
                    current_prefix
                )
                new_item["Layer"] = {"S": layer}
                dynamodb_client.put_item(
                    TableName=DYNAMODB_PERMISSIONS_TABLE, Item=new_item
                )
            item_keys = {
                key: value for key, value in item.items() if key in ["PK", "SK"]
            }
            dynamodb_client.delete_item(
                TableName=DYNAMODB_PERMISSIONS_TABLE, Key=item_keys
            )

    print("-- Finished migrating the protected domain permissions")


def migrate_tables(layer: str, glue_client, athena_adapter: AthenaAdapter):
    print("- Starting to migrate the tables")
    tables = fetch_all_tables(glue_client, layer)

    for table in tables:
        print(f"-- Migrating the table: {table['Name']}")

        partition_indexes = glue_client.get_partition_indexes(
            DatabaseName=GLUE_DB,
            TableName=table["Name"],
        )

        glue_client.create_table(
            DatabaseName=GLUE_DB,
            TableInput={
                "Name": f"{layer}_{table['Name']}",
                "Owner": "hadoop",
                "StorageDescriptor": {
                    "Columns": table["StorageDescriptor"]["Columns"],
                    "Location": table["StorageDescriptor"]["Location"].replace(
                        "/data/", f"/data/{layer}/"
                    ),
                    "InputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat",
                    "OutputFormat": "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat",
                    "Compressed": False,
                    "SerdeInfo": {
                        "SerializationLibrary": "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe",
                        "Parameters": {"serialization.format": "1"},
                    },
                    "NumberOfBuckets": -1,
                    "StoredAsSubDirectories": False,
                },
                "PartitionKeys": table["PartitionKeys"],
                "TableType": "EXTERNAL_TABLE",
                "Parameters": {
                    "classification": "parquet",
                    "typeOfData": "file",
                    "compressionType": "none",
                    "EXTERNAL": "TRUE",
                },
            },
            PartitionIndexes=[
                {
                    "Keys": [
                        key["Name"]
                        for key in partition_indexes["PartitionIndexDescriptorList"][0][
                            "Keys"
                        ]
                    ],
                    "IndexName": partition_indexes["PartitionIndexDescriptorList"][0][
                        "IndexName"
                    ],
                }
            ]
            if partition_indexes["PartitionIndexDescriptorList"]
            else [],
        )

        athena_adapter.query_sql_async(f"MSCK REPAIR TABLE `f{layer}_{table['Name']}`;")
        glue_client.delete_table(Name=table["Name"], DatabaseName=GLUE_DB)


def migrate_crawlers(glue_client, resource_client):
    """
    Steps:
    1. Fetch all of the crawlers
    2. Delete the crawlers
    """
    print("- Starting to migrate the crawlers")
    crawlers = fetch_all_crawlers(resource_client)

    for crawler in crawlers:
        glue_client.delete_crawler(Name=crawler["Name"])

    print("- Finished migrating the crawlers")


def fetch_all_tables(glue_client, layer):
    paginator = glue_client.get_paginator("get_tables")
    page_iterator = paginator.paginate(DatabaseName=GLUE_DB)
    return [
        item
        for page in page_iterator
        for item in page["TableList"]
        if not item["Name"].startswith(f"{layer}_")
    ]


def fetch_all_crawlers(resource_client):
    paginator = resource_client.get_paginator("get_resources")
    page_iterator = paginator.paginate(ResourceTypeFilters=["glue:crawler"])
    resources = [
        item for page in page_iterator for item in page["ResourceTagMappingList"]
    ]
    crawlers = [
        {**resource, **{"Name": resource["ResourceARN"].split(":crawler/")[-1]}}
        for resource in resources
        if f":crawler/{RESOURCE_PREFIX}_crawler/" in resource["ResourceARN"]
    ]
    return crawlers


def migrate_schemas(layer, schema_service: SchemaService, glue_client):
    print("- Migrating the schemas")

    errors = []

    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(
        Bucket=DATA_BUCKET, Prefix=f"data/{layer}/schemas"
    )
    files = [item for page in page_iterator for item in page["Contents"]]
    for file in files:
        # Read in and write to dynamodb with layer
        print(f"-- Migrating the schema: {file['Key']}")
        res = s3_client.get_object(Bucket=DATA_BUCKET, Key=file["Key"])
        json_object = json.loads(res["Body"].read().decode("utf-8"))
        json_object["metadata"] = {"layer": layer, **json_object["metadata"]}

        schema = Schema.parse_obj(json_object)
        old_table_name = f"{schema.metadata.domain}_{schema.metadata.dataset}_{schema.metadata.version}"
        try:
            old_table = glue_client.get_table(DatabaseName=GLUE_DB, Name=old_table_name)
            glue_column_types = {
                col["Name"]: col["Type"]
                for col in old_table["Table"]["StorageDescriptor"]["Columns"]
                + old_table["Table"]["PartitionKeys"]
            }

            for column in schema.columns:
                column.data_type = glue_column_types[column.name]

            schema_service.store_schema(schema)
            latest_version = schema_service.get_latest_schema(schema.metadata)

            if (
                latest_version.dataset_identifier()
                != schema.metadata.dataset_identifier()
            ):
                schema_service.deprecate_schema(schema.metadata)

            s3_client.delete_object(Bucket=DATA_BUCKET, Key=file["Key"])

        except glue_client.exceptions.EntityNotFoundException:
            errors.append(
                f"-- Schema [{file['Key']}] could not be migrated because there is no corresponding table. Please delete the file manually and recreate it"
            )

    print("- Finished migrating the schemas")

    return errors


def migrate_files(layer: str, s3_client):
    print("- Migrating the files")
    # Data
    move_files_by_prefix(s3_client, "data/", f"data/{layer}/")

    # Raw data
    move_files_by_prefix(s3_client, "raw_data/", f"raw_data/{layer}/")
    print("- Finished migrating the files")


def move_files_by_prefix(s3_client, src_prefix: str, dest_prefix: str):
    print(f"-- Moving files from the prefix [{src_prefix}] to [{dest_prefix}]")
    paginator = s3_client.get_paginator("list_objects_v2")
    page_iterator = paginator.paginate(Bucket=DATA_BUCKET, Prefix=src_prefix)

    try:
        files = [item for page in page_iterator for item in page["Contents"]]
    except KeyError:
        print(f"-- There were no files in the prefix [{src_prefix}] to migrate")
        return None

    for file in files:
        src_key = file["Key"]
        # Don't move files if they are already in the destination - can happen if the script is run twice
        if not src_key.startswith(dest_prefix):
            dest_key = re.sub(f"^{src_prefix}", dest_prefix, src_key)
            copy_source = {"Bucket": DATA_BUCKET, "Key": src_key}
            s3_client.copy_object(
                Bucket=DATA_BUCKET,
                CopySource=copy_source,
                Key=dest_key,
            )

            s3_client.delete_object(Bucket=DATA_BUCKET, Key=src_key)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--layer",
        help="Specify the layer to migrate the resources to. Defaults to 'default'",
    )
    parser.add_argument(
        "--all-layers",
        help="Specify all the layers that will exist on this rAPId instance as strings separated by commas e.g 'raw,staging,presentation'. Defaults to 'default'",
    )
    args = parser.parse_args()
    if args.layer:
        layer = args.layer
    else:
        layer = "default"

    if args.all_layers:
        all_layers = args.all_layers.split(",")
    else:
        all_layers = ["default"]

    print(f"Migration to layer [{layer}] with {all_layers} starting")
    s3_client = boto3.client("s3")
    glue_client = boto3.client("glue", region_name=AWS_REGION)
    resource_client = boto3.client("resourcegroupstaggingapi", region_name=AWS_REGION)
    dynamodb_client = boto3.client("dynamodb", region_name=AWS_REGION)
    schema_service = SchemaService()
    athena_adapter = AthenaAdapter()
    main(
        layer,
        all_layers,
        s3_client,
        glue_client,
        resource_client,
        dynamodb_client,
        schema_service,
        athena_adapter,
    )
    print("Migration finished")
