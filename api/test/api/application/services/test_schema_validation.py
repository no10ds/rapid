from typing import List, Any

import pytest
from pydantic import ValidationError

from api.application.services.schema_validation import validate_schema
from api.application.services.schema_validation import (
    validate_schema_for_upload,
    schema_has_valid_tag_set,
)
from api.common.config.auth import Sensitivity
from api.common.config.aws import MAX_TAG_COUNT
from api.common.custom_exceptions import SchemaValidationError
from api.domain.schema import Schema, Column
from api.domain.schema_metadata import Owner, UpdateBehaviour, SchemaMetadata

class TestSchemaValidation:
    def setup_method(self):
        self.valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="somedomain",
                dataset="otherDataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=0,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                ),
                "colname3": Column(
                    partition_index=None,
                    dtype="boolean",
                    nullable=False,
                ),
            },
        )

    def _assert_validate_schema_raises_error(
        self, invalid_schema: Schema, message_pattern: str
    ):
        with pytest.raises(SchemaValidationError, match=message_pattern):
            validate_schema(invalid_schema)

    def test_valid_schema(self):
        try:
            validate_schema(self.valid_schema)
        except SchemaValidationError:
            pytest.fail("Unexpected SchemaError was thrown")

    def test_is_invalid_schema_with_no_columns(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={},
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "You need to define at least one column"
        )

    def test_is_invalid_schema_with_domain_name_containing_hyphen(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="test-domain",
                dataset="dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            sensitivity="PUBLIC",
            owners=[Owner(name="owner", email="owner@email.com")],
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="int",
                    nullable=True,
                )
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema,
            r"The value set for domain \[test-domain\] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character",
        )

    def test_is_invalid_schema_with_dataset_name_containing_hyphen(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="domain",
                dataset="test-dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="int",
                    nullable=True,
                )
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema,
            r"The value set for dataset \[test-dataset\] can only contain alphanumeric and underscore `_` characters and must start with an alphabetic character",
        )

    def test_is_invalid_schema_with_empty_column_name(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                )
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "You can not have empty column names"
        )

    def test_is_invalid_schema_with_invalid_inferred_column_name_from_empty_name(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "unnamed_1": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=False,
                )
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "You can not have empty column names"
        )

    # TODO Pandera: Do we need this? Dictionaries cannot have duplicate keys - need to design behaviour around this
    #  def test_is_invalid_schema_with_duplicate_column_name(self):
    #     invalid_schema = Schema(
    #         metadata=SchemaMetadata(
            #     layer="raw",
            #     domain="some",
            #     dataset="other",
            #     sensitivity="PUBLIC",
            #     owners=[Owner(name="owner", email="owner@email.com")],
            # ),
    #         columns={
    #             "colname1": Column(
    #                 partition_index=0,
    #                 dtype="int",
    #                 nullable=False,
    #             ),
    #             "colname1": Column(
    #                 partition_index=None,
    #                 dtype="string",
    #                 nullable=True,
    #             ),
    #         },
    #     )
    #     self._assert_validate_schema_raises_error(
    #         invalid_schema, "You can not have duplicated column names"
    #     )

    def test_is_invalid_schema_with_empty_domain(self):
        with pytest.raises(ValidationError):
            Schema(
                metadata=SchemaMetadata(
                    layer="raw",
                    domain="",
                    dataset="other",
                    sensitivity="PUBLIC",
                    owners=[Owner(name="owner", email="owner@email.com")],
                ),
                columns={
                    "colname1": Column(
                        partition_index=0,
                        dtype="int",
                        nullable=False,
                    ),
                    "colname2": Column(
                        partition_index=None,
                        dtype="string",
                        nullable=True,
                    ),
                },
            )

    def test_is_invalid_schema_with_empty_dataset(self):
        with pytest.raises(ValidationError):
            Schema(
                metadata=SchemaMetadata(
                    layer="raw",
                    domain="domain",
                    sensitivity="PUBLIC",
                    owners=[Owner(name="owner", email="owner@email.com")],
                ),
                columns={
                    "colname1": Column(
                        partition_index=0,
                        dtype="int",
                        nullable=False,
                    ),
                    "colname2": Column(
                        partition_index=None,
                        dtype="string",
                        nullable=True,
                    ),
                },
            )

    def test_is_invalid_schema_with_empty_sensitivity(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                sensitivity="",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                )
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "You can not have empty metadata values"
        )

    @pytest.mark.parametrize(
        "col_name",
        [
            "col 1",
            "col 1/",
            "COL1!",
            " COL1!",
            "123 3",
            "CO! 23",
            "C+2312",
            "h e l l o",
            "_________",
            "/////////",
        ],
    )
    def test_is_invalid_schema_with_invalid_column_name(self, col_name: str):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="domain",
                dataset="dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                col_name: Column(
                    partition_index=0,
                    dtype="int",
                    nullable=False,
                )
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "You must conform to the column heading style guide"
        )

    def test_is_invalid_schema_with_duplicate_partition_number(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=0,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(
                    partition_index=0,
                    dtype="string",
                    nullable=False,
                ),
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "You can not have duplicated partition indexes"
        )

    def test_is_invalid_schema_with_negative_partition_number(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="change_me", email="change_me@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=-1,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(
                    partition_index=0,
                    dtype="string",
                    nullable=False,
                ),
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "You can not a negative partition number"
        )

    def test_is_invalid_schema_with_partition_number_higher_than_the_number_of_partitioned_columns(
        self,
    ):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=2,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(
                    partition_index=0,
                    dtype="string",
                    nullable=False,
                ),
                "colname3": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema,
            "You can not have a partition number greater than the number of partition columns",
        )

    def test_is_invalid_schema_when_all_columns_are_partitioned(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=1,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(
                    partition_index=0,
                    dtype="string",
                    nullable=False,
                ),
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "At least one column should not be partitioned"
        )

    def test_is_invalid_schema_when_partitioned_columns_nullable_values(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=1,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(
                    partition_index=0,
                    dtype="string",
                    nullable=True,
                ),
                "colname3": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )
        self._assert_validate_schema_raises_error(
            invalid_schema, "Partition columns cannot allow null values"
        )

    @pytest.mark.parametrize(
        "dtype",
        [
            "number",
            "something",
            "else",
        ],
    )
    def test_is_invalid_schema_when_has_not_accepted_dtypes(self, dtype: str):
        
        message_pattern = "You are specifying one or more unaccepted data types"
        with pytest.raises(SchemaValidationError, match=message_pattern):
            Schema(
                metadata=SchemaMetadata(
                layer="raw",
                domain="test_domain",
                dataset="test_dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
                columns={
                    "colname1": Column(
                        partition_index=None,
                        dtype=dtype,
                        nullable=False,
                    )
                },
            )
    
    # @pytest.mark.parametrize(
    #     "dtype",
    #     [
    #         "object",
    #         # TODO Pandera: This is supported now?
    #         # "datetime",
    #     ],
    # )
    # def test_is_invalid_schema_when_has_not_accepted_athena_dtypes(self, dtype: str):
    #     invalid_schema = Schema(
    #         dataset_metadata=DatasetMetadata(
    #             layer="raw",
    #             domain="test_domain",
    #             dataset="test_dataset",
    #         ),
    #         sensitivity="PUBLIC",
    #         owners=[Owner(name="owner", email="owner@email.com")],
    #         columns={
    #             "colname1": Column(
    #                 partition_index=None,
    #                 dtype=dtype,
    #                 nullable=False,
    #             )
    #         },
    #     )

    #     self._assert_validate_schema_raises_error(
    #         invalid_schema, "You are specifying one or more unaccepted data types"
    #     )

    def test_is_invalid_when_date_type_column_does_not_define_format(self):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="date",
                    nullable=True,
                    format=None,
                ),
            },
        )

        self._assert_validate_schema_raises_error(
            invalid_schema, "You must specify all required fields"
        )

    @pytest.mark.parametrize(
        "date_format",
        [
            "13 September",
            "%Y/%Y/%Y",
            "%m/%m",
            "%d",
            "%d/%m",
            "%Y:%m:%d",
            "%Y%m%d",
            "something",
            "else",
        ],
    )
    def test_is_invalid_when_date_type_column_has_incorrectly_defined_format(
        self, date_format: str
    ):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="date",
                    nullable=True,
                    format=date_format,
                ),
            },
        )

        self._assert_validate_schema_raises_error(
            invalid_schema,
            rf"You must specify a valid data format. \[{date_format}\] is not accepted",
        )

    @pytest.mark.parametrize(
        "date_format",
        [
            "%Y/%m/%d",
            "%m/%Y",
            "%Y/%m",
            "%Y/%d/%m",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%m-%Y",
            "%Y-%m",
            "%Y-%d-%m",
            "%d-%m-%Y",
            "%m-%d-%Y",
            "%Y-%m-%d",
        ],
    )
    def test_is_valid_when_date_type_column_has_correctly_defined_format(
        self, date_format: str
    ):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="date",
                    nullable=True,
                    format=date_format,
                ),
            },
        )

        try:
            validate_schema(valid_schema)
        except SchemaValidationError:
            pytest.fail("Unexpected SchemaValidationError was thrown")

    @pytest.mark.parametrize(
        "provided_sensitivity",
        list(Sensitivity),
    )
    def test_is_valid_when_provided_sensitivity_is_supported(
        self, provided_sensitivity: str
    ):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity=provided_sensitivity,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        try:
            validate_schema(valid_schema)
        except SchemaValidationError:
            pytest.fail("Unexpected SchemaValidationError was thrown")

    @pytest.mark.parametrize(
        "provided_sensitivity",
        [
            # lowercase versions of accepted values
            "public",
            "private",
            "protected",
            # blatantly incorrect values
            "WRONG",
            "INCORRECT",
            "not provided",
            "67",
        ],
    )
    def test_invalid_schema_when_provided_sensitivity_is_unsupported(
        self, provided_sensitivity: str
    ):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity=provided_sensitivity,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(
                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        self._assert_validate_schema_raises_error(
            invalid_schema,
            r"You must specify a valid sensitivity level. Accepted values: \['PUBLIC', 'PRIVATE', 'PROTECTED'\]",
        )

    @pytest.mark.parametrize(
        "provided_update_behaviour",
        list(UpdateBehaviour),
    )
    def test_is_valid_when_provided_update_behaviour_is_supported(
        self, provided_update_behaviour: str
    ):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                update_behaviour=provided_update_behaviour,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        try:
            validate_schema(valid_schema)
        except SchemaValidationError:
            pytest.fail("Unexpected SchemaValidationError was thrown")

    @pytest.mark.parametrize(
        "provided_update_behaviour",
        [
            # lowercase versions of accepted values
            "update",
            "append",
            # blatantly incorrect values
            "WRONG",
            "INCORRECT",
            "not provided",
            "67",
        ],
    )
    def test_is_invalid_when_provided_update_behaviour_is_unsupported(
        self, provided_update_behaviour: str
    ):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                update_behaviour=provided_update_behaviour,
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        self._assert_validate_schema_raises_error(
            invalid_schema,
            r"You must specify a valid update behaviour. Accepted values: \['APPEND', 'OVERWRITE'\]",
        )

    def test_valid_schema_when_all_tags_are_set(self):
        tags = {f"tag_{index}": "" for index in range(MAX_TAG_COUNT - 1)}

        valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags=tags,
                key_only_tags=["tag"],
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        try:
            validate_schema(valid_schema)
        except SchemaValidationError:
            pytest.fail("Unexpected SchemaValidationError was thrown")

    def test_invalid_schema_when_too_many_tags_are_specified(self):
        key_value_tags = {f"tag_{index}": "" for index in range(MAX_TAG_COUNT - 1)}
        key_only_tags = ["tag1", "tag2"]

        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags=key_value_tags,
                key_only_tags=key_only_tags,
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        with pytest.raises(
            SchemaValidationError,
            match=f"You cannot specify more than {MAX_TAG_COUNT} tags",
        ):
            validate_schema_for_upload(invalid_schema)

    @pytest.mark.parametrize(
        "tags, message",
        [
            ({"aws:": "", "valid_tag": ""}, "You cannot prefix tags with `aws`"),
            (
                {"": "", "valid_tag": ""},
                "Tag keys can only include alphanumeric characters, underscores and hyphens between 1 and 128 characters",
            ),
            (
                {"Tag/1": ""},
                "Tag keys can only include alphanumeric characters, underscores and hyphens between 1 and 128 characters",
            ),
            (
                {"T!ag+1": ""},
                "Tag keys can only include alphanumeric characters, underscores and hyphens between 1 and 128 characters",
            ),
            (
                {"====": ""},
                "Tag keys can only include alphanumeric characters, underscores and hyphens between 1 and 128 characters",
            ),
            (
                {"A" * 129: ""},
                "Tag keys can only include alphanumeric characters, underscores and hyphens between 1 and 128 characters",
            ),
        ],
    )
    def test_invalid_schema_when_tag_keys_are_in_wrong_format(
        self, tags: List[Any], message: str
    ):
        key_only_tags = [tag.split(":")[0].strip('"') for tag in tags]
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags=tags,
                key_only_tags=key_only_tags,
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        with pytest.raises(SchemaValidationError, match=message):
            validate_schema_for_upload(invalid_schema)

    @pytest.mark.parametrize(
        "tags, message",
        [
            (
                {"Tag1": "value/1"},
                "Tag values can only include alphanumeric characters, underscores and hyphens up to 256 characters",
            ),
            (
                {"Tag1": "v!lue+1"},
                "Tag values can only include alphanumeric characters, underscores and hyphens up to 256 characters",
            ),
            (
                {"Tag1": "===="},
                "Tag values can only include alphanumeric characters, underscores and hyphens up to 256 characters",
            ),
            (
                {"Tag1": "A" * 257},
                "Tag values can only include alphanumeric characters, underscores and hyphens up to 256 characters",
            ),
        ],
    )
    def test_invalid_schema_when_tag_values_are_in_wrong_format(
        self, tags: List[Any], message: str
    ):
        invalid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags=tags,
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        with pytest.raises(SchemaValidationError, match=message):
            validate_schema_for_upload(invalid_schema)

    @pytest.mark.parametrize(
        "tags",
        [
            {},  # No tags are allowed
            {"tag1": "some-value", "tag2": "val2"},
            {"tag1": "value-1", "Tag1": "val1"},
            {"Tag_1": "value1", "Tag-2": "Value2", "68tag3": "Value_3"},
            {"A" * 128: "A" * 256},
        ],
    )
    def test_valid_schema_when_tags_are_correct(self, tags: List[Any]):
        key_only_tags = [tag.split(":")[0].strip('"') for tag in tags]
        valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags=tags,
                key_only_tags=key_only_tags,
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        try:
            validate_schema(valid_schema)
        except SchemaValidationError:
            pytest.fail("Unexpected SchemaValidationError was thrown")

    def test_validate_schema_removes_duplicated_tags(self):
        valid_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                version=3,
                owners=[Owner(name="owner", email="owner@email.com")],
                key_value_tags={"tag1": "value-1", "Tag1": "val1", "tag2": "val2"},
                key_only_tags=["Tag1", "tag2", "tag4"],
            ),
            columns={
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
            },
        )

        result_dict = {
            "layer": "raw",
            "domain": "some",
            "dataset": "other",
            "sensitivity": "PUBLIC",
            "version": 3,
            "description": "",
            "key_value_tags": {"tag1": "value-1", "Tag1": "val1", "tag2": "val2"},
            "key_only_tags": ["tag4"],
            "owners": [{"name": "owner", "email": "owner@email.com"}],
            "update_behaviour": "APPEND",
            "is_latest_version": True,
        }

        schema_has_valid_tag_set(valid_schema)

        assert valid_schema.dict(exclude="columns") == result_dict

    def test_is_valid_when_schema_for_upload_has_valid_owners_email_address(self):
        try:
            validate_schema_for_upload(self.valid_schema)
        except SchemaValidationError:
            pytest.fail("Unexpected SchemaValidationError was thrown")

    @pytest.mark.parametrize(
        "owners",
        [
            [Owner(name="owner", email="change_me@email.com")],
            [
                Owner(name="owner", email="change_me@email.com"),
                Owner(name="owner2", email="owner2@email.com"),
            ],
            [
                Owner(name="owner1", email="owner1@email.com"),
                Owner(name="owner", email="change_me@email.com"),
            ],
        ],
    )
    def test_is_invalid_when_schema_for_upload_has_invalid_owners_email_address(
        self, owners: List[Owner]
    ):
        invalid_upload_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=owners,
            ),
            columns={
                "colname1": Column(

                    partition_index=0,
                    dtype="int",
                    nullable=False,
                ),
                "colname1": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
                "colname1": Column(

                    partition_index=None,
                    dtype="boolean",
                    nullable=False,
                ),
            },
        )

        with pytest.raises(SchemaValidationError):
            validate_schema_for_upload(invalid_upload_schema)

    @pytest.mark.parametrize(
        "owners",
        [[], None],
    )
    def test_is_invalid_when_schema_for_upload_has_no_owners(self, owners: List[Owner]):
        invalid_upload_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="other",
                sensitivity="PUBLIC",
                owners=owners,
            ),
            columns={
                "colname1": Column(

                    partition_index=0,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
                "colname3": Column(

                    partition_index=None,
                    dtype="boolean",
                    nullable=False,
                ),
            },
        )

        with pytest.raises(SchemaValidationError):
            validate_schema_for_upload(invalid_upload_schema)

    @pytest.mark.parametrize(
        "domain",
        [
            "_domain",
            "4domain",
            "dom-ain",
            "1234567",
        ],
    )
    def test_is_invalid_when_domain_has_incorrect_format(self, domain):
        invalid_upload_schema = Schema(
             metadata=SchemaMetadata(
                layer="raw",
                domain=domain,
                dataset="dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(

                    partition_index=0,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=True,
                ),
                "colname3": Column(

                    partition_index=None,
                    dtype="boolean",
                    nullable=False,
                ),
            },
        )

        with pytest.raises(SchemaValidationError):
            validate_schema_for_upload(invalid_upload_schema)

    @pytest.mark.parametrize(
        "dataset",
        [
            "_dataset",
            "4dataset",
            "&dataset",
            "data-set",
            "dataset^",
            "12345678",
        ],
    )
    def test_is_invalid_when_dataset_has_incorrect_format(self, dataset):
        invalid_upload_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset=dataset,
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
            ),
            columns={
                "colname1": Column(

                    partition_index=0,
                    dtype="int",
                    nullable=False,
                ),
                "colname2": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=False,
                ),
                "colname3": Column(

                    partition_index=None,
                    dtype="boolean",
                    nullable=False,
                ),
            },
        )

        with pytest.raises(SchemaValidationError):
            validate_schema_for_upload(invalid_upload_schema)

    def test_is_invalid_when_dataset_is_append_and_forces_unique(self):
        invalid_upload_schema = Schema(
            metadata=SchemaMetadata(
                layer="raw",
                domain="some",
                dataset="dataset",
                sensitivity="PUBLIC",
                owners=[Owner(name="owner", email="owner@email.com")],
                update_behaviour="APPEND",
            ),
            columns={
                "colname1": Column(

                    partition_index=0,
                    dtype="int",
                    nullable=False,
                    unique=True,
                ),
                "colname2": Column(

                    partition_index=None,
                    dtype="string",
                    nullable=False,
                    unique=False,
                ),
            },
        )
        try:
            validate_schema(invalid_upload_schema)
        except Exception as e:
            print(e)
            pass

        self._assert_validate_schema_raises_error(
            invalid_upload_schema,
            r"Schema with APPEND update behaviour cannot force unique values in columns",
        )
