"""Schema management tools for the Rapid MCP server."""

import json
from typing import Dict, Any
import httpx

from ..api_client import RapidAPIClient


def get_schema(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Get detailed schema definition for a dataset.
    """
    try:
        layer = arguments["layer"]
        domain = arguments["domain"]
        dataset = arguments["dataset"]
        version = arguments.get("version")

        # Get dataset info which includes the schema
        endpoint = f"/datasets/{layer}/{domain}/{dataset}/info"
        params = {"version": version} if version else {}

        info = client.get(endpoint, params=params)

        schema = info.get("schema", {})

        return json.dumps({
            "layer": layer,
            "domain": domain,
            "dataset": dataset,
            "version": version or "latest",
            "schema": schema
        }, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def create_schema(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Create a new schema for a dataset.
    """
    try:
        # Build the schema payload according to the API format
        owners = []
        for owner_data in arguments["owners"]:
            owners.append({
                "name": owner_data["name"],
                "email": owner_data["email"]
            })

        columns = []
        for col_data in arguments["columns"]:
            column = {
                "name": col_data["name"],
                "data_type": col_data["data_type"],
                "allow_null": col_data.get("allow_null", True),
            }
            if "partition_index" in col_data and col_data["partition_index"] is not None:
                column["partition_index"] = col_data["partition_index"]
            if "format" in col_data and col_data["format"]:
                column["format"] = col_data["format"]
            columns.append(column)

        schema_payload = {
            "metadata": {
                "layer": arguments["layer"],
                "domain": arguments["domain"],
                "dataset": arguments["dataset"],
                "sensitivity": arguments["sensitivity"],
                "owners": owners,
                "description": arguments.get("description", ""),
                "key_value_tags": arguments.get("key_value_tags", {}),
                "key_only_tags": arguments.get("key_only_tags", []),
                "update_behaviour": arguments.get("update_behaviour", "APPEND")
            },
            "columns": columns
        }

        # POST to /schema endpoint
        result = client.post("/schema", json=schema_payload)

        return json.dumps({
            "success": True,
            "message": f"Schema created successfully for {arguments['layer']}/{arguments['domain']}/{arguments['dataset']}",
            "sensitivity": arguments["sensitivity"],
            "column_count": len(columns),
            "result": result
        }, indent=2)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def update_schema(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Update an existing schema.
    """
    try:
        # Build the schema payload according to the API format
        owners = []
        for owner_data in arguments["owners"]:
            owners.append({
                "name": owner_data["name"],
                "email": owner_data["email"]
            })

        columns = []
        for col_data in arguments["columns"]:
            column = {
                "name": col_data["name"],
                "data_type": col_data["data_type"],
                "allow_null": col_data.get("allow_null", True),
            }
            if "partition_index" in col_data and col_data["partition_index"] is not None:
                column["partition_index"] = col_data["partition_index"]
            if "format" in col_data and col_data["format"]:
                column["format"] = col_data["format"]
            columns.append(column)

        schema_payload = {
            "metadata": {
                "layer": arguments["layer"],
                "domain": arguments["domain"],
                "dataset": arguments["dataset"],
                "sensitivity": arguments["sensitivity"],
                "owners": owners,
                "description": arguments.get("description", ""),
                "key_value_tags": arguments.get("key_value_tags", {}),
                "key_only_tags": arguments.get("key_only_tags", []),
                "update_behaviour": arguments.get("update_behaviour", "APPEND")
            },
            "columns": columns
        }

        # PUT to /schema endpoint
        result = client.put("/schema", json=schema_payload)

        return json.dumps({
            "success": True,
            "message": f"Schema updated successfully for {arguments['layer']}/{arguments['domain']}/{arguments['dataset']}",
            "result": result
        }, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
