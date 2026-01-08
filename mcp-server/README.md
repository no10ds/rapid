# Rapid MCP Server

A Model Context Protocol (MCP) server that enables Claude to interact with the [rAPId data platform](https://github.com/no10ds/rapid) to query datasets, manage schemas, create users, and troubleshoot issues.

## Features

The Rapid MCP Server provides Claude with 16 tools across 4 categories:

### Dataset Operations
- **list_datasets** - List all available datasets
- **get_dataset_info** - Get detailed information about a dataset
- **query_dataset** - Query datasets with filters and column selection
- **search_datasets** - Search for datasets by term

### Schema Management
- **get_schema** - View schema definitions
- **create_schema** - Create new schemas (requires DATA_ADMIN)
- **update_schema** - Update existing schemas (requires DATA_ADMIN)

### User Management
- **list_subjects** - List all users and clients (requires USER_ADMIN)
- **create_user** - Create new users (requires USER_ADMIN)
- **update_permissions** - Update user/client permissions (requires USER_ADMIN)
- **get_available_permissions** - List available permission types

### Job Debugging
- **get_job_status** - Check job status with error details
- **get_job_error_details** - Enhanced error analysis with troubleshooting

## Prerequisites

- Python 3.10 or higher
- Access to a Rapid instance with client credentials
- Claude Desktop or Claude CLI

## Installation

### Install from source

```bash
git clone https://github.com/no10ds/rapid.git
cd rapid/mcp-server
pip install -e .
```

## Configuration

You have two options to configure the Rapid MCP server:

### Option 1: Using Claude CLI command

```bash
claude mcp add --scope user \
  --env RAPID_URL=https://your-rapid-instance.com \
  --env RAPID_CLIENT_ID=your-client-id \
  --env RAPID_CLIENT_SECRET=your-client-secret \
  rapid \
  -- python -m rapid_mcp_server.server
```

You can also add additional rapid instances:

```bash
claude mcp add --scope user \
  --env RAPID_URL=http://localhost:8000 \
  --env RAPID_CLIENT_ID=dev-id \
  --env RAPID_CLIENT_SECRET=dev-secret \
  rapid-dev \
  -- python -m rapid_mcp_server.server
```

### Option 2: Manual configuration in settings file

Edit your MCP settings file (`~/.claude.json`):

```json
{
  "mcpServers": {
    "rapid": {
      "command": "python",
      "args": ["-m", "rapid_mcp_server.server"],
      "env": {
        "RAPID_URL": "https://your-rapid-instance.com",
        "RAPID_CLIENT_ID": "your-client-id",
        "RAPID_CLIENT_SECRET": "your-client-secret"
      }
    }
  }
}
```

After configuration, reload Claude.

## Usage Examples

Once configured, you can ask Claude natural language questions about your Rapid data:

- What datasets do I have access to?
- Show me information about the raw/example/gapminder dataset
- Query the raw/example/gapminder  dataset and show me the first 10 rows
- What's the schema for raw/example/gapminder?
- Create a new schema for raw/example/gapminder with columns: year (int), country (string), lifeexp (float), continent (string)
- Create a user john.doe@example.com with READ_ALL and WRITE_PUBLIC permissions
- Who has access to the system?
- Why did job abc123 fail?
- What's the status of my recent upload job xyz789?