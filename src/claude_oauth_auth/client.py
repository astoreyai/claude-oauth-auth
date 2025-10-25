"""
Claude Client with OAuth Support

This module provides an enhanced Claude SDK client that adds comprehensive
authentication support including Claude Code OAuth tokens, while maintaining
100% backward compatibility with existing code.

Key Features:
- OAuth token support from Claude Code credentials
- Automatic authentication discovery (API keys, OAuth, config files)
- Detailed authentication diagnostics
- Verbose mode for debugging
- Support for both api_key AND auth_token parameters

Usage:
    >>> from claude_oauth_auth import ClaudeClient
    >>>
    >>> # Auto-discover credentials (API key, OAuth, or config file)
    >>> client = ClaudeClient()
    >>>
    >>> # Generate text
    >>> response = client.generate("Explain Python decorators")
    >>> print(response)
    >>>
    >>> # Check which auth method was used
    >>> info = client.get_auth_info()
    >>> print(f"Using: {info['auth_type']} from {info['source']}")

Architecture:
    This client uses UnifiedAuthManager for credential discovery, which
    implements a cascading fallback across multiple authentication sources:

    Priority Order:
    1. Explicit auth_token parameter (OAuth)
    2. Explicit api_key parameter (API key)
    3. ANTHROPIC_AUTH_TOKEN environment variable (OAuth)
    4. ANTHROPIC_API_KEY environment variable (API key)
    5. Claude Code OAuth credentials (~/.claude/.credentials.json)
    6. Config files (~/.anthropic/config, etc.)

    The client then creates the appropriate Anthropic SDK instance:
    - Anthropic(auth_token=...) for OAuth tokens (Claude Max)
    - Anthropic(api_key=...) for API keys (standard billing)
"""

import logging
from typing import Any, Dict, Optional

from anthropic import Anthropic

from .auth_manager import AuthCredentials, AuthType, UnifiedAuthManager


