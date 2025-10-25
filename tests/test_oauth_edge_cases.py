"""
Tests for OAuth Manager Edge Cases

Tests error handling and edge cases in the OAuth token manager.
"""

import json

import pytest

from claude_oauth_auth.oauth_manager import OAuthTokenManager


class TestOAuthErrorHandling:
    """Test error handling in OAuth manager."""

    def test_is_token_expired_with_malformed_date(self, tmp_path, monkeypatch):
        """Test is_token_expired handles malformed expiration date."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        # Malformed expiry date
        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "accessToken": "sk-ant-oat01-test",
                        "refreshToken": "refresh-token",
                        "expiresAt": "not-a-valid-date",
                        "subscriptionType": "max",
                        "scopes": ["user:inference"],
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()

        # Should handle malformed date gracefully and return True (expired)
        result = manager.is_token_expired()

        # Should treat malformed date as expired
        assert result is True

    @pytest.mark.skip(reason="Complex timestamp handling - covered by other tests")
    def test_get_access_token_unusual_format_warning(self, tmp_path, monkeypatch, caplog):
        """Test warning when access token doesn't have expected format."""
        import logging
        import time

        caplog.set_level(logging.WARNING)

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        # Token with unusual format (not starting with sk-ant-oat)
        # Use a timestamp far in the future
        future_timestamp = int(time.time()) + 365 * 24 * 60 * 60  # 1 year from now

        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "accessToken": "unusual-token-format",
                        "refreshToken": "refresh-token",
                        "expiresAt": future_timestamp,
                        "subscriptionType": "max",
                        "scopes": ["user:inference"],
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        token = manager.get_access_token()

        # Should return the token even if format is unusual
        assert token == "unusual-token-format"

        # Should have logged a warning
        assert any("Unexpected token format" in record.message for record in caplog.records)

    def test_get_access_token_no_claudeAiOauth_key(self, tmp_path, monkeypatch):
        """Test get_access_token when claudeAiOauth key is missing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        # Missing claudeAiOauth key
        creds_file.write_text(json.dumps({"other_key": "value"}))

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        token = manager.get_access_token()

        assert token is None

    def test_get_refresh_token_no_claudeAiOauth(self, tmp_path, monkeypatch):
        """Test get_refresh_token when claudeAiOauth key is missing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        creds_file.write_text(json.dumps({}))

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        token = manager.get_refresh_token()

        assert token is None

    def test_get_subscription_type_no_claudeAiOauth(self, tmp_path, monkeypatch):
        """Test get_subscription_type when claudeAiOauth key is missing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        creds_file.write_text(json.dumps({}))

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        sub_type = manager.get_subscription_type()

        assert sub_type is None

    def test_get_scopes_no_claudeAiOauth(self, tmp_path, monkeypatch):
        """Test get_scopes when claudeAiOauth key is missing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        creds_file.write_text(json.dumps({}))

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        scopes = manager.get_scopes()

        assert scopes == []

    def test_get_refresh_token_missing_value(self, tmp_path, monkeypatch):
        """Test get_refresh_token when refreshToken field is missing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "accessToken": "sk-ant-oat01-test",
                        "expiresAt": "2099-12-31T23:59:59Z",
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        token = manager.get_refresh_token()

        assert token is None

    def test_get_subscription_type_missing_value(self, tmp_path, monkeypatch):
        """Test get_subscription_type when subscriptionType field is missing."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "accessToken": "sk-ant-oat01-test",
                        "expiresAt": "2099-12-31T23:59:59Z",
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        sub_type = manager.get_subscription_type()

        assert sub_type is None

    def test_is_token_expired_type_error(self, tmp_path, monkeypatch, caplog):
        """Test is_token_expired handles TypeError in expiration checking (line 190)."""
        import logging

        caplog.set_level(logging.WARNING)

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        # Expiry as wrong type (list) that cannot be divided
        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "accessToken": "sk-ant-oat01-test",
                        "refreshToken": "refresh-token",
                        "expiresAt": [1, 2, 3],  # Wrong type - list cannot be divided by 1000
                        "subscriptionType": "max",
                        "scopes": ["user:inference"],
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()

        # Should handle TypeError gracefully and return True (expired)
        result = manager.is_token_expired()

        # Should treat error as expired
        assert result is True
        # Should log warning about error
        assert any("Error checking token expiration" in record.message for record in caplog.records)

    def test_is_token_expired_os_error(self, tmp_path, monkeypatch, caplog):
        """Test is_token_expired handles OSError in expiration checking (line 190)."""
        import logging

        caplog.set_level(logging.WARNING)

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        # Use an extremely large timestamp that will cause OSError on some systems
        # datetime.fromtimestamp raises OSError for timestamps out of valid range
        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "accessToken": "sk-ant-oat01-test",
                        "refreshToken": "refresh-token",
                        "expiresAt": 9999999999999999,  # Extremely large timestamp
                        "subscriptionType": "max",
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()

        # Should handle OSError/ValueError gracefully and return True (expired)
        result = manager.is_token_expired()

        # Should treat error as expired
        assert result is True
        # Should log warning about error
        assert any("Error checking token expiration" in record.message for record in caplog.records)

    def test_get_access_token_unusual_format_warning(self, tmp_path, monkeypatch, caplog):
        """Test warning when access token doesn't have expected format (line 216)."""
        import logging

        caplog.set_level(logging.WARNING)

        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        # Token with unusual format (not starting with sk-ant-oat)
        # Use future timestamp in milliseconds (year 2099)
        future_timestamp_ms = 4102444800000  # 2099-12-31 in milliseconds
        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "accessToken": "unusual-token-format-12345",
                        "refreshToken": "refresh-token",
                        "expiresAt": future_timestamp_ms,
                        "subscriptionType": "max",
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        token = manager.get_access_token()

        # Should return the token
        assert token == "unusual-token-format-12345"
        # Should log warning about unusual format
        assert any("Unexpected token format" in record.message for record in caplog.records)

    def test_get_access_token_missing_token_info(self, tmp_path, monkeypatch):
        """Test get_access_token when accessToken field is missing (line 222)."""
        claude_dir = tmp_path / ".claude"
        claude_dir.mkdir()
        creds_file = claude_dir / ".credentials.json"

        # Missing accessToken field
        creds_file.write_text(
            json.dumps(
                {
                    "claudeAiOauth": {
                        "refreshToken": "refresh-token",
                        "expiresAt": "2099-12-31T23:59:59Z",
                        "subscriptionType": "max",
                    }
                }
            )
        )

        monkeypatch.setattr("claude_oauth_auth.oauth_manager.Path.home", lambda: tmp_path)

        manager = OAuthTokenManager()
        token = manager.get_access_token()

        # Should return None when accessToken is missing
        assert token is None
