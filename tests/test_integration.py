"""
Integration Tests for claude-oauth-auth

End-to-end integration tests that verify complete workflows across
multiple components (OAuth manager, auth manager, and client).

Test Coverage:
- Complete OAuth workflow from file to client
- Complete API key workflow from env to client
- Cross-component integration
- Real credential discovery (optional, marked with @real)
- Thread safety across components
- Error propagation through stack

Usage:
    # Run all integration tests (except real API tests)
    pytest tests/test_integration.py -v

    # Run with real credentials (requires actual Claude credentials)
    pytest tests/test_integration.py -v -m real

    # Skip integration tests
    pytest -v -m "not integration"
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from claude_oauth_auth.auth_manager import AuthSource, AuthType, UnifiedAuthManager
from claude_oauth_auth.client import ClaudeClient, create_client
from claude_oauth_auth.oauth_manager import OAuthTokenManager, get_token_manager


@pytest.mark.integration
class TestOAuthWorkflow:
    """Integration tests for complete OAuth workflow."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_oauth_file_to_client_workflow(
        self, mock_anthropic, mock_credentials_file, monkeypatch
    ):
        """Test complete workflow from OAuth file to client usage."""
        # Setup
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home", lambda: mock_credentials_file.parent.parent
        )

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="OAuth response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Step 1: OAuth manager reads credentials
        oauth_manager = OAuthTokenManager()
        token = oauth_manager.get_access_token()
        assert token is not None
        assert token.startswith("sk-ant-oat")

        # Step 2: Auth manager discovers OAuth credentials
        auth_manager = UnifiedAuthManager()
        creds = auth_manager.discover_credentials()
        assert creds.auth_type == AuthType.OAUTH_TOKEN
        assert creds.source == AuthSource.CLAUDE_CODE_OAUTH

        # Step 3: Client uses discovered credentials
        client = ClaudeClient()
        response = client.generate("Test prompt")
        assert response == "OAuth response"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_oauth_priority_over_api_key(
        self, mock_anthropic, mock_multiple_credentials, clean_env, monkeypatch
    ):
        """Test that OAuth takes priority when multiple credentials available."""
        # Setup multiple credential sources
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home",
            lambda: mock_multiple_credentials["home_dir"],
        )
        monkeypatch.setattr(
            "claude_oauth_auth.auth_manager.Path.home",
            lambda: mock_multiple_credentials["home_dir"],
        )

        # Set env vars
        for key, value in mock_multiple_credentials["env_vars"].items():
            clean_env.setenv(key, value)

        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client

        # Client should use OAuth (highest auto-discovered priority)
        auth_manager = UnifiedAuthManager()
        creds = auth_manager.discover_credentials()

        # Should prefer env OAuth over env API key
        assert creds.auth_type == AuthType.OAUTH_TOKEN
        assert creds.source == AuthSource.ENV_OAUTH


@pytest.mark.integration
class TestAPIKeyWorkflow:
    """Integration tests for API key workflow."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_env_api_key_to_client_workflow(self, mock_anthropic, clean_env):
        """Test complete workflow from environment API key to client."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test-key")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="API response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Client should auto-discover from environment
        client = ClaudeClient()
        assert client.credentials.auth_type == AuthType.API_KEY
        assert client.credentials.source == AuthSource.ENV_API_KEY

        response = client.generate("Test")
        assert response == "API response"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_config_file_to_client_workflow(
        self, mock_anthropic, mock_api_key_config, clean_env, monkeypatch
    ):
        """Test complete workflow from config file to client."""
        monkeypatch.setattr(
            "claude_oauth_auth.auth_manager.Path.home", lambda: mock_api_key_config.parent.parent
        )

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Config response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Client should discover from config file
        client = ClaudeClient()
        assert client.credentials.auth_type == AuthType.API_KEY
        assert client.credentials.source == AuthSource.CONFIG_FILE

        response = client.generate("Test")
        assert response == "Config response"


