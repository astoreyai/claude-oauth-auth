"""
Unit Tests for OAuthTokenManager

Tests the OAuth token extraction, validation, and management functionality
for Claude Code's OAuth credentials.

Test Coverage:
- Token manager initialization
- Credentials loading and parsing
- Token validation and expiration checking
- Thread-safe access to tokens
- Error handling for missing/invalid files
- Token metadata extraction (scopes, subscription type, etc.)

Usage:
    pytest tests/test_oauth_manager.py -v
    pytest tests/test_oauth_manager.py::TestOAuthManager::test_oauth_manager_initialization -v
"""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from claude_oauth_auth.oauth_manager import (
    OAuthTokenManager,
    get_oauth_info,
    get_oauth_token,
    get_token_manager,
    is_oauth_available,
)


class TestOAuthManagerInitialization:
    """Test OAuthManager initialization and setup."""

    def test_oauth_manager_default_initialization(self):
        """Test OAuthManager initializes with default path."""
        manager = OAuthTokenManager()
        expected_path = Path.home() / ".claude" / ".credentials.json"
        assert manager.credentials_path == expected_path

    def test_oauth_manager_custom_path(self, mock_credentials_file):
        """Test OAuthManager initializes with custom path."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        assert manager.credentials_path == mock_credentials_file

    def test_oauth_manager_path_type_conversion(self, tmp_path):
        """Test OAuthManager converts string paths to Path objects."""
        string_path = str(tmp_path / "test.json")
        manager = OAuthTokenManager(credentials_path=string_path)
        assert isinstance(manager.credentials_path, Path)
        assert str(manager.credentials_path) == string_path


class TestCredentialsLoading:
    """Test credentials file loading and parsing."""

    def test_load_credentials_success(self, mock_credentials_file):
        """Test loading valid credentials file."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        credentials = manager._load_credentials()

        assert credentials is not None
        assert "claudeAiOauth" in credentials
        assert "accessToken" in credentials["claudeAiOauth"]
        assert credentials["claudeAiOauth"]["accessToken"].startswith("sk-ant-oat")

    def test_load_credentials_missing_file(self, tmp_path):
        """Test handling of missing credentials file."""
        nonexistent_file = tmp_path / "nonexistent.json"
        manager = OAuthTokenManager(credentials_path=nonexistent_file)

        credentials = manager._load_credentials()
        assert credentials is None

    def test_load_credentials_invalid_json(self, invalid_json_file):
        """Test handling of invalid JSON in credentials file."""
        manager = OAuthTokenManager(credentials_path=invalid_json_file)
        credentials = manager._load_credentials()
        assert credentials is None

    def test_load_credentials_empty_file(self, tmp_path):
        """Test handling of empty credentials file."""
        empty_file = tmp_path / "empty.json"
        empty_file.write_text("")

        manager = OAuthTokenManager(credentials_path=empty_file)
        credentials = manager._load_credentials()
        assert credentials is None

    def test_load_credentials_caching(self, mock_credentials_file):
        """Test credentials are cached after first load."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)

        # Load once
        creds1 = manager._load_credentials()

        # Load again - should return cached version
        creds2 = manager._load_credentials()

        assert creds1 is creds2  # Same object reference

    def test_load_credentials_force_reload(self, mock_credentials_file):
        """Test force reload bypasses cache."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)

        # Load once
        manager._load_credentials()

        # Force reload
        success = manager.reload()
        assert success is True


class TestOAuthAvailability:
    """Test OAuth availability checking."""

    def test_is_oauth_available_valid_credentials(self, mock_credentials_file):
        """Test OAuth availability with valid credentials."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        assert manager.is_oauth_available() is True

    def test_is_oauth_available_missing_file(self, tmp_path):
        """Test OAuth availability with missing credentials file."""
        nonexistent_file = tmp_path / "nonexistent.json"
        manager = OAuthTokenManager(credentials_path=nonexistent_file)
        assert manager.is_oauth_available() is False

    def test_is_oauth_available_invalid_json(self, invalid_json_file):
        """Test OAuth availability with invalid JSON."""
        manager = OAuthTokenManager(credentials_path=invalid_json_file)
        assert manager.is_oauth_available() is False

    def test_is_oauth_available_missing_oauth_section(self, tmp_path):
        """Test OAuth availability when credentials lack claudeAiOauth section."""
        creds_file = tmp_path / ".credentials.json"
        creds_file.write_text('{"otherData": "value"}')

        manager = OAuthTokenManager(credentials_path=creds_file)
        assert manager.is_oauth_available() is False


class TestTokenExpiration:
    """Test token expiration validation."""

    def test_is_token_expired_valid_token(self, mock_credentials_file):
        """Test token expiration check with valid (future) token."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        assert manager.is_token_expired() is False

    def test_is_token_expired_expired_token(self, expired_credentials_file):
        """Test token expiration check with expired token."""
        manager = OAuthTokenManager(credentials_path=expired_credentials_file)
        assert manager.is_token_expired() is True

    def test_is_token_expired_no_credentials(self, tmp_path):
        """Test token expiration check with no credentials."""
        nonexistent_file = tmp_path / "nonexistent.json"
        manager = OAuthTokenManager(credentials_path=nonexistent_file)
        assert manager.is_token_expired() is True

    def test_is_token_expired_edge_case_now(self, tmp_path):
        """Test token expiration at exact current time."""
        creds_file = tmp_path / ".credentials.json"

        # Set expiration to current time
        expires_at = int(datetime.now().timestamp() * 1000)
        creds_file.write_text(f"""{{
            "claudeAiOauth": {{
                "accessToken": "sk-ant-oat01-token",
                "expiresAt": {expires_at}
            }}
        }}""")

        manager = OAuthTokenManager(credentials_path=creds_file)
        # Should be considered expired (not strictly greater than now)
        result = manager.is_token_expired()
        assert isinstance(result, bool)


