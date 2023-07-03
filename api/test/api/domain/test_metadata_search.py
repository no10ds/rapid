import pytest

from api.domain.metadata_search import generate_where_clause, metadata_search_query


@pytest.mark.parametrize(
    "term, expected",
    [
        ("foo", "lower(data) LIKE '%foo%'"),
        ("foo bar", "lower(data) LIKE '%foo%' OR lower(data) LIKE '%bar%'"),
    ],
)
def test_generate_where_clause(term, expected):
    res = generate_where_clause(term)
    assert expected == res


def test_metadata_search_query():
    search_term = "foo bar"
    expected = """
SELECT * FROM (
    SELECT
        metadata.dataset as dataset,
        metadata.domain as domain,
        metadata.version as version,
        "column".name as data,
        'column_name' as data_type
    FROM "rapid_catalogue_db"."rapid_metadata_table"
    CROSS JOIN UNNEST("columns") AS t ("column")
    UNION ALL
    SELECT
        metadata.dataset as dataset,
        metadata.domain as domain,
        metadata.version as version,
        metadata.description as data,
        'description' as data_type
    FROM "rapid_catalogue_db"."rapid_metadata_table"
    UNION ALL
    SELECT
        metadata.dataset as dataset,
        metadata.domain as domain,
        metadata.version as version,
        metadata.dataset as data,
        'dataset_name' as data_type
    FROM "rapid_catalogue_db"."rapid_metadata_table"
)
WHERE lower(data) LIKE '%foo%' OR lower(data) LIKE '%bar%'
    """
    res = metadata_search_query(search_term)
    # Remove whitespace to compare
    assert "".join(res.split()) == "".join(expected.split())