@pytest.mark.integration
class TestCredentialDiscovery:
    """Integration tests for credential discovery across components."""

    def test_oauth_manager_integration_with_auth_manager(self, mock_credentials_file, monkeypatch):
        """Test OAuth manager integrates correctly with auth manager."""
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home", lambda: mock_credentials_file.parent.parent
        )

        # OAuth manager
        oauth_manager = OAuthTokenManager()
        oauth_token = oauth_manager.get_access_token()

        # Auth manager should find the same token
        auth_manager = UnifiedAuthManager()
        creds = auth_manager.discover_credentials()

        assert creds.credential == oauth_token
        assert creds.auth_type == AuthType.OAUTH_TOKEN

    @patch("claude_oauth_auth.client.Anthropic")
    def test_explicit_credentials_bypass_discovery(
        self, mock_anthropic, mock_credentials_file, clean_env, monkeypatch
    ):
        """Test that explicit credentials bypass auto-discovery."""
        # Setup OAuth credentials
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home", lambda: mock_credentials_file.parent.parent
        )

        mock_anthropic.return_value = MagicMock()

        # Even though OAuth is available, explicit API key should be used
        client = ClaudeClient(api_key="sk-ant-api03-explicit")

        assert client.credentials.auth_type == AuthType.API_KEY
        assert client.credentials.source == AuthSource.EXPLICIT_API_KEY
        assert client.credentials.credential == "sk-ant-api03-explicit"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_credential_fallback_chain(self, mock_anthropic, tmp_path, clean_env, monkeypatch):
        """Test credential discovery fallback through multiple sources."""
        # Only provide config file
        config_dir = tmp_path / ".anthropic"
        config_dir.mkdir()
        config_file = config_dir / "config"
        config_file.write_text("[default]\napi_key = sk-ant-api03-config\n")

        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)

        mock_anthropic.return_value = MagicMock()

        # Should fall back to config file
        client = ClaudeClient()
        assert client.credentials.source == AuthSource.CONFIG_FILE


@pytest.mark.integration
class TestErrorPropagation:
    """Integration tests for error handling across components."""

    def test_expired_oauth_error_propagation(
        self, expired_credentials_file, clean_env, monkeypatch, tmp_path
    ):
        """Test that expired OAuth tokens are handled correctly throughout stack."""
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home",
            lambda: expired_credentials_file.parent.parent,
        )
        monkeypatch.setattr(
            "claude_oauth_auth.auth_manager.Path.home",
            lambda: tmp_path,  # Empty, no fallback
        )

        # OAuth manager should detect expiration
        oauth_manager = OAuthTokenManager()
        assert oauth_manager.is_token_expired() is True
        assert oauth_manager.get_access_token() is None

        # Auth manager should skip expired OAuth and fail
        with pytest.raises(ValueError) as exc_info:
            ClaudeClient()

        assert "No Anthropic API credentials found" in str(exc_info.value)

    def test_no_credentials_error_propagation(self, clean_env, tmp_path, monkeypatch):
        """Test error propagation when no credentials are available."""
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        # Should fail at auth manager level
        auth_manager = UnifiedAuthManager()
        with pytest.raises(ValueError) as exc_info:
            auth_manager.discover_credentials()

        assert "No Anthropic API credentials found" in str(exc_info.value)

        # Should also fail at client level
        with pytest.raises(ValueError):
            ClaudeClient()


