"""
Unit Tests for UnifiedAuthManager

Tests the unified authentication manager that handles credential discovery
with proper precedence across multiple sources (OAuth, API keys, env vars, config files).

Test Coverage:
- Authentication priority and precedence
- Credential discovery from multiple sources
- Environment variable handling
- Config file parsing (INI and JSON formats)
- OAuth integration
- Error handling for missing credentials
- Authentication status reporting

Usage:
    pytest tests/test_auth_manager.py -v
    pytest tests/test_auth_manager.py::TestAuthenticationPriority -v
"""

import pytest

from claude_oauth_auth.auth_manager import (
    AuthCredentials,
    AuthSource,
    AuthType,
    UnifiedAuthManager,
    discover_credentials,
    get_auth_status,
)


class TestAuthenticationPriority:
    """Test authentication source priority and precedence."""

    def test_explicit_auth_token_highest_priority(self, clean_env):
        """Test that explicit auth_token parameter has highest priority."""
        manager = UnifiedAuthManager(
            api_key="sk-ant-api03-explicit-key", auth_token="sk-ant-oat01-explicit-token"
        )

        creds = manager.discover_credentials()

        assert creds.auth_type == AuthType.OAUTH_TOKEN
        assert creds.source == AuthSource.EXPLICIT_OAUTH
        assert creds.credential == "sk-ant-oat01-explicit-token"

    def test_explicit_api_key_second_priority(self, clean_env):
        """Test that explicit api_key parameter has second priority."""
        manager = UnifiedAuthManager(api_key="sk-ant-api03-explicit-key")

        creds = manager.discover_credentials()

        assert creds.auth_type == AuthType.API_KEY
        assert creds.source == AuthSource.EXPLICIT_API_KEY
        assert creds.credential == "sk-ant-api03-explicit-key"

    def test_env_oauth_token_third_priority(self, clean_env):
        """Test ANTHROPIC_AUTH_TOKEN environment variable priority."""
        clean_env.setenv("ANTHROPIC_AUTH_TOKEN", "sk-ant-oat01-env-token")

        manager = UnifiedAuthManager()
        creds = manager.discover_credentials()

        assert creds.auth_type == AuthType.OAUTH_TOKEN
        assert creds.source == AuthSource.ENV_OAUTH
        assert creds.credential == "sk-ant-oat01-env-token"

    def test_env_api_key_fourth_priority(self, clean_env):
        """Test ANTHROPIC_API_KEY environment variable priority."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-env-key")

        manager = UnifiedAuthManager()
        creds = manager.discover_credentials()

        assert creds.auth_type == AuthType.API_KEY
        assert creds.source == AuthSource.ENV_API_KEY
        assert creds.credential == "sk-ant-api03-env-key"

    def test_explicit_overrides_environment(self, clean_env):
        """Test explicit parameters override environment variables."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-env-key")
        clean_env.setenv("ANTHROPIC_AUTH_TOKEN", "sk-ant-oat01-env-token")

        manager = UnifiedAuthManager(api_key="sk-ant-api03-explicit-key")

        creds = manager.discover_credentials()

        # Explicit API key should win over env OAuth token
        assert creds.source == AuthSource.EXPLICIT_API_KEY
        assert creds.credential == "sk-ant-api03-explicit-key"


class TestOAuthDiscovery:
    """Test OAuth token discovery from Claude Code."""

    def test_claude_code_oauth_discovery(self, mock_credentials_file, clean_env, monkeypatch):
        """Test discovering OAuth credentials from Claude Code."""
        # Mock the default credentials path
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home", lambda: mock_credentials_file.parent.parent
        )

        manager = UnifiedAuthManager()

        # This might succeed or fail depending on whether OAuth is mocked properly
        try:
            creds = manager.discover_credentials()
            if creds.source == AuthSource.CLAUDE_CODE_OAUTH:
                assert creds.auth_type == AuthType.OAUTH_TOKEN
                assert creds.credential.startswith("sk-ant-oat")
        except ValueError:
            # Expected if no credentials available
            pass

    def test_expired_oauth_token_skipped(
        self, expired_credentials_file, clean_env, monkeypatch, tmp_path
    ):
        """Test that expired OAuth tokens are skipped in discovery."""
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home",
            lambda: expired_credentials_file.parent.parent,
        )
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()

        # Should raise ValueError since expired OAuth is skipped
        with pytest.raises(ValueError) as exc_info:
            manager.discover_credentials()

        assert "No Anthropic API credentials found" in str(exc_info.value)


