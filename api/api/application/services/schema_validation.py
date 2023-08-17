import re
from typing import List, Union, Any, Optional

from api.common.config.auth import Sensitivity
from api.common.config.aws import INFERRED_UNNAMED_COLUMN_PREFIX, MAX_CUSTOM_TAG_COUNT
from api.common.config.constants import (
    TAG_VALUES_REGEX,
    TAG_KEYS_REGEX,
    DATE_FORMAT_REGEX,
    COLUMN_NAME_REGEX,
)
from api.common.custom_exceptions import SchemaValidationError
from api.domain.data_types import AthenaDataType, is_date_type
from api.domain.schema import Schema
from api.domain.schema_metadata import UpdateBehaviour, Owner


def validate_schema_for_upload(schema: Schema):
    validate_schema(schema)
    schema_has_valid_data_owner(schema)
    schema_has_valid_tag_set(schema)


def validate_schema(schema: Schema):
    schema_has_valid_column_definitions(schema)
    schema_has_valid_metadata(schema)


def schema_has_valid_column_definitions(schema: Schema):
    has_columns(schema)
    has_non_empty_column_names(schema)
    has_valid_inferred_column_names(schema)
    has_unique_column_names(schema)
    has_clean_column_headings(schema)
    has_unique_partition_indexes(schema)
    has_valid_partition_index_values(schema)
    has_allow_null_false_on_partitioned_columns(schema)
    has_only_accepted_data_types(schema)
    has_valid_date_column_definition(schema)


def has_columns(schema: Schema):
    if not schema.columns:
        raise SchemaValidationError("You need to define at least one column")


def has_non_empty_column_names(schema: Schema):
    if any((not column.name for column in schema.columns)):
        raise SchemaValidationError("You can not have empty column names")


def has_valid_inferred_column_names(schema: Schema):
    if any(
        (
            column.name.startswith(INFERRED_UNNAMED_COLUMN_PREFIX)
            for column in schema.columns
        )
    ):
        raise SchemaValidationError("You can not have empty column names")


def has_unique_column_names(schema: Schema):
    __has_unique_value(schema.get_column_names(), schema.columns, "column names")


def has_clean_column_headings(schema: Schema):
    col_names = schema.get_column_names()
    for col_name in col_names:
        if __has_punctuation_or_only_one_type_of_character(col_name):
            raise SchemaValidationError(
                "You must conform to the column heading style guide"
            )


def schema_has_valid_metadata(schema: Schema):
    schema_has_metadata_values(schema)
    schema_has_valid_metadata_values(schema)


def schema_has_metadata_values(schema: Schema):
    metadata = schema.metadata
    if not (metadata.domain and metadata.dataset and metadata.sensitivity):
        raise SchemaValidationError("You can not have empty metadata values")


def schema_has_valid_metadata_values(schema: Schema):
    domain_name = schema.get_domain()
    dataset_name = schema.get_dataset()

    if not valid_domain_name(domain_name):
        raise SchemaValidationError(
            f"The value set for domain [{domain_name}] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character"
        )

    if not valid_dataset_name(dataset_name):
        raise SchemaValidationError(
            f"The value set for dataset [{dataset_name}] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character"
        )
    has_valid_sensitivity_level(schema)
    has_valid_update_behaviour(schema)


def valid_domain_name(domain: str) -> bool:
    return validate_metadata_character_string(domain)


def valid_dataset_name(dataset: str) -> bool:
    return validate_metadata_character_string(dataset)


def validate_metadata_character_string(string_input: str) -> bool:
    regex = re.compile("^[a-zA-Z][_a-zA-Z0-9]*$", re.I)
    match = regex.match(string_input)
    return bool(match)


