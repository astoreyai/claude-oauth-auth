"""
Validation utilities for Claude OAuth authentication.

This module provides validation functions for API keys, OAuth tokens,
and credentials to help users diagnose authentication issues.

Usage:
    >>> from claude_oauth_auth.validate import validate_api_key, validate_oauth_token
    >>>
    >>> # Validate API key format
    >>> is_valid, message = validate_api_key("sk-ant-api03-...")
    >>> print(f"Valid: {is_valid}, Message: {message}")
    >>>
    >>> # Validate OAuth token format
    >>> is_valid, message = validate_oauth_token("sk-ant-oat01-...")
    >>> print(f"Valid: {is_valid}, Message: {message}")
"""

import logging
import re
from datetime import datetime
from typing import Optional, Tuple

from .oauth_manager import OAuthTokenManager


logger = logging.getLogger(__name__)


# Regex patterns for credential validation
API_KEY_PATTERN = re.compile(r"^sk-ant-api03-[A-Za-z0-9_-]{95}$")
OAUTH_TOKEN_PATTERN = re.compile(r"^sk-ant-oat01-[A-Za-z0-9_-]{95}$")
REFRESH_TOKEN_PATTERN = re.compile(r"^sk-ant-ort01-[A-Za-z0-9_-]{95}$")


def validate_api_key(key: str) -> Tuple[bool, str]:
    """
    Validate the format of an Anthropic API key.

    API keys should start with 'sk-ant-api03-' followed by 95 characters.

    Args:
        key: The API key string to validate

    Returns:
        Tuple of (is_valid, message):
        - is_valid: True if the key format is valid
        - message: Explanation of validation result

    Example:
        >>> from claude_oauth_auth.validate import validate_api_key
        >>> is_valid, msg = validate_api_key("sk-ant-api03-...")
        >>> if not is_valid:
        ...     print(f"Invalid API key: {msg}")
    """
    if not key:
        return False, "API key is empty or None"

    if not isinstance(key, str):
        return False, f"API key must be a string, got {type(key).__name__}"

    if not key.startswith("sk-ant-api03-"):
        return False, (
            "API key must start with 'sk-ant-api03-'. "
            "Found: '{}'... "
            "Did you mean to use an OAuth token? "
            "OAuth tokens start with 'sk-ant-oat01-'"
        ).format(key[:20])

    if len(key) != 108:  # sk-ant-api03- (13) + 95 chars
        return False, (
            f"API key has incorrect length: {len(key)} characters. "
            f"Expected 108 characters (sk-ant-api03- + 95 chars). "
            f"Please check your key from https://console.anthropic.com/settings/keys"
        )

    if not API_KEY_PATTERN.match(key):
        return False, (
            "API key contains invalid characters. "
            "Only alphanumeric, underscore, and hyphen are allowed. "
            "Please copy the key again from https://console.anthropic.com/settings/keys"
        )

    return True, "API key format is valid"


def validate_oauth_token(token: str) -> Tuple[bool, str]:
    """
    Validate the format of an OAuth access token.

    OAuth tokens should start with 'sk-ant-oat01-' followed by 95 characters.

    Args:
        token: The OAuth token string to validate

    Returns:
        Tuple of (is_valid, message):
        - is_valid: True if the token format is valid
        - message: Explanation of validation result

    Example:
        >>> from claude_oauth_auth.validate import validate_oauth_token
        >>> is_valid, msg = validate_oauth_token("sk-ant-oat01-...")
        >>> if not is_valid:
        ...     print(f"Invalid OAuth token: {msg}")
    """
    if not token:
        return False, "OAuth token is empty or None"

    if not isinstance(token, str):
        return False, f"OAuth token must be a string, got {type(token).__name__}"

    if not token.startswith("sk-ant-oat01-"):
        return False, (
            "OAuth token must start with 'sk-ant-oat01-'. "
            "Found: '{}'... "
            "Did you mean to use an API key? "
            "API keys start with 'sk-ant-api03-'"
        ).format(token[:20])

    if len(token) != 108:  # sk-ant-oat01- (13) + 95 chars
        return False, (
            f"OAuth token has incorrect length: {len(token)} characters. "
            f"Expected 108 characters (sk-ant-oat01- + 95 chars). "
            f"Please check your Claude Code credentials."
        )

    if not OAUTH_TOKEN_PATTERN.match(token):
        return False, (
            "OAuth token contains invalid characters. "
            "Only alphanumeric, underscore, and hyphen are allowed. "
            "Please re-authenticate with Claude Code."
        )

    return True, "OAuth token format is valid"


def validate_refresh_token(token: str) -> Tuple[bool, str]:
    """
    Validate the format of an OAuth refresh token.

    Refresh tokens should start with 'sk-ant-ort01-' followed by 95 characters.

    Args:
        token: The refresh token string to validate

    Returns:
        Tuple of (is_valid, message):
        - is_valid: True if the token format is valid
        - message: Explanation of validation result
    """
    if not token:
        return False, "Refresh token is empty or None"

    if not isinstance(token, str):
        return False, f"Refresh token must be a string, got {type(token).__name__}"

    if not token.startswith("sk-ant-ort01-"):
        return False, f"Refresh token must start with 'sk-ant-ort01-'. Found: {token[:20]}..."

    if len(token) != 108:
        return False, (
            f"Refresh token has incorrect length: {len(token)} characters. "
            f"Expected 108 characters."
        )

    if not REFRESH_TOKEN_PATTERN.match(token):
        return False, "Refresh token contains invalid characters"

    return True, "Refresh token format is valid"