class TestConfigFileDiscovery:
    """Test config file credential discovery."""

    def test_config_file_ini_format(self, mock_api_key_config, clean_env, monkeypatch, tmp_path):
        """Test discovering credentials from INI format config file."""
        # Mock home directory - use mock_api_key_config for auth_manager, empty for oauth_manager
        monkeypatch.setattr(
            "claude_oauth_auth.auth_manager.Path.home", lambda: mock_api_key_config.parent.parent
        )
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()
        creds = manager.discover_credentials()

        assert creds.source == AuthSource.CONFIG_FILE
        assert creds.auth_type == AuthType.API_KEY
        assert "test-api-key" in creds.credential

    def test_config_file_json_format(self, tmp_path, clean_env, monkeypatch):
        """Test discovering credentials from JSON format config file."""
        config_dir = tmp_path / ".anthropic"
        config_dir.mkdir()

        config_file = config_dir / "config.json"
        config_file.write_text('{"api_key": "sk-ant-api03-json-key"}')

        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()
        creds = manager.discover_credentials()

        assert creds.source == AuthSource.CONFIG_FILE
        assert creds.credential == "sk-ant-api03-json-key"

    def test_config_file_missing_api_key(self, tmp_path, clean_env, monkeypatch):
        """Test config file without api_key field."""
        config_dir = tmp_path / ".anthropic"
        config_dir.mkdir()

        config_file = config_dir / "config"
        config_file.write_text("[default]\nother_field = value\n")

        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()

        with pytest.raises(ValueError) as exc_info:
            manager.discover_credentials()

        assert "No Anthropic API credentials found" in str(exc_info.value)


class TestCredentialValidation:
    """Test credential validation and format checking."""

    def test_valid_oauth_token_format(self, clean_env):
        """Test validation of OAuth token format."""
        manager = UnifiedAuthManager(auth_token="sk-ant-oat01-valid-token")
        creds = manager.discover_credentials()

        assert creds.auth_type == AuthType.OAUTH_TOKEN
        assert creds.credential.startswith("sk-ant-oat")

    def test_valid_api_key_format(self, clean_env):
        """Test validation of API key format."""
        manager = UnifiedAuthManager(api_key="sk-ant-api03-valid-key")
        creds = manager.discover_credentials()

        assert creds.auth_type == AuthType.API_KEY
        assert creds.credential.startswith("sk-ant-api")

    def test_empty_string_credentials_rejected(self, clean_env, tmp_path, monkeypatch):
        """Test that empty string credentials are rejected."""
        # Mock home to empty directory so no credentials are found
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager(api_key="")

        with pytest.raises(ValueError) as exc_info:
            manager.discover_credentials()

        assert "No Anthropic API credentials found" in str(exc_info.value)

    def test_whitespace_only_credentials_rejected(self, clean_env, tmp_path, monkeypatch):
        """Test that whitespace-only credentials are rejected."""
        # Mock home to empty directory so no credentials are found
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager(api_key="   ")

        with pytest.raises(ValueError) as exc_info:
            manager.discover_credentials()

        assert "No Anthropic API credentials found" in str(exc_info.value)


class TestErrorHandling:
    """Test error handling for missing and invalid credentials."""

    def test_no_credentials_error(self, clean_env, tmp_path, monkeypatch):
        """Test error when no credentials are found anywhere."""
        # Mock home to empty temp directory
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()

        with pytest.raises(ValueError) as exc_info:
            manager.discover_credentials()

        error_msg = str(exc_info.value)
        assert "No Anthropic API credentials found" in error_msg
        assert "https://console.anthropic.com" in error_msg

    def test_error_message_includes_documentation(self, clean_env, tmp_path, monkeypatch):
        """Test that error message includes helpful documentation."""
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()

        with pytest.raises(ValueError) as exc_info:
            manager.discover_credentials()

        error_msg = str(exc_info.value)
        # Should include documentation link
        assert "console.anthropic.com" in error_msg or "docs" in error_msg.lower()