def schema_has_valid_tag_set(schema: Schema):
    schema.metadata.remove_duplicates()
    if len(schema.get_custom_tags()) > MAX_CUSTOM_TAG_COUNT:
        raise SchemaValidationError(
            f"You cannot specify more than {MAX_CUSTOM_TAG_COUNT} tags"
        )

    for key, value in schema.get_tags().items():
        if key.startswith("aws"):
            raise SchemaValidationError("You cannot prefix tags with `aws`")
        if not re.match(TAG_KEYS_REGEX, key):
            raise SchemaValidationError(
                "Tag keys can only include alphanumeric characters, underscores and hyphens between 1 and 128 characters"
            )
        if not re.match(TAG_VALUES_REGEX, value):
            raise SchemaValidationError(
                "Tag values can only include alphanumeric characters, underscores and hyphens up to 256 characters"
            )


def has_unique_partition_indexes(schema: Schema):
    __has_unique_value(
        schema.get_partition_indexes(), schema.get_partitions(), "partition indexes"
    )


def has_valid_partition_index_values(schema: Schema):
    if any(partition < 0 for partition in schema.get_partition_indexes()):
        raise SchemaValidationError("You can not a negative partition number")
    if len(schema.get_partition_indexes()) == len(schema.columns):
        raise SchemaValidationError("At least one column should not be partitioned")
    if any(
        partition >= len(schema.get_partitions())
        for partition in schema.get_partition_indexes()
    ):
        raise SchemaValidationError(
            "You can not have a partition number greater than the number of partition columns"
        )


def has_allow_null_false_on_partitioned_columns(schema):
    for partitioned_col in schema.get_partition_columns():
        if partitioned_col.allow_null:
            raise SchemaValidationError("Partition columns cannot allow null values")


def has_only_accepted_data_types(schema: Schema):
    data_types = schema.get_data_types()
    try:
        for data_type in data_types:
            AthenaDataType(data_type)
    except ValueError:
        raise SchemaValidationError(
            "You are specifying one or more unaccepted data types",
        )


def has_valid_date_column_definition(schema: Schema):
    for column in schema.columns:
        if is_date_type(column.data_type) and __has_value_for(column.format):
            __has_valid_date_format(column.format)


def has_valid_sensitivity_level(schema: Schema):
    if schema.get_sensitivity() not in list(Sensitivity):
        raise SchemaValidationError(
            f"You must specify a valid sensitivity level. Accepted values: {Sensitivity._member_names_}"
        )


def schema_has_valid_data_owner(schema: Schema):
    owners = schema.metadata.get_owners()
    if owners is None or len(owners) == 0:
        raise SchemaValidationError("You must specify at least one owner")
    else:
        for owner in owners:
            _owner_email_is_changed(owner)


def _owner_email_is_changed(owner: Owner):
    if owner.email == "change_me@email.com":
        raise SchemaValidationError("You must change the default owner")


def has_valid_update_behaviour(schema: Schema):
    if schema.get_update_behaviour() not in list(UpdateBehaviour):
        raise SchemaValidationError(
            f"You must specify a valid update behaviour. Accepted values: {UpdateBehaviour._member_names_}"
        )


def __has_unique_value(
    set_to_compare: List[Union[str, int]], actual_value: List[Any], field_name: str
):
    if len(set(set_to_compare)) != len(actual_value):
        raise SchemaValidationError(f"You can not have duplicated {field_name}")


def __has_value_for(value: Optional[Any]) -> bool:
    if not value:
        raise SchemaValidationError("You must specify all required fields")
    return True


def __has_valid_date_format(date_format: str):
    accepted_format = DATE_FORMAT_REGEX
    accepted_date_format_codes = ["Y", "m", "d"]

    matches_accepted_format = re.match(accepted_format, date_format)
    duplicate_format_codes = any(
        date_format.count(letter) > 1 for letter in accepted_date_format_codes
    )
    print(duplicate_format_codes)

    if duplicate_format_codes or not matches_accepted_format:
        raise SchemaValidationError(
            f"You must specify a valid data format. [{date_format}] is not accepted"
        )


def __has_punctuation_or_only_one_type_of_character(col_name: str) -> bool:
    if (
        re.findall(COLUMN_NAME_REGEX, col_name)
        or re.match("\\d+", col_name)
        or re.match("_+", col_name)
    ):
        return True
