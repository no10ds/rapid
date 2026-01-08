"""Dataset management tools for the Rapid MCP server."""

import json
from typing import Dict, Any, Optional, List
from rapid import Rapid
from rapid.items.query import Query, QueryOrderBy


def list_datasets(client: Rapid, arguments: Dict[str, Any]) -> str:
    """List all datasets available in the Rapid platform.
    """
    try:
        datasets = client.list_datasets()

        if isinstance(datasets, list):
            formatted = []
            for ds in datasets:
                if isinstance(ds, dict):
                    formatted.append({
                        "layer": ds.get("layer"),
                        "domain": ds.get("domain"),
                        "dataset": ds.get("dataset"),
                        "version": ds.get("version"),
                        "tags": ds.get("tags", {}),
                    })
                else:
                    formatted.append(str(ds))

            return json.dumps({
                "count": len(formatted),
                "datasets": formatted
            }, indent=2)
        else:
            return json.dumps({"datasets": datasets}, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def get_dataset_info(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Get detailed information about a specific dataset.
    """
    try:
        layer = arguments["layer"]
        domain = arguments["domain"]
        dataset = arguments["dataset"]
        version = arguments.get("version")

        info = client.fetch_dataset_info(
            layer=layer,
            domain=domain,
            dataset=dataset
        )

        return json.dumps(info, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def query_dataset(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Query a dataset with optional filters and column selection.
    """
    try:
        layer = arguments["layer"]
        domain = arguments["domain"]
        dataset = arguments["dataset"]
        version = arguments.get("version")

        query_params = {}

        if "select_columns" in arguments and arguments["select_columns"]:
            query_params["select_columns"] = arguments["select_columns"]

        if "filter" in arguments and arguments["filter"]:
            query_params["filter"] = arguments["filter"]

        if "limit" in arguments and arguments["limit"]:
            query_params["limit"] = arguments["limit"]

        query = Query(**query_params) if query_params else None

        df = client.download_dataframe(
            layer=layer,
            domain=domain,
            dataset=dataset,
            version=version,
            query=query
        )

        result = df.to_dict(orient='records')
        display_limit = 100
        truncated = len(result) > display_limit

        return json.dumps({
            "row_count": len(result),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data": result[:display_limit],
            "truncated": truncated,
            "message": f"Showing {min(len(result), display_limit)} of {len(result)} rows" if truncated else None
        }, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def search_datasets(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Search for datasets by term in metadata.
    """
    try:
        search_term = arguments["search_term"]

        try:
            results = client.list_datasets()

            filtered = []
            search_lower = search_term.lower()

            if isinstance(results, list):
                for ds in results:
                    if isinstance(ds, dict):
                        searchable = " ".join([
                            str(ds.get("domain", "")),
                            str(ds.get("dataset", "")),
                            str(ds.get("tags", "")),
                        ]).lower()

                        if search_lower in searchable:
                            filtered.append(ds)

            return json.dumps({
                "search_term": search_term,
                "match_count": len(filtered),
                "results": filtered
            }, indent=2, default=str)

        except Exception:
            return json.dumps({"error": "Search failed"}, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
