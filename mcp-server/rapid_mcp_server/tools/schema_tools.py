"""Schema management tools for the Rapid MCP server."""

import json
from typing import Dict, Any
from rapid import Rapid
from rapid.items.schema import Schema, SchemaMetadata, Column, Owner


def get_schema(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Get detailed schema definition for a dataset.
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

        schema = info.get("schema", {})

        return json.dumps({
            "layer": layer,
            "domain": domain,
            "dataset": dataset,
            "version": version or "latest",
            "schema": schema
        }, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def create_schema(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Create a new schema for a dataset.
    """
    try:
        owners = []
        for owner_data in arguments["owners"]:
            owners.append(Owner(
                name=owner_data["name"],
                email=owner_data["email"]
            ))

        metadata = SchemaMetadata(
            layer=arguments["layer"],
            domain=arguments["domain"],
            dataset=arguments["dataset"],
            sensitivity=arguments["sensitivity"],
            owners=owners,
            description=arguments.get("description", ""),
            key_value_tags=arguments.get("key_value_tags", {}),
            key_only_tags=arguments.get("key_only_tags", []),
            update_behaviour=arguments.get("update_behaviour", "APPEND")
        )

        columns = []
        for col_data in arguments["columns"]:
            columns.append(Column(
                name=col_data["name"],
                partition_index=col_data.get("partition_index"),
                data_type=col_data["data_type"],
                allow_null=col_data.get("allow_null", True),
                format=col_data.get("format"),
            ))

        schema = Schema(
            metadata=metadata,
            columns=columns
        )

        client.create_schema(schema)

        return json.dumps({
            "success": True,
            "message": f"Schema created successfully for {arguments['layer']}/{arguments['domain']}/{arguments['dataset']}",
            "sensitivity": arguments["sensitivity"],
            "column_count": len(columns)
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def update_schema(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Update an existing schema.
    """
    try:
        owners = []
        for owner_data in arguments["owners"]:
            owners.append(Owner(
                name=owner_data["name"],
                email=owner_data["email"]
            ))

        metadata = SchemaMetadata(
            layer=arguments["layer"],
            domain=arguments["domain"],
            dataset=arguments["dataset"],
            sensitivity=arguments["sensitivity"],
            owners=owners,
            description=arguments.get("description", ""),
            key_value_tags=arguments.get("key_value_tags", {}),
            key_only_tags=arguments.get("key_only_tags", []),
            update_behaviour=arguments.get("update_behaviour", "APPEND")
        )

        columns = []
        for col_data in arguments["columns"]:
            columns.append(Column(
                name=col_data["name"],
                partition_index=col_data.get("partition_index"),
                data_type=col_data["data_type"],
                allow_null=col_data.get("allow_null", True),
                format=col_data.get("format"),
            ))

        schema = Schema(
            metadata=metadata,
            columns=columns
        )

        result = client.update_schema(schema)

        return json.dumps({
            "success": True,
            "message": f"Schema updated successfully for {arguments['layer']}/{arguments['domain']}/{arguments['dataset']}",
            "result": result
        }, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