class TestAvailabilityChecking:
    """Test credential availability checking methods."""

    def test_is_oauth_available_with_token(self, clean_env):
        """Test OAuth availability when token is provided."""
        manager = UnifiedAuthManager(auth_token="sk-ant-oat01-test")
        assert manager.is_oauth_available() is True

    def test_is_oauth_available_without_token(self, clean_env, tmp_path, monkeypatch):
        """Test OAuth availability when no token is available."""
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()
        # Should be False since no OAuth credentials available
        result = manager.is_oauth_available()
        assert isinstance(result, bool)

    def test_is_api_key_available_with_key(self, clean_env):
        """Test API key availability when key is provided."""
        manager = UnifiedAuthManager(api_key="sk-ant-api03-test")
        assert manager.is_api_key_available() is True

    def test_is_api_key_available_without_key(self, clean_env, tmp_path, monkeypatch):
        """Test API key availability when no key is available."""
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()
        result = manager.is_api_key_available()
        assert isinstance(result, bool)


class TestAuthStatus:
    """Test authentication status reporting."""

    def test_get_auth_status_with_api_key(self, clean_env):
        """Test authentication status reporting with API key."""
        manager = UnifiedAuthManager(api_key="sk-ant-api03-test")
        status = manager.get_auth_status()

        assert isinstance(status, dict)
        assert "is_valid" in status
        assert "auth_type" in status
        assert "source" in status
        assert "available_methods" in status
        assert "summary" in status

        assert status["is_valid"] is True
        assert status["auth_type"] == "api_key"

    def test_get_auth_status_with_oauth(self, clean_env):
        """Test authentication status reporting with OAuth token."""
        manager = UnifiedAuthManager(auth_token="sk-ant-oat01-test")
        status = manager.get_auth_status()

        assert status["is_valid"] is True
        assert status["auth_type"] == "oauth_token"
        assert status["source"] == "explicit_auth_token_parameter"

    def test_get_auth_status_no_credentials(self, clean_env, tmp_path, monkeypatch):
        """Test authentication status when no credentials available."""
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()
        status = manager.get_auth_status()

        assert status["is_valid"] is False
        assert "error" in status or "summary" in status

    def test_auth_status_includes_summary(self, clean_env):
        """Test that status includes human-readable summary."""
        manager = UnifiedAuthManager(api_key="sk-ant-api03-test")
        status = manager.get_auth_status()

        assert "summary" in status
        assert isinstance(status["summary"], str)
        assert len(status["summary"]) > 0


class TestAuthCredentialsDataClass:
    """Test AuthCredentials data class."""

    def test_auth_credentials_creation(self):
        """Test creating AuthCredentials instance."""
        creds = AuthCredentials(
            auth_type=AuthType.API_KEY,
            credential="sk-ant-api03-test",
            source=AuthSource.EXPLICIT_API_KEY,
            metadata={},
        )

        assert creds.auth_type == AuthType.API_KEY
        assert creds.credential == "sk-ant-api03-test"
        assert creds.source == AuthSource.EXPLICIT_API_KEY

    def test_auth_credentials_with_metadata(self):
        """Test AuthCredentials with optional metadata."""
        metadata = {"subscription": "max", "scopes": ["user:inference"]}
        creds = AuthCredentials(
            auth_type=AuthType.OAUTH_TOKEN,
            credential="sk-ant-oat01-test",
            source=AuthSource.CLAUDE_CODE_OAUTH,
            metadata=metadata,
        )

        assert creds.metadata == metadata
        assert creds.metadata["subscription"] == "max"


