import base64
import json
from typing import Dict

import boto3
from botocore.exceptions import ClientError

from api.common.config.aws import AWS_REGION


class AuthenticationFailedError(Exception):
    pass


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
