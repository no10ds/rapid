"""Main MCP server implementation for Rapid data platform."""

import sys
from mcp.server.fastmcp import FastMCP

from .config import get_client
from .tools import dataset_tools, schema_tools, user_tools, job_tools

# Initialize FastMCP server
mcp = FastMCP("rapid")


# Dataset Tools
@mcp.tool()
def list_datasets() -> str:
    """List all datasets available in the Rapid platform.

    Returns a list of all datasets the authenticated user has access to,
    organized by layer/domain/dataset/version structure.
    """
    client = get_client()
    return dataset_tools.list_datasets(client, {})


@mcp.tool()
def get_dataset_info(layer: str, domain: str, dataset: str, version: int = None) -> str:
    """Get detailed information about a specific dataset.
    """
    client = get_client()
    return dataset_tools.get_dataset_info(client, {
        "layer": layer,
        "domain": domain,
        "dataset": dataset,
        "version": version
    })


@mcp.tool()
def query_dataset(
    layer: str,
    domain: str,
    dataset: str,
    version: int = None,
    select_columns: list[str] = None,
    filter: str = None,
    limit: int = None
) -> str:
    """Query a dataset with optional filters and column selection.
    """
    client = get_client()
    return dataset_tools.query_dataset(client, {
        "layer": layer,
        "domain": domain,
        "dataset": dataset,
        "version": version,
        "select_columns": select_columns,
        "filter": filter,
        "limit": limit
    })


@mcp.tool()
def search_datasets(search_term: str) -> str:
    """Search for datasets by term in metadata.
    """
    client = get_client()
    return dataset_tools.search_datasets(client, {"search_term": search_term})


# Schema Tools
@mcp.tool()
def get_schema(layer: str, domain: str, dataset: str, version: int = None) -> str:
    """Get the schema definition for a dataset.
    """
    client = get_client()
    return schema_tools.get_schema(client, {
        "layer": layer,
        "domain": domain,
        "dataset": dataset,
        "version": version
    })


@mcp.tool()
def create_schema(
    layer: str,
    domain: str,
    dataset: str,
    sensitivity: str,
    columns: list[dict],
    owners: list[dict],
    description: str = "",
    key_value_tags: dict = None,
    key_only_tags: list[str] = None,
    update_behaviour: str = "APPEND"
) -> str:
    """Create a new schema for a dataset.
    """
    client = get_client()
    return schema_tools.create_schema(client, {
        "layer": layer,
        "domain": domain,
        "dataset": dataset,
        "sensitivity": sensitivity,
        "columns": columns,
        "owners": owners,
        "description": description,
        "key_value_tags": key_value_tags or {},
        "key_only_tags": key_only_tags or [],
        "update_behaviour": update_behaviour
    })


@mcp.tool()
def update_schema(
    layer: str,
    domain: str,
    dataset: str,
    sensitivity: str,
    columns: list[dict],
    owners: list[dict],
    description: str = "",
    key_value_tags: dict = None,
    key_only_tags: list[str] = None,
    update_behaviour: str = "APPEND"
) -> str:
    """Update an existing schema.
    """
    client = get_client()
    return schema_tools.update_schema(client, {
        "layer": layer,
        "domain": domain,
        "dataset": dataset,
        "sensitivity": sensitivity,
        "columns": columns,
        "owners": owners,
        "description": description,
        "key_value_tags": key_value_tags or {},
        "key_only_tags": key_only_tags or [],
        "update_behaviour": update_behaviour
    })


# User Management Tools
@mcp.tool()
def list_subjects() -> str:
    """List all users and clients (subjects) in the system.

    Requires USER_ADMIN permissions.
    """
    client = get_client()
    return user_tools.list_subjects(client, {})


@mcp.tool()
def create_user(username: str, email: str, permissions: list[str]) -> str:
    """Create a new user in the Rapid platform.

    Requires USER_ADMIN permissions.
    """
    client = get_client()
    return user_tools.create_user(client, {
        "username": username,
        "email": email,
        "permissions": permissions
    })


@mcp.tool()
def update_permissions(subject_id: str, permissions: list[str]) -> str:
    """Update permissions for a user or client.
    """
    client = get_client()
    return user_tools.update_permissions(client, {
        "subject_id": subject_id,
        "permissions": permissions
    })


@mcp.tool()
def get_available_permissions() -> str:
    """Get a list of all available permissions in the system.
    """
    client = get_client()
    return user_tools.get_available_permissions(client, {})


# Job Debugging Tools
@mcp.tool()
def get_job_status(job_id: str) -> str:
    """Get detailed status and error information for a job.

    Use this to understand why a schema upload, data upload, or other
    async operation succeeded or failed.
    """
    client = get_client()
    return job_tools.get_job_status(client, {"job_id": job_id})


@mcp.tool()
def get_job_error_details(job_id: str) -> str:
    """Get enhanced error analysis for a failed job.

    This provides more detailed troubleshooting than get_job_status,
    including error categorization and specific resolution steps.
    """
    client = get_client()
    return job_tools.get_job_error_details(client, {"job_id": job_id})


def main():
    """Main entry point for the MCP server."""
    try:
        # Test configuration on startup
        from .config import get_config
        config = get_config()
        print(f"Rapid MCP Server starting...", file=sys.stderr)
        print(f"Connected to: {config.rapid_url}", file=sys.stderr)

        # Run the server
        mcp.run()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        print("Please set RAPID_URL, RAPID_CLIENT_ID, and RAPID_CLIENT_SECRET environment variables", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
