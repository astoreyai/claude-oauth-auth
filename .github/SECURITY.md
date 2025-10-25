# Security Policy

## Supported Versions

We release patches for security vulnerabilities in the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

**Note**: Once version 1.0 is released, we will maintain security updates for the current major version and the previous major version.

## Reporting a Vulnerability

We take the security of claude-oauth-auth seriously. If you believe you have found a security vulnerability, please report it to us as described below.

### Please Do NOT:

- Open a public GitHub issue for security vulnerabilities
- Discuss the vulnerability in public forums or social media
- Exploit the vulnerability beyond what is necessary to demonstrate it

### Please DO:

**Report security vulnerabilities privately** using one of these methods:

1. **GitHub Security Advisories** (Preferred)
   - Go to https://github.com/astoreyai/claude-oauth-auth/security/advisories/new
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email**
   - Send details to: security@claude-oauth-auth.dev
   - Use subject line: "Security Vulnerability Report"
   - Include "SECURITY" in the email subject

### What to Include

When reporting a vulnerability, please include:

1. **Description** - Clear description of the vulnerability
2. **Impact** - What could an attacker do with this vulnerability?
3. **Steps to Reproduce** - Detailed steps to reproduce the issue
4. **Affected Versions** - Which versions are affected?
5. **Proof of Concept** - Code or steps demonstrating the vulnerability
6. **Suggested Fix** - If you have ideas on how to fix it (optional)
7. **Your Contact Information** - So we can follow up with questions

### Example Report

```
Subject: [SECURITY] Token exposure in debug logging

Description:
Access tokens are being logged in plaintext when debug logging is enabled.

Impact:
Attackers with access to log files could obtain valid access tokens.

Steps to Reproduce:
1. Enable debug logging: logging.basicConfig(level=logging.DEBUG)
2. Authenticate with ClaudeOAuthClient
3. Check logs - access token is visible in plaintext

Affected Versions:
All versions up to and including 0.1.0

Proof of Concept:
[Code or screenshots demonstrating the issue]

Suggested Fix:
Redact tokens in log messages or disable token logging in production mode.
```

## Response Timeline

We will make our best effort to respond according to the following timeline:

- **Initial Response**: Within 48 hours
- **Confirmation**: Within 5 business days
- **Fix Development**: Varies by severity (see below)
- **Public Disclosure**: After fix is released and users have time to update

### Severity Levels

| Severity | Response Time | Public Disclosure |
|----------|--------------|-------------------|
| Critical | 1-7 days     | After 30 days     |
| High     | 7-14 days    | After 60 days     |
| Medium   | 14-30 days   | After 90 days     |
| Low      | 30-90 days   | After 120 days    |

## Security Update Process

When a security vulnerability is confirmed:

1. **Acknowledgment** - We'll confirm receipt and assessment
2. **Investigation** - We'll investigate and validate the issue
3. **Fix Development** - We'll develop and test a fix
4. **Security Advisory** - We'll prepare a security advisory
5. **Release** - We'll release a patch version
6. **Notification** - We'll notify users via:
   - GitHub Security Advisory
   - Release notes
   - Email to maintainers list (if applicable)
7. **Public Disclosure** - After sufficient time for users to update

## Security Best Practices for Users

### For Application Developers

1. **Keep Dependencies Updated**
   ```bash
   pip install --upgrade claude-oauth-auth
   ```

2. **Never Commit Credentials**
   - Add `.env` to `.gitignore`
   - Never hardcode API keys or secrets
   - Use environment variables or secure vaults

3. **Use PKCE for Public Clients**
   ```python
   client = ClaudeOAuthClient(
       client_id="your_client_id",
       redirect_uri="http://localhost:8080/callback",
       # Don't include client_secret for public clients
   )
   ```

4. **Secure Token Storage**
   ```python
   # Use appropriate file permissions
   client = ClaudeOAuthClient(
       token_file="~/.claude/tokens.json"  # Store in user directory
   )
   ```

5. **Use HTTPS in Production**
   ```python
   # Development
   redirect_uri="http://localhost:8080/callback"  # OK for dev

   # Production
   redirect_uri="https://yourdomain.com/callback"  # Required for prod
   ```

6. **Validate Tokens**
   ```python
   # Always check token validity
   if not client.is_token_valid():
       client.refresh_token()
   ```

7. **Handle Errors Securely**
   ```python
   try:
       token = client.get_access_token()
   except Exception as e:
       # Don't log sensitive information
       logger.error("Authentication failed", exc_info=False)
   ```

8. **Rotate Credentials Regularly**
   - Rotate client secrets periodically
   - Revoke unused tokens
   - Monitor for suspicious activity

### For Package Maintainers

1. **Review Dependencies**
   - Regularly audit dependencies for vulnerabilities
   - Use tools like `safety` or `pip-audit`

2. **Code Review**
   - All security-sensitive changes require review
   - Follow secure coding practices

3. **Testing**
   - Include security tests in test suite
   - Test authentication edge cases
   - Validate token handling

## Vulnerability Disclosure Policy

We follow **Coordinated Vulnerability Disclosure**:

- Reporters are credited in security advisories (unless they prefer to remain anonymous)
- We request that reporters give us reasonable time to fix issues before public disclosure
- We will acknowledge and credit reporters in release notes
- We will not take legal action against reporters who follow this policy

## Security Hall of Fame

We appreciate security researchers who responsibly disclose vulnerabilities:

<!-- When we receive our first security report, we'll list reporters here -->

*No security vulnerabilities have been reported yet.*

## Known Security Considerations

### OAuth Security

This package implements OAuth 2.0 authentication. Users should be aware of:

1. **PKCE is Recommended** - Use PKCE (Proof Key for Code Exchange) for public clients
2. **State Parameter** - We use state parameter to prevent CSRF attacks
3. **Token Storage** - Tokens are stored locally; ensure appropriate file permissions
4. **HTTPS Required** - Always use HTTPS redirect URIs in production
5. **Token Expiration** - Tokens expire; the package handles refresh automatically

### What We Do

- Implement PKCE (RFC 7636) for enhanced security
- Use secure random state generation
- Validate redirect URIs
- Automatic token refresh
- Secure token storage with appropriate permissions

### What You Must Do

- Use HTTPS in production
- Protect your client secrets
- Store tokens securely
- Validate all inputs
- Keep the package updated

## Security Resources

- [OWASP OAuth Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OAuth2_Cheat_Sheet.html)
- [RFC 6749 - OAuth 2.0](https://datatracker.ietf.org/doc/html/rfc6749)
- [RFC 7636 - PKCE](https://datatracker.ietf.org/doc/html/rfc7636)
- [OAuth 2.0 Security Best Practices](https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics)

## Contact

- **Security Issues**: security@claude-oauth-auth.dev
- **GitHub Security Advisories**: https://github.com/astoreyai/claude-oauth-auth/security/advisories
- **General Questions**: https://github.com/astoreyai/claude-oauth-auth/discussions

---

**Last Updated**: October 2025

Thank you for helping keep claude-oauth-auth and its users safe!
