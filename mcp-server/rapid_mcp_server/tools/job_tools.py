"""Job status and debugging tools for the Rapid MCP server."""

import json
from typing import Dict, Any
from rapid import Rapid


def get_job_status(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Get detailed status and error information for a job.
    """
    try:
        job_id = arguments["job_id"]

        job_status = client.fetch_job_progress(job_id)

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

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)


def get_job_error_details(client: Rapid, arguments: Dict[str, Any]) -> str:
    """Get error analysis for a failed job.
    """
    try:
        job_id = arguments["job_id"]
        job_status = client.fetch_job_progress(job_id)

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

    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)
