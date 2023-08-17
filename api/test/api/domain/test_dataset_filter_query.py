import pytest

from api.common.custom_exceptions import UserError
from api.domain.dataset_filters import DatasetFilters
from boto3.dynamodb.conditions import Attr


def test_returns_empty_tag_filter_list_when_query_is_empty():
    query = DatasetFilters()
    query.format_resource_query() is None


def test_build_key_only_tags():
    filters = DatasetFilters(key_only_tags=["Key1", "Key2"])
    expected = Attr("KeyOnlyTags").contains("Key1") & Attr("KeyOnlyTags").contains(
        "Key2"
    )
    res = filters.build_key_only_tags()
    assert res == expected


def test_build_key_value_tags():
    filters = DatasetFilters(key_value_tags={"Tag1": "Value1", "Tag2": "Value2"})
    expected = Attr("KeyValueTags.Tag1").eq("Value1") & Attr("KeyValueTags.Tag2").eq(
        "Value2"
    )
    res = filters.build_key_value_tags()
    assert res == expected


def test_build_generic_filter_with_single_value():
    expected = Attr("Name").eq("value")

    res = DatasetFilters.build_generic_filter("Name", "value")
    assert res == expected


def test_build_generic_filter_with_list_of_values():
    expected = Attr("Name").is_in(["value1", "value2"])

    res = DatasetFilters.build_generic_filter("Name", ["value1", "value2"])
    assert res == expected


def test_format_resource_query_with_all_values():
    filters = DatasetFilters(
        key_value_tags={"tag2": "value2"},
        key_only_tags=["tag3"],
        sensitivity=["PUBLIC", "PRIVATE"],
        domain="domain",
        layer="raw",
    )

    expected = (
        Attr("KeyValueTags.tag2").eq("value2")
        & Attr("KeyOnlyTags").contains("tag3")
        & Attr("Sensitivity").is_in(["PUBLIC", "PRIVATE"])
        & Attr("Layer").eq("raw")
        & Attr("Domain").eq("domain")
    )

    res = filters.format_resource_query()
    assert res == expected


def test_format_resource_query_with_some_values():
    filters = DatasetFilters(
        key_value_tags={"tag2": "value2"},
        sensitivity="PUBLIC",
        layer=["raw", "layer"],
    )

    expected = (
        Attr("KeyValueTags.tag2").eq("value2")
        & Attr("Sensitivity").eq("PUBLIC")
        & Attr("Layer").is_in(["raw", "layer"])
    )

    res = filters.format_resource_query()
    assert res == expected


def test_returns_tag_filter_list_when_querying_for_sensitivity_and_by_tag():
    query = DatasetFilters(
        sensitivity="PRIVATE", key_value_tags={"Sensitivity": "PRIVATE"}
    )

    with pytest.raises(
        UserError,
        match="You cannot specify Sensitivity both at the root level and in the tags",
    ):
        query.format_resource_query()
