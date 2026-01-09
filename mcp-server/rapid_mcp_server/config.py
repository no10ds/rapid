"""Configuration management for the Rapid MCP server."""

import os
from typing import Optional
import httpx
from dotenv import load_dotenv

from .api_client import RapidAPIClient

# Load environment variables from .env file if present
load_dotenv()


class Config:
    """Configuration for Rapid MCP server."""

    def __init__(self):
        """Initialize configuration from environment variables."""
        self.rapid_url = os.getenv("RAPID_URL")
        self.client_id = os.getenv("RAPID_CLIENT_ID")
        self.client_secret = os.getenv("RAPID_CLIENT_SECRET")

        # Validate required configuration
        if not self.rapid_url:
            raise ValueError("RAPID_URL environment variable is required")
        if not self.client_id:
            raise ValueError("RAPID_CLIENT_ID environment variable is required")
        if not self.client_secret:
            raise ValueError("RAPID_CLIENT_SECRET environment variable is required")

        # Get the access token on initialization
        self._token = self._fetch_token()

    def _fetch_token(self) -> str:
        """Fetch OAuth2 access token from the Rapid API.

        Returns:
            str: Access token

        Raises:
            Exception: If authentication fails
        """
        try:
            auth_url = f"{self.rapid_url.rstrip('/')}/oauth2/token"
            auth = httpx.BasicAuth(self.client_id, self.client_secret)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client_id,
            }

            response = httpx.post(
                auth_url,
                auth=auth,
                headers=headers,
                json=data,
                timeout=30.0,
            )
            response.raise_for_status()

            token_data = response.json()
            return token_data["access_token"]
        except Exception as e:
            raise Exception(f"Failed to authenticate with Rapid: {str(e)}")

    def create_client(self) -> RapidAPIClient:
        """Create and return an authenticated Rapid API client.

        Returns:
            RapidAPIClient: Authenticated API client

        Raises:
            ValueError: If configuration is invalid
            Exception: If authentication fails
        """
        return RapidAPIClient(self.rapid_url, self._token)


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create the global configuration instance.

    Returns:
        Config: Global configuration instance
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def get_client() -> RapidAPIClient:
    """Get an authenticated Rapid API client.

    Returns:
        RapidAPIClient: Authenticated API client
    """
    return get_config().create_client()
