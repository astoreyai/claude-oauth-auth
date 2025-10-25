# Frequently Asked Questions

Common questions and answers about `claude-oauth-auth`.

## Table of Contents

- [General Questions](#general-questions)
- [Authentication](#authentication)
- [OAuth vs API Key](#oauth-vs-api-key)
- [Installation and Setup](#installation-and-setup)
- [Usage and Integration](#usage-and-integration)
- [Error Handling](#error-handling)
- [Performance](#performance)
- [Security](#security)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

## General Questions

### What is claude-oauth-auth?

`claude-oauth-auth` is a Python library that simplifies authentication for the Anthropic Claude API. It provides:

- Automatic credential discovery from multiple sources
- Support for both OAuth and API key authentication
- Automatic token refresh for OAuth
- Drop-in replacement for the standard Anthropic client

**Learn more**: [Quick Start](quickstart.md) | [User Guide](guide.md)

### Why should I use this instead of the official Anthropic SDK?

The official SDK is great! `claude-oauth-auth` builds on top of it to add:

1. **Zero-configuration** setup for Claude Code users
2. **Automatic credential discovery** from multiple sources
3. **OAuth token management** with automatic refresh
4. **Simplified API** with sensible defaults

You can think of it as a convenience layer on top of the official SDK.

### Is this an official Anthropic library?

No, `claude-oauth-auth` is a community-maintained library extracted from the AI Scientist project. It's designed to work with Anthropic's official API and SDK.

### What Python versions are supported?

Python 3.8 and higher are supported. We test on:

- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12

### Is it production-ready?

Yes! The library is used in production applications. It includes:

- Comprehensive test coverage (90%+)
- Thread-safe operations
- Proper error handling
- Logging support
- Security best practices

**Learn more**: [Production Setup Tutorial](tutorial.md#step-5-production-setup)

### How do I get help?

1. Check this FAQ
2. Read the [Troubleshooting Guide](troubleshooting.md)
3. Review the [Examples](examples.md)
4. Open an issue on [GitHub](https://github.com/astoreyai/claude-oauth-auth/issues)

## Authentication

### What authentication methods are supported?

Two methods are supported:

1. **OAuth 2.0** (recommended)
   - Uses refresh tokens for automatic renewal
   - More secure for long-lived applications
   - Required for some Anthropic features

2. **API Key**
   - Simple and straightforward
   - Good for scripts and testing
   - Works everywhere

**Learn more**: [Authentication Guide](guide.md#authentication-methods)

### How does credential discovery work?

The library searches for credentials in this order:

1. Explicit credentials (passed to constructor)
2. OAuth tokens from custom location (`CLAUDE_AUTH_FILE` env var)
3. OAuth tokens from default location (`~/.config/claude/auth.json`)
4. API key from environment variable (`ANTHROPIC_API_KEY`)

First one found is used.

**Learn more**: [Credential Discovery Flow](architecture.md#credential-discovery-flow)

### Where are OAuth tokens stored?

Default locations:

- **Linux/macOS**: `~/.config/claude/auth.json`
- **Windows**: `%APPDATA%/claude/auth.json`

You can customize this with the `CLAUDE_AUTH_FILE` environment variable.

### How do I check which authentication method is being used?

```python
from claude_oauth_auth import UnifiedAuthManager

auth = UnifiedAuthManager()
print(f"Method: {auth.auth_method}")  # "oauth" or "api_key"
```

Or get detailed diagnostics:

```python
from claude_oauth_auth import get_auth_status

status = get_auth_status()
print(status['summary'])
```

**Learn more**: [Tutorial Step 3](tutorial.md#step-3-understanding-authentication)

### Can I use both OAuth and API key?

The library uses one method at a time, with OAuth taking priority. However, it automatically falls back to API key if OAuth is unavailable.

To force API key usage:

```python
from claude_oauth_auth import ClaudeClient

client = ClaudeClient(api_key="your-key")  # Ignores OAuth
```

## OAuth vs API Key

### When should I use OAuth instead of API key?

Use **OAuth** when:

- You're using Claude Code
- You need automatic token refresh
- Building a long-lived application
- Security is a top concern
- You want to avoid managing secrets

Use **API Key** when:

- Writing simple scripts
- Testing or development
- You don't have OAuth setup
- Deployment to serverless environments
- You need maximum simplicity

### How do OAuth tokens expire?

OAuth access tokens typically expire after several hours. The library:

1. Checks token expiration before each use
2. Automatically refreshes if within 5 minutes of expiry
3. Uses refresh token to get new access token
4. Saves new token to disk

This is completely transparent to your application.

### What happens when a refresh token expires?

Refresh tokens typically last 30-90 days. When expired:

1. Automatic refresh fails
2. Library falls back to API key (if available)
3. Or raises `AuthenticationError`

You'll need to re-authenticate with Claude Code or get a new refresh token.

### Can I use OAuth without Claude Code?

Currently, the easiest way to get OAuth tokens is through Claude Code. However, you can:

1. Implement your own OAuth flow
2. Manually populate the token file
3. Use tokens from another source

```python
from claude_oauth_auth import OAuthTokenManager

manager = OAuthTokenManager(
    access_token="your-access-token",
    refresh_token="your-refresh-token",
    token_expiry=1234567890  # Unix timestamp
)
```

### How do I rotate API keys?

For zero-downtime rotation:

1. Generate new API key in Anthropic console
2. Update environment variable or configuration
3. Restart application
4. Revoke old key

For gradual rotation:

```python
import os

# Try new key first, fall back to old
new_key = os.getenv("ANTHROPIC_API_KEY_NEW")
old_key = os.getenv("ANTHROPIC_API_KEY_OLD")

from claude_oauth_auth import ClaudeClient

try:
    client = ClaudeClient(api_key=new_key)
    client.messages.create(...)  # Test it
except:
    client = ClaudeClient(api_key=old_key)  # Fall back
```

## Installation and Setup

### How do I install claude-oauth-auth?

```bash
pip install claude-oauth-auth
```

For development dependencies:

```bash
pip install claude-oauth-auth[dev]
```

**Learn more**: [Installation](quickstart.md#installation)

### Do I need to install Claude Code?

No, but it makes setup easier. Claude Code provides OAuth tokens automatically.

Without Claude Code, you'll need an API key from https://console.anthropic.com/

### What are the dependencies?

Minimal dependencies:

- `anthropic` (>=0.18.0) - Official Anthropic SDK
- Python standard library only

Optional:
- `pytest` - For running tests
- `mkdocs` - For building documentation

### Can I use this in a virtual environment?

Yes, and it's recommended!

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install claude-oauth-auth
```

### How do I upgrade to the latest version?

```bash
pip install --upgrade claude-oauth-auth
```

Check your version:

```python
import claude_oauth_auth
print(claude_oauth_auth.__version__)
```

### Does it work with Poetry/Pipenv/etc?

Yes! Works with any Python package manager:

**Poetry:**
```bash
poetry add claude-oauth-auth
```

**Pipenv:**
```bash
pipenv install claude-oauth-auth
```

**Conda:**
```bash
pip install claude-oauth-auth  # Install via pip in conda env
```

## Usage and Integration

### Is the API the same as the official Anthropic client?

Yes! `ClaudeClient` is a thin wrapper around the official client:

```python
# Official SDK
import anthropic
client = anthropic.Anthropic(api_key="...")
response = client.messages.create(...)

# claude-oauth-auth (same API)
from claude_oauth_auth import ClaudeClient
client = ClaudeClient()
response = client.messages.create(...)  # Identical
```

### Can I use this with async/await?

The Anthropic SDK (and therefore this library) is synchronous. For async usage, wrap in a thread pool:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from claude_oauth_auth import ClaudeClient

executor = ThreadPoolExecutor()

async def async_chat(prompt):
    client = ClaudeClient()
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        executor,
        lambda: client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}]
        )
    )
    return response

# Usage
response = await async_chat("Hello!")
```

**Learn more**: [Async Pattern](advanced.md#asyncawait-pattern)

### How do I use this with Flask?

```python
from flask import Flask, request, jsonify
from claude_oauth_auth import ClaudeClient

app = Flask(__name__)
client = ClaudeClient()  # Create once at startup

@app.route('/chat', methods=['POST'])
def chat():
    prompt = request.json['prompt']
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return jsonify({'response': response.content[0].text})

if __name__ == '__main__':
    app.run()
```

**Learn more**: [Flask Integration](advanced.md#flask-integration)

### How do I use this with FastAPI?

```python
from fastapi import FastAPI
from claude_oauth_auth import ClaudeClient

app = FastAPI()
client = ClaudeClient()

@app.post("/chat")
async def chat(prompt: str):
    # Run in thread pool since Anthropic SDK is sync
    from concurrent.futures import ThreadPoolExecutor
    executor = ThreadPoolExecutor()
    loop = asyncio.get_event_loop()

    response = await loop.run_in_executor(
        executor,
        lambda: client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
    )
    return {"response": response.content[0].text}
```

**Learn more**: [FastAPI Integration](advanced.md#fastapi-integration)

### Can I use multiple clients with different credentials?

Yes! Each client can have different credentials:

```python
from claude_oauth_auth import ClaudeClient

# Client 1: OAuth
client1 = ClaudeClient()

# Client 2: Specific API key
client2 = ClaudeClient(api_key="key-for-user-2")

# Client 3: Different API key
client3 = ClaudeClient(api_key="key-for-user-3")
```

### How do I handle rate limits?

Implement exponential backoff:

```python
from claude_oauth_auth import ClaudeClient
from anthropic import RateLimitError
import time

def chat_with_backoff(prompt, max_retries=3):
    client = ClaudeClient()

    for attempt in range(max_retries):
        try:
            return client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
        except RateLimitError:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                time.sleep(wait)
            else:
                raise
```

**Learn more**: [Error Handling](tutorial.md#step-4-error-handling)

### Can I use this in a Jupyter notebook?

Yes! Works perfectly in Jupyter:

```python
# Cell 1: Install
!pip install claude-oauth-auth

# Cell 2: Import and use
from claude_oauth_auth import ClaudeClient

client = ClaudeClient()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.content[0].text)
```

## Error Handling

### What exceptions can be raised?

Common exceptions:

```python
from anthropic import (
    AuthenticationError,  # Invalid credentials
    RateLimitError,       # Rate limit exceeded
    APIError,             # General API error
    APIConnectionError,   # Network error
)

from claude_oauth_auth import ClaudeClient

try:
    client = ClaudeClient()
    response = client.messages.create(...)
except AuthenticationError:
    print("Invalid credentials")
except RateLimitError:
    print("Rate limit exceeded")
except APIConnectionError:
    print("Network error")
except APIError as e:
    print(f"API error: {e}")
```

### How do I handle "No credentials found" error?

This means the library couldn't find any credentials. Solutions:

1. **Install and authenticate Claude Code**
2. **Set API key**:
   ```bash
   export ANTHROPIC_API_KEY="your-key"
   ```
3. **Pass key explicitly**:
   ```python
   client = ClaudeClient(api_key="your-key")
   ```

Check what's available:

```python
from claude_oauth_auth import get_auth_status
print(get_auth_status()['summary'])
```

### What if token refresh fails?

When OAuth refresh fails, the library:

1. Attempts to fall back to API key (if available)
2. Raises `AuthenticationError` if no fallback

To handle:

```python
from claude_oauth_auth import ClaudeClient
from anthropic import AuthenticationError

try:
    client = ClaudeClient()
except AuthenticationError:
    # Re-authenticate or use API key
    client = ClaudeClient(api_key="backup-key")
```

### How do I debug authentication issues?

Enable debug logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from claude_oauth_auth import UnifiedAuthManager

auth = UnifiedAuthManager()  # Will print detailed logs
```

Use diagnostics:

```python
from claude_oauth_auth import get_auth_status

status = get_auth_status()
print(f"Summary: {status['summary']}")
print(f"OAuth available: {status['oauth_available']}")
print(f"API key available: {status['api_key_available']}")
```

**Learn more**: [Debugging Techniques](advanced.md#debugging-techniques)

## Performance

### Is there any performance overhead?

Minimal overhead:

- **First request**: ~10-50ms for credential discovery and client initialization
- **Subsequent requests**: ~0-1ms overhead (credentials cached)
- **Token refresh**: ~100-500ms (happens automatically, infrequently)

The actual API call time dominates (typically 1-5 seconds).

### How can I optimize for high-throughput scenarios?

1. **Reuse client instances**:
   ```python
   client = ClaudeClient()  # Create once
   for prompt in prompts:
       response = client.messages.create(...)  # Reuse
   ```

2. **Use connection pooling** (automatic in Anthropic SDK)

3. **Concurrent requests**:
   ```python
   from concurrent.futures import ThreadPoolExecutor

   def process_batch(prompts):
       client = ClaudeClient()
       with ThreadPoolExecutor(max_workers=10) as executor:
           futures = [
               executor.submit(client.messages.create, ...)
               for prompt in prompts
           ]
           return [f.result() for f in futures]
   ```

**Learn more**: [Performance Optimization](advanced.md#performance-optimization)

### Does it work with concurrent requests?

Yes! The library is thread-safe:

```python
from claude_oauth_auth import ClaudeClient
from concurrent.futures import ThreadPoolExecutor

client = ClaudeClient()  # One client, shared across threads

def make_request(prompt):
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

with ThreadPoolExecutor(max_workers=5) as executor:
    results = executor.map(make_request, prompts)
```

**Learn more**: [Thread Safety](advanced.md#thread-safety-considerations)

### How much memory does it use?

Minimal memory footprint:

- ~1-2 MB for the library itself
- ~10-50 KB for cached credentials
- ~1-5 MB for the Anthropic SDK client

Memory usage is dominated by response data, not the library.

### Can I cache responses?

The library doesn't cache responses (by design), but you can add caching:

```python
from functools import lru_cache
from claude_oauth_auth import ClaudeClient

client = ClaudeClient()

@lru_cache(maxsize=100)
def cached_chat(prompt):
    """Cache responses for repeated prompts"""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# First call: hits API
result1 = cached_chat("What is 2+2?")

# Second call: returns cached result
result2 = cached_chat("What is 2+2?")
```

## Security

### Is it safe to store OAuth tokens in files?

The library follows security best practices:

1. **File permissions**: Set to 600 (user-only read/write)
2. **Location**: In user's home directory (not in project)
3. **No logging**: Tokens never logged or printed

However, file storage is less secure than:
- OS keychain (macOS Keychain, Windows Credential Manager)
- Hardware security modules (HSM)
- Cloud secret managers (AWS Secrets Manager, etc.)

For maximum security, consider extending the library to use these backends.

**Learn more**: [Security Architecture](architecture.md#security-architecture)

### How do I secure API keys in production?

Best practices:

1. **Use environment variables**, not hardcoded keys
2. **Use secrets managers** (AWS Secrets Manager, HashiCorp Vault)
3. **Rotate keys regularly** (every 90 days)
4. **Use different keys** for dev/staging/production
5. **Never commit** keys to version control

Example with AWS Secrets Manager:

```python
import boto3
from claude_oauth_auth import ClaudeClient

def get_api_key():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId='claude/api_key')
    return json.loads(response['SecretString'])['api_key']

client = ClaudeClient(api_key=get_api_key())
```

**Learn more**: [Custom Credential Sources](advanced.md#custom-credential-sources)

### Can I encrypt the token file?

Not built-in, but you can extend the library:

```python
from cryptography.fernet import Fernet
from claude_oauth_auth import OAuthTokenManager
import os

class EncryptedTokenManager(OAuthTokenManager):
    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
        super().__init__()

    def _load_tokens(self):
        # Load and decrypt
        with open(self.token_file, 'rb') as f:
            encrypted = f.read()
        decrypted = self.cipher.decrypt(encrypted)
        # Parse JSON, set tokens...

    def _save_tokens(self):
        # Encrypt and save
        # ...
```

**Learn more**: [Security Hardening](advanced.md#security-hardening)

### What data is sent to Anthropic?

Only what you send:
- Your API requests (messages, parameters)
- Authentication credentials (OAuth token or API key)

The library doesn't send:
- Telemetry
- Usage statistics
- Any other data

All communication is over HTTPS with the official Anthropic API.

### Should I use OAuth or API key for production?

Both are secure when handled properly. Choose based on your needs:

**OAuth** is better for:
- Long-lived applications
- Automatic token rotation
- Delegated access scenarios

**API Key** is better for:
- Simple deployments
- Serverless functions
- When OAuth setup is impractical

In production, the most important factors are:
1. Proper secrets management
2. Regular key rotation
3. Monitoring and alerting
4. Principle of least privilege

## Troubleshooting

### Why can't the library find my credentials?

Check each source:

```python
import os

# 1. Check OAuth file
oauth_file = os.path.expanduser("~/.config/claude/auth.json")
print(f"OAuth file exists: {os.path.exists(oauth_file)}")

# 2. Check API key
api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API key set: {api_key is not None}")

# 3. Check custom location
custom = os.getenv("CLAUDE_AUTH_FILE")
print(f"Custom location: {custom}")
```

**Learn more**: [Troubleshooting Guide](troubleshooting.md)

### Why do I get "permission denied" on the token file?

Fix file permissions:

```bash
# macOS/Linux
chmod 600 ~/.config/claude/auth.json

# Windows: Use File Properties > Security
```

Or specify a different location:

```bash
export CLAUDE_AUTH_FILE="/path/to/writable/location/auth.json"
```

### My tokens keep expiring, what's wrong?

Check token expiry:

```python
from claude_oauth_auth import OAuthTokenManager
import json

manager = OAuthTokenManager()
with open(manager.token_file) as f:
    tokens = json.load(f)

from datetime import datetime
expiry = datetime.fromtimestamp(tokens['token_expiry'])
print(f"Token expires: {expiry}")

import time
print(f"Hours until expiry: {(tokens['token_expiry'] - time.time()) / 3600}")
```

If tokens expire too quickly, you may need to refresh more frequently or check if the refresh token itself is expired.

### How do I report a bug?

1. Check existing issues: https://github.com/astoreyai/claude-oauth-auth/issues
2. Gather information:
   - Python version
   - Library version
   - Error messages
   - Minimal reproduction code
3. Open a new issue with details

### Where can I get more help?

1. Read the [Troubleshooting Guide](troubleshooting.md)
2. Check [Examples](examples.md)
3. Review [Architecture Documentation](architecture.md)
4. Open an issue on GitHub
5. Check the Anthropic community forums

## Advanced Topics

### Can I extend the library for custom authentication?

Yes! Extend `UnifiedAuthManager`:

```python
from claude_oauth_auth import UnifiedAuthManager

class CustomAuth(UnifiedAuthManager):
    def _discover_credentials(self):
        # Your custom logic
        custom_creds = self.load_from_somewhere()
        if custom_creds:
            return custom_creds
        return super()._discover_credentials()
```

**Learn more**: [Custom Credential Sources](advanced.md#custom-credential-sources)

### How does the priority cascade work?

Credentials are discovered in this priority order:

1. Explicit (passed to constructor) - highest priority
2. Custom OAuth file (`CLAUDE_AUTH_FILE` env var)
3. Default OAuth file (`~/.config/claude/auth.json`)
4. Environment API key (`ANTHROPIC_API_KEY`)
5. No credentials - error

First match wins.

**Learn more**: [Priority Cascade](advanced.md#priority-cascade-explained)

### Can I use this with other LLM APIs?

The library is specifically designed for Anthropic's Claude API. For other APIs, you'd need:

1. Different authentication flows
2. Different token formats
3. Different API endpoints

However, the architecture could be adapted for other APIs.

### How do I contribute to the project?

Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

See CONTRIBUTING.md for details.

### Is there a commercial support option?

Currently this is a community-maintained project with no commercial support. For enterprise support, contact the maintainers via GitHub.

### What's the license?

MIT License - free for commercial and personal use.

### How do I stay updated on new releases?

1. Watch the GitHub repository
2. Check the [Changelog](changelog.md)
3. Follow release notes

### Can I use this in a Docker container?

Yes! Example Dockerfile:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
CMD ["python", "app.py"]
```

**Learn more**: [Docker Configuration](tutorial.md#step-5-production-setup)

## Still Have Questions?

- Check the [User Guide](guide.md) for comprehensive documentation
- Review [Examples](examples.md) for code samples
- Read the [Architecture Documentation](architecture.md) for internals
- Open an issue on [GitHub](https://github.com/astoreyai/claude-oauth-auth/issues)