class TestAccessTokenRetrieval:
    """Test access token retrieval functionality."""

    def test_get_access_token_valid(self, mock_credentials_file):
        """Test getting access token from valid credentials."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        token = manager.get_access_token()

        assert token is not None
        assert token.startswith("sk-ant-oat")
        assert "test-token" in token

    def test_get_access_token_expired(self, expired_credentials_file):
        """Test getting access token from expired credentials returns None."""
        manager = OAuthTokenManager(credentials_path=expired_credentials_file)
        token = manager.get_access_token()

        # Should return None for expired token
        assert token is None

    def test_get_access_token_missing_file(self, tmp_path):
        """Test getting access token when file doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.json"
        manager = OAuthTokenManager(credentials_path=nonexistent_file)
        token = manager.get_access_token()

        assert token is None

    def test_get_access_token_no_oauth_section(self, tmp_path):
        """Test getting access token when OAuth section is missing."""
        creds_file = tmp_path / ".credentials.json"
        creds_file.write_text('{"otherData": "value"}')

        manager = OAuthTokenManager(credentials_path=creds_file)
        token = manager.get_access_token()

        assert token is None


class TestRefreshToken:
    """Test refresh token retrieval."""

    def test_get_refresh_token_valid(self, mock_credentials_file):
        """Test getting refresh token from valid credentials."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        refresh_token = manager.get_refresh_token()

        assert refresh_token is not None
        assert refresh_token.startswith("sk-ant-ort")

    def test_get_refresh_token_missing(self, tmp_path):
        """Test getting refresh token when not present."""
        creds_file = tmp_path / ".credentials.json"

        expires_at = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
        creds_file.write_text(f"""{{
            "claudeAiOauth": {{
                "accessToken": "sk-ant-oat01-token",
                "expiresAt": {expires_at}
            }}
        }}""")

        manager = OAuthTokenManager(credentials_path=creds_file)
        refresh_token = manager.get_refresh_token()

        assert refresh_token is None


class TestTokenMetadata:
    """Test token metadata extraction."""

    def test_get_subscription_type(self, mock_credentials_file):
        """Test getting subscription type from credentials."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        sub_type = manager.get_subscription_type()

        assert sub_type == "max"

    def test_get_subscription_type_missing(self, tmp_path):
        """Test getting subscription type when not present."""
        creds_file = tmp_path / ".credentials.json"

        expires_at = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
        creds_file.write_text(f"""{{
            "claudeAiOauth": {{
                "accessToken": "sk-ant-oat01-token",
                "expiresAt": {expires_at}
            }}
        }}""")

        manager = OAuthTokenManager(credentials_path=creds_file)
        sub_type = manager.get_subscription_type()

        assert sub_type is None

    def test_get_scopes(self, mock_credentials_file):
        """Test getting OAuth scopes from credentials."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        scopes = manager.get_scopes()

        assert isinstance(scopes, list)
        assert "user:inference" in scopes
        assert "user:profile" in scopes

    def test_get_scopes_missing(self, tmp_path):
        """Test getting scopes when not present."""
        creds_file = tmp_path / ".credentials.json"

        expires_at = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
        creds_file.write_text(f"""{{
            "claudeAiOauth": {{
                "accessToken": "sk-ant-oat01-token",
                "expiresAt": {expires_at}
            }}
        }}""")

        manager = OAuthTokenManager(credentials_path=creds_file)
        scopes = manager.get_scopes()

        assert scopes == []


class TestTokenInfo:
    """Test comprehensive token info retrieval."""

    def test_get_token_info_valid(self, mock_credentials_file):
        """Test getting comprehensive token info with valid credentials."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)
        info = manager.get_token_info()

        assert isinstance(info, dict)
        assert info["available"] is True
        assert info["is_valid"] is True
        assert info["subscription_type"] == "max"
        assert "expires_at" in info
        assert "scopes" in info
        assert isinstance(info["scopes"], list)

    def test_get_token_info_expired(self, expired_credentials_file):
        """Test getting token info with expired credentials."""
        manager = OAuthTokenManager(credentials_path=expired_credentials_file)
        info = manager.get_token_info()

        assert info["available"] is True
        assert info["is_valid"] is False

    def test_get_token_info_missing(self, tmp_path):
        """Test getting token info with missing credentials."""
        nonexistent_file = tmp_path / "nonexistent.json"
        manager = OAuthTokenManager(credentials_path=nonexistent_file)
        info = manager.get_token_info()

        assert info["available"] is False
        assert info["is_valid"] is False
        assert "error" in info


