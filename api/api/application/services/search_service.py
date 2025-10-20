from typing import List
import logging

from pandas import DataFrame

from api.adapter.athena_adapter import AthenaAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter, ExpressionAttribute
from api.domain.search_metadata import SearchMetadata, MatchField
from api.domain.dataset_metadata import DatasetMetadata, LAYER, DOMAIN, DATASET, VERSION
from api.domain.schema_metadata import DESCRIPTION
from api.domain.schema import COLUMNS

logger = logging.getLogger()

MATCHING_DATA = "matching_data"
MATCHING_FIELD = "matching_field"


class SearchService:
    def __init__(
        self,
        athena_adapter=AthenaAdapter(),
        dynamodb_adapter=DynamoDBAdapter(),
    ):
        self.athena_adapter = athena_adapter
        self.dynamodb_adapter = dynamodb_adapter

    def search(self, search_term: str) -> List[SearchMetadata]:
        df = self.fetch_schema_data()
        df = self.find_matches(df, search_term)
        return self.convert_dataframe_to_search_metadata(df)

    def find_matches(self, df: DataFrame, search_term: str) -> DataFrame:
        """
        Finds matches for the search term in the given dataframe.
        The order of these functions is significant in terms of which matches are surfaced if there are duplicates.
        Any subsequent matches on the same dataset will be ignored.
        """
        return (
            self.produce_generic_matches(search_term, MatchField.Dataset, df)
            .combine_first(
                self.produce_generic_matches(search_term, MatchField.Description, df)
            )
            .combine_first(self.produce_column_matches(search_term, df))
        )

    @property
    def output_columns(self) -> List[str]:
        return DatasetMetadata.get_fields() + [
            MATCHING_DATA,
            MATCHING_FIELD,
        ]

    @property
    def input_columns(self) -> List[str]:
        return DatasetMetadata.get_fields() + [
            DESCRIPTION,
            COLUMNS,
        ]

    def _generate_expression_attributes(self) -> List[ExpressionAttribute]:
        return [
            ExpressionAttribute(column, column[0:2]) for column in self.input_columns
        ]

    def fetch_schema_data(self) -> DataFrame:
        return DataFrame(
            data=self.dynamodb_adapter.get_latest_schemas(
                attributes=self._generate_expression_attributes()
            ),
            columns=self.input_columns,
        )

    def produce_generic_matches(
        self, search_term: str, column: MatchField, df: DataFrame
    ) -> DataFrame:
        """
        Looks for matches in the given dataframe for the given search term in the given column
        """
        mask = df[column].str.contains(search_term, case=False, na=False)
        matches = df.loc[mask].assign(
            **{MATCHING_FIELD: column, MATCHING_DATA: lambda x: x[column]}
        )
        return matches[self.output_columns]

    def produce_column_matches(self, search_term: str, df: DataFrame) -> DataFrame:
        # Temporary columns
        index_col = "index_col"
        column_names = "column_names"
        is_matching = "is_matching"

        # Transforms
        df[index_col] = df.index

        # Debug: Log the raw Columns data before explode
        logger.info(f"=== DEBUG: Analyzing Columns data for search term '{search_term}' ===")
        if not df.empty:
            logger.info(f"DataFrame has {len(df)} rows before explode")
            for idx, row in df.head(3).iterrows():
                col_data = row.get(MatchField.Columns)
                logger.info(f"Row {idx} - Columns type: {type(col_data)}, length: {len(col_data) if col_data else 0}")
                logger.info(f"Row {idx} - Columns value: {col_data}")

        # Debug: Check what data type we're getting in Columns after explode
        exploded_df = df.explode(MatchField.Columns)
        logger.info(f"DataFrame has {len(exploded_df)} rows after explode")

        if not exploded_df.empty:
            # Sample multiple rows to see variety
            sample_size = min(5, len(exploded_df))
            logger.info(f"Examining {sample_size} sample rows after explode:")

            for i in range(sample_size):
                sample_col = exploded_df[MatchField.Columns].iloc[i]
                logger.info(f"Sample {i + 1} - Type: {type(sample_col).__name__}")
                logger.info(f"Sample {i + 1} - Value: {sample_col}")

                if isinstance(sample_col, dict):
                    logger.info(f"Sample {i + 1} - Dict keys: {list(sample_col.keys())}")
                    logger.info(f"Sample {i + 1} - Dict full content: {sample_col}")
                elif isinstance(sample_col, str):
                    logger.info(f"Sample {i + 1} - String length: {len(sample_col)}")
                else:
                    logger.info(f"Sample {i + 1} - Unexpected type, repr: {repr(sample_col)}")

        transformed_df = (
            exploded_df
            .assign(
                **{
                    column_names: lambda x: x[MatchField.Columns].apply(
                        lambda col: col["name"] if isinstance(col, dict) else col
                    ),
                    is_matching: lambda x: x[column_names].str.contains(
                        search_term, case=False
                    ),
                }
            )
            .query(is_matching)
            .groupby(index_col)[column_names]
            .apply(list)
            .reset_index(name=MATCHING_DATA)
            .assign(**{MATCHING_FIELD: MatchField.Columns})
        )

        logger.info(f"Found {len(transformed_df)} column matches for search term '{search_term}'")
        logger.info("=== END DEBUG ===")
        return df.merge(transformed_df, how="inner", on=index_col)[self.output_columns]

    def convert_dataframe_to_search_metadata(
        self,
        df: DataFrame,
    ) -> List[SearchMetadata]:
        return [
            SearchMetadata(
                layer=item[LAYER],
                domain=item[DOMAIN],
                dataset=item[DATASET],
                version=item[VERSION],
                matching_data=item[MATCHING_DATA],
                matching_field=item[MATCHING_FIELD],
            )
            for item in df.to_dict("records")
        ]
