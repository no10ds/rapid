import base64
import json
from io import StringIO
from typing import Dict

import boto3
from botocore.exceptions import ClientError
from botocore.response import StreamingBody

from api.common.config.aws import AWS_REGION
from api.common.config.constants import CONTENT_ENCODING


def get_secret(secret_name: str) -> Dict:
    client = boto3.client(service_name="secretsmanager", region_name=AWS_REGION)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as error:
        raise error
    else:
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]
        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    return json.loads(secret)


def set_encoded_content(string_content: str) -> bytes:
    return bytes(string_content.encode(CONTENT_ENCODING))


def mock_schema_response():
    body_json = {
        "metadata": {
            "layer": "raw",
            "domain": "test_domain",
            "dataset": "test_dataset",
            "sensitivity": "PUBLIC",
            "description": "some test description",
            "version": 1,
        },
        "columns": {
            "colname1": {
                "partition_index": 0,
                "data_type": "int",
                "nullable": True,
            }
        }
    }

    body_encoded = json.dumps(body_json)
    response_body = StreamingBody(StringIO(body_encoded), len(body_encoded))

    return {"Body": response_body}


def mock_list_schemas_response(
    layer: str = "raw",
    domain: str = "test_domain",
    dataset: str = "test_dataset",
    sensitivity: str = "PUBLIC",
):
    return [
        {
            "NextToken": "xxx",
            "ResponseMetadata": {"key": "value"},
            "Contents": [
                {"Key": "schemas"},
                {"Key": f"schemas/{layer}/"},
                {"Key": f"schemas/{layer}/{sensitivity}/"},
                {
                    "Key": f"schemas/{layer}/{sensitivity}/{domain}/{dataset}/1/schema.json",
                },
            ],
            "Name": "bucket-name",
            "Prefix": "schemas",
            "EncodingType": "url",
        }
    ]


def mock_secure_dataset_endpoint():
    """Naming is very important with dependency overrides; unfortunately we cannot just return a Mock object"""

    def secure_dataset_endpoint():
        pass

    return secure_dataset_endpoint


def mock_secure_endpoint():
    """Naming is very important with dependency overrides; unfortunately we cannot just return a Mock object"""

    def secure_endpoint():
        pass

    return secure_endpoint
