import codecs
import csv
import json
import os
import re
from typing import Set, Tuple

import requests
import boto3
import pandas as pd
from botocore.exceptions import ClientError

AWS_REGION = os.environ["AWS_REGION"]
AWS_ACCOUNT = os.environ["AWS_ACCOUNT"]
RESOURCE_PREFIX = os.environ["RESOURCE_PREFIX"]
GLUE_CATALOGUE_DB_NAME = RESOURCE_PREFIX + "_catalogue_db"
DATA_BUCKET = os.environ["DATA_BUCKET"]
DOMAIN_NAME = os.environ["DOMAIN_NAME"]
DATA_PATH = "data/"
SCHEMAS_PATH = "data/schemas/"
RAW_DATA_PATH = "raw_data/"

s3 = boto3.resource("s3")
s3_client = boto3.client("s3")
glue_client = boto3.client("glue", region_name=AWS_REGION)
resource_client = boto3.client("resourcegroupstaggingapi", region_name=AWS_REGION)

datasets_updated = set()


def _list_of_folders(path: str):
    response = s3_client.list_objects(
        Bucket=DATA_BUCKET,
        Prefix=path,
    )

    return response.get("Contents")


def version_raw_data(path: str):
    list_of_raw_data_folders = _list_of_folders(path)

    if list_of_raw_data_folders is None:
        return "No folders to loop through"
    old_structure_path = re.compile(
        "raw_data/[a-zA-Z1-9_]*/[a-zA-Z1-9_]*/[^/]*(.csv|.parquet)"
    )
    for folder in list_of_raw_data_folders:
        folder_key = folder["Key"]
        if old_structure_path.match(folder_key):
            raw_data, domain, dataset, file = folder_key.split("/")
            versioned_file_path = f"{raw_data}/{domain}/{dataset}/1/{file}"
            unversioned_file_path = f"{raw_data}/{domain}/{dataset}/{file}"
            copy_source = {"Bucket": DATA_BUCKET, "Key": unversioned_file_path}
            s3.meta.client.copy(copy_source, DATA_BUCKET, versioned_file_path)
            s3_client.delete_object(
                Bucket=DATA_BUCKET,
                Key=unversioned_file_path,
            )


def read_version_into_schema(folder_key):
    obj = s3.Object(DATA_BUCKET, folder_key)
    data = json.load(obj.get()["Body"])
    data["metadata"]["version"] = "1"
    return data


def version_schemas(folder_key: str):
    old_structure_path = re.compile(
        "data/schemas/(PROTECTED|PUBLIC|PRIVATE)/[a-zA-Z1-9_]*-[a-zA-Z1-9_]*.json"
    )
    if old_structure_path.match(folder_key):
        result = re.search(
            r"data/schemas/(?P<sensitivity>.+)/(?P<domain>.+)-(?P<dataset>.+).json",
            folder_key,
        )
        sensitivity = result.group("sensitivity")
        domain = result.group("domain")
        dataset = result.group("dataset")

        versioned_file_path = (
            f"data/schemas/{sensitivity}/{domain}/{dataset}/1/schema.json"
        )
        unversioned_file_path = f"data/schemas/{sensitivity}/{domain}-{dataset}.json"

        versioned_schema = read_version_into_schema(folder_key)
        _update_file_paths(unversioned_file_path, versioned_file_path, versioned_schema)


def _convert_to_parquet_and_upload(domain, dataset, file, unversioned_file_path):
    file_df = transform_file_to_df(unversioned_file_path)
    file = create_parquet_file_from_csv(file_df, file)
    versioned_file_path = f"data/{domain}/{dataset}/1/{file}"
    with open(file, "rb") as data:
        s3_client.put_object(Body=data, Bucket=DATA_BUCKET, Key=versioned_file_path)
    s3_client.delete_object(
        Bucket=DATA_BUCKET,
        Key=unversioned_file_path,
    )
    os.remove(file)


def version_data(path: str, step_by_step_migration: bool) -> Set[Tuple[str, str]]:
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=DATA_BUCKET, Prefix=path)
    list_of_datasets = set()
    new_structure_path = re.compile(
        r"data/[a-zA-Z1-9_]*/[a-zA-Z1-9_]*/\d{1,3}/.*(.csv|.parquet)"
    )
    old_structure_path = re.compile(
        "data/[a-zA-Z1-9_]*/[a-zA-Z1-9_]*/.*(.csv|.parquet)"
    )
    for page in pages:
        for folder in page["Contents"]:
            folder_key = folder["Key"]
            if SCHEMAS_PATH in folder_key:
                version_schemas(folder_key)
                continue
            if not new_structure_path.match(folder_key) and old_structure_path.match(
                folder_key
            ):
                (
                    unversioned_file_path,
                    versioned_file_path,
                    domain,
                    dataset,
                    file,
                ) = _get_file_paths(folder_key)
                if dataset not in list_of_datasets and step_by_step_migration:
                    list_of_datasets.add(dataset)
                    print(
                        f"Dataset {dataset} will be updated now to a new folder hierarchy."
                    )
                    input("Press Enter if you want to continue.")

                if file.endswith("csv"):
                    _convert_to_parquet_and_upload(
                        domain, dataset, file, unversioned_file_path
                    )

                else:
                    copy_source = {"Bucket": DATA_BUCKET, "Key": unversioned_file_path}
                    s3.meta.client.copy(copy_source, DATA_BUCKET, versioned_file_path)
                    print(unversioned_file_path)
                    s3_client.delete_object(
                        Bucket=DATA_BUCKET,
                        Key=unversioned_file_path,
                    )
                    # _update_file_paths(unversioned_file_path, versioned_file_path, None, None)
                print(f"File {unversioned_file_path} deleted")
    return datasets_updated


