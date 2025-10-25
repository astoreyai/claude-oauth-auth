# claude-oauth-auth

**OAuth 2.0 authentication manager for Anthropic Claude API with unified credential discovery**

## Overview

`claude-oauth-auth` is a Python library that simplifies authentication with the Anthropic Claude API by providing seamless OAuth 2.0 support alongside traditional API key authentication. It automatically discovers credentials from multiple sources and manages OAuth token refresh, making it easy to integrate Claude into your applications.

## Key Features

- **OAuth 2.0 Support**: Full OAuth 2.0 implementation with automatic token refresh
- **Unified Credential Discovery**: Automatically searches for credentials in multiple locations:
  - OAuth tokens (refresh tokens, access tokens)
  - API keys from environment variables
  - Configuration files
  - Command-line arguments
- **Token Management**: Automatic token refresh and validation
- **Fallback Mechanism**: Gracefully falls back to API key authentication if OAuth is unavailable
- **Type Safety**: Fully typed with mypy support
- **Thread-Safe**: Designed for concurrent operations with threading support
- **Easy Integration**: Drop-in replacement for standard Anthropic client
- **Secure**: Never logs or exposes sensitive credentials
- **Flexible**: Works with Claude Code, custom applications, and CI/CD pipelines

## Quick Installation

Install via pip:

```bash
pip install claude-oauth-auth
```

Or with development dependencies:

```bash
pip install claude-oauth-auth[dev]
```

## Quick Example

```python
from claude_oauth_auth import UnifiedAuthManager, ClaudeClient

# Automatically discovers OAuth tokens or API keys
auth_manager = UnifiedAuthManager()
client = ClaudeClient(auth_manager)

# Use the client just like the standard Anthropic client
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello, Claude!"}]
)
print(response.content[0].text)
```

## Requirements

- **Python**: 3.8 or higher
- **Dependencies**:
  - `anthropic>=0.7.0` - Official Anthropic Python SDK

## Compatibility

- **Operating Systems**: Linux, macOS, Windows
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Claude API**: Compatible with all Claude models (Opus, Sonnet, Haiku)
- **Authentication Methods**: OAuth 2.0, API keys, environment variables

## Why claude-oauth-auth?

The Anthropic Claude API supports both OAuth 2.0 and API key authentication, but managing these authentication methods can be complex:

1. **OAuth Complexity**: OAuth 2.0 requires token refresh, expiration handling, and storage
2. **Multiple Credential Sources**: Developers need to check environment variables, config files, and OAuth tokens
3. **Token Management**: Refresh tokens need to be securely stored and automatically renewed
4. **Fallback Logic**: Applications should gracefully degrade to API keys if OAuth is unavailable

`claude-oauth-auth` solves all these problems with a unified, simple interface that handles authentication automatically.

## Next Steps

- **[Quick Start](quickstart.md)**: Get up and running in 5 minutes
- **[User Guide](guide.md)**: Learn about all authentication methods and configuration options
- **[API Reference](api.md)**: Detailed API documentation
- **[Examples](examples.md)**: Real-world usage examples
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions

## Support

- **GitHub**: [astoreyai/claude-oauth-auth](https://github.com/astoreyai/claude-oauth-auth)
- **Issues**: [Report bugs or request features](https://github.com/astoreyai/claude-oauth-auth/issues)
- **PyPI**: [claude-oauth-auth](https://pypi.org/project/claude-oauth-auth/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
