"""
Tests for ClaudeClient to improve coverage.

Focused tests to cover verbose logging and OAuth client creation.
"""

import pytest

from claude_oauth_auth import ClaudeClient


class TestClaudeClientVerbose:
    """Test ClaudeClient verbose logging."""

    def test_client_with_oauth_verbose(self, clean_env, caplog):
        """Test ClaudeClient creation with OAuth token and verbose mode."""
        import logging

        caplog.set_level(logging.DEBUG)

        try:
            ClaudeClient(auth_token="sk-ant-oat01-test-token", verbose=True)

            # Should have logged OAuth authentication
            assert any("OAuth" in record.message for record in caplog.records)
        except ImportError:
            # Anthropic SDK not installed
            pytest.skip("Anthropic SDK not available")

    def test_client_with_api_key_verbose(self, clean_env, caplog):
        """Test ClaudeClient creation with API key and verbose mode."""
        import logging

        caplog.set_level(logging.DEBUG)

        try:
            ClaudeClient(api_key="sk-ant-api03-test-key", verbose=True)

            # Should have logged API key authentication
            assert any(
                "api" in record.message.lower() or "key" in record.message.lower()
                for record in caplog.records
            )
        except ImportError:
            pytest.skip("Anthropic SDK not available")


class TestClaudeClientStringRepresentation:
    """Test ClaudeClient __str__ method."""

    def test_client_str_with_oauth(self, clean_env):
        """Test __str__ method with OAuth authentication."""
        try:
            client = ClaudeClient(auth_token="sk-ant-oat01-test-token")
            str_repr = str(client)

            assert "OAuth" in str_repr
            assert "claude" in str_repr.lower()
        except ImportError:
            pytest.skip("Anthropic SDK not available")

    def test_client_str_with_api_key(self, clean_env):
        """Test __str__ method with API key authentication."""
        try:
            client = ClaudeClient(api_key="sk-ant-api03-test-key")
            str_repr = str(client)

            assert "API Key" in str_repr
            assert "claude" in str_repr.lower()
        except ImportError:
            pytest.skip("Anthropic SDK not available")
