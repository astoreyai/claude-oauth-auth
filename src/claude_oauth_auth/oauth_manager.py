"""
OAuth Token Manager for Claude Code Integration

This module provides OAuth token extraction and management for Claude Code's
OAuth credentials stored in ~/.claude/.credentials.json. It enables the
Anthropic Python SDK to use Claude Max subscription instead of API credits.

Key Features:
- Extract OAuth access tokens from Claude Code credentials
- Validate token expiration
- Thread-safe token caching
- Clean API for integration with authentication systems

Usage:
    >>> from claude_oauth_auth.oauth_manager import get_oauth_token
    >>> token = get_oauth_token()
    >>> if token:
    ...     client = Anthropic(auth_token=token)

    >>> # Advanced usage
    >>> from claude_oauth_auth.oauth_manager import OAuthTokenManager
    >>> manager = OAuthTokenManager()
    >>> if not manager.is_token_expired():
    ...     token = manager.get_access_token()
    ...     info = manager.get_token_info()
    ...     print(f"Token expires: {info['expires_at']}")

Architecture:
    This module implements the OAuth token discovery from Claude Code's
    credential storage. It does NOT add "Bearer " prefix - the Anthropic
    SDK automatically handles that when using the auth_token parameter.

    Token Format:
    - OAuth tokens start with: sk-ant-oat01-
    - NOT to be confused with API keys: sk-ant-api03-

    Credential File Structure:
    {
      "claudeAiOauth": {
        "accessToken": "sk-ant-oat01-...",
        "refreshToken": "sk-ant-ort01-...",
        "expiresAt": 1761378353784,
        "scopes": ["user:inference", "user:profile"],
        "subscriptionType": "max"
      }
    }
"""

import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


# Configure module logger
logger = logging.getLogger(__name__)


