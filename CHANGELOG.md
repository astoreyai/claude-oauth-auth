# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Upcoming features will be listed here

### Changed
- Upcoming changes will be listed here

### Deprecated
- Features to be removed in future versions

### Removed
- Removed features will be listed here

### Fixed
- Bug fixes will be listed here

### Security
- Security improvements will be listed here

## [0.1.0] - 2025-10-24

### Added
- Initial release of claude-oauth-auth
- Complete OAuth 2.0 authorization code flow implementation
- PKCE (Proof Key for Code Exchange) support for enhanced security
- Automatic token refresh mechanism
- Secure token storage with file-based persistence
- High-level `ClaudeOAuthClient` for simplified OAuth workflows
- Low-level `OAuthManager` for granular OAuth operations
- `AuthManager` for token lifecycle management
- Comprehensive test suite with 95%+ code coverage
- Full type hints for better IDE integration
- Detailed documentation and examples
- Support for Python 3.8+

### Security
- Implemented PKCE (RFC 7636) for public client protection
- Secure state parameter generation to prevent CSRF attacks
- Automatic token expiration handling
- Secure token storage with appropriate file permissions

## Release Links

[Unreleased]: https://github.com/astoreyai/claude-oauth-auth/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/astoreyai/claude-oauth-auth/releases/tag/v0.1.0

---

## How to Use This Changelog

### For Maintainers

When preparing a release:

1. Move items from `[Unreleased]` to a new version section
2. Update the version number and date
3. Add a link to the release at the bottom
4. Follow the categories: Added, Changed, Deprecated, Removed, Fixed, Security

### Categories Explained

- **Added** - New features
- **Changed** - Changes in existing functionality
- **Deprecated** - Features that will be removed in upcoming releases
- **Removed** - Features that have been removed
- **Fixed** - Bug fixes
- **Security** - Security improvements and vulnerability fixes

### Formatting Guidelines

- Use present tense ("Add feature" not "Added feature")
- Reference issues and pull requests: `(#123)`, `(#456)`
- Credit contributors: `Thanks @username`
- Group similar changes together
- Keep entries concise but descriptive

### Example Entry

```markdown
## [0.2.0] - 2025-11-15

### Added
- Support for custom OAuth scopes (#42)
- Automatic token revocation on logout (#45)
- CLI tool for OAuth flow testing (#48) - Thanks @contributor

### Changed
- Improved error messages for authentication failures (#50)
- Updated dependencies to latest versions (#52)

### Fixed
- Token refresh race condition (#44)
- PKCE verifier generation on Windows (#47)

### Security
- Updated cryptography library to address CVE-2025-XXXX (#53)
```

---

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for guidelines on how to contribute changes that should be documented here.