def is_token_expired(
    token_manager: Optional[OAuthTokenManager] = None,
    credentials_path: Optional[str] = None
) -> Tuple[bool, Optional[str], Optional[datetime]]:
    """
    Check if OAuth token is expired.

    Args:
        token_manager: Optional OAuthTokenManager instance
        credentials_path: Optional path to credentials file

    Returns:
        Tuple of (is_expired, error_message, expiration_time):
        - is_expired: True if token is expired or unavailable
        - error_message: Error message if token check failed, None otherwise
        - expiration_time: When the token expires (if available)

    Example:
        >>> from claude_oauth_auth.validate import is_token_expired
        >>> expired, error, expires_at = is_token_expired()
        >>> if expired:
        ...     print(f"Token expired: {error}")
        >>> else:
        ...     print(f"Token valid until: {expires_at}")
    """
    if token_manager is None:
        from .oauth_manager import get_token_manager
        token_manager = get_token_manager()

    try:
        info = token_manager.get_token_info()

        if not info.get("available"):
            return True, info.get("error", "Token not available"), None

        is_expired = not info.get("is_valid", False)

        if is_expired:
            expires_at_str = info.get("expires_at")
            if expires_at_str:
                try:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    now = datetime.now()
                    time_ago = now - expires_at
                    return True, f"Token expired {time_ago} ago", expires_at
                except (ValueError, TypeError):
                    return True, "Token expired (could not parse expiration time)", None
            return True, "Token expired", None

        # Token is valid
        expires_at_str = info.get("expires_at")
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                return False, None, expires_at
            except (ValueError, TypeError):
                return False, None, None

        return False, None, None

    except Exception as e:
        logger.error(f"Error checking token expiration: {e}")
        return True, f"Error checking token expiration: {e}", None


def validate_credential(credential: str) -> Tuple[bool, str, Optional[str]]:
    """
    Validate any type of credential (API key or OAuth token).

    Automatically detects the credential type and validates accordingly.

    Args:
        credential: The credential string to validate

    Returns:
        Tuple of (is_valid, message, credential_type):
        - is_valid: True if the credential format is valid
        - message: Explanation of validation result
        - credential_type: "api_key", "oauth_token", or None if invalid

    Example:
        >>> from claude_oauth_auth.validate import validate_credential
        >>> is_valid, msg, cred_type = validate_credential("sk-ant-...")
        >>> print(f"Type: {cred_type}, Valid: {is_valid}, Message: {msg}")
    """
    if not credential:
        return False, "Credential is empty or None", None

    if not isinstance(credential, str):
        return False, f"Credential must be a string, got {type(credential).__name__}", None

    # Check if it's an API key
    if credential.startswith("sk-ant-api03-"):
        is_valid, message = validate_api_key(credential)
        return is_valid, message, "api_key" if is_valid else None

    # Check if it's an OAuth token
    if credential.startswith("sk-ant-oat01-"):
        is_valid, message = validate_oauth_token(credential)
        return is_valid, message, "oauth_token" if is_valid else None

    # Unknown credential type
    return False, (
        f"Unknown credential type. Found prefix: {credential[:20]}... "
        f"Expected 'sk-ant-api03-' (API key) or 'sk-ant-oat01-' (OAuth token). "
        f"See https://console.anthropic.com/settings/keys for API keys or "
        f"install Claude Code for OAuth tokens."
    ), None


def get_validation_hints(credential: str) -> str:
    """
    Get helpful hints for fixing invalid credentials.

    Args:
        credential: The credential to analyze

    Returns:
        String with helpful hints for fixing the credential

    Example:
        >>> from claude_oauth_auth.validate import get_validation_hints
        >>> hints = get_validation_hints("sk-ant-wrong-...")
        >>> print(hints)
    """
    if not credential:
        return (
            "No credential provided. To fix:\n"
            "1. Get an API key from https://console.anthropic.com/settings/keys\n"
            "2. Set environment variable: export ANTHROPIC_API_KEY='sk-ant-api03-...'\n"
            "3. Or install Claude Code for OAuth: https://claude.com/claude-code\n"
            "4. Or pass explicitly: ClaudeClient(api_key='sk-ant-api03-...')"
        )

    hints = []

    # Check for common mistakes
    if credential.startswith("Bearer "):
        hints.append(
            "Remove 'Bearer ' prefix - the SDK adds it automatically. "
            "Use just: 'sk-ant-...'"
        )

    if credential.startswith("sk-ant-") and not credential.startswith(("sk-ant-api03-", "sk-ant-oat01-")):
        hints.append(
            f"Unknown Anthropic credential prefix: {credential[:15]}... "
            f"Valid prefixes: 'sk-ant-api03-' (API key) or 'sk-ant-oat01-' (OAuth token)"
        )

    if len(credential) < 50:
        hints.append(
            f"Credential is too short ({len(credential)} chars). "
            f"Valid credentials are 108 characters. "
            f"Please copy the complete key from Anthropic Console."
        )

    if " " in credential or "\n" in credential or "\t" in credential:
        hints.append(
            "Credential contains whitespace. "
            "Remove all spaces, newlines, and tabs."
        )

    if not hints:
        hints.append(
            "Credential format is invalid. "
            "Please get a new key from https://console.anthropic.com/settings/keys "
            "or authenticate with Claude Code."
        )

    return "\n".join(f"  - {hint}" for hint in hints)