class OAuthTokenManager:
    """
    Manages OAuth tokens from Claude Code's credential storage.

    This class provides thread-safe access to Claude Code OAuth tokens,
    including validation, expiration checking, and metadata access.

    The manager implements lazy loading and caching to avoid repeated
    file system access, while ensuring thread safety for concurrent usage.

    Attributes:
        credentials_path: Path to Claude Code credentials file

    Example:
        >>> manager = OAuthTokenManager()
        >>> if manager.is_oauth_available():
        ...     token = manager.get_access_token()
        ...     print(f"Token type: {manager.get_subscription_type()}")
    """

    def __init__(self, credentials_path: Optional[Path] = None):
        """
        Initialize OAuth token manager.

        Args:
            credentials_path: Optional path to credentials file.
                            Defaults to ~/.claude/.credentials.json
        """
        if credentials_path is None:
            credentials_path = Path.home() / ".claude" / ".credentials.json"

        self.credentials_path = Path(credentials_path)
        self._credentials: Optional[Dict[str, Any]] = None
        self._lock = threading.Lock()
        self._last_load_time: Optional[float] = None

    def _load_credentials(self, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """
        Load credentials from file with caching.

        Args:
            force_reload: If True, bypass cache and reload from file

        Returns:
            Credentials dictionary or None if file doesn't exist or is invalid
        """
        with self._lock:
            # Return cached credentials if available and not forcing reload
            if self._credentials is not None and not force_reload:
                return self._credentials

            # Check if credentials file exists
            if not self.credentials_path.exists():
                logger.warning(
                    f"Claude Code credentials not found at: {self.credentials_path}\n"
                    f"To fix this:\n"
                    f"  1. Install Claude Code from https://claude.com/claude-code\n"
                    f"  2. Run 'claude' in your terminal and log in\n"
                    f"  3. Verify the credentials file is created"
                )
                return None

            try:
                # Read and parse credentials file
                with open(self.credentials_path) as f:
                    data = json.load(f)

                # Validate structure
                if "claudeAiOauth" not in data:
                    logger.warning(
                        f"Invalid Claude Code credentials format: missing 'claudeAiOauth' key\n"
                        f"File: {self.credentials_path}\n"
                        f"Expected structure: {{'claudeAiOauth': {{'accessToken': '...', ...}}}}\n"
                        f"To fix this:\n"
                        f"  1. Run 'claude' in your terminal\n"
                        f"  2. Log in with your Claude account\n"
                        f"  3. This will refresh your credentials"
                    )
                    return None

                # Cache credentials
                self._credentials = data
                self._last_load_time = datetime.now().timestamp()

                logger.debug(f"Loaded OAuth credentials from {self.credentials_path}")

                return self._credentials

            except json.JSONDecodeError as e:
                logger.error(
                    f"Failed to parse credentials file: {self.credentials_path}\n"
                    f"Error: {e}\n"
                    f"The file may be corrupted. To fix:\n"
                    f"  1. Backup the current file: mv {self.credentials_path} {self.credentials_path}.bak\n"
                    f"  2. Run 'claude' and log in again\n"
                    f"  3. This will create a fresh credentials file"
                )
                return None
            except PermissionError as e:
                logger.error(
                    f"Permission denied reading credentials file: {self.credentials_path}\n"
                    f"Error: {e}\n"
                    f"To fix:\n"
                    f"  1. Check file permissions: ls -l {self.credentials_path}\n"
                    f"  2. Fix permissions: chmod 600 {self.credentials_path}\n"
                    f"  3. Or re-run 'claude' to regenerate the file"
                )
                return None
            except Exception as e:
                logger.error(
                    f"Unexpected error loading credentials from {self.credentials_path}\n"
                    f"Error: {e}\n"
                    f"For help, run: python -m claude_oauth_auth diagnose"
                )
                return None

    def is_oauth_available(self) -> bool:
        """
        Check if OAuth credentials are available.

        Returns:
            True if credentials file exists and is valid
        """
        credentials = self._load_credentials()
        return credentials is not None and "claudeAiOauth" in credentials

    def is_token_expired(self) -> bool:
        """
        Check if the OAuth token is expired.

        Returns:
            True if token is expired or unavailable, False if valid
        """
        credentials = self._load_credentials()
        if not credentials or "claudeAiOauth" not in credentials:
            return True

        oauth_data = credentials["claudeAiOauth"]

        # Get expiration timestamp (in milliseconds)
        expires_at_ms = oauth_data.get("expiresAt")
        if expires_at_ms is None:
            logger.warning(
                "OAuth token missing expiration timestamp\n"
                "This may indicate corrupted credentials. To fix:\n"
                "  1. Run 'claude' and log in again\n"
                "  2. This will refresh your OAuth token with proper expiration"
            )
            return True

        try:
            # Convert to seconds and compare with current time
            # Handle both int and string timestamps
            if isinstance(expires_at_ms, str):
                try:
                    expires_at_ms = int(expires_at_ms)
                except (ValueError, TypeError):
                    logger.warning(f"Invalid expiration timestamp format: {expires_at_ms}")
                    return True

            expires_at = datetime.fromtimestamp(expires_at_ms / 1000)
            now = datetime.now()

            is_expired = now >= expires_at

            if is_expired:
                time_ago = now - expires_at
                logger.warning(
                    f"OAuth token expired {time_ago} ago (expired at: {expires_at})\n"
                    f"To fix this:\n"
                    f"  1. Run 'claude' in your terminal\n"
                    f"  2. Log in with your Claude account\n"
                    f"  3. Your token will be automatically refreshed\n"
                    f"  4. Then try your request again"
                )

            return is_expired
        except (TypeError, ValueError, OSError) as e:
            logger.warning(
                f"Error checking token expiration: {e}\n"
                f"This may indicate an invalid timestamp format.\n"
                f"To fix: Run 'claude' and log in to refresh credentials"
            )
            return True

    def get_access_token(self) -> Optional[str]:
        """
        Get the OAuth access token.

        Returns the raw access token WITHOUT "Bearer " prefix.
        The Anthropic SDK adds the prefix automatically when using
        the auth_token parameter.

        Returns:
            Access token string (sk-ant-oat01-...) or None if unavailable/expired

        Example:
            >>> manager = OAuthTokenManager()
            >>> token = manager.get_access_token()
            >>> if token:
            ...     client = Anthropic(auth_token=token)  # SDK adds "Bearer "
        """
        if self.is_token_expired():
            return None

        credentials = self._load_credentials()
        if not credentials or "claudeAiOauth" not in credentials:
            return None

        oauth_data = credentials["claudeAiOauth"]
        access_token = oauth_data.get("accessToken")

        if access_token and not access_token.startswith("sk-ant-oat"):
            logger.warning(
                f"Unexpected token format: {access_token[:15]}...\n"
                f"Expected format: sk-ant-oat01-...\n"
                f"This may indicate corrupted credentials. To fix:\n"
                f"  1. Run 'claude' and log in again\n"
                f"  2. This will refresh your OAuth token"
            )

        # Type annotation: ensure we return Optional[str]
        return str(access_token) if access_token else None

    def get_refresh_token(self) -> Optional[str]:
        """
        Get the OAuth refresh token.

        Returns:
            Refresh token string or None if unavailable
        """
        credentials = self._load_credentials()
        if not credentials or "claudeAiOauth" not in credentials:
            return None

        refresh_token = credentials["claudeAiOauth"].get("refreshToken")
        return str(refresh_token) if refresh_token else None

    def get_subscription_type(self) -> Optional[str]:
        """
        Get the Claude subscription type.

        Returns:
            Subscription type (e.g., "max", "pro") or None
        """
        credentials = self._load_credentials()
        if not credentials or "claudeAiOauth" not in credentials:
            return None

        subscription_type = credentials["claudeAiOauth"].get("subscriptionType")
        return str(subscription_type) if subscription_type else None

    def get_scopes(self) -> list[str]:
        """
        Get the OAuth scopes.

        Returns:
            List of scope strings (e.g., ["user:inference", "user:profile"])
        """
        credentials = self._load_credentials()
        if not credentials or "claudeAiOauth" not in credentials:
            return []

        scopes = credentials["claudeAiOauth"].get("scopes", [])
        # Type annotation: ensure we return list[str]
        return list(scopes) if isinstance(scopes, list) else []

    def get_token_info(self) -> Dict[str, Any]:
        """
        Get comprehensive token information.

        Returns:
            Dictionary with token metadata including expiration, scopes, etc.

        Example:
            >>> manager = OAuthTokenManager()
            >>> info = manager.get_token_info()
            >>> print(f"Expires: {info['expires_at']}")
            >>> print(f"Subscription: {info['subscription_type']}")
            >>> print(f"Valid: {info['is_valid']}")
        """
        credentials = self._load_credentials()

        if not credentials or "claudeAiOauth" not in credentials:
            return {"available": False, "is_valid": False, "error": "Credentials not available"}

        oauth_data = credentials["claudeAiOauth"]
        expires_at_ms = oauth_data.get("expiresAt", 0)
        expires_at = datetime.fromtimestamp(expires_at_ms / 1000)

        return {
            "available": True,
            "is_valid": not self.is_token_expired(),
            "expires_at": expires_at.isoformat(),
            "subscription_type": oauth_data.get("subscriptionType"),
            "scopes": oauth_data.get("scopes", []),
            "token_prefix": oauth_data.get("accessToken", "")[:15] + "...",
            "credentials_path": str(self.credentials_path),
        }

    def reload(self) -> bool:
        """
        Force reload credentials from file.

        Useful if credentials were refreshed externally.

        Returns:
            True if reload succeeded, False otherwise
        """
        credentials = self._load_credentials(force_reload=True)
        return credentials is not None


# Module-level singleton instance for convenient access
_default_manager: Optional[OAuthTokenManager] = None
_manager_lock = threading.Lock()


def get_token_manager() -> OAuthTokenManager:
    """
    Get the module-level OAuth token manager singleton.

    This provides a convenient way to access OAuth tokens without
    creating multiple manager instances.

    Returns:
        OAuthTokenManager instance

    Example:
        >>> from claude_oauth_auth.oauth_manager import get_token_manager
        >>> manager = get_token_manager()
        >>> token = manager.get_access_token()
    """
    global _default_manager

    with _manager_lock:
        if _default_manager is None:
            _default_manager = OAuthTokenManager()
        return _default_manager


def get_oauth_token() -> Optional[str]:
    """
    Convenience function to get OAuth access token.

    This is the simplest way to get a Claude Code OAuth token for use
    with the Anthropic SDK.

    Returns:
        OAuth access token or None if unavailable/expired

    Example:
        >>> from claude_oauth_auth.oauth_manager import get_oauth_token
        >>> from anthropic import Anthropic
        >>>
        >>> token = get_oauth_token()
        >>> if token:
        ...     client = Anthropic(auth_token=token)
        ...     response = client.messages.create(
        ...         model="claude-sonnet-4-5-20250929",
        ...         max_tokens=1024,
        ...         messages=[{"role": "user", "content": "Hello!"}]
        ...     )
    """
    manager = get_token_manager()
    return manager.get_access_token()


def is_oauth_available() -> bool:
    """
    Check if OAuth credentials are available.

    Returns:
        True if Claude Code OAuth credentials exist and are valid

    Example:
        >>> from claude_oauth_auth.oauth_manager import is_oauth_available
        >>> if is_oauth_available():
        ...     print("Can use Claude Max subscription!")
        ... else:
        ...     print("Need to set up API key")
    """
    manager = get_token_manager()
    return manager.is_oauth_available() and not manager.is_token_expired()


def get_oauth_info() -> Dict[str, Any]:
    """
    Get OAuth token information for diagnostics.

    Returns:
        Dictionary with OAuth token metadata

    Example:
        >>> from claude_oauth_auth.oauth_manager import get_oauth_info
        >>> info = get_oauth_info()
        >>> if info['is_valid']:
        ...     print(f"Using {info['subscription_type']} subscription")
        ...     print(f"Token expires: {info['expires_at']}")
    """
    manager = get_token_manager()
    return manager.get_token_info()
