# Troubleshooting

Common issues and solutions for `claude-oauth-auth`.

## Table of Contents

- [Authentication Issues](#authentication-issues)
- [OAuth Token Problems](#oauth-token-problems)
- [API Key Issues](#api-key-issues)
- [Import and Installation](#import-and-installation-errors)
- [Network and Connection](#network-and-connection-issues)
- [Debug Mode](#enabling-debug-mode)

## Authentication Issues

### No Credentials Found

**Problem:** Getting "No credentials found" error.

```
AuthenticationError: No credentials found
```

**Solutions:**

1. **Check for OAuth tokens:**

```bash
# Linux/macOS
ls -la ~/.config/claude/auth.json

# Windows
dir %APPDATA%\claude\auth.json
```

2. **Set API key environment variable:**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

3. **Pass API key directly:**

```python
from claude_oauth_auth import ClaudeClient

client = ClaudeClient(api_key="sk-ant-...")
```

4. **Verify credentials are available:**

```python
from claude_oauth_auth import UnifiedAuthManager

auth = UnifiedAuthManager()
print(f"Has credentials: {auth.has_credentials()}")
print(f"Auth method: {auth.auth_method}")
```

### Authentication Method Not Working

**Problem:** Expected OAuth but using API key (or vice versa).

**Solution:** Check which method is being used:

```python
from claude_oauth_auth import UnifiedAuthManager

auth = UnifiedAuthManager()
print(f"Using: {auth.auth_method}")

# Force specific method
if auth.auth_method != "oauth":
    print("OAuth not available, using API key fallback")
```

**Debug OAuth availability:**

```python
from claude_oauth_auth import OAuthTokenManager

try:
    oauth = OAuthTokenManager()
    if oauth.is_token_valid():
        print("OAuth tokens are valid")
    else:
        print("OAuth tokens expired or invalid")
except Exception as e:
    print(f"OAuth not available: {e}")
```

## OAuth Token Problems

### Token Expired

**Problem:** OAuth token has expired and isn't refreshing automatically.

```
TokenRefreshError: Failed to refresh OAuth token
```

**Solutions:**

1. **Manual refresh:**

```python
from claude_oauth_auth import OAuthTokenManager

token_manager = OAuthTokenManager()

try:
    new_token = token_manager.refresh_token()
    print("Token refreshed successfully")
except Exception as e:
    print(f"Refresh failed: {e}")
    print("You may need to re-authenticate with Claude Code")
```

2. **Check token expiration:**

```python
from claude_oauth_auth import OAuthTokenManager
from datetime import datetime

token_manager = OAuthTokenManager()
expiry = token_manager.get_token_expiration()
time_left = expiry - datetime.now()

print(f"Token expires: {expiry}")
print(f"Time remaining: {time_left}")

if time_left.total_seconds() < 0:
    print("Token has expired - refresh needed")
```

3. **Re-authenticate with Claude Code:**

If refresh fails, you may need to re-authenticate:

```bash
# Re-login to Claude Code
claude auth login
```

### Token File Not Found

**Problem:** Can't find OAuth token file.

**Solution:** Specify custom token location:

```python
from claude_oauth_auth import OAuthTokenManager
import os

# Option 1: Environment variable
os.environ['CLAUDE_AUTH_FILE'] = '/path/to/auth.json'
token_manager = OAuthTokenManager()

# Option 2: Direct parameter
token_manager = OAuthTokenManager(
    token_file='/path/to/auth.json'
)
```

### Token File Permissions

**Problem:** Can't read token file due to permissions.

**Solution:** Fix file permissions:

```bash
# Linux/macOS
chmod 600 ~/.config/claude/auth.json

# Check current permissions
ls -l ~/.config/claude/auth.json
```

```python
# Verify in Python
import os

token_file = os.path.expanduser("~/.config/claude/auth.json")
if os.path.exists(token_file):
    mode = oct(os.stat(token_file).st_mode)[-3:]
    print(f"File permissions: {mode}")
    if mode != '600':
        print("Warning: File should have 600 permissions")
```

### Invalid Token Format

**Problem:** Token file is corrupted or invalid format.

**Solution:** Validate token file:

```python
import json
import os

token_file = os.path.expanduser("~/.config/claude/auth.json")

try:
    with open(token_file) as f:
        data = json.load(f)

    # Check required fields
    required_fields = ['access_token', 'refresh_token', 'expires_at']
    for field in required_fields:
        if field not in data:
            print(f"Missing required field: {field}")

    print("Token file is valid")

except json.JSONDecodeError as e:
    print(f"Invalid JSON: {e}")
    print("Token file is corrupted - re-authenticate with Claude Code")

except FileNotFoundError:
    print("Token file not found")
```

## API Key Issues

### Invalid API Key Format

**Problem:** API key format is incorrect.

**Solution:** Verify API key format:

```python
from claude_oauth_auth import validate_api_key

api_key = "your-key-here"

if validate_api_key(api_key):
    print("Valid format")
else:
    print("Invalid format - should start with 'sk-ant-'")
```

Anthropic API keys should:
- Start with `sk-ant-`
- Be followed by a long string of characters
- Example: `sk-ant-api03-...`

### API Key Not Being Found

**Problem:** Set `ANTHROPIC_API_KEY` but it's not being used.

**Solutions:**

1. **Verify environment variable:**

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Check in Python
import os
print(f"API Key set: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
```

2. **Set in current process:**

```python
import os

os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'

# Then create client
from claude_oauth_auth import ClaudeClient
client = ClaudeClient()
```

3. **Check for OAuth override:**

```python
from claude_oauth_auth import UnifiedAuthManager

auth = UnifiedAuthManager()

# If OAuth is found, it takes precedence
if auth.auth_method == 'oauth':
    print("OAuth is being used instead of API key")
    # Force API key by disabling OAuth
    auth = UnifiedAuthManager(
        api_key=os.getenv('ANTHROPIC_API_KEY')
    )
```

### API Key Permissions

**Problem:** API key doesn't have required permissions.

**Solution:** Verify API key permissions and usage:

```python
from claude_oauth_auth import ClaudeClient

client = ClaudeClient()

try:
    # Test with simple request
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )
    print("API key is working")

except Exception as e:
    print(f"API key error: {e}")
    print("Check that your API key has proper permissions")
```

## Import and Installation Errors

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'claude_oauth_auth'`

**Solutions:**

1. **Install the package:**

```bash
pip install claude-oauth-auth
```

2. **Verify installation:**

```bash
pip list | grep claude-oauth-auth
```

3. **Check Python path:**

```python
import sys
print("Python executable:", sys.executable)
print("Python path:", sys.path)

# Verify installation
try:
    import claude_oauth_auth
    print("Package installed at:", claude_oauth_auth.__file__)
except ImportError as e:
    print(f"Import failed: {e}")
```

4. **Use virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

pip install claude-oauth-auth
```

### Import Errors for Specific Classes

**Problem:** `ImportError: cannot import name 'XYZ'`

**Solution:** Verify correct import paths:

```python
# Correct imports
from claude_oauth_auth import (
    UnifiedAuthManager,
    OAuthTokenManager,
    ClaudeClient,
    AsyncClaudeClient,
    AuthenticationError,
    TokenRefreshError
)

# Check what's available
import claude_oauth_auth
print("Available:", dir(claude_oauth_auth))
```

### Version Conflicts

**Problem:** Dependency version conflicts.

**Solution:**

1. **Check versions:**

```bash
pip show claude-oauth-auth
pip show anthropic
```

2. **Update dependencies:**

```bash
pip install --upgrade claude-oauth-auth
pip install --upgrade anthropic
```

3. **Use specific versions:**

```bash
pip install claude-oauth-auth==0.1.0
pip install anthropic>=0.7.0
```

## Network and Connection Issues

### Connection Timeout

**Problem:** Requests timing out.

**Solution:** Increase timeout or check network:

```python
from claude_oauth_auth import ClaudeClient
import anthropic

# Set custom timeout
client = ClaudeClient(timeout=60.0)

try:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hi"}]
    )
except anthropic.APITimeoutError as e:
    print(f"Request timed out: {e}")
    print("Check your internet connection")
```

### Rate Limiting

**Problem:** Getting rate limit errors.

```
anthropic.RateLimitError: Rate limit exceeded
```

**Solution:** Implement retry with exponential backoff:

```python
from claude_oauth_auth import ClaudeClient
import time
import anthropic

client = ClaudeClient()

def create_with_retry(max_retries=5, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + 1  # Exponential backoff
            print(f"Rate limited, waiting {wait_time}s...")
            time.sleep(wait_time)

response = create_with_retry(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hi"}]
)
```

### SSL/TLS Errors

**Problem:** SSL certificate verification errors.

**Solution:**

1. **Update certificates:**

```bash
# Update certifi
pip install --upgrade certifi
```

2. **Check system time:**

Ensure your system clock is correct.

3. **Use custom SSL context (not recommended for production):**

```python
import ssl
import anthropic

# Only for debugging - don't use in production
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE
```

## Enabling Debug Mode

### Enable Logging

Get detailed information about what's happening:

```python
import logging

# Enable debug logging for claude-oauth-auth
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now run your code
from claude_oauth_auth import UnifiedAuthManager

auth = UnifiedAuthManager()
```

### Detailed Diagnostics

Run comprehensive diagnostics:

```python
import os
import sys
from pathlib import Path

def diagnose():
    """Run comprehensive diagnostics."""
    print("=== Claude OAuth Auth Diagnostics ===\n")

    # Python info
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}\n")

    # Package info
    try:
        import claude_oauth_auth
        print(f"Package installed: Yes")
        print(f"Package location: {claude_oauth_auth.__file__}")
        print(f"Package version: {claude_oauth_auth.__version__}\n")
    except ImportError as e:
        print(f"Package installed: No ({e})\n")
        return

    # Environment variables
    print("Environment variables:")
    print(f"  ANTHROPIC_API_KEY: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Not set'}")
    print(f"  CLAUDE_AUTH_FILE: {os.getenv('CLAUDE_AUTH_FILE', 'Not set')}\n")

    # Token file
    from claude_oauth_auth import get_default_token_path
    token_path = get_default_token_path()
    print(f"Default token path: {token_path}")
    print(f"Token file exists: {Path(token_path).exists()}\n")

    # Authentication
    try:
        from claude_oauth_auth import UnifiedAuthManager
        auth = UnifiedAuthManager()
        print(f"Authentication method: {auth.auth_method}")
        print(f"Has credentials: {auth.has_credentials()}\n")
    except Exception as e:
        print(f"Authentication error: {e}\n")

    # OAuth status
    try:
        from claude_oauth_auth import OAuthTokenManager
        oauth = OAuthTokenManager()
        print("OAuth status:")
        print(f"  Token valid: {oauth.is_token_valid()}")
        if oauth.is_token_valid():
            expiry = oauth.get_token_expiration()
            print(f"  Expires at: {expiry}")
    except Exception as e:
        print(f"OAuth error: {e}")

    print("\n=== End Diagnostics ===")

diagnose()
```

### Test Connection

Verify everything is working:

```python
def test_connection():
    """Test connection to Claude API."""
    try:
        from claude_oauth_auth import ClaudeClient

        print("Creating client...")
        client = ClaudeClient()

        print("Sending test request...")
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": "Say 'test successful'"}]
        )

        print(f"Response: {response.content[0].text}")
        print("\nConnection test successful!")

    except Exception as e:
        print(f"Connection test failed: {e}")
        import traceback
        traceback.print_exc()

test_connection()
```

## Still Having Issues?

If you're still experiencing problems:

1. **Check the GitHub Issues**: [claude-oauth-auth/issues](https://github.com/astoreyai/claude-oauth-auth/issues)
2. **Review the documentation**: [User Guide](guide.md) | [API Reference](api.md)
3. **Run diagnostics**: Use the diagnostic script above
4. **Open an issue**: Include:
   - Python version
   - Package version
   - Error message and full traceback
   - Diagnostic output (remove sensitive info)
   - Minimal reproducible example

## Common Error Messages Quick Reference

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `No credentials found` | No OAuth tokens or API key | Set `ANTHROPIC_API_KEY` or use Claude Code |
| `Token expired` | OAuth token needs refresh | Run `token_manager.refresh_token()` |
| `Module not found` | Package not installed | Run `pip install claude-oauth-auth` |
| `Rate limit exceeded` | Too many requests | Implement exponential backoff |
| `Invalid API key` | Wrong key format | Verify key starts with `sk-ant-` |
| `Permission denied` | Token file permissions | Run `chmod 600 auth.json` |
| `Connection timeout` | Network issue | Increase timeout or check connection |

## Next Steps

- **[API Reference](api.md)**: Detailed API documentation
- **[Examples](examples.md)**: Working code examples
- **[User Guide](guide.md)**: Best practices and advanced usage
