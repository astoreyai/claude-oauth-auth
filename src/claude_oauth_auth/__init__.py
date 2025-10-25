"""
Claude OAuth Auth - Simplified Authentication for Anthropic Claude API

This package provides a unified authentication system for the Anthropic Claude API
with support for multiple credential sources including Claude Code OAuth tokens.

Features:
- OAuth token support from Claude Code credentials (~/.claude/.credentials.json)
- Automatic credential discovery from multiple sources
- Support for API keys and OAuth tokens
- Comprehensive authentication diagnostics
- Zero-configuration setup for Claude Code users

Quick Start:
    >>> from claude_oauth_auth import ClaudeClient
    >>>
    >>> # Automatic credential discovery
    >>> client = ClaudeClient()
    >>> response = client.generate("Hello, Claude!")
    >>> print(response)

    >>> # Check authentication status
    >>> from claude_oauth_auth import get_auth_status
    >>> status = get_auth_status()
    >>> print(status['summary'])

Public API:
    Client Classes:
        - ClaudeClient: Main client for Claude API with OAuth support
        - create_client: Convenience function to create a client

    Authentication Managers:
        - UnifiedAuthManager: Comprehensive authentication discovery
        - OAuthTokenManager: OAuth token management for Claude Code

    Authentication Discovery:
        - discover_credentials: Auto-discover credentials
        - get_auth_status: Get authentication diagnostics
        - create_anthropic_client: Create Anthropic SDK client
        - get_oauth_token: Get OAuth token from Claude Code
        - is_oauth_available: Check if OAuth is available

    Types and Enums:
        - AuthType: Enum for authentication types (API_KEY, OAUTH_TOKEN)
        - AuthSource: Enum for credential sources
        - AuthCredentials: Dataclass for discovered credentials

Version: 0.1.0
Author: Extracted from AI Scientist project
License: MIT
"""

__version__ = "0.1.0"
__author__ = "AI Scientist Team"
__license__ = "MIT"

# Import main client
# Import authentication manager
from .auth_manager import (
    AuthCredentials,
    AuthSource,
    AuthType,
    UnifiedAuthManager,
    create_anthropic_client,
    discover_credentials,
    get_auth_status,
)
from .client import ClaudeClient, create_client

# Import OAuth manager
from .oauth_manager import (
    OAuthTokenManager,
    get_oauth_info,
    get_oauth_token,
    get_token_manager,
    is_oauth_available,
)

# Import debug utilities
from .debug import (
    diagnose,
    export_diagnostics,
    get_diagnostics,
)

# Import validation utilities
from .validate import (
    validate_api_key,
    validate_oauth_token,
    validate_credential,
    is_token_expired,
    get_validation_hints,
)


# Define public API
__all__ = [
    "AuthCredentials",
    "AuthSource",
    "AuthType",
    # Main client
    "ClaudeClient",
    # OAuth manager
    "OAuthTokenManager",
    # Authentication manager
    "UnifiedAuthManager",
    "__author__",
    "__license__",
    # Version info
    "__version__",
    "create_anthropic_client",
    "create_client",
    # Debug utilities
    "diagnose",
    "discover_credentials",
    "export_diagnostics",
    "get_auth_status",
    "get_diagnostics",
    "get_oauth_info",
    "get_oauth_token",
    "get_token_manager",
    "get_validation_hints",
    "is_oauth_available",
    "is_token_expired",
    "validate_api_key",
    "validate_credential",
    "validate_oauth_token",
]


# Package-level convenience functions
def get_version() -> str:
    """Get the package version."""
    return __version__


def get_package_info() -> dict:
    """
    Get comprehensive package information.

    Returns:
        Dictionary with package metadata

    Example:
        >>> from claude_oauth_auth import get_package_info
        >>> info = get_package_info()
        >>> print(f"Version: {info['version']}")
        >>> print(f"Features: {', '.join(info['features'])}")
    """
    return {
        "name": "claude-oauth-auth",
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "description": "Simplified authentication for Anthropic Claude API with OAuth support",
        "features": [
            "OAuth token support from Claude Code",
            "Automatic credential discovery",
            "Support for API keys and OAuth tokens",
            "Comprehensive authentication diagnostics",
            "Zero-configuration setup",
            "Enhanced error messages with actionable fixes",
            "Built-in validation utilities",
            "Command-line diagnostic tools",
            "Troubleshooting script for support",
        ],
        "public_api": __all__,
    }


# Add to public API
__all__.extend(["get_package_info", "get_version"])
