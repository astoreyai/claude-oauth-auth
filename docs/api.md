# API Reference

Complete API documentation for `claude-oauth-auth`.

## Overview

The `claude-oauth-auth` library provides three main components:

1. **`OAuthTokenManager`**: Manages OAuth 2.0 tokens with automatic refresh
2. **`UnifiedAuthManager`**: Unified authentication with multiple fallback methods
3. **`ClaudeClient`**: Ready-to-use client for the Claude API

## Core Classes

### UnifiedAuthManager

The main authentication manager that automatically discovers and manages credentials.

::: claude_oauth_auth.UnifiedAuthManager
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

#### Example

```python
from claude_oauth_auth import UnifiedAuthManager

# Automatic credential discovery
auth = UnifiedAuthManager()

# Check authentication status
if auth.has_credentials():
    print(f"Using: {auth.auth_method}")
else:
    print("No credentials found")

# Get current credentials
credentials = auth.get_credentials()
```

#### Methods

##### `__init__(oauth_manager=None, api_key=None, config=None)`

Initialize the unified authentication manager.

**Parameters:**

- `oauth_manager` (OAuthTokenManager, optional): Custom OAuth token manager
- `api_key` (str, optional): API key for fallback authentication
- `config` (dict, optional): Configuration dictionary

**Example:**

```python
# Default initialization
auth = UnifiedAuthManager()

# With API key fallback
auth = UnifiedAuthManager(api_key="sk-ant-...")

# With custom OAuth manager
from claude_oauth_auth import OAuthTokenManager
oauth = OAuthTokenManager(refresh_token="...")
auth = UnifiedAuthManager(oauth_manager=oauth)
```

##### `has_credentials() -> bool`

Check if any credentials are available.

**Returns:** `bool` - True if credentials are available

##### `get_credentials() -> dict`

Get the current credentials.

**Returns:** `dict` - Credentials dictionary with keys:
- `type`: "oauth" or "api_key"
- `token`: Access token or API key
- `metadata`: Additional metadata

##### `auth_method -> str`

Get the authentication method being used.

**Returns:** `str` - "oauth", "api_key", or "none"

---

### OAuthTokenManager

Manages OAuth 2.0 tokens with automatic refresh and secure storage.

::: claude_oauth_auth.OAuthTokenManager
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

#### Example

```python
from claude_oauth_auth import OAuthTokenManager

# Automatic token discovery from Claude Code
token_manager = OAuthTokenManager()

# Get a valid access token (auto-refreshes if needed)
access_token = token_manager.get_valid_token()

# Check token status
if token_manager.is_token_valid():
    expiry = token_manager.get_token_expiration()
    print(f"Token valid until: {expiry}")
```

#### Methods

##### `__init__(refresh_token=None, access_token=None, token_expiry=None, client_id=None, token_file=None)`

Initialize the OAuth token manager.

**Parameters:**

- `refresh_token` (str, optional): OAuth refresh token
- `access_token` (str, optional): Current access token
- `token_expiry` (int, optional): Token expiration timestamp
- `client_id` (str, optional): OAuth client ID
- `token_file` (str, optional): Path to token storage file

**Example:**

```python
# Automatic discovery
token_manager = OAuthTokenManager()

# Manual configuration
token_manager = OAuthTokenManager(
    refresh_token="refresh_token_here",
    client_id="your_client_id",
    token_file="~/.my-app/tokens.json"
)
```

##### `get_valid_token() -> str`

Get a valid access token, refreshing if necessary.

**Returns:** `str` - Valid access token

**Raises:** `AuthenticationError` - If token refresh fails

**Example:**

```python
try:
    token = token_manager.get_valid_token()
    print(f"Token: {token[:20]}...")
except AuthenticationError as e:
    print(f"Failed to get token: {e}")
```

##### `is_token_valid() -> bool`

Check if the current access token is valid.

**Returns:** `bool` - True if token is valid and not expired

##### `refresh_token() -> str`

Manually refresh the access token.

**Returns:** `str` - New access token

**Raises:** `AuthenticationError` - If refresh fails

##### `get_token_expiration() -> datetime`

Get the token expiration time.

**Returns:** `datetime` - Token expiration timestamp

##### `save_tokens()`

Save tokens to persistent storage.

**Example:**

