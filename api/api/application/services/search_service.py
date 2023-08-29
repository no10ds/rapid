from typing import List, Union

from api.adapter.athena_adapter import AthenaAdapter
from api.adapter.dynamodb_adapter import DynamoDBAdapter, ExpressionAttribute

from api.domain.search_metadata import SearchMetadata, MatchField
from api.domain.dataset_filters import DatasetFilters, SearchFilter


class SearchService:
    def __init__(
        self,
        athena_adapter=AthenaAdapter(),
        dynamodb_adapter=DynamoDBAdapter(),
    ):
        self.athena_adapter = athena_adapter
        self.dynamodb_adapter = dynamodb_adapter

    def search(
        self, search_term: str, include_columns: bool = False
    ) -> List[SearchMetadata]:
        items = self.query_database_for_search_filter(
            SearchFilter(name=MatchField.Dataset, value=search_term)
        ) + self.query_database_for_search_filter(
            SearchFilter(name=MatchField.Description, value=search_term)
        )
        if include_columns:
            items += self.search_columns(search_term)

        return self.remove_duplicates_from_search_results(items)

    def query_database_for_search_filter(
        self, search_filter: SearchFilter
    ) -> List[SearchMetadata]:
        return [
            self.convert_item_to_search_metadata(
                item, search_filter.name, item[search_filter.name]
            )
            for item in self.dynamodb_adapter.get_latest_schemas(
                DatasetFilters(search_filter=search_filter)
            )
        ]

    def search_columns(self, search_term: str) -> List[SearchMetadata]:
        items = self.dynamodb_adapter.get_latest_schemas(
            attributes=[
                ExpressionAttribute("Layer", "L"),
                ExpressionAttribute("Domain", "Do"),
                ExpressionAttribute("Dataset", "Da"),
                ExpressionAttribute("Version", "V"),
                ExpressionAttribute("Columns", "C"),
            ]
        )

        matching_items = []
        for item in items:
            matching_columns = [
                col["name"] for col in item["Columns"] if search_term in col["name"]
            ]
            if matching_columns:
                matching_items.append(
                    self.convert_item_to_search_metadata(
                        item, MatchField.Columns, matching_columns
                    )
                )

        return matching_items

    def convert_item_to_search_metadata(
        self,
        item: dict,
        matching_field: MatchField,
        matching_data: Union[str, List[str]],
    ) -> SearchMetadata:
        return SearchMetadata(
            layer=item["Layer"],
            domain=item["Domain"],
            dataset=item["Dataset"],
            version=item["Version"],
            matching_data=matching_data,
            matching_field=matching_field,
        )

    def remove_duplicates_from_search_results(
        self, metadatas: List[SearchMetadata]
    ) -> List[SearchMetadata]:
        seen_metadatas = set()
        result = []

        for metadata in metadatas:
            identifier = metadata.dataset_identifier(with_version=False)
            if identifier not in seen_metadatas:
                seen_metadatas.add(identifier)
                result.append(metadata)

        return result
