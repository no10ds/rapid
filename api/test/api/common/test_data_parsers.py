import pytest

from api.common.data_parsers import parse_categorisation


def test_finds_categorisation_from_provided_path():
    path = "some/value/here/and/others"
    categories = ["there", "where", "here"]

    result = parse_categorisation(path, categories)

    assert result == "here"


def test_raises_error_when_categorisation_cannot_be_found():
    path = "some/value/here/and/others"
    categories = ["there", "where"]

    with pytest.raises(ValueError, match="Could not find categorisation"):
        parse_categorisation(path, categories)


def test_raises_error_with_customised_message_when_categorisation_cannot_be_found():
    path = "some/value/here/and/others"
    categories = ["there", "where"]

    with pytest.raises(ValueError, match="Could not find custom name"):
        parse_categorisation(path, categories, category_name="custom name")
