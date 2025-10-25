# Changelog

All notable changes to `claude-oauth-auth` will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- OAuth authorization code flow implementation
- PKCE support for enhanced security
- Multiple OAuth provider support
- Token encryption at rest
- Session management utilities
- Web-based authentication flow helpers

## [0.1.0] - 2025-10-24

### Added

#### Core Functionality
- **OAuth Token Management**: Complete OAuth 2.0 token lifecycle management
  - Automatic token refresh before expiration
  - Token validation and expiration checking
  - Secure token storage with file permissions
  - Token discovery from Claude Code installation

- **Unified Authentication**: Single interface for multiple authentication methods
  - Automatic credential discovery (OAuth → API key)
  - Seamless fallback between authentication methods
  - Support for environment variables
  - Direct API key authentication

- **Claude Client**: Ready-to-use client for Anthropic Claude API
  - Drop-in replacement for Anthropic Python SDK
  - Automatic authentication injection
  - Support for all Claude models (Opus, Sonnet, Haiku)
  - Async client support for concurrent operations

#### Features
- **Multi-Platform Support**:
  - Linux, macOS, and Windows compatibility
  - Platform-specific token file locations
  - Environment variable integration

- **Developer Tools**:
  - Comprehensive logging and debugging
  - Type hints for IDE support
  - Detailed error messages
  - Token expiration warnings

- **Security**:
  - Secure token file permissions (600)
  - No credential logging
  - Environment variable support
  - Token refresh without re-authentication

#### Documentation
- Complete MkDocs documentation site
- Quick start guide
- Comprehensive user guide
- API reference with examples
- Troubleshooting guide
- Multiple usage examples

#### Testing
- Unit tests with pytest
- Integration tests
- Mock authentication for testing
- 95%+ code coverage requirement
- Type checking with mypy
- Linting with ruff

#### Development Tools
- GitHub Actions CI/CD
- Automated testing on multiple Python versions (3.8-3.12)
- Code quality checks (ruff, mypy)
- Documentation building and deployment
- PyPI publishing workflow

### Configuration
- Support for `ANTHROPIC_API_KEY` environment variable
- Support for `CLAUDE_AUTH_FILE` custom token location
- Platform-specific default paths
- JSON configuration file support

### Dependencies
- Python 3.8+ support
- `anthropic>=0.7.0` - Official Anthropic SDK
- Development dependencies: pytest, ruff, mypy
- Documentation dependencies: mkdocs, mkdocs-material, mkdocstrings

### Package Structure
```
claude-oauth-auth/
├── src/claude_oauth_auth/
│   ├── __init__.py
│   ├── oauth_manager.py
│   ├── unified_auth.py
│   └── client.py
├── tests/
├── docs/
└── pyproject.toml
```

## Version History

### Version Numbering

This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

### Release Process

1. Update version in `pyproject.toml`
2. Update this CHANGELOG.md
3. Create git tag: `git tag -a v0.1.0 -m "Release version 0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions automatically publishes to PyPI

## Migration Guides

### From Direct Anthropic SDK

If you're currently using the Anthropic SDK directly:

**Before:**
```python
import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
response = client.messages.create(...)
```

**After:**
```python
from claude_oauth_auth import ClaudeClient

client = ClaudeClient()  # Auto-discovers credentials
response = client.messages.create(...)
```

### From Manual OAuth Implementation

**Before:**
```python
# Your custom OAuth code
def get_token():
    # Manual token refresh logic
    pass

api_key = get_token()
client = Anthropic(api_key=api_key)
```

**After:**
```python
from claude_oauth_auth import ClaudeClient

# OAuth handled automatically
client = ClaudeClient()
```

## Deprecation Notices

### Current Version (0.1.0)
No deprecations in this initial release.

### Future Deprecations
None planned at this time.

## Security Updates

### 0.1.0
- Initial security implementations:
  - Token file permissions set to 600 (user read/write only)
  - No credential logging
  - Secure environment variable handling
  - Token expiration validation

## Known Issues

### 0.1.0

#### OAuth Limitations
- Requires existing OAuth tokens (from Claude Code or manual setup)
- Does not implement full OAuth authorization flow
- No built-in OAuth provider discovery

**Workaround**: Use Claude Code for OAuth setup, or provide tokens manually.

#### Platform-Specific
- Windows token file permissions not enforced as strictly as Unix systems

**Workaround**: Manually secure token files on Windows.

## Contributing

We welcome contributions! Please see our contributing guidelines.

### How to Report Issues
1. Check existing issues first
2. Include version information (`pip show claude-oauth-auth`)
3. Provide minimal reproducible example
4. Include error messages and tracebacks

### How to Suggest Features
1. Open an issue with `[Feature Request]` prefix
2. Describe the use case
3. Provide example API or code snippet
4. Explain why it would be useful

## Links

- **GitHub**: https://github.com/astoreyai/claude-oauth-auth
- **PyPI**: https://pypi.org/project/claude-oauth-auth/
- **Documentation**: https://astoreyai.github.io/claude-oauth-auth/
- **Issue Tracker**: https://github.com/astoreyai/claude-oauth-auth/issues
- **Changelog**: https://github.com/astoreyai/claude-oauth-auth/blob/main/CHANGELOG.md

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/astoreyai/claude-oauth-auth/blob/main/LICENSE) file for details.

---

[Unreleased]: https://github.com/astoreyai/claude-oauth-auth/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/astoreyai/claude-oauth-auth/releases/tag/v0.1.0