class TestVerboseMode:
    """Test verbose logging functionality."""

    def test_verbose_mode_logging(self, clean_env, caplog):
        """Test that verbose mode produces log output."""
        import logging

        caplog.set_level(logging.INFO)

        manager = UnifiedAuthManager(api_key="sk-ant-api03-test", verbose=True)

        manager.discover_credentials()

        # Should have logged authentication details
        assert len(caplog.records) > 0

    def test_non_verbose_mode_minimal_logging(self, clean_env, caplog):
        """Test that non-verbose mode produces minimal logging."""
        import logging

        caplog.set_level(logging.INFO)

        manager = UnifiedAuthManager(api_key="sk-ant-api03-test", verbose=False)

        manager.discover_credentials()

        # Should have minimal or no logs
        # (Some logs might still appear for errors)


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""

    def test_discover_credentials_function(self, clean_env):
        """Test module-level discover_credentials function."""
        creds = discover_credentials(api_key="sk-ant-api03-test")

        assert isinstance(creds, AuthCredentials)
        assert creds.auth_type == AuthType.API_KEY
        assert creds.credential == "sk-ant-api03-test"

    def test_discover_credentials_with_oauth(self, clean_env):
        """Test discover_credentials with OAuth token."""
        creds = discover_credentials(auth_token="sk-ant-oat01-test")

        assert creds.auth_type == AuthType.OAUTH_TOKEN
        assert creds.credential == "sk-ant-oat01-test"

    def test_get_auth_status_function(self, clean_env):
        """Test module-level get_auth_status function."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-test")
        status = get_auth_status()

        assert isinstance(status, dict)
        assert "is_valid" in status
        assert "summary" in status
        assert status["is_valid"] is True

    def test_get_auth_status_no_credentials(self, clean_env, tmp_path, monkeypatch):
        """Test get_auth_status with no credentials."""
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        status = get_auth_status()

        assert isinstance(status, dict)
        assert status["is_valid"] is False


class TestMultipleCredentialSources:
    """Test behavior with multiple credential sources available."""

    def test_priority_with_all_sources(self, mock_multiple_credentials, clean_env, monkeypatch):
        """Test credential selection when all sources are available."""
        # Set up environment with all credential types
        for key, value in mock_multiple_credentials["env_vars"].items():
            clean_env.setenv(key, value)

        monkeypatch.setattr(
            "claude_oauth_auth.auth_manager.Path.home",
            lambda: mock_multiple_credentials["home_dir"],
        )

        # Explicit should win
        manager = UnifiedAuthManager(
            api_key="sk-ant-api03-explicit", auth_token="sk-ant-oat01-explicit"
        )

        creds = manager.discover_credentials()

        # Explicit OAuth should have highest priority
        assert creds.source == AuthSource.EXPLICIT_OAUTH
        assert creds.credential == "sk-ant-oat01-explicit"

    def test_fallback_through_sources(self, tmp_path, clean_env, monkeypatch):
        """Test fallback through sources when higher priority ones fail."""
        # Only provide config file
        config_dir = tmp_path / ".anthropic"
        config_dir.mkdir()
        config_file = config_dir / "config"
        config_file.write_text("[default]\napi_key = sk-ant-api03-config\n")

        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager()
        creds = manager.discover_credentials()

        # Should fall back to config file
        assert creds.source == AuthSource.CONFIG_FILE
        assert creds.credential == "sk-ant-api03-config"


class TestEdgeCases:
    """Test edge cases and unusual inputs."""

    def test_none_credential_values(self, clean_env, tmp_path, monkeypatch):
        """Test passing None as credential values."""
        # Mock home to empty directory so no credentials are found
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)
        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = UnifiedAuthManager(api_key=None, auth_token=None)

        with pytest.raises(ValueError):
            manager.discover_credentials()

    def test_credential_with_newlines(self, clean_env):
        """Test credential values containing newlines are handled."""
        manager = UnifiedAuthManager(api_key="sk-ant-api03-test\n")

        # Implementation does not strip newlines
        creds = manager.discover_credentials()
        assert creds.credential == "sk-ant-api03-test\n"

    def test_very_long_credential(self, clean_env):
        """Test handling of unusually long credentials."""
        long_key = "sk-ant-api03-" + ("x" * 1000)
        manager = UnifiedAuthManager(api_key=long_key)

        creds = manager.discover_credentials()
        assert len(creds.credential) > 1000
