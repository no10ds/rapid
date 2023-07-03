"""
Removes the whitespace and add a description field to the schemas
"""

import os
import boto3
import dotenv
import json

dotenv.load_dotenv()

AWS_REGION = os.environ["AWS_REGION"]
DATA_BUCKET = os.environ["DATA_BUCKET"]

s3_client = boto3.client("s3")
glue_client = boto3.client("glue", region_name=AWS_REGION)

paginator = s3_client.get_paginator("list_objects_v2")
pages = paginator.paginate(Bucket=DATA_BUCKET, Prefix="data/schemas", MaxKeys=10)
keys = set()
for page in pages:
    for folder in page["Contents"]:
        folder_key = folder["Key"]
        folder_size = folder["Size"]
        if folder_size != 0:
            keys.add(folder_key)

for key in keys:
    res = s3_client.get_object(Bucket=DATA_BUCKET, Key=key)
    json_object = json.loads(res["Body"].read().decode("utf-8"))
    json_object["metadata"] |= {"description": "some base test description"}
    s3_client.put_object(Body=json.dumps(json_object), Bucket=DATA_BUCKET, Key=key)