```python
# Update tokens
token_manager.access_token = "new_token"
token_manager.refresh_token = "new_refresh_token"

# Save to file
token_manager.save_tokens()
```

##### `load_tokens() -> bool`

Load tokens from persistent storage.

**Returns:** `bool` - True if tokens were successfully loaded

---

### ClaudeClient

Ready-to-use client for the Anthropic Claude API with authentication.

::: claude_oauth_auth.ClaudeClient
    options:
      show_root_heading: true
      show_source: true
      heading_level: 4

#### Example

```python
from claude_oauth_auth import ClaudeClient

# With automatic authentication
client = ClaudeClient()

# With specific API key
client = ClaudeClient(api_key="sk-ant-...")

# With custom auth manager
from claude_oauth_auth import UnifiedAuthManager
auth = UnifiedAuthManager()
client = ClaudeClient(auth_manager=auth)
```

#### Methods

##### `__init__(auth_manager=None, api_key=None, **kwargs)`

Initialize the Claude client.

**Parameters:**

- `auth_manager` (UnifiedAuthManager, optional): Authentication manager
- `api_key` (str, optional): Direct API key
- `**kwargs`: Additional arguments passed to Anthropic client

**Example:**

```python
# Default (uses OAuth or ANTHROPIC_API_KEY)
client = ClaudeClient()

# With API key
client = ClaudeClient(api_key="sk-ant-...")

# With custom configuration
client = ClaudeClient(
    api_key="sk-ant-...",
    max_retries=3,
    timeout=30.0
)
```

##### `messages.create(**kwargs)`

Create a message using the Claude API.

**Parameters:**

- `model` (str): Model identifier (e.g., "claude-3-5-sonnet-20241022")
- `max_tokens` (int): Maximum tokens in response
- `messages` (list): List of message dictionaries
- `**kwargs`: Additional API parameters

**Returns:** `Message` - API response object

**Example:**

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude!"}
    ],
    temperature=0.7,
    system="You are a helpful assistant."
)

print(response.content[0].text)
```

---

## Helper Functions

### discover_credentials()

Automatically discover credentials from all available sources.

::: claude_oauth_auth.discover_credentials
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

**Example:**

```python
from claude_oauth_auth import discover_credentials

credentials = discover_credentials()
if credentials:
    print(f"Found credentials: {credentials.type}")
    print(f"Source: {credentials.source}")
else:
    print("No credentials found")
```

### get_auth_status()

Get detailed authentication diagnostics.

::: claude_oauth_auth.get_auth_status
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

**Example:**

```python
from claude_oauth_auth import get_auth_status

status = get_auth_status()
print(status['summary'])
print(f"OAuth available: {status['oauth_available']}")
print(f"API key available: {status['api_key_available']}")
```

### create_anthropic_client()

Create an Anthropic SDK client with discovered credentials.

::: claude_oauth_auth.create_anthropic_client
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

**Example:**

```python
from claude_oauth_auth import create_anthropic_client

# Automatically uses best available credentials
client = create_anthropic_client()
```

### get_oauth_token()

Get an OAuth token from Claude Code.

::: claude_oauth_auth.get_oauth_token
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

**Example:**

```python
from claude_oauth_auth import get_oauth_token

token = get_oauth_token()
if token:
    print(f"OAuth token: {token[:20]}...")
else:
    print("No OAuth token available")
```

### is_oauth_available()

Check if OAuth authentication is available.

::: claude_oauth_auth.is_oauth_available
    options:
      show_root_heading: true
      show_source: false
      heading_level: 4

**Example:**

```python
from claude_oauth_auth import is_oauth_available

if is_oauth_available():
    print("OAuth is available")
else:
    print("OAuth not available, will use API key")
```

---

## Type Hints

All classes and methods include full type hints for IDE support and type checking.

```python
from typing import Optional, Dict, Any
from claude_oauth_auth import UnifiedAuthManager

def get_authenticated_client(
    api_key: Optional[str] = None
) -> UnifiedAuthManager:
    """Get an authenticated manager with type safety."""
    return UnifiedAuthManager(api_key=api_key)
```

---

## Next Steps

- **[Examples](examples.md)**: See real-world usage examples
- **[Troubleshooting](troubleshooting.md)**: Solve common issues
- **[User Guide](guide.md)**: Learn best practices
