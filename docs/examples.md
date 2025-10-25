# Examples

Real-world code examples for `claude-oauth-auth`.

## Table of Contents

- [Basic Usage](#basic-usage)
- [OAuth Examples](#oauth-examples)
- [API Key Examples](#api-key-examples)
- [Error Handling](#error-handling)
- [Advanced Patterns](#advanced-patterns)
- [Integration Examples](#integration-examples)

## Basic Usage

### Simplest Possible Usage

```python
from claude_oauth_auth import ClaudeClient

# One line - automatic authentication
client = ClaudeClient()

# Make a request
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.content[0].text)
```

### Check Authentication Status

```python
from claude_oauth_auth import UnifiedAuthManager

auth = UnifiedAuthManager()

if auth.has_credentials():
    print(f"Authenticated via: {auth.auth_method}")
    credentials = auth.get_credentials()
    print(f"Credential type: {credentials['type']}")
else:
    print("No credentials found")
    print("Please set ANTHROPIC_API_KEY or configure OAuth")
```

### Multi-Turn Conversation

```python
from claude_oauth_auth import ClaudeClient

client = ClaudeClient()

# Start a conversation
messages = []

def chat(user_message):
    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=messages
    )

    assistant_message = response.content[0].text
    messages.append({"role": "assistant", "content": assistant_message})

    return assistant_message

# Have a conversation
print(chat("What is Python?"))
print(chat("Can you give me a code example?"))
print(chat("Explain that example in detail"))
```

## OAuth Examples

### Using Claude Code OAuth

```python
from claude_oauth_auth import OAuthTokenManager

# Automatically uses tokens from Claude Code
token_manager = OAuthTokenManager()

# Get token info
if token_manager.is_token_valid():
    expiry = token_manager.get_token_expiration()
    print(f"Token valid until: {expiry}")

    # Get the actual token
    access_token = token_manager.get_valid_token()
    print(f"Access token: {access_token[:20]}...")
else:
    print("No valid OAuth token found")
```

### Manual Token Refresh

```python
from claude_oauth_auth import OAuthTokenManager, TokenRefreshError

token_manager = OAuthTokenManager()

try:
    # Check if refresh is needed
    if not token_manager.is_token_valid():
        print("Token expired, refreshing...")
        new_token = token_manager.refresh_token()
        print(f"New token obtained: {new_token[:20]}...")
    else:
        print("Token still valid")
except TokenRefreshError as e:
    print(f"Failed to refresh token: {e}")
```

### Custom Token Storage

```python
from claude_oauth_auth import OAuthTokenManager
import os

# Use custom token location
custom_path = os.path.expanduser("~/.my-app/oauth_tokens.json")

token_manager = OAuthTokenManager(token_file=custom_path)

# Use the token
access_token = token_manager.get_valid_token()
```

### OAuth with Environment Variable

```python
import os
from claude_oauth_auth import OAuthTokenManager

# Point to custom auth file
os.environ['CLAUDE_AUTH_FILE'] = '/path/to/custom/auth.json'

# Will use the custom path
token_manager = OAuthTokenManager()
token = token_manager.get_valid_token()
```

## API Key Examples

### From Environment Variable

```python
import os
from claude_oauth_auth import ClaudeClient

# Set environment variable
os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'

# Client will automatically use it
client = ClaudeClient()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Direct API Key

```python
from claude_oauth_auth import ClaudeClient

# Pass API key directly
client = ClaudeClient(api_key="sk-ant-...")

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### API Key from Configuration File

```python
import json
from claude_oauth_auth import ClaudeClient

# Load from config file
with open('config.json') as f:
    config = json.load(f)

client = ClaudeClient(api_key=config['anthropic_api_key'])
```

### API Key from Secrets Manager

```python
from claude_oauth_auth import ClaudeClient
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response['SecretString'])
    except ClientError as e:
        raise e

# Get API key from AWS Secrets Manager
secrets = get_secret('claude-api-credentials')
client = ClaudeClient(api_key=secrets['api_key'])
```

## Error Handling

### Comprehensive Error Handling

```python
from claude_oauth_auth import (
    ClaudeClient,
    AuthenticationError,
    TokenRefreshError,
    ConfigurationError
)
import anthropic

try:
    client = ClaudeClient()

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": "Hello!"}]
    )

    print(response.content[0].text)

except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Please check your credentials")

except TokenRefreshError as e:
    print(f"Token refresh failed: {e}")
    print("Please re-authenticate")

except anthropic.APIError as e:
    print(f"API error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

### Retry with Exponential Backoff

```python
from claude_oauth_auth import ClaudeClient
import time

client = ClaudeClient()

def create_message_with_retry(max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            return client.messages.create(**kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
            time.sleep(wait_time)

# Use with retry
response = create_message_with_retry(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Graceful Degradation

```python
from claude_oauth_auth import UnifiedAuthManager, AuthenticationError

def get_authenticated_client():
    """Get client with graceful degradation."""
    try:
        # Try OAuth first
        auth = UnifiedAuthManager()
        if auth.auth_method == "oauth":
            print("Using OAuth authentication")
            return ClaudeClient(auth_manager=auth)
    except Exception as e:
        print(f"OAuth failed: {e}")

    try:
        # Fall back to API key
        print("Falling back to API key")
        return ClaudeClient()  # Will use ANTHROPIC_API_KEY
    except Exception as e:
        print(f"API key authentication failed: {e}")

    raise AuthenticationError("No authentication method available")

client = get_authenticated_client()
```

## Advanced Patterns

### Async/Await Pattern

```python
# Note: Async support is planned for a future release
# For now, use synchronous client with threading for concurrency

from concurrent.futures import ThreadPoolExecutor
from claude_oauth_auth import ClaudeClient

def process_request(question_num):
    client = ClaudeClient()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": f"Question {question_num}"}]
    )
    return response.content[0].text

# Process 10 requests concurrently using threads
with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(process_request, i) for i in range(10)]
    responses = [future.result() for future in futures]

for i, response in enumerate(responses):
    print(f"Response {i}: {response}")
```

### Context Manager Pattern

```python
from claude_oauth_auth import ClaudeClient
from contextlib import contextmanager

@contextmanager
def claude_session(api_key=None):
    """Context manager for Claude client."""
    client = ClaudeClient(api_key=api_key)
    try:
        yield client
    finally:
        # Cleanup if needed
        pass

# Use with context manager
with claude_session() as client:
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.content[0].text)
```

### Streaming Responses

```python
from claude_oauth_auth import ClaudeClient

client = ClaudeClient()

# Stream the response
with client.messages.stream(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a story"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

### Token Usage Tracking

```python
from claude_oauth_auth import ClaudeClient

client = ClaudeClient()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)

# Track token usage
usage = response.usage
print(f"Input tokens: {usage.input_tokens}")
print(f"Output tokens: {usage.output_tokens}")
print(f"Total tokens: {usage.input_tokens + usage.output_tokens}")
```

## Integration Examples

### Flask Web Application

```python
from flask import Flask, request, jsonify
from claude_oauth_auth import ClaudeClient

app = Flask(__name__)
client = ClaudeClient()

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": user_message}]
        )

        return jsonify({
            'response': response.content[0].text,
            'model': response.model,
            'usage': {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

### FastAPI Application

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from claude_oauth_auth import ClaudeClient

app = FastAPI()
client = ClaudeClient()

class ChatRequest(BaseModel):
    message: str
    max_tokens: int = 1024

class ChatResponse(BaseModel):
    response: str
    model: str
    input_tokens: int
    output_tokens: int

@app.post('/chat', response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=request.max_tokens,
            messages=[{"role": "user", "content": request.message}]
        )

        return ChatResponse(
            response=response.content[0].text,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Command-Line Tool

```python
#!/usr/bin/env python3
import argparse
from claude_oauth_auth import ClaudeClient

def main():
    parser = argparse.ArgumentParser(description='Claude CLI')
    parser.add_argument('message', help='Message to send to Claude')
    parser.add_argument('--model', default='claude-3-5-sonnet-20241022')
    parser.add_argument('--max-tokens', type=int, default=1024)
    parser.add_argument('--api-key', help='API key (optional)')

    args = parser.parse_args()

    client = ClaudeClient(api_key=args.api_key)

    response = client.messages.create(
        model=args.model,
        max_tokens=args.max_tokens,
        messages=[{"role": "user", "content": args.message}]
    )

    print(response.content[0].text)

if __name__ == '__main__':
    main()
```

Usage:

```bash
# With OAuth
./claude-cli.py "What is Python?"

# With API key
./claude-cli.py "What is Python?" --api-key sk-ant-...

# With custom model
./claude-cli.py "Hello" --model claude-3-opus-20240229
```

### Jupyter Notebook

```python
# Cell 1: Setup
from claude_oauth_auth import ClaudeClient
import os

# Configure
os.environ['ANTHROPIC_API_KEY'] = 'your-key-here'  # Or use OAuth
client = ClaudeClient()

# Cell 2: Helper function
def ask_claude(question, max_tokens=1024):
    """Ask Claude a question and display the response."""
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text

# Cell 3: Use it
answer = ask_claude("Explain machine learning in simple terms")
print(answer)
```

### Testing with Pytest

```python
import pytest
from unittest.mock import patch, MagicMock
from claude_oauth_auth import UnifiedAuthManager, ClaudeClient

@pytest.fixture
def mock_client():
    """Fixture providing a mocked Claude client."""
    with patch('claude_oauth_auth.ClaudeClient') as mock:
        yield mock

def test_authentication_with_api_key():
    """Test authentication with API key."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        auth = UnifiedAuthManager()
        assert auth.has_credentials()
        assert auth.auth_method == 'api_key'

def test_oauth_authentication():
    """Test OAuth authentication."""
    with patch('claude_oauth_auth.OAuthTokenManager') as mock_oauth:
        mock_oauth.return_value.is_token_valid.return_value = True
        mock_oauth.return_value.get_valid_token.return_value = 'test-token'

        auth = UnifiedAuthManager()
        assert auth.has_credentials()

def test_message_creation(mock_client):
    """Test message creation."""
    mock_response = MagicMock()
    mock_response.content[0].text = "Hello!"
    mock_client.return_value.messages.create.return_value = mock_response

    client = ClaudeClient()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hi"}]
    )

    assert response.content[0].text == "Hello!"
```

## Production-Ready Integration Examples

For complete, runnable applications demonstrating best practices, see the **[examples/](../examples/)** directory which includes:

### Web Frameworks

- **[Flask Application](../examples/flask_app/)**: Complete Flask web app with request handlers, error handling, streaming responses, and session management. Perfect for building web interfaces that interact with Claude API.

- **[FastAPI Application](../examples/fastapi_app/)**: Modern async FastAPI app with dependency injection, WebSocket streaming, OpenAPI documentation, and Pydantic validation. Ideal for high-performance API services.

### Command-Line Tools

- **[CLI Tool](../examples/cli_tool/)**: Production CLI using Click with interactive mode, file I/O, configuration management, progress indicators, and rich terminal output. Great for command-line automation.

### Batch Processing

- **[Batch Processor](../examples/batch_processor/)**: Efficiently process multiple prompts concurrently with thread pool, progress tracking, error recovery, rate limiting, and results export (JSON/CSV).

### Notebooks

- **[Jupyter Notebook](../examples/jupyter/)**: Interactive notebook with cell-by-cell examples, authentication diagnostics, visualizations, and exploratory analysis patterns.

### Testing

- **[Testing Integration](../examples/testing/)**: Comprehensive pytest examples with mocking, fixtures, integration tests, test coverage setup, and CI/CD patterns.

### Deployment

- **[Docker Deployment](../examples/docker/)**: Containerized application with Dockerfile, docker-compose, environment configuration, health checks, and production deployment best practices.

Each example includes:
- Complete, runnable code
- `requirements.txt` with all dependencies
- Comprehensive `README.md` with setup and usage instructions
- Proper error handling and logging
- Comments explaining key concepts

See **[examples/README.md](../examples/README.md)** for detailed overview and quick start instructions.

## Next Steps

- **[API Reference](api.md)**: Detailed API documentation
- **[Troubleshooting](troubleshooting.md)**: Solve common issues
- **[User Guide](guide.md)**: Learn best practices
