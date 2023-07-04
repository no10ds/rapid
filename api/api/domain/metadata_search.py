from jinja2 import Template
from typing import List

from api.common.config.aws import GLUE_CATALOGUE_DB_NAME, METADATA_CATALOGUE_DB_NAME


DATASET_COLUMN = "dataset"
DOMAIN_COLUMN = "domain"
VERSION_COLUMN = "version"
DATA_COLUMN = "data"
DATA_TYPE_COLUMN = "data_type"

# fmt: off
METADATA_QUERY = Template(
    f"""
SELECT * FROM (
    SELECT
        metadata.dataset as {DATASET_COLUMN},
        metadata.domain as {DOMAIN_COLUMN},
        metadata.version as {VERSION_COLUMN},
        "column".name as {DATA_COLUMN},
        'column_name' as {DATA_TYPE_COLUMN}
    FROM "{GLUE_CATALOGUE_DB_NAME}"."{METADATA_CATALOGUE_DB_NAME}"
    CROSS JOIN UNNEST("columns") AS t ("column")
    UNION ALL
    SELECT
        metadata.dataset as {DATASET_COLUMN},
        metadata.domain as {DOMAIN_COLUMN},
        metadata.version as {VERSION_COLUMN},
        metadata.description as {DATA_COLUMN},
        'description' as {DATA_TYPE_COLUMN}
    FROM "{GLUE_CATALOGUE_DB_NAME}"."{METADATA_CATALOGUE_DB_NAME}"
    UNION ALL
    SELECT
        metadata.dataset as {DATASET_COLUMN},
        metadata.domain as {DOMAIN_COLUMN},
        metadata.version as {VERSION_COLUMN},
        metadata.dataset as {DATA_COLUMN},
        'dataset_name' as {DATA_TYPE_COLUMN}
    FROM "{GLUE_CATALOGUE_DB_NAME}"."{METADATA_CATALOGUE_DB_NAME}"
)
WHERE {{{{ where_clause }}}}
"""  # nosec B608
)
# fmt: on


def generate_where_clause(search_term: str) -> List[str]:
    return " OR ".join(
        [
            f"lower({DATA_COLUMN}) LIKE '%{word.lower()}%'"
            for word in search_term.split(" ")
        ]
    )


def metadata_search_query(search_term: str) -> str:
    where_clause = generate_where_clause(search_term)
    return METADATA_QUERY.render(where_clause=where_clause)
