from enum import Enum
from typing import List, Union

from api.adapter.aws_resource_adapter import AWSResourceAdapter
from api.common.custom_exceptions import BaseAppException
from api.common.logger import AppLogger

aws_resource_adapter = AWSResourceAdapter()


class BaseEnum(Enum):
    @classmethod
    def values(cls):
        return [item.value for item in cls]

    @classmethod
    def from_string(cls, value: str):
        if value not in cls.values():
            raise ValueError(f"{value} is not an accepted value")
        return cls(value)


def handle_version_retrieval(domain, dataset, version) -> int:
    if not version:
        AppLogger.info(
            "No version provided by the user. Retrieving the latest version from the crawler."
        )
        version = aws_resource_adapter.get_version_from_crawler_tags(domain, dataset)
    return version


def build_error_message_list(error: Union[Exception, BaseAppException]) -> List[str]:
    try:
        if isinstance(error.message, list):
            return error.message
        else:
            return [error.message]
    except AttributeError:
        return [str(error)]


def strtobool(val):
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return True
    elif val in ("n", "no", "f", "false", "off", "0"):
        return False
    else:
        raise ValueError("invalid truth value %r" % (val,))
