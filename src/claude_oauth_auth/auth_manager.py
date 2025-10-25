"""
Unified Authentication Manager for Anthropic Claude API

This module provides a comprehensive authentication discovery system that
supports multiple credential sources with intelligent fallback:
1. Explicit parameters (api_key or auth_token)
2. Environment variables (ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN)
3. OAuth tokens from Claude Code (~/.claude/.credentials.json)
4. Config files (~/.anthropic/config, ~/.anthropic/config.json, etc.)
5. Helpful error messages with setup instructions

The manager automatically detects the best available authentication method
and provides diagnostic information for troubleshooting.

Usage:
    >>> from claude_oauth_auth.auth_manager import UnifiedAuthManager
    >>> manager = UnifiedAuthManager()
    >>> credential, cred_type, source = manager.discover_credentials()
    >>> print(f"Using {cred_type} from {source}")

    >>> # Create Anthropic client
    >>> client = manager.create_anthropic_client()

    >>> # Get authentication status
    >>> status = manager.get_auth_status()
    >>> print(status['summary'])

Architecture:
    The Anthropic SDK supports TWO authentication methods:
    1. API Keys: Anthropic(api_key="sk-ant-api03-...")
    2. OAuth Tokens: Anthropic(auth_token="sk-ant-oat01-...")

    This manager discovers credentials and returns the appropriate type,
    which the SDK client uses to initialize the correct authentication mode.
"""

import configparser
import json
import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

# Import the OAuth manager
from .oauth_manager import get_token_manager


# Configure module logger
logger = logging.getLogger(__name__)


class AuthType(Enum):
    """Types of authentication credentials."""

    API_KEY = "api_key"
    OAUTH_TOKEN = "oauth_token"


class AuthSource(Enum):
    """Sources where credentials can be discovered."""

    EXPLICIT_API_KEY = "explicit_api_key_parameter"
    EXPLICIT_OAUTH = "explicit_auth_token_parameter"
    ENV_API_KEY = "ANTHROPIC_API_KEY_environment_variable"
    ENV_OAUTH = "ANTHROPIC_AUTH_TOKEN_environment_variable"
    CLAUDE_CODE_OAUTH = "claude_code_oauth_credentials"
    CONFIG_FILE = "config_file"
    NONE = "no_credentials_found"


@dataclass
class AuthCredentials:
    """
    Container for discovered authentication credentials.

    Attributes:
        credential: The API key or OAuth token
        auth_type: Type of credential (API_KEY or OAUTH_TOKEN)
        source: Where the credential was discovered
        metadata: Additional information about the credential
    """

    credential: str
    auth_type: AuthType
    source: AuthSource
    metadata: Dict[str, Any]

    def __repr__(self) -> str:
        """String representation with credential partially masked."""
        masked_cred = self.credential[:15] + "..." + self.credential[-4:]
        return (
            f"AuthCredentials("
            f"type={self.auth_type.value}, "
            f"source={self.source.value}, "
            f"credential={masked_cred})"
        )


