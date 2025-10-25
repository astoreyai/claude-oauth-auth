# Migration Guide

This guide helps you migrate from various authentication approaches to `claude-oauth-auth`.

## Table of Contents

- [Migration Scenarios](#migration-scenarios)
- [Migration Path 1: Raw API Key Usage](#migration-path-1-raw-api-key-usage)
- [Migration Path 2: Manual OAuth Implementation](#migration-path-2-manual-oauth-implementation)
- [Migration Path 3: Direct Anthropic SDK](#migration-path-3-direct-anthropic-sdk)
- [Migration Path 4: Custom Auth Solutions](#migration-path-4-custom-auth-solutions)
- [Step-by-Step Migration Checklist](#step-by-step-migration-checklist)
- [Common Pitfalls and Solutions](#common-pitfalls-and-solutions)
- [Testing Your Migration](#testing-your-migration)
- [Rollback Strategy](#rollback-strategy)

## Migration Scenarios

Before starting, identify which scenario matches your current setup:

| Current Setup | Complexity | Migration Time | Risk Level |
|--------------|------------|----------------|------------|
| Hardcoded API keys | Low | 15 minutes | Low |
| Environment variable API keys | Low | 10 minutes | Very Low |
| Manual OAuth flow | Medium | 1-2 hours | Medium |
| Custom auth solution | High | 2-4 hours | Medium |
| Multiple credential sources | High | 2-3 hours | Low |

## Migration Path 1: Raw API Key Usage

### Before: Hardcoded API Keys

```python
import anthropic

# ❌ Old approach - hardcoded credentials
client = anthropic.Anthropic(
    api_key="sk-ant-api03-xxx"  # Hardcoded - security risk!
)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Problems:**
- Security risk (credentials in code)
- No token refresh capability
- Difficult to rotate credentials
- Can't leverage OAuth benefits

### After: Unified Authentication

```python
from claude_oauth_auth import ClaudeClient

# ✅ New approach - automatic credential discovery
client = ClaudeClient()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Benefits:**
- No hardcoded credentials
- Automatic OAuth token discovery
- Fallback to API keys
- Automatic token refresh

### Migration Steps

1. **Install the package:**

```bash
pip install claude-oauth-auth
```

2. **Set environment variable (temporary fallback):**

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-xxx"
```

3. **Update your code:**

```python
# Old import
# import anthropic

# New import
from claude_oauth_auth import ClaudeClient

# Old client creation
# client = anthropic.Anthropic(api_key="sk-ant-api03-xxx")

# New client creation
client = ClaudeClient()

# All other code stays the same!
```

4. **Remove hardcoded credentials from code**

5. **Test thoroughly**

### Environment Variable Migration

If you're already using environment variables:

```python
# Before
import anthropic
import os

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)
```

```python
# After
from claude_oauth_auth import ClaudeClient

# Automatically reads ANTHROPIC_API_KEY
client = ClaudeClient()
```

**No other changes needed!** The library automatically detects `ANTHROPIC_API_KEY`.

## Migration Path 2: Manual OAuth Implementation

### Before: Manual OAuth Flow

```python
import requests
import json
from datetime import datetime, timedelta

class ManualOAuthHandler:
    def __init__(self):
        self.token_file = "tokens.json"
        self.access_token = None
        self.refresh_token = None
        self.expiry = None

    def load_tokens(self):
        with open(self.token_file) as f:
            data = json.load(f)
            self.access_token = data["access_token"]
            self.refresh_token = data["refresh_token"]
            self.expiry = datetime.fromisoformat(data["expiry"])

    def is_expired(self):
        return datetime.now() >= self.expiry

    def refresh_access_token(self):
        response = requests.post(
            "https://api.anthropic.com/v1/oauth/token",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
                "client_id": "your_client_id"
            }
        )
        data = response.json()
        self.access_token = data["access_token"]
        self.expiry = datetime.now() + timedelta(seconds=data["expires_in"])
        self.save_tokens()

    def get_valid_token(self):
        if self.is_expired():
            self.refresh_access_token()
        return self.access_token

    def save_tokens(self):
        with open(self.token_file, 'w') as f:
            json.dump({
                "access_token": self.access_token,
                "refresh_token": self.refresh_token,
                "expiry": self.expiry.isoformat()
            }, f)

# Usage
oauth_handler = ManualOAuthHandler()
oauth_handler.load_tokens()
token = oauth_handler.get_valid_token()

# Use token with client
import anthropic
client = anthropic.Anthropic(api_key=token)
```

**Problems:**
- 50+ lines of boilerplate code
- Manual token refresh logic
- No error handling
- File I/O management
- Expiry calculation complexity

### After: Automated OAuth Management

```python
from claude_oauth_auth import ClaudeClient

# ✅ All OAuth management handled automatically
client = ClaudeClient()

# That's it! Token loading, refresh, and management are automatic
```

**Benefits:**
- 2 lines vs 50+ lines
- Automatic token refresh
- Built-in error handling
- Thread-safe operations
- Automatic file management

### Detailed Migration Steps

1. **Back up your existing token file:**

```bash
cp tokens.json tokens.json.backup
```

2. **Identify your token location:**

```python
# Your current token file location
old_token_file = "tokens.json"  # or wherever you store them
```

3. **Install claude-oauth-auth:**

```bash
pip install claude-oauth-auth
```

4. **Check token format compatibility:**

```python
# Old format (example)
{
    "access_token": "xxx",
    "refresh_token": "yyy",
    "expiry": "2024-01-01T00:00:00"
}

# claude-oauth-auth expects (from Claude Code):
{
    "access_token": "xxx",
    "refresh_token": "yyy",
    "token_expiry": 1234567890,  # Unix timestamp
    "session_key": "zzz"
}
```

5. **Option A: Use Claude Code tokens (recommended):**

If you have Claude Code installed, just use its tokens:

```python
from claude_oauth_auth import ClaudeClient

# Automatically finds tokens from Claude Code
client = ClaudeClient()
```

6. **Option B: Migrate your existing tokens:**

```python
from claude_oauth_auth import OAuthTokenManager
import json
from datetime import datetime

# Load your old tokens
with open("tokens.json") as f:
    old_tokens = json.load(f)

# Create token manager with your tokens
token_manager = OAuthTokenManager(
    access_token=old_tokens["access_token"],
    refresh_token=old_tokens["refresh_token"],
    token_expiry=int(datetime.fromisoformat(old_tokens["expiry"]).timestamp())
)

# Use with client
from claude_oauth_auth import ClaudeClient
client = ClaudeClient(auth=token_manager)
```

7. **Remove old OAuth code:**

Delete your custom OAuth implementation classes and functions.

8. **Update all client instantiations:**

```python
# Before
oauth_handler = ManualOAuthHandler()
oauth_handler.load_tokens()
token = oauth_handler.get_valid_token()
client = anthropic.Anthropic(api_key=token)

# After
from claude_oauth_auth import ClaudeClient
client = ClaudeClient()
```

## Migration Path 3: Direct Anthropic SDK

### Before: Standard Anthropic SDK Usage

```python
import anthropic
import os

# Using Anthropic SDK directly
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### After: Enhanced with OAuth Support

```python
from claude_oauth_auth import ClaudeClient

# Drop-in replacement with OAuth support
client = ClaudeClient()

# Same API - no changes to request code!
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello"}]
)
```

### Migration Steps

1. **Install claude-oauth-auth:**

```bash
pip install claude-oauth-auth
```

2. **Replace imports:**

```python
# Before
import anthropic

# After
from claude_oauth_auth import ClaudeClient
```

3. **Update client initialization:**

```python
# Before
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# After
client = ClaudeClient()  # Automatically discovers credentials
```

4. **Keep all other code unchanged** - the API is identical!

### Advanced: Using Both Libraries

If you need gradual migration:

```python
from claude_oauth_auth import UnifiedAuthManager, create_anthropic_client
import anthropic

# Get credentials via claude-oauth-auth
auth = UnifiedAuthManager()

# Use with standard Anthropic client if needed
if auth.auth_method == "api_key":
    client = anthropic.Anthropic(api_key=auth.get_api_key())
else:
    # Use OAuth token
    token = auth.get_oauth_token()
    client = anthropic.Anthropic(api_key=token)

# Or use the helper function
client = create_anthropic_client()  # Handles both cases
```

## Migration Path 4: Custom Auth Solutions

### Before: Custom Authentication Manager

```python
class CustomAuthManager:
    def __init__(self):
        self.credentials = self.load_from_vault()

    def load_from_vault(self):
        # Custom logic to load from secrets manager
        pass

    def get_credentials(self):
        # Custom credential retrieval
        pass

    def rotate_credentials(self):
        # Custom rotation logic
        pass

auth = CustomAuthManager()
credentials = auth.get_credentials()
client = anthropic.Anthropic(api_key=credentials["api_key"])
```

### After: Extended Unified Manager

```python
from claude_oauth_auth import UnifiedAuthManager

class VaultAuthManager(UnifiedAuthManager):
    def __init__(self, vault_client):
        self.vault_client = vault_client
        super().__init__()

    def _discover_api_key(self):
        """Override to load from vault"""
        try:
            secret = self.vault_client.read_secret("claude/api_key")
            return secret["api_key"]
        except Exception:
            # Fall back to default discovery
            return super()._discover_api_key()

# Use extended manager
from my_vault import VaultClient
vault = VaultClient()
auth = VaultAuthManager(vault)

from claude_oauth_auth import ClaudeClient
client = ClaudeClient(auth=auth)
```

### Migration Steps

1. **Identify extension points:**

   - Credential loading
   - Credential rotation
   - Custom storage backends
   - Special authentication flows

2. **Extend UnifiedAuthManager:**

```python
from claude_oauth_auth import UnifiedAuthManager

class ExtendedAuthManager(UnifiedAuthManager):
    def _discover_credentials(self):
        """Add your custom discovery logic"""
        # Try custom sources first
        custom_creds = self.load_from_custom_source()
        if custom_creds:
            return custom_creds

        # Fall back to standard discovery
        return super()._discover_credentials()

    def load_from_custom_source(self):
        """Your custom logic here"""
        pass
```

3. **Replace custom manager:**

```python
# Before
auth = CustomAuthManager()

# After
auth = ExtendedAuthManager()
```

4. **Test edge cases thoroughly**

## Step-by-Step Migration Checklist

### Pre-Migration

- [ ] Identify current authentication method
- [ ] Document all credential sources
- [ ] Back up existing token/credential files
- [ ] Review security requirements
- [ ] Set up test environment
- [ ] Install claude-oauth-auth in test environment

### Migration

- [ ] Update imports in codebase
- [ ] Replace client initialization code
- [ ] Update credential loading logic
- [ ] Remove old authentication code
- [ ] Update environment variable names if needed
- [ ] Configure credential discovery paths
- [ ] Test basic authentication flow

### Testing

- [ ] Test with OAuth tokens (if available)
- [ ] Test with API key fallback
- [ ] Test token refresh mechanism
- [ ] Test error handling
- [ ] Verify all API calls work
- [ ] Load test with concurrent requests
- [ ] Test credential rotation

### Post-Migration

- [ ] Monitor authentication metrics
- [ ] Update documentation
- [ ] Train team on new system
- [ ] Remove old authentication libraries
- [ ] Update CI/CD pipelines
- [ ] Archive old credential files securely

### Production Deployment

- [ ] Deploy to staging environment
- [ ] Run smoke tests
- [ ] Deploy to production with monitoring
- [ ] Keep old system available for rollback
- [ ] Monitor error rates
- [ ] Verify performance metrics

## Common Pitfalls and Solutions

### Pitfall 1: Token File Not Found

**Problem:**
```python
from claude_oauth_auth import ClaudeClient
client = ClaudeClient()
# Error: No credentials found
```

**Solutions:**

1. **Set CLAUDE_AUTH_FILE environment variable:**

```bash
export CLAUDE_AUTH_FILE="/path/to/your/auth.json"
```

2. **Use API key fallback:**

```bash
export ANTHROPIC_API_KEY="sk-ant-xxx"
```

3. **Specify token location explicitly:**

```python
from claude_oauth_auth import OAuthTokenManager
token_manager = OAuthTokenManager(
    token_file="/path/to/tokens.json"
)

from claude_oauth_auth import ClaudeClient
client = ClaudeClient(auth=token_manager)
```

### Pitfall 2: Token Format Mismatch

**Problem:**
Your existing tokens don't match expected format.

**Solution:**
Convert your token format:

```python
import json
from datetime import datetime

# Load old format
with open("old_tokens.json") as f:
    old = json.load(f)

# Convert to new format
new_format = {
    "access_token": old["access_token"],
    "refresh_token": old["refresh_token"],
    "token_expiry": int(datetime.fromisoformat(old["expiry"]).timestamp()),
    "session_key": old.get("session_key", "")
}

# Save in new location
import os
new_path = os.path.expanduser("~/.config/claude/auth.json")
os.makedirs(os.path.dirname(new_path), exist_ok=True)

with open(new_path, 'w') as f:
    json.dump(new_format, f)
```

### Pitfall 3: Environment Variable Conflicts

**Problem:**
Multiple environment variables causing confusion.

**Solution:**

```python
# Clear old variables
import os
old_vars = ['OLD_CLAUDE_KEY', 'CLAUDE_TOKEN', 'CUSTOM_API_KEY']
for var in old_vars:
    os.environ.pop(var, None)

# Set standard variable
os.environ['ANTHROPIC_API_KEY'] = your_api_key

# Or use explicit configuration
from claude_oauth_auth import ClaudeClient
client = ClaudeClient(api_key=your_api_key)
```

### Pitfall 4: Thread Safety Issues

**Problem:**
Concurrent requests causing token refresh conflicts.

**Solution:**

```python
from claude_oauth_auth import ClaudeClient, UnifiedAuthManager

# Create one auth manager (thread-safe)
auth = UnifiedAuthManager()

# Share across threads
from concurrent.futures import ThreadPoolExecutor

def make_request(prompt):
    # Each thread gets its own client
    client = ClaudeClient(auth=auth)  # Reuse auth manager
    return client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}]
    )

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(make_request, prompts))
```

### Pitfall 5: Missing Dependencies

**Problem:**
Import errors after migration.

**Solution:**

```bash
# Ensure all dependencies installed
pip install claude-oauth-auth

# Or with specific version
pip install 'claude-oauth-auth>=0.1.0'

# For development features
pip install 'claude-oauth-auth[dev]'
```

### Pitfall 6: OAuth vs API Key Confusion

**Problem:**
Not sure which authentication method is being used.

**Solution:**

```python
from claude_oauth_auth import UnifiedAuthManager, get_auth_status

# Check authentication status
auth = UnifiedAuthManager()
print(f"Auth method: {auth.auth_method}")  # "oauth" or "api_key"

# Get detailed diagnostics
status = get_auth_status()
print(status['summary'])
```

### Pitfall 7: Credential Rotation During Migration

**Problem:**
Credentials change during migration process.

**Solution:**

```python
from claude_oauth_auth import UnifiedAuthManager

# Support multiple credential sources during transition
class TransitionAuthManager(UnifiedAuthManager):
    def __init__(self):
        super().__init__()
        self.old_api_key = self.load_old_credentials()

    def _discover_api_key(self):
        # Try new location first
        new_key = super()._discover_api_key()
        if new_key:
            return new_key

        # Fall back to old location during transition
        return self.old_api_key

    def load_old_credentials(self):
        # Load from your old location
        pass

auth = TransitionAuthManager()
```

## Testing Your Migration

### Unit Tests

```python
import pytest
from claude_oauth_auth import UnifiedAuthManager, ClaudeClient

def test_basic_authentication():
    """Test basic authentication works"""
    auth = UnifiedAuthManager()
    assert auth.has_credentials()
    assert auth.auth_method in ["oauth", "api_key"]

def test_client_creation():
    """Test client can be created"""
    client = ClaudeClient()
    assert client is not None

def test_api_call():
    """Test actual API call works"""
    client = ClaudeClient()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Hi"}]
    )
    assert response is not None
    assert len(response.content) > 0

@pytest.mark.parametrize("method", ["oauth", "api_key"])
def test_different_auth_methods(method, monkeypatch):
    """Test both authentication methods"""
    if method == "oauth":
        # Set up OAuth test environment
        monkeypatch.setenv("CLAUDE_AUTH_FILE", "/path/to/test/auth.json")
    else:
        # Set up API key test environment
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    auth = UnifiedAuthManager()
    assert auth.has_credentials()
```

### Integration Tests

```python
def test_end_to_end_migration():
    """Test complete migration flow"""
    # 1. Create client with old method (API key)
    import anthropic
    old_client = anthropic.Anthropic(api_key="test-key")

    # 2. Migrate to new client
    from claude_oauth_auth import ClaudeClient
    new_client = ClaudeClient(api_key="test-key")

    # 3. Verify same functionality
    old_response = old_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Test"}]
    )

    new_response = new_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Test"}]
    )

    assert type(old_response) == type(new_response)
```

### Performance Testing

```python
import time
from claude_oauth_auth import ClaudeClient

def test_authentication_performance():
    """Ensure migration doesn't degrade performance"""
    start = time.time()

    # Create 100 clients
    clients = [ClaudeClient() for _ in range(100)]

    elapsed = time.time() - start

    # Should be fast (under 1 second for 100 clients)
    assert elapsed < 1.0
    assert len(clients) == 100
```

## Rollback Strategy

### Preparation

Before migration, prepare rollback plan:

1. **Keep old code in version control:**

```bash
git checkout -b migration-backup
git add .
git commit -m "Backup before claude-oauth-auth migration"
git checkout main
```

2. **Document old configuration:**

```bash
# Save current environment
env | grep -E "(ANTHROPIC|CLAUDE)" > env_backup.txt

# Save current dependencies
pip freeze > requirements_old.txt
```

### Rollback Procedure

If you need to rollback:

1. **Revert code changes:**

```bash
git revert <migration-commit-hash>
```

2. **Reinstall old dependencies:**

```bash
pip install -r requirements_old.txt
```

3. **Restore environment variables:**

```bash
source env_backup.txt
```

4. **Verify old system works:**

```python
# Test old authentication
import anthropic
client = anthropic.Anthropic(api_key="your-key")
response = client.messages.create(...)
assert response is not None
```

### Gradual Rollback

For gradual rollback, support both systems temporarily:

```python
import os
from claude_oauth_auth import ClaudeClient
import anthropic

USE_NEW_AUTH = os.getenv("USE_NEW_AUTH", "false").lower() == "true"

if USE_NEW_AUTH:
    # New system
    client = ClaudeClient()
else:
    # Old system
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Rest of code works with either client
```

## Next Steps

After successful migration:

- Read the [Advanced Guide](advanced.md) for optimization tips
- Review [Architecture Documentation](architecture.md) to understand internals
- Check [FAQ](faq.md) for common questions
- Explore [Examples](examples.md) for integration patterns

## Getting Help

If you encounter issues during migration:

1. Check [Troubleshooting Guide](troubleshooting.md)
2. Review [FAQ](faq.md)
3. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
4. Open an issue on [GitHub](https://github.com/astoreyai/claude-oauth-auth/issues)
