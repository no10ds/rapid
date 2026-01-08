"""Tests for configuration management."""

import os
import pytest
from rapid_mcp_server.config import Config


def test_config_requires_rapid_url(monkeypatch):
    """Test that Config raises ValueError if RAPID_URL is not set."""
    monkeypatch.delenv("RAPID_URL", raising=False)
    monkeypatch.setenv("RAPID_CLIENT_ID", "test-id")
    monkeypatch.setenv("RAPID_CLIENT_SECRET", "test-secret")

    with pytest.raises(ValueError, match="RAPID_URL"):
        Config()


def test_config_requires_client_id(monkeypatch):
    """Test that Config raises ValueError if RAPID_CLIENT_ID is not set."""
    monkeypatch.setenv("RAPID_URL", "https://example.com")
    monkeypatch.delenv("RAPID_CLIENT_ID", raising=False)
    monkeypatch.setenv("RAPID_CLIENT_SECRET", "test-secret")

    with pytest.raises(ValueError, match="RAPID_CLIENT_ID"):
        Config()


def test_config_requires_client_secret(monkeypatch):
    """Test that Config raises ValueError if RAPID_CLIENT_SECRET is not set."""
    monkeypatch.setenv("RAPID_URL", "https://example.com")
    monkeypatch.setenv("RAPID_CLIENT_ID", "test-id")
    monkeypatch.delenv("RAPID_CLIENT_SECRET", raising=False)

    with pytest.raises(ValueError, match="RAPID_CLIENT_SECRET"):
        Config()


def test_config_loads_all_variables(monkeypatch):
    """Test that Config successfully loads all required variables."""
    monkeypatch.setenv("RAPID_URL", "https://example.com")
    monkeypatch.setenv("RAPID_CLIENT_ID", "test-id")
    monkeypatch.setenv("RAPID_CLIENT_SECRET", "test-secret")

    config = Config()

    assert config.rapid_url == "https://example.com"
    assert config.client_id == "test-id"
    assert config.client_secret == "test-secret"