# Configure module logger
logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Enhanced LLM client that uses Claude API via Anthropic SDK with OAuth support.

    This client provides comprehensive authentication support including OAuth tokens
    from Claude Code, with automatic credential discovery.

    Features:
    - Automatic credential discovery (OAuth, API keys, config files)
    - Support for Claude Max subscription (via OAuth)
    - Support for API key billing (via API keys)
    - Verbose mode for debugging authentication
    - Authentication diagnostics

    Example:
        >>> # Simple usage (auto-discovers credentials)
        >>> client = ClaudeClient()
        >>> response = client.generate("Hello, Claude!")
        >>> print(response)
        >>>
        >>> # Explicit API key
        >>> client = ClaudeClient(api_key="sk-ant-api03-...")
        >>>
        >>> # Explicit OAuth token (Claude Max)
        >>> client = ClaudeClient(auth_token="sk-ant-oat01-...")
        >>>
        >>> # Verbose mode (shows auth source)
        >>> client = ClaudeClient(verbose=True)
        >>> # Output: "Using oauth_token from claude_code_oauth_credentials"
        >>>
        >>> # Check auth info
        >>> info = client.get_auth_info()
        >>> print(f"Auth: {info['auth_type']} from {info['source']}")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        auth_token: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        verbose: bool = False,
    ):
        """
        Initialize Claude client with enhanced authentication.

        Args:
            api_key: Optional Anthropic API key (sk-ant-api03-...)
                    If provided, takes priority over other auth methods.
                    If None, auto-discovers from environment or Claude Code.

            auth_token: Optional OAuth token (sk-ant-oat01-...)
                       For Claude Max subscription authentication.
                       Takes highest priority if provided.

            model: Claude model to use. Defaults to claude-sonnet-4-5-20250929
                   for optimal research and reasoning performance.

            temperature: Sampling temperature (0-1). Higher = more creative.
                        Default 0.7 balances creativity with coherence.

            max_tokens: Maximum tokens to generate per response.
                       Default 4096 for substantive research outputs.

            verbose: If True, logs authentication discovery details.
                    Useful for debugging credential issues.

        Raises:
            ValueError: If no credentials can be discovered from any source.

        Example:
            >>> # Auto-discovery (tries OAuth, then API key, then config)
            >>> client = ClaudeClient()
            >>>
            >>> # Explicit API key
            >>> client = ClaudeClient(api_key="sk-ant-api03-...")
            >>>
            >>> # Explicit OAuth token (Claude Max)
            >>> client = ClaudeClient(auth_token="sk-ant-oat01-...")
            >>>
            >>> # Debug authentication
            >>> client = ClaudeClient(verbose=True)
        """
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.verbose = verbose

        # Create authentication manager
        self.auth_manager = UnifiedAuthManager(
            api_key=api_key, auth_token=auth_token, verbose=verbose
        )

        # Discover credentials using unified manager
        try:
            self.credentials: AuthCredentials = self.auth_manager.discover_credentials()

            if verbose:
                logger.info(
                    f"Discovered {self.credentials.auth_type.value} "
                    f"from {self.credentials.source.value}"
                )

        except ValueError as e:
            error_msg = (
                f"❌ Authentication Setup Required\n\n"
                f"{e!s}\n\n"
                f"Quick Fix:\n"
                f"  1. Check current status: python -m claude_oauth_auth status\n"
                f"  2. Run diagnostics: python -m claude_oauth_auth diagnose\n"
                f"  3. See troubleshooting: python scripts/troubleshoot.py\n"
            )
            raise ValueError(error_msg) from e

        # Create Anthropic client based on credential type
        self.client = self._create_anthropic_client()

        if verbose:
            logger.info(f"Initialized ClaudeClient with {self.model}")

    def _create_anthropic_client(self) -> Anthropic:
        """
        Create Anthropic SDK client with appropriate authentication.

        The Anthropic SDK supports two authentication methods:
        - api_key parameter for API keys (sk-ant-api03-...)
        - auth_token parameter for OAuth tokens (sk-ant-oat01-...)

        Returns:
            Configured Anthropic client instance
        """
        if self.credentials.auth_type == AuthType.OAUTH_TOKEN:
            # Use OAuth token (Claude Max subscription)
            if self.verbose:
                logger.info("Creating Anthropic client with OAuth authentication")
            return Anthropic(auth_token=self.credentials.credential)
        else:
            # Use API key (standard billing)
            if self.verbose:
                logger.info("Creating Anthropic client with API key authentication")
            return Anthropic(api_key=self.credentials.credential)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        """
        Generate text using Claude API.

        Args:
            prompt: The prompt to send to Claude

            **kwargs: Optional overrides:
                - temperature: Override default temperature
                - max_tokens: Override default max_tokens
                - model: Override default model
                - system: System prompt (optional)

        Returns:
            Generated text as string

        Raises:
            RuntimeError: If the Claude API call fails

        Example:
            >>> client = ClaudeClient()
            >>>
            >>> # Simple generation
            >>> response = client.generate("Explain quantum computing")
            >>> print(response)
            >>>
            >>> # With parameter overrides
            >>> response = client.generate(
            ...     "Generate 5 research hypotheses about dark matter",
            ...     temperature=0.8,
            ...     max_tokens=2000
            ... )
            >>>
            >>> # With system prompt
            >>> response = client.generate(
            ...     "What are the ethical implications?",
            ...     system="You are an AI ethics researcher."
            ... )
        """
        # Override defaults with kwargs
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        model = kwargs.get("model", self.model)
        system_prompt = kwargs.get("system")

        try:
            # Build message parameters
            params: Dict[str, Any] = {
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            # Add system prompt if provided
            if system_prompt:
                params["system"] = system_prompt

            # Make API call to Claude
            response = self.client.messages.create(**params)

            # Extract text from response
            # Response format: response.content[0].text
            # Type annotation: ensure we return str
            text = response.content[0].text
            return str(text)

        except Exception as e:
            # Build helpful error message
            error_details = (
                f"❌ Claude API Call Failed\n\n"
                f"Error: {e}\n\n"
                f"Request Details:\n"
                f"  - Model: {model}\n"
                f"  - Prompt length: {len(prompt)} characters\n"
                f"  - Temperature: {temperature}\n"
                f"  - Max tokens: {max_tokens}\n\n"
                f"Authentication:\n"
                f"  - Type: {self.credentials.auth_type.value}\n"
                f"  - Source: {self.credentials.source.value}\n\n"
            )

            # Add specific help based on error type
            error_str = str(e).lower()

            if "authentication" in error_str or "api key" in error_str or "401" in error_str:
                error_details += (
                    "Possible Causes:\n"
                    "  - Invalid or expired credentials\n"
                    "  - OAuth token expired (if using Claude Code)\n\n"
                    "How to Fix:\n"
                    "  1. Check credentials: python -m claude_oauth_auth status\n"
                    "  2. If using OAuth: Run 'claude' and log in again\n"
                    "  3. If using API key: Verify key at https://console.anthropic.com/settings/keys\n"
                )
            elif "rate limit" in error_str or "429" in error_str:
                error_details += (
                    "Rate Limit Exceeded:\n"
                    "  - You've made too many requests too quickly\n\n"
                    "How to Fix:\n"
                    "  1. Wait a few minutes before retrying\n"
                    "  2. Implement exponential backoff in your code\n"
                    "  3. Consider upgrading your API tier\n"
                )
            elif "quota" in error_str or "insufficient" in error_str:
                error_details += (
                    "Quota/Credit Issue:\n"
                    "  - Insufficient API credits or quota exceeded\n\n"
                    "How to Fix:\n"
                    "  1. Check your account balance: https://console.anthropic.com/\n"
                    "  2. Add credits to your account\n"
                    "  3. Or use Claude Code OAuth with Max subscription\n"
                )
            elif "model" in error_str or "404" in error_str:
                error_details += (
                    "Model Issue:\n"
                    "  - Model may not exist or you don't have access\n\n"
                    "How to Fix:\n"
                    "  1. Verify model name is correct\n"
                    "  2. Check available models: https://docs.anthropic.com/models\n"
                    "  3. Ensure your account has access to this model\n"
                )
            elif "timeout" in error_str or "connection" in error_str:
                error_details += (
                    "Connection Issue:\n"
                    "  - Network timeout or connection error\n\n"
                    "How to Fix:\n"
                    "  1. Check your internet connection\n"
                    "  2. Retry the request\n"
                    "  3. Check Anthropic status: https://status.anthropic.com/\n"
                )
            else:
                error_details += (
                    "Troubleshooting:\n"
                    "  1. Run diagnostics: python -m claude_oauth_auth diagnose\n"
                    "  2. Check Anthropic status: https://status.anthropic.com/\n"
                    "  3. Review API docs: https://docs.anthropic.com/\n"
                    "  4. Get help: https://github.com/astoreyai/claude-oauth-auth/issues\n"
                )

            raise RuntimeError(error_details) from e

    def get_auth_info(self) -> Dict[str, Any]:
        """
        Get information about the authentication method being used.

        This is useful for debugging and understanding which credentials
        are being used for API calls.

        Returns:
            Dictionary with authentication details:
            - auth_type: "api_key" or "oauth_token"
            - source: Where the credential was discovered
            - metadata: Additional information (e.g., subscription type for OAuth)
            - credential_prefix: First 15 chars of credential (for verification)

        Example:
            >>> client = ClaudeClient()
            >>> info = client.get_auth_info()
            >>> print(f"Using: {info['auth_type']}")
            >>> print(f"Source: {info['source']}")
            >>> if info['auth_type'] == 'oauth_token':
            ...     print(f"Subscription: {info['metadata'].get('subscription_type')}")
        """
        return {
            "auth_type": self.credentials.auth_type.value,
            "source": self.credentials.source.value,
            "metadata": self.credentials.metadata,
            "credential_prefix": self.credentials.credential[:15] + "...",
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

    def get_full_auth_status(self) -> Dict[str, Any]:
        """
        Get comprehensive authentication status including available methods.

        Returns:
            Dictionary with complete authentication status

        Example:
            >>> client = ClaudeClient()
            >>> status = client.get_full_auth_status()
            >>> print(status['summary'])
            >>> for method in status['available_methods']:
            ...     print(f"  - {method}")
        """
        return self.auth_manager.get_auth_status()

    def __repr__(self) -> str:
        """String representation for debugging."""
        auth_type = self.credentials.auth_type.value
        source = self.credentials.source.value
        return (
            f"ClaudeClient("
            f"model={self.model}, "
            f"temperature={self.temperature}, "
            f"max_tokens={self.max_tokens}, "
            f"auth={auth_type} from {source}"
            ")"
        )

    def __str__(self) -> str:
        """Human-readable string representation."""
        auth_type = "OAuth" if self.credentials.auth_type == AuthType.OAUTH_TOKEN else "API Key"
        return f"Claude Client using {self.model} (auth: {auth_type})"


# Convenience function for quick initialization
def create_client(
    api_key: Optional[str] = None, auth_token: Optional[str] = None, **kwargs: Any
) -> ClaudeClient:
    """
    Convenience function to create a Claude client.

    This function provides a quick way to create a Claude client with
    automatic credential discovery.

    Args:
        api_key: Optional API key (uses auto-discovery if not provided)
        auth_token: Optional OAuth token (for Claude Max)
        **kwargs: Additional arguments passed to ClaudeClient

    Returns:
        Configured ClaudeClient instance

    Example:
        >>> # Auto-discovery
        >>> client = create_client()
        >>>
        >>> # Explicit API key
        >>> client = create_client(api_key="sk-ant-api03-...")
        >>>
        >>> # OAuth token
        >>> client = create_client(auth_token="sk-ant-oat01-...")
        >>>
        >>> # With verbose mode
        >>> client = create_client(verbose=True)
    """
    return ClaudeClient(api_key=api_key, auth_token=auth_token, **kwargs)