def transform_file_to_df(unversioned_file_path):
    data = s3_client.get_object(Bucket=DATA_BUCKET, Key=unversioned_file_path)
    csv_file = csv.DictReader(codecs.getreader("utf-8")(data["Body"]))
    df = pd.DataFrame(csv_file)
    return df


def create_parquet_file_from_csv(df, file):
    df.columns = df.columns.astype(str)
    filename = file.rsplit(".", 1)[0]
    df.to_parquet(f"{filename}.parquet")
    return f"{filename}.parquet"


def get_all_crawlers():
    return resource_client.get_resources(ResourceTypeFilters=["glue:crawler"])


# returns a crawler or None
def get_crawler(domain: str, dataset: str, all_crawlers):
    crawler_resource = None
    for resource in all_crawlers["ResourceTagMappingList"]:
        if resource["ResourceARN"].endswith(
            f":crawler/{RESOURCE_PREFIX}_crawler/{domain}/{dataset}"
        ):
            crawler_resource = resource
    return crawler_resource


def set_crawler_version_tag(crawler_name):
    glue_crawler_arn = (
        "arn:aws:glue:{region}:{account_id}:crawler/{glue_crawler}".format(
            region=AWS_REGION,
            account_id=AWS_ACCOUNT,
            glue_crawler=crawler_name,
        )
    )
    glue_client.tag_resource(
        ResourceArn=glue_crawler_arn,
        TagsToAdd={"no_of_versions": "1"},
    )


def run_crawler(crawler_name):
    glue_client.start_crawler(Name=crawler_name)


def delete_old_table(domain, dataset):
    try:
        glue_client.delete_table(
            DatabaseName=GLUE_CATALOGUE_DB_NAME,
            Name=f"{domain}_{dataset}",
        )
    except ClientError as error:
        print(error)


def update_crawler(domain, dataset, crawler):
    glue_table_prefix = f"{domain}_{dataset}_"
    crawler_name = f"{RESOURCE_PREFIX}_crawler/{domain}/{dataset}"
    if crawler:
        glue_client.update_crawler(
            Name=crawler_name,
            TablePrefix=glue_table_prefix,
            Configuration=json.dumps(
                {
                    "Version": 1.0,
                    "Grouping": {
                        "TableLevelConfiguration": 5,
                        "TableGroupingPolicy": "CombineCompatibleSchemas",
                    },
                }
            ),
        )
        set_crawler_version_tag(crawler_name)
        run_crawler(crawler_name)
        _update_table_config(domain, dataset)
        delete_old_table(domain, dataset)


def _update_table_config(domain: str, dataset: str):
    url = f"https://{DOMAIN_NAME}/table_config?domain={domain}&dataset={dataset}"
    headers = {
        "Accept": "text/csv",
    }
    requests.post(url, headers=headers)


def update_crawlers(datasets_changed: Set[Tuple[str, str]], all_crawlers):
    for domain, dataset in datasets_changed:
        print(
            f"The crawler for domain {domain} and dataset {dataset} will be created now."
        )
        update_crawler(domain, dataset, get_crawler(domain, dataset, all_crawlers))


def migrate_datasets(step_by_step_migration: bool):
    print("Versioning of raw data folder starts.")
    version_raw_data(RAW_DATA_PATH)
    print("Versioning of data folder starts.")
    datasets_changed = version_data(DATA_PATH, step_by_step_migration)
    print("List of the datasets for which crawlers need to be updated:")
    print(datasets_changed)
    input("Press Enter to continue...")
    update_crawlers(datasets_changed, get_all_crawlers())


def _get_partitions(folder_key_split):
    start_index = 3
    partitions = ""
    while start_index < len(folder_key_split) - 1:
        partition = folder_key_split[start_index]
        start_index += 1
        partitions = partitions + "/" + partition
    return partitions


def _get_file_paths(folder_key):
    folder_key_split = folder_key.split("/")
    domain = folder_key_split[1]
    dataset = folder_key_split[2]
    file = folder_key_split[len(folder_key_split) - 1]

    datasets_updated.add((domain, dataset))

    partitions = _get_partitions(folder_key_split)

    if partitions == "":
        unversioned_file_path = f"data/{domain}/{dataset}/{file}"
        versioned_file_path = f"data/{domain}/{dataset}/1/{file}"
    else:
        unversioned_file_path = f"data/{domain}/{dataset}{partitions}/{file}"
        versioned_file_path = f"data/{domain}/{dataset}/1{partitions}/{file}"

    return unversioned_file_path, versioned_file_path, domain, dataset, file


def _update_file_paths(unversioned_file_path, versioned_file_path, schema):
    s3_client.put_object(
        Body=json.dumps(schema, indent=4, separators=(",", ": ")),
        Bucket=DATA_BUCKET,
        Key=versioned_file_path,
    )
    s3_client.delete_object(
        Bucket=DATA_BUCKET,
        Key=unversioned_file_path,
    )


if __name__ == "__main__":
    step_by_step_migration = False
    a = input(
        'Type "y" if you want a step by step migration of data folder and "n" if you want to migrate all datasets at once: '
    )
    print(a)
    if a.lower() == "y":
        step_by_step_migration = True
        migrate_datasets(step_by_step_migration)
    elif a.lower() == "n":
        migrate_datasets(step_by_step_migration)
    else:
        print("Wrong answer.")