class UnifiedAuthManager:
    """
    Manages authentication credential discovery and validation.

    This class implements a comprehensive authentication discovery system
    with intelligent fallback across multiple credential sources.

    Example:
        >>> manager = UnifiedAuthManager()
        >>>
        >>> # Discover credentials automatically
        >>> try:
        ...     creds = manager.discover_credentials()
        ...     print(f"Found {creds.auth_type.value} from {creds.source.value}")
        ... except ValueError as e:
        ...     print(f"Authentication setup required: {e}")
        >>>
        >>> # Create Anthropic client
        >>> client = manager.create_anthropic_client()
        >>>
        >>> # Check authentication status
        >>> status = manager.get_auth_status()
        >>> print(status['summary'])
    """

    def __init__(
        self, api_key: Optional[str] = None, auth_token: Optional[str] = None, verbose: bool = False
    ):
        """
        Initialize unified authentication manager.

        Args:
            api_key: Optional explicit API key (sk-ant-api03-...)
            auth_token: Optional explicit OAuth token (sk-ant-oat01-...)
            verbose: If True, log detailed authentication discovery info
        """
        self.explicit_api_key = api_key
        self.explicit_auth_token = auth_token
        self.verbose = verbose

        # Set logging level based on verbose flag
        if verbose:
            logger.setLevel(logging.DEBUG)

        # OAuth manager for Claude Code credentials
        self.oauth_manager = get_token_manager()

    def discover_credentials(self) -> AuthCredentials:
        """
        Discover authentication credentials using priority cascade.

        Priority order:
        1. Explicit auth_token parameter (OAuth)
        2. Explicit api_key parameter (API key)
        3. ANTHROPIC_AUTH_TOKEN environment variable (OAuth)
        4. ANTHROPIC_API_KEY environment variable (API key)
        5. Claude Code OAuth credentials (~/.claude/.credentials.json)
        6. Config files (~/.anthropic/config, etc.)

        Returns:
            AuthCredentials with discovered credential

        Raises:
            ValueError: If no credentials found in any source

        Example:
            >>> manager = UnifiedAuthManager()
            >>> creds = manager.discover_credentials()
            >>> if creds.auth_type == AuthType.OAUTH_TOKEN:
            ...     print("Using Claude Max subscription!")
        """
        # Priority 1: Explicit auth_token parameter (OAuth)
        if self.explicit_auth_token and self.explicit_auth_token.strip():
            if self.verbose:
                logger.info("Using explicit auth_token parameter")

            return AuthCredentials(
                credential=self.explicit_auth_token,
                auth_type=AuthType.OAUTH_TOKEN,
                source=AuthSource.EXPLICIT_OAUTH,
                metadata={"note": "Explicit OAuth token provided to constructor"},
            )

        # Priority 2: Explicit api_key parameter (API key)
        if self.explicit_api_key and self.explicit_api_key.strip():
            if self.verbose:
                logger.info("Using explicit api_key parameter")

            return AuthCredentials(
                credential=self.explicit_api_key,
                auth_type=AuthType.API_KEY,
                source=AuthSource.EXPLICIT_API_KEY,
                metadata={"note": "Explicit API key provided to constructor"},
            )

        # Priority 3: ANTHROPIC_AUTH_TOKEN environment variable (OAuth)
        env_oauth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")
        if env_oauth_token and env_oauth_token.strip():
            if self.verbose:
                logger.info("Using ANTHROPIC_AUTH_TOKEN environment variable")

            return AuthCredentials(
                credential=env_oauth_token,
                auth_type=AuthType.OAUTH_TOKEN,
                source=AuthSource.ENV_OAUTH,
                metadata={"note": "OAuth token from ANTHROPIC_AUTH_TOKEN env var"},
            )

        # Priority 4: ANTHROPIC_API_KEY environment variable (API key)
        env_api_key = os.getenv("ANTHROPIC_API_KEY")
        if env_api_key and env_api_key.strip():
            if self.verbose:
                logger.info("Using ANTHROPIC_API_KEY environment variable")

            return AuthCredentials(
                credential=env_api_key,
                auth_type=AuthType.API_KEY,
                source=AuthSource.ENV_API_KEY,
                metadata={"note": "API key from ANTHROPIC_API_KEY env var"},
            )

        # Priority 5: Claude Code OAuth credentials
        oauth_token = self.oauth_manager.get_access_token()
        if oauth_token:
            if self.verbose:
                oauth_info = self.oauth_manager.get_token_info()
                logger.info(
                    f"Using Claude Code OAuth credentials "
                    f"(subscription: {oauth_info.get('subscription_type')})"
                )

            return AuthCredentials(
                credential=oauth_token,
                auth_type=AuthType.OAUTH_TOKEN,
                source=AuthSource.CLAUDE_CODE_OAUTH,
                metadata=self.oauth_manager.get_token_info(),
            )

        # Priority 6: Config files
        config_cred = self._discover_from_config_files()
        if config_cred:
            if self.verbose:
                logger.info(f"Using credentials from {config_cred.metadata['file']}")
            return config_cred

        # No credentials found - provide helpful error
        raise ValueError(self._get_setup_instructions())

    def _discover_from_config_files(self) -> Optional[AuthCredentials]:
        """
        Discover credentials from config files.

        Searches multiple config file locations in order:
        1. ~/.anthropic/config (INI format)
        2. ~/.anthropic/config.json (JSON format)
        3. ~/.anthropic/api_key (plain text)
        4. ~/.config/anthropic/config (XDG config)
        5. ./config/credentials.yaml (project-local)
        6. ./.env (dotenv format)

        Returns:
            AuthCredentials if found, None otherwise
        """
        config_locations = [
            (Path.home() / ".anthropic" / "config", self._read_ini_config),
            (Path.home() / ".anthropic" / "config.json", self._read_json_config),
            (Path.home() / ".anthropic" / "api_key", self._read_plain_text_config),
            (Path.home() / ".config" / "anthropic" / "config", self._read_ini_config),
            (Path("config") / "credentials.yaml", self._read_yaml_config),
            (Path(".env"), self._read_env_file),
        ]

        for config_path, reader in config_locations:
            if config_path.exists():
                try:
                    credential = reader(config_path)
                    if credential:
                        # Determine if it's an API key or OAuth token
                        auth_type = (
                            AuthType.OAUTH_TOKEN
                            if credential.startswith("sk-ant-oat")
                            else AuthType.API_KEY
                        )

                        return AuthCredentials(
                            credential=credential,
                            auth_type=auth_type,
                            source=AuthSource.CONFIG_FILE,
                            metadata={"file": str(config_path), "format": reader.__name__},
                        )
                except Exception as e:
                    logger.debug(
                        f"Error reading config file: {config_path}\n"
                        f"Error: {e}\n"
                        f"This file will be skipped."
                    )

        return None

    def _read_ini_config(self, path: Path) -> Optional[str]:
        """Read API key from INI config file."""
        config = configparser.ConfigParser()
        config.read(path)

        # Try multiple key names
        for section in ["default", "anthropic", "DEFAULT"]:
            if section in config:
                for key in ["api_key", "auth_token", "key", "token"]:
                    if key in config[section]:
                        return config[section][key].strip()

        return None

    def _read_json_config(self, path: Path) -> Optional[str]:
        """Read API key from JSON config file."""
        with open(path) as f:
            data = json.load(f)

        # Try multiple key names
        for key in ["api_key", "auth_token", "key", "token", "ANTHROPIC_API_KEY"]:
            if key in data:
                value = data[key]
                # Type annotation: ensure we return Optional[str]
                if value is None or (isinstance(value, str) and not value.strip()):
                    continue
                return str(value).strip()

        return None

    def _read_plain_text_config(self, path: Path) -> Optional[str]:
        """Read API key from plain text file."""
        with open(path) as f:
            content = f.read().strip()

        # Return if it looks like a valid key
        if content.startswith("sk-ant-"):
            return content

        return None

    def _read_yaml_config(self, path: Path) -> Optional[str]:
        """Read API key from YAML config file (basic parsing)."""
        try:
            import yaml

            with open(path) as f:
                data = yaml.safe_load(f)

            for key in ["api_key", "auth_token", "ANTHROPIC_API_KEY"]:
                if key in data:
                    value = data[key]
                    # Type annotation: ensure we return Optional[str]
                    if value is None or (isinstance(value, str) and not value.strip()):
                        continue
                    return str(value).strip()
        except ImportError:
            # Fall back to simple parsing if PyYAML not available
            with open(path) as f:
                for line in f:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        if key.strip() in ["api_key", "auth_token"]:
                            stripped = value.strip().strip('"').strip("'")
                            if stripped:
                                return stripped

        return None

    def _read_env_file(self, path: Path) -> Optional[str]:
        """Read API key from .env file."""
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY=") or line.startswith(
                    "ANTHROPIC_AUTH_TOKEN="
                ):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")

        return None

    def _get_setup_instructions(self) -> str:
        """Get helpful setup instructions when no credentials are found."""
        return """
No Anthropic API credentials found. Please set up authentication using one of these methods:

METHOD 1: Claude Code OAuth (RECOMMENDED - Uses Claude Max subscription)
   What: Free API access if you have Claude Max/Pro subscription
   How:
     1. Install Claude Code: https://claude.com/claude-code
     2. Run 'claude' in terminal and log in
     3. Credentials saved to: ~/.claude/.credentials.json
   Status: Run 'python -m claude_oauth_auth status' to check

METHOD 2: API Key (Standard - Billed separately)
   What: Direct API access with per-token billing
   How:
     a) Get API key: https://console.anthropic.com/settings/keys
     b) Set environment variable:
        export ANTHROPIC_API_KEY="sk-ant-api03-..."
     c) Or create config file:
        mkdir -p ~/.anthropic
        echo 'sk-ant-api03-...' > ~/.anthropic/api_key
   Status: Check with 'echo $ANTHROPIC_API_KEY'

METHOD 3: Explicit Parameter (Quick testing)
   What: Pass credentials directly in code
   How:
     from claude_oauth_auth import ClaudeClient
     # With API key:
     client = ClaudeClient(api_key="sk-ant-api03-...")
     # Or with OAuth token:
     client = ClaudeClient(auth_token="sk-ant-oat01-...")

TROUBLESHOOTING:
   - Run diagnostics: python -m claude_oauth_auth diagnose
   - Check status: python -m claude_oauth_auth status
   - Documentation: https://github.com/astoreyai/claude-oauth-auth
   - Get help: https://github.com/astoreyai/claude-oauth-auth/issues
        """.strip()

    def is_oauth_available(self) -> bool:
        """
        Check if OAuth authentication is available.

        Returns:
            True if OAuth token can be discovered
        """
        if self.explicit_auth_token:
            return True

        if os.getenv("ANTHROPIC_AUTH_TOKEN"):
            return True

        return self.oauth_manager.is_oauth_available() and not self.oauth_manager.is_token_expired()

    def is_api_key_available(self) -> bool:
        """
        Check if API key authentication is available.

        Returns:
            True if API key can be discovered
        """
        if self.explicit_api_key:
            return True

        if os.getenv("ANTHROPIC_API_KEY"):
            return True

        # Check config files
        return self._discover_from_config_files() is not None

    def get_auth_status(self) -> Dict[str, Any]:
        """
        Get comprehensive authentication status for diagnostics.

        Returns:
            Dictionary with authentication status and available methods

        Example:
            >>> manager = UnifiedAuthManager(verbose=True)
            >>> status = manager.get_auth_status()
            >>> print(status['summary'])
            >>> for method in status['available_methods']:
            ...     print(f"  - {method}")
        """
        try:
            creds = self.discover_credentials()
            auth_type = creds.auth_type.value
            source = creds.source.value
            is_valid = True
            error = None
        except ValueError as e:
            auth_type = None
            source = None
            is_valid = False
            error = str(e)

        # Check what methods are available
        available_methods = []

        if self.explicit_api_key:
            available_methods.append("explicit_api_key")
        if self.explicit_auth_token:
            available_methods.append("explicit_auth_token")
        if os.getenv("ANTHROPIC_API_KEY"):
            available_methods.append("ANTHROPIC_API_KEY_env_var")
        if os.getenv("ANTHROPIC_AUTH_TOKEN"):
            available_methods.append("ANTHROPIC_AUTH_TOKEN_env_var")
        if self.oauth_manager.is_oauth_available():
            if self.oauth_manager.is_token_expired():
                available_methods.append("claude_code_oauth_EXPIRED")
            else:
                available_methods.append("claude_code_oauth")
        if self._discover_from_config_files():
            available_methods.append("config_file")

        # OAuth token info if available
        oauth_info = None
        if self.oauth_manager.is_oauth_available():
            oauth_info = self.oauth_manager.get_token_info()

        summary = (
            f"Authentication: {'Valid' if is_valid else 'No credentials found'}\n"
            f"Type: {auth_type or 'N/A'}\n"
            f"Source: {source or 'N/A'}\n"
            f"Available methods: {', '.join(available_methods) if available_methods else 'None'}"
        )

        return {
            "is_valid": is_valid,
            "auth_type": auth_type,
            "source": source,
            "available_methods": available_methods,
            "oauth_info": oauth_info,
            "error": error,
            "summary": summary,
        }

    def create_anthropic_client(self, **kwargs: Any) -> Any:
        """
        Create an Anthropic client with discovered credentials.

        This method discovers credentials and creates the appropriate
        Anthropic client (using api_key or auth_token parameter).

        Args:
            **kwargs: Additional arguments passed to Anthropic constructor
                     (model, temperature, max_tokens, etc.)

        Returns:
            Anthropic client instance

        Raises:
            ValueError: If no credentials can be discovered

        Example:
            >>> from claude_oauth_auth.auth_manager import UnifiedAuthManager
            >>> manager = UnifiedAuthManager()
            >>> client = manager.create_anthropic_client()
            >>> response = client.messages.create(
            ...     model="claude-sonnet-4-5-20250929",
            ...     max_tokens=1024,
            ...     messages=[{"role": "user", "content": "Hello!"}]
            ... )
        """
        from anthropic import Anthropic

        creds = self.discover_credentials()

        if self.verbose:
            logger.info(f"Creating Anthropic client with {creds.auth_type.value}")

        # Create client based on credential type
        if creds.auth_type == AuthType.OAUTH_TOKEN:
            return Anthropic(auth_token=creds.credential, **kwargs)
        else:  # API_KEY
            return Anthropic(api_key=creds.credential, **kwargs)


