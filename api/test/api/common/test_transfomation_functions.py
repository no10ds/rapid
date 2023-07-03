import pytest

from api.common.value_transformers import clean_column_name


@pytest.mark.parametrize(
    "given_column,expected_transformed_column",
    [
        (" col1 ", "col1"),
        (" col 2", "col_2"),
        ("c_o_l_3", "c_o_l_3"),
        ("COL5", "col5"),
        ("cOl6", "col6"),
        ("!co#l7!", "col7"),
        ("!co #l8!", "co_l8"),
    ],
)
def test_cleans_column_headings(given_column, expected_transformed_column):
    assert clean_column_name(given_column) == expected_transformed_column
