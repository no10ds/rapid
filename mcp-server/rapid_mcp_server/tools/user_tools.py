"""User and subject management tools for the Rapid MCP server."""

import json
from typing import Dict, Any
import httpx

from ..api_client import RapidAPIClient


def list_subjects(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """List all users and clients (subjects) in the system.
    """
    try:
        # GET /subjects endpoint
        subjects = client.get("/subjects")

        return json.dumps({
            "count": len(subjects) if isinstance(subjects, list) else 0,
            "subjects": subjects
        }, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def create_user(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Create a new user in the Rapid platform.
    """
    try:
        username = arguments["username"]
        email = arguments["email"]
        permissions = arguments["permissions"]

        user_payload = {
            "username": username,
            "email": email,
            "permissions": permissions
        }

        # POST to /user endpoint
        result = client.post("/user", json=user_payload)

        return json.dumps({
            "success": True,
            "message": f"User '{username}' created successfully",
            "username": username,
            "email": email,
            "permissions": permissions,
            "result": result
        }, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def update_permissions(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Update permissions for a user or client.
    """
    try:
        subject_id = arguments["subject_id"]
        permissions = arguments["permissions"]

        permissions_payload = {
            "subject_id": subject_id,
            "permissions": permissions
        }

        # PUT to /subjects/permissions endpoint
        result = client.put("/subjects/permissions", json=permissions_payload)

        return json.dumps({
            "success": True,
            "message": f"Permissions updated for subject {subject_id}",
            "subject_id": subject_id,
            "new_permissions": permissions,
            "result": result
        }, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def get_available_permissions(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Get list of all available permissions in the system.
    """
    permissions = {
        "read_permissions": [
            "READ_ALL",
            "READ_PUBLIC",
            "READ_PRIVATE",
            "READ_PROTECTED_{DOMAIN}"
        ],
        "write_permissions": [
            "WRITE_ALL",
            "WRITE_PUBLIC",
            "WRITE_PRIVATE",
            "WRITE_PROTECTED_{DOMAIN}"
        ],
        "admin_permissions": [
            "DATA_ADMIN",
            "USER_ADMIN"
        ],
        "notes": {
            "READ_PROTECTED": "Replace {DOMAIN} with actual protected domain name",
            "WRITE_PROTECTED": "Replace {DOMAIN} with actual protected domain name",
            "READ_PUBLIC": "Default permission for new users",
            "DATA_ADMIN": "Required for schema and data management operations",
            "USER_ADMIN": "Required for user and permission management"
        }
    }

    return json.dumps(permissions, indent=2)
