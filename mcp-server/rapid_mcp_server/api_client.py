"""API client for making direct HTTP calls to the Rapid API."""

import httpx
from typing import Optional, Dict, Any


class RapidAPIClient:
    """Client for making authenticated requests to the Rapid API."""

    def __init__(self, base_url: str, token: str):
        """Initialize the API client.

        Args:
            base_url: Base URL of the Rapid API
            token: OAuth2 access token for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.client = httpx.Client(timeout=30.0)

    @property
    def headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint (e.g., "/datasets")
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.client.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request to the API.

        Args:
            endpoint: API endpoint
            json: JSON body
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.client.post(url, headers=self.headers, json=json, params=params)
        response.raise_for_status()
        return response.json()

    def put(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request to the API.

        Args:
            endpoint: API endpoint
            json: JSON body
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.client.put(url, headers=self.headers, json=json, params=params)
        response.raise_for_status()
        return response.json()

    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make a DELETE request to the API.

        Args:
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response JSON as dictionary

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = self.client.delete(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the HTTP client."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