# Convenience functions for simple usage


def discover_credentials(
    api_key: Optional[str] = None, auth_token: Optional[str] = None
) -> AuthCredentials:
    """
    Convenience function to discover credentials.

    Args:
        api_key: Optional explicit API key
        auth_token: Optional explicit OAuth token

    Returns:
        AuthCredentials with discovered credential

    Example:
        >>> from claude_oauth_auth.auth_manager import discover_credentials
        >>> creds = discover_credentials()
        >>> print(f"Found {creds.auth_type.value} from {creds.source.value}")
    """
    manager = UnifiedAuthManager(api_key=api_key, auth_token=auth_token)
    return manager.discover_credentials()


def get_auth_status(
    api_key: Optional[str] = None, auth_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to get authentication status.

    Args:
        api_key: Optional explicit API key
        auth_token: Optional explicit OAuth token

    Returns:
        Dictionary with authentication status

    Example:
        >>> from claude_oauth_auth.auth_manager import get_auth_status
        >>> status = get_auth_status()
        >>> print(status['summary'])
    """
    manager = UnifiedAuthManager(api_key=api_key, auth_token=auth_token, verbose=True)
    return manager.get_auth_status()


def create_anthropic_client(**kwargs: Any) -> Any:
    """
    Convenience function to create Anthropic client with auto-discovery.

    Args:
        **kwargs: Arguments passed to Anthropic constructor

    Returns:
        Anthropic client instance

    Example:
        >>> from claude_oauth_auth.auth_manager import create_anthropic_client
        >>> client = create_anthropic_client()
        >>> response = client.messages.create(
        ...     model="claude-sonnet-4-5-20250929",
        ...     max_tokens=1024,
        ...     messages=[{"role": "user", "content": "Hello!"}]
        ... )
    """
    manager = UnifiedAuthManager()
    return manager.create_anthropic_client(**kwargs)
