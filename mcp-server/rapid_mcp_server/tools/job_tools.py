"""Job status and debugging tools for the Rapid MCP server."""

import json
from typing import Dict, Any
import httpx

from ..api_client import RapidAPIClient


def get_job_status(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Get detailed status and error information for a job.
    """
    try:
        job_id = arguments["job_id"]

        # GET /jobs/{job_id} endpoint
        endpoint = f"/jobs/{job_id}"
        job_status = client.get(endpoint)

        status = job_status.get("status", "UNKNOWN")
        errors = job_status.get("errors", [])

        response = {
            "job_id": job_id,
            "status": status,
            "step": job_status.get("step", "Unknown"),
            "details": job_status
        }

        if status == "FAILED" and errors:
            response["error_count"] = len(errors)
            response["errors"] = errors

        elif status == "SUCCESS":
            response["message"] = "Job completed successfully"

        elif status == "PENDING":
            response["message"] = "Job is still in progress"

        return json.dumps(response, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def get_job_error_details(client: RapidAPIClient, arguments: Dict[str, Any]) -> str:
    """Get error analysis for a failed job.
    """
    try:
        job_id = arguments["job_id"]

        # GET /jobs/{job_id} endpoint
        endpoint = f"/jobs/{job_id}"
        job_status = client.get(endpoint)

        status = job_status.get("status", "UNKNOWN")
        errors = job_status.get("errors", [])
        step = job_status.get("step", "Unknown")

        response = {
            "job_id": job_id,
            "status": status,
            "step": step,
            "errors": errors,
            "raw_job_data": job_status
        }

        return json.dumps(response, indent=2, default=str)

    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"HTTP {e.response.status_code}: {e.response.text}"}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
