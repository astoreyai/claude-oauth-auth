# claude-oauth-auth

[![PyPI version](https://badge.fury.io/py/claude-oauth-auth.svg)](https://badge.fury.io/py/claude-oauth-auth)
[![Python Versions](https://img.shields.io/pypi/pyversions/claude-oauth-auth.svg)](https://pypi.org/project/claude-oauth-auth/)
[![License](https://img.shields.io/github/license/astoreyai/claude-oauth-auth.svg)](https://github.com/astoreyai/claude-oauth-auth/blob/main/LICENSE)
[![Tests](https://github.com/astoreyai/claude-oauth-auth/workflows/Tests/badge.svg)](https://github.com/astoreyai/claude-oauth-auth/actions/workflows/test.yml)
[![Quality](https://github.com/astoreyai/claude-oauth-auth/workflows/Quality%20Checks/badge.svg)](https://github.com/astoreyai/claude-oauth-auth/actions/workflows/quality.yml)
[![Security](https://github.com/astoreyai/claude-oauth-auth/workflows/Security%20Scanning/badge.svg)](https://github.com/astoreyai/claude-oauth-auth/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/astoreyai/claude-oauth-auth/branch/main/graph/badge.svg)](https://codecov.io/gh/astoreyai/claude-oauth-auth)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](.github/CODE_OF_CONDUCT.md)

A Python package for handling OAuth authentication with Claude API, providing secure token management and authentication workflows.

## Features

- **Complete OAuth 2.0 Implementation**: Full support for OAuth authorization code flow
- **PKCE Support**: Enhanced security with Proof Key for Code Exchange (RFC 7636)
- **Automatic Token Management**: Handles token refresh and expiration automatically
- **Secure Token Storage**: Safe persistence of authentication credentials
- **Simple High-Level API**: Easy-to-use client interface for common workflows
- **Type Hints**: Full type annotation support for better IDE integration

## Installation

```bash
pip install claude-oauth-auth
```

## Quick Start

```python
from claude_oauth_auth import ClaudeOAuthClient

# Initialize the client with your OAuth credentials
client = ClaudeOAuthClient(
    client_id="your_client_id",
    client_secret="your_client_secret",  # Optional for PKCE
    redirect_uri="http://localhost:8080/callback",
    token_file="~/.claude/tokens.json"  # Optional: persist tokens
)

# Authenticate with Claude API
if client.authenticate():
    print("Successfully authenticated!")

    # Get a valid access token
    token = client.get_access_token()

    # Use the token for API requests
    # ...
else:
    print("Authentication failed")
```

## Advanced Usage

### Using Individual Components

```python
from claude_oauth_auth import OAuthManager, AuthManager

# Low-level OAuth operations
oauth_manager = OAuthManager(
    client_id="your_client_id",
    client_secret="your_client_secret",
    redirect_uri="http://localhost:8080/callback"
)

# Get authorization URL
auth_url = oauth_manager.get_authorization_url()
print(f"Visit: {auth_url}")

# Exchange code for token (after user authorization)
tokens = oauth_manager.exchange_code_for_token(code)

# Token management
auth_manager = AuthManager(
    token_file="~/.claude/tokens.json",
    oauth_manager=oauth_manager
)

# Save and load tokens
auth_manager.save_tokens(tokens)
valid_token = auth_manager.get_valid_token()
```

## Requirements

- Python 3.8 or higher
- Dependencies listed in `requirements.txt`

## Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/claude-oauth-auth.git
cd claude-oauth-auth

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=claude_oauth_auth --cov-report=html
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=claude_oauth_auth

# Run specific test file
pytest tests/test_oauth_manager.py

# Run with verbose output
pytest -v
```

## Documentation

Full documentation is available at [https://claude-oauth-auth.readthedocs.io/](https://claude-oauth-auth.readthedocs.io/)

- [Installation Guide](docs/installation.md)
- [Authentication Flow](docs/authentication.md)
- [API Reference](docs/api.md)
- [Examples](docs/examples.md)

## Project Structure

```
claude-oauth-auth/
├── src/
│   └── claude_oauth_auth/
│       ├── __init__.py          # Package initialization and exports
│       ├── oauth_manager.py     # OAuth 2.0 flow management
│       ├── auth_manager.py      # Token storage and session management
│       └── client.py            # High-level client interface
├── tests/                       # Test suite
├── docs/                        # Documentation
├── README.md                    # This file
├── LICENSE                      # MIT License
└── pyproject.toml              # Project configuration
```

## Security Considerations

- **Never commit tokens or credentials** to version control
- **Use PKCE** for public clients (mobile/desktop apps)
- **Store tokens securely** using the built-in token storage
- **Use HTTPS** for redirect URIs in production
- **Rotate credentials** regularly

## Contributing

We welcome contributions from the community! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### Quick Start

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Run tests and linting (`pytest`, `ruff check`, `mypy`)
5. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
6. Push to the branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

### Guidelines

Please read our [Contributing Guide](.github/CONTRIBUTING.md) for detailed information on:
- Development setup
- Code style guidelines
- Testing requirements
- Pull request process

We also have a [Code of Conduct](.github/CODE_OF_CONDUCT.md) that all contributors are expected to follow.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for the Claude API by Anthropic
- Follows OAuth 2.0 RFC 6749 and PKCE RFC 7636 standards
- Inspired by best practices from the Python OAuth ecosystem

## Community

### Getting Help

- **Documentation**: [README](https://github.com/astoreyai/claude-oauth-auth#readme)
- **Issues**: [Report bugs or request features](https://github.com/astoreyai/claude-oauth-auth/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/astoreyai/claude-oauth-auth/discussions)
- **Security**: See our [Security Policy](.github/SECURITY.md) for reporting vulnerabilities

### Stay Updated

- **Releases**: [GitHub Releases](https://github.com/astoreyai/claude-oauth-auth/releases)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **PyPI**: [claude-oauth-auth on PyPI](https://pypi.org/project/claude-oauth-auth/)

### Contributing

We welcome contributions! See our [Contributing Guide](.github/CONTRIBUTING.md) to get started.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes in each version.

---

**Note**: This package is under active development. APIs may change before the 1.0 release.