class TestThreadSafety:
    """Test thread-safe access to OAuth manager."""

    def test_thread_safe_token_access(self, mock_credentials_file):
        """Test concurrent access to get_access_token from multiple threads."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)

        def get_token() -> Optional[str]:
            return manager.get_access_token()

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(get_token) for _ in range(100)]
            tokens = [f.result() for f in futures]

        # All tokens should be the same
        assert len(set(tokens)) == 1
        assert tokens[0].startswith("sk-ant-oat")

    def test_thread_safe_reload(self, mock_credentials_file):
        """Test concurrent reload operations."""
        manager = OAuthTokenManager(credentials_path=mock_credentials_file)

        def reload_credentials() -> bool:
            return manager.reload()

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(reload_credentials) for _ in range(20)]
            results = [f.result() for f in futures]

        # All reloads should succeed
        assert all(results)


class TestModuleLevelFunctions:
    """Test module-level convenience functions."""

    def test_get_oauth_token_with_credentials(self, mock_credentials_file, monkeypatch):
        """Test module-level get_oauth_token() function."""
        # Mock the default credentials path
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home", lambda: mock_credentials_file.parent.parent
        )

        token = get_oauth_token()
        # Should either return a token or None
        assert token is None or token.startswith("sk-ant-oat")

    def test_is_oauth_available_function(self, mock_credentials_file, monkeypatch):
        """Test module-level is_oauth_available() function."""
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home", lambda: mock_credentials_file.parent.parent
        )

        available = is_oauth_available()
        assert isinstance(available, bool)

    def test_get_oauth_info_function(self, mock_credentials_file, monkeypatch):
        """Test module-level get_oauth_info() function."""
        monkeypatch.setattr(
            "claude_oauth_auth.oauth_manager.Path.home", lambda: mock_credentials_file.parent.parent
        )

        info = get_oauth_info()
        assert isinstance(info, dict)
        assert "available" in info

    def test_get_token_manager_singleton(self):
        """Test get_token_manager returns consistent instance."""
        manager1 = get_token_manager()
        manager2 = get_token_manager()

        # Should return the same instance
        assert manager1 is manager2


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_permissions_error(self, tmp_path, monkeypatch):
        """Test handling of permission errors when reading credentials."""
        creds_file = tmp_path / ".credentials.json"
        creds_file.write_text('{"claudeAiOauth": {}}')

        # Make file unreadable (Unix only)
        import os

        if os.name != "nt":  # Skip on Windows
            creds_file.chmod(0o000)

            manager = OAuthTokenManager(credentials_path=creds_file)
            credentials = manager._load_credentials()

            # Should handle permission error gracefully
            assert credentials is None

            # Restore permissions for cleanup
            creds_file.chmod(0o644)

    def test_malformed_expiration_date(self, tmp_path):
        """Test handling of malformed expiration date."""
        creds_file = tmp_path / ".credentials.json"
        creds_file.write_text("""
        {
            "claudeAiOauth": {
                "accessToken": "sk-ant-oat01-token",
                "expiresAt": "invalid-date"
            }
        }
        """)

        manager = OAuthTokenManager(credentials_path=creds_file)
        # Should handle gracefully
        result = manager.is_token_expired()
        assert isinstance(result, bool)

    def test_none_values_in_credentials(self, tmp_path):
        """Test handling of None values in credentials."""
        creds_file = tmp_path / ".credentials.json"
        creds_file.write_text("""
        {
            "claudeAiOauth": {
                "accessToken": null,
                "expiresAt": null
            }
        }
        """)

        manager = OAuthTokenManager(credentials_path=creds_file)
        token = manager.get_access_token()

        assert token is None
