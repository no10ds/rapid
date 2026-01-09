"""Dataset management tools for the Rapid MCP server."""

import json
from typing import Dict, Any
import httpx

from ..api_client import RapidAPIClient


def list_datasets(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """List datasets with server-side filtering by layer and/or domain.

    Filters are applied by the Rapid API before returning results.
    """
    try:
        # Build filter payload
        filter_payload = {}
        if "layer" in arguments and arguments["layer"]:
            filter_payload["layer"] = arguments["layer"]
        if "domain" in arguments and arguments["domain"]:
            filter_payload["domain"] = arguments["domain"]

        # Call the POST /datasets endpoint with optional filters
        response = client.post("/datasets", json=filter_payload)

        # Format the response
        if isinstance(response, list):
            formatted = []
            for ds in response:
                if isinstance(ds, dict):
                    formatted.append({
                        "layer": ds.get("layer"),
                        "domain": ds.get("domain"),
                        "dataset": ds.get("dataset"),
                        "version": ds.get("version"),
                        "tags": ds.get("tags", {}),
                        "sensitivity": ds.get("sensitivity"),
                    })
                else:
                    formatted.append(ds)

            result = {
                "count": len(formatted),
                "datasets": formatted
            }

            # Add filter info if filters were applied
            if filter_payload:
                result["filters_applied"] = filter_payload
                result["note"] = "Filters were applied by the API before returning these results"

            return json.dumps(result, indent=2)
        else:
            return json.dumps({"datasets": response}, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def get_dataset_info(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Get detailed information about a specific dataset.
    """
    try:
        layer = arguments["layer"]
        domain = arguments["domain"]
        dataset = arguments["dataset"]
        version = arguments.get("version")

        # Build the endpoint URL
        endpoint = f"/datasets/{layer}/{domain}/{dataset}/info"
        params = {"version": version} if version else {}

        info = client.get(endpoint, params=params)

        return json.dumps(info, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def query_dataset(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Query a dataset with optional filters and column selection.
    """
    try:
        layer = arguments["layer"]
        domain = arguments["domain"]
        dataset = arguments["dataset"]
        version = arguments.get("version")

        # Build query parameters
        query_body = {}
        if "select_columns" in arguments and arguments["select_columns"]:
            query_body["select_columns"] = arguments["select_columns"]
        if "filter" in arguments and arguments["filter"]:
            query_body["filter"] = arguments["filter"]
        if "limit" in arguments and arguments["limit"]:
            query_body["limit"] = arguments["limit"]

        # Build the endpoint URL
        endpoint = f"/datasets/{layer}/{domain}/{dataset}/query"
        params = {"version": version} if version else {}

        result = client.post(endpoint, json=query_body, params=params)

        # The result is already in JSON format from the API
        # Format it for display with row/column info
        if isinstance(result, dict):
            row_count = len(result)
            columns = list(result[next(iter(result))].keys()) if result else []

            # Limit display to 100 rows
            display_limit = 100
            truncated = row_count > display_limit

            # Convert to list format
            data = [result[str(i)] for i in range(min(row_count, display_limit))]

            return json.dumps({
                "row_count": row_count,
                "column_count": len(columns),
                "columns": columns,
                "data": data,
                "truncated": truncated,
                "message": f"Showing {min(row_count, display_limit)} of {row_count} rows" if truncated else None
            }, indent=2, default=str)
        else:
            return json.dumps(result, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def search_datasets(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Search for datasets by term in metadata.
    """
    try:
        search_term = arguments["search_term"]

        # Try using the search endpoint if available
        try:
            endpoint = f"/datasets/search/{search_term}"
            results = client.get(endpoint)

            return json.dumps({
                "search_term": search_term,
                "match_count": len(results) if isinstance(results, list) else 0,
                "results": results
            }, indent=2, default=str)
        except httpx.HTTPStatusError as e:
            # If search endpoint doesn't exist or is disabled, fall back to client-side filtering
            if e.response.status_code == 404:
                datasets = client.post("/datasets", json={})

                filtered = []
                search_lower = search_term.lower()

                if isinstance(datasets, list):
                    for ds in datasets:
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
            else:
                raise

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