@pytest.mark.integration
class TestThreadSafety:
    """Integration tests for thread safety across components."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_concurrent_client_creation(self, mock_anthropic, clean_env):
        """Test creating multiple clients concurrently."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test")

        mock_anthropic.return_value = MagicMock()

        def create_client():
            return ClaudeClient()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_client) for _ in range(50)]
            clients = [f.result() for f in futures]

        # All clients should be created successfully
        assert len(clients) == 50
        # All should have same credentials
        creds = [c.credentials.credential for c in clients]
        assert len(set(creds)) == 1

    @patch("claude_oauth_auth.client.Anthropic")
    def test_concurrent_generation(self, mock_anthropic, clean_env):
        """Test concurrent message generation with single client."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient()

        def generate_message(prompt):
            return client.generate(prompt)

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(generate_message, f"Prompt {i}") for i in range(50)]
            responses = [f.result() for f in futures]

        # All should succeed
        assert len(responses) == 50
        assert all(r == "Response" for r in responses)


@pytest.mark.integration
class TestConvenienceFunctions:
    """Integration tests for convenience functions."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_create_client_end_to_end(self, mock_anthropic, clean_env):
        """Test create_client convenience function end-to-end."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create client with convenience function
        client = create_client()

        # Should work end-to-end
        response = client.generate("Test")
        assert response == "Test response"

        # Auth info should be available
        info = client.get_auth_info()
        assert info["auth_type"] == "api_key"


@pytest.mark.integration
class TestAuthStatusReporting:
    """Integration tests for authentication status reporting."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_auth_status_consistency(self, mock_anthropic, clean_env):
        """Test auth status is consistent across components."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test")

        mock_anthropic.return_value = MagicMock()

        # Auth manager status
        auth_manager = UnifiedAuthManager()
        auth_status = auth_manager.get_auth_status()

        # Client status
        client = ClaudeClient()
        client_status = client.get_full_auth_status()

        # Should be consistent
        assert auth_status["auth_type"] == client_status["auth_type"]
        assert auth_status["is_valid"] == client_status["is_valid"]


@pytest.mark.integration
@pytest.mark.real
class TestRealCredentials:
    """Integration tests with real credentials (optional)."""

    @pytest.mark.skipif(
        not Path.home().joinpath(".claude", ".credentials.json").exists(),
        reason="Claude Code credentials not found",
    )
    def test_real_oauth_discovery(self):
        """Test real OAuth token discovery from Claude Code."""
        manager = get_token_manager()

        if manager.is_oauth_available() and not manager.is_token_expired():
            token = manager.get_access_token()
            assert token is not None
            assert token.startswith("sk-ant-oat")

            info = manager.get_token_info()
            assert info["is_valid"] is True
            assert info["subscription_type"] in ["max", "pro"]

    @pytest.mark.skipif(
        not Path.home().joinpath(".claude", ".credentials.json").exists(),
        reason="Claude Code credentials not found",
    )
    @patch("claude_oauth_auth.client.Anthropic")
    def test_real_oauth_to_client(self, mock_anthropic):
        """Test real OAuth credentials flow to client."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello!")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        try:
            # Try to use real OAuth credentials
            client = ClaudeClient()
            response = client.generate("Hello!")

            assert response == "Hello!"

            # Check auth info
            info = client.get_auth_info()
            assert info["auth_type"] in ["api_key", "oauth_token"]

        except ValueError:
            # Expected if no credentials available
            pytest.skip("No credentials available for integration test")


@pytest.mark.integration
class TestComplexScenarios:
    """Integration tests for complex real-world scenarios."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_multiple_clients_different_auth(self, mock_anthropic, clean_env):
        """Test using multiple clients with different authentication methods."""
        mock_anthropic.return_value = MagicMock()

        # Client 1: Explicit API key
        client1 = ClaudeClient(api_key="sk-ant-api03-key1")

        # Client 2: Explicit OAuth
        client2 = ClaudeClient(auth_token="sk-ant-oat01-token2")

        # Client 3: Environment variable
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-env")
        client3 = ClaudeClient()

        # All should have different credentials
        assert client1.credentials.credential == "sk-ant-api03-key1"
        assert client2.credentials.credential == "sk-ant-oat01-token2"
        assert client3.credentials.credential == "sk-ant-api03-env"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_reuse_across_requests(self, mock_anthropic, clean_env):
        """Test reusing a single client for multiple requests."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test")

        mock_client = MagicMock()
        call_count = [0]

        def create_response(*args, **kwargs):
            call_count[0] += 1
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=f"Response {call_count[0]}")]
            return mock_response

        mock_client.messages.create.side_effect = create_response
        mock_anthropic.return_value = mock_client

        # Create one client
        client = ClaudeClient()

        # Make multiple requests
        responses = []
        for i in range(5):
            responses.append(client.generate(f"Prompt {i}"))

        # All should succeed
        assert len(responses) == 5
        assert responses[0] == "Response 1"
        assert responses[4] == "Response 5"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_switching_credentials_requires_new_client(self, mock_anthropic, clean_env):
        """Test that switching credentials requires creating new client."""
        mock_anthropic.return_value = MagicMock()

        # Client with first credential
        client1 = ClaudeClient(api_key="sk-ant-api03-key1")
        cred1 = client1.credentials.credential

        # Client with different credential
        client2 = ClaudeClient(api_key="sk-ant-api03-key2")
        cred2 = client2.credentials.credential

        # Clients should have different credentials
        assert cred1 != cred2
        assert cred1 == "sk-ant-api03-key1"
        assert cred2 == "sk-ant-api03-key2"


@pytest.mark.integration
class TestVerboseModeIntegration:
    """Integration tests for verbose mode across components."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_verbose_mode_end_to_end(self, mock_anthropic, clean_env, caplog):
        """Test verbose mode logging throughout the stack."""
        import logging

        caplog.set_level(logging.INFO)

        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test")

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        # Create client with verbose mode
        client = ClaudeClient(verbose=True)
        client.generate("Test")

        # Should have logging from auth discovery and client usage
        assert len(caplog.records) > 0
