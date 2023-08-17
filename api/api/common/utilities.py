from typing import List, Optional, Union

from api.application.services.schema_service import SchemaService
from api.common.config.layers import Layer
from api.common.custom_exceptions import BaseAppException
from api.domain.dataset_metadata import DatasetMetadata

schema_service = SchemaService()


def construct_dataset_metadata(
    layer: Layer, domain: str, dataset: str, version: Optional[int] = None
) -> DatasetMetadata:
    dataset = DatasetMetadata(layer, domain, dataset, version)
    dataset.set_version(schema_service)
    return dataset


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
