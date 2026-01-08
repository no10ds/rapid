"""Configuration management for the Rapid MCP server."""

import os
from typing import Optional
from dotenv import load_dotenv
from rapid import Rapid, RapidAuth

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

    def create_client(self) -> Rapid:
        """Create and return an authenticated Rapid client.

        Returns:
            Rapid: Authenticated Rapid SDK client

        Raises:
            ValueError: If configuration is invalid
            Exception: If authentication fails
        """
        try:
            # Initialize authentication
            auth = RapidAuth(
                client_id=self.client_id,
                client_secret=self.client_secret,
                url=self.rapid_url
            )

            # Create and return authenticated client
            return Rapid(auth)
        except Exception as e:
            raise Exception(f"Failed to authenticate with Rapid: {str(e)}")


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


def get_client() -> Rapid:
    """Get an authenticated Rapid client.

    Returns:
        Rapid: Authenticated Rapid SDK client
    """
    return get_config().create_client()
