# Complete Beginner Tutorial

A step-by-step guide to getting started with `claude-oauth-auth`. Perfect for developers new to the Claude API or OAuth authentication.

## Table of Contents

- [What You'll Learn](#what-youll-learn)
- [Prerequisites](#prerequisites)
- [Step 1: Installation](#step-1-installation)
- [Step 2: Your First API Call](#step-2-your-first-api-call)
- [Step 3: Understanding Authentication](#step-3-understanding-authentication)
- [Step 4: Error Handling](#step-4-error-handling)
- [Step 5: Production Setup](#step-5-production-setup)
- [Step 6: Testing Your Integration](#step-6-testing-your-integration)
- [Next Steps](#next-steps)
- [Troubleshooting](#troubleshooting)

## What You'll Learn

By the end of this tutorial, you'll be able to:

- Install and configure `claude-oauth-auth`
- Make your first API call to Claude
- Understand different authentication methods
- Handle errors gracefully
- Set up a production-ready configuration
- Test your integration thoroughly

**Time Required**: 30-45 minutes

## Prerequisites

Before starting, ensure you have:

- Python 3.8 or higher installed
- Basic knowledge of Python
- A terminal/command prompt
- Access to Claude API (either OAuth tokens or API key)

**Check Python Version:**

```bash
python --version
# Should show Python 3.8.x or higher
```

**Getting Claude API Access:**

You need ONE of the following:

1. **Claude Code** installed (provides OAuth tokens automatically)
   - Download from: https://claude.ai/code

2. **Anthropic API Key**
   - Get from: https://console.anthropic.com/

## Step 1: Installation

### 1.1 Create a Project Directory

```bash
# Create and navigate to project directory
mkdir claude-tutorial
cd claude-tutorial
```

### 1.2 Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### 1.3 Install claude-oauth-auth

```bash
pip install claude-oauth-auth
```

**Expected Output:**
```
Collecting claude-oauth-auth
  Downloading claude_oauth_auth-0.1.0-py3-none-any.whl
Collecting anthropic>=0.18.0
  Downloading anthropic-0.18.0-py3-none-any.whl
Installing collected packages: anthropic, claude-oauth-auth
Successfully installed anthropic-0.18.0 claude-oauth-auth-0.1.0
```

### 1.4 Verify Installation

```bash
python -c "import claude_oauth_auth; print(claude_oauth_auth.__version__)"
```

**Expected Output:**
```
0.1.0
```

**Checkpoint**: Installation complete!

## Step 2: Your First API Call

### 2.1 Create Your First Script

Create a file named `hello_claude.py`:

```python
"""
hello_claude.py - Your first Claude API call
"""

from claude_oauth_auth import ClaudeClient

# Create a client (automatically finds credentials)
client = ClaudeClient()

# Send a message to Claude
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=100,
    messages=[
        {"role": "user", "content": "Say hello and introduce yourself!"}
    ]
)

# Print the response
print("Claude says:")
print(response.content[0].text)
```

### 2.2 Run Your Script

```bash
python hello_claude.py
```

**Expected Output:**
```
Claude says:
Hello! I'm Claude, an AI assistant created by Anthropic. I'm here to help you with a wide variety of tasks...
```

### 2.3 What Just Happened?

Let's break down the code:

```python
# 1. Import the client
from claude_oauth_auth import ClaudeClient
```
This imports the main client class.

```python
# 2. Create a client
client = ClaudeClient()
```
This automatically:
- Searches for OAuth tokens from Claude Code
- Falls back to API key from environment
- Handles authentication for you

```python
# 3. Send a message
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # Which model to use
    max_tokens=100,                        # Maximum response length
    messages=[{"role": "user", "content": "..."}]  # Your message
)
```
This sends your message to Claude and gets a response.

```python
# 4. Extract the text
print(response.content[0].text)
```
The response contains the text from Claude.

**Checkpoint**: You've made your first API call!

## Step 3: Understanding Authentication

### 3.1 Check Your Authentication Method

Create a file named `check_auth.py`:

```python
"""
check_auth.py - Check which authentication method is being used
"""

from claude_oauth_auth import UnifiedAuthManager, get_auth_status

# Create auth manager
auth = UnifiedAuthManager()

# Print authentication method
print(f"Authentication method: {auth.auth_method}")
print(f"Has credentials: {auth.has_credentials()}")

# Get detailed status
print("\n=== Detailed Status ===")
status = get_auth_status()
print(status['summary'])

if status['oauth_available']:
    print(f"\nOAuth Token:")
    print(f"  - File: {status['oauth_token_file']}")
    print(f"  - Valid: {status['oauth_token_valid']}")
    if status['oauth_token_expiry']:
        print(f"  - Expires: {status['oauth_token_expiry']}")

if status['api_key_available']:
    print(f"\nAPI Key:")
    print(f"  - Source: {status['api_key_source']}")
```

### 3.2 Run Authentication Check

```bash
python check_auth.py
```

**Example Output (OAuth):**
```
Authentication method: oauth
Has credentials: True

=== Detailed Status ===
Authentication configured successfully using OAuth tokens

OAuth Token:
  - File: /home/user/.config/claude/auth.json
  - Valid: True
  - Expires: 2024-12-31 23:59:59
```

**Example Output (API Key):**
```
Authentication method: api_key
Has credentials: True

=== Detailed Status ===
Authentication configured successfully using API key

API Key:
  - Source: environment
```

### 3.3 Setting Up API Key Authentication

If you don't have Claude Code, set up API key authentication:

**Option A: Environment Variable (Recommended)**

```bash
# On macOS/Linux:
export ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"

# On Windows (Command Prompt):
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here

# On Windows (PowerShell):
$env:ANTHROPIC_API_KEY="sk-ant-api03-your-key-here"
```

**Option B: Direct in Code**

```python
from claude_oauth_auth import ClaudeClient

# Pass API key directly
client = ClaudeClient(api_key="sk-ant-api03-your-key-here")
```

**Option C: .env File**

Create a file named `.env`:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Then use python-dotenv:

```bash
pip install python-dotenv
```

```python
from dotenv import load_dotenv
from claude_oauth_auth import ClaudeClient

# Load environment variables from .env
load_dotenv()

# Create client (uses ANTHROPIC_API_KEY from .env)
client = ClaudeClient()
```

**Important**: Never commit `.env` or API keys to version control!

**Checkpoint**: You understand authentication methods!

## Step 4: Error Handling

### 4.1 Handling Common Errors

Create a file named `error_handling.py`:

```python
"""
error_handling.py - Proper error handling
"""

from claude_oauth_auth import ClaudeClient
from anthropic import APIError, AuthenticationError, RateLimitError

def safe_chat(prompt):
    """
    Send a message to Claude with error handling
    """
    try:
        client = ClaudeClient()
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Please check your API key or OAuth tokens.")
        return None

    except RateLimitError as e:
        print(f"Rate limit exceeded: {e}")
        print("Please wait before making more requests.")
        return None

    except APIError as e:
        print(f"API error occurred: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Test the function
if __name__ == "__main__":
    result = safe_chat("What is 2 + 2?")

    if result:
        print(f"Claude's answer: {result}")
    else:
        print("Failed to get response from Claude")
```

### 4.2 Adding Retry Logic

Create a file named `retry_example.py`:

```python
"""
retry_example.py - Retry logic for transient failures
"""

from claude_oauth_auth import ClaudeClient
from anthropic import APIError
import time

def chat_with_retry(prompt, max_retries=3):
    """
    Send a message with automatic retry on failure
    """
    client = ClaudeClient()

    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text

        except APIError as e:
            if attempt < max_retries - 1:
                # Calculate exponential backoff
                wait_time = 2 ** attempt
                print(f"Attempt {attempt + 1} failed. Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"All {max_retries} attempts failed: {e}")
                raise

# Test the function
if __name__ == "__main__":
    result = chat_with_retry("Tell me a short joke")
    print(f"Claude says: {result}")
```

### 4.3 Validating Credentials Before Use

```python
"""
validate_credentials.py - Check credentials before making requests
"""

from claude_oauth_auth import UnifiedAuthManager

def validate_setup():
    """
    Validate authentication setup before using
    """
    try:
        auth = UnifiedAuthManager()

        if not auth.has_credentials():
            print("ERROR: No credentials found!")
            print("\nPlease set up authentication:")
            print("  1. Install Claude Code, OR")
            print("  2. Set ANTHROPIC_API_KEY environment variable")
            return False

        print(f"✓ Credentials found")
        print(f"✓ Using {auth.auth_method} authentication")
        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    if validate_setup():
        print("\nReady to make API calls!")
        from claude_oauth_auth import ClaudeClient
        client = ClaudeClient()
        # ... make your API calls
    else:
        print("\nPlease fix authentication before continuing.")
```

**Checkpoint**: You can handle errors gracefully!

## Step 5: Production Setup

### 5.1 Environment-Specific Configuration

Create a file named `config.py`:

```python
"""
config.py - Environment-specific configuration
"""

import os

class Config:
    """Base configuration"""
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    MAX_TOKENS = 1024
    TIMEOUT = 30

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Uses OAuth from Claude Code in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Uses API key from environment in production
    API_KEY = os.getenv("ANTHROPIC_API_KEY")

    @classmethod
    def validate(cls):
        """Validate production configuration"""
        if not cls.API_KEY:
            raise ValueError("ANTHROPIC_API_KEY must be set in production")

# Select configuration based on environment
ENV = os.getenv("APP_ENV", "development")
if ENV == "production":
    config = ProductionConfig
    config.validate()
else:
    config = DevelopmentConfig
```

### 5.2 Create Production-Ready Client

Create a file named `production_client.py`:

```python
"""
production_client.py - Production-ready Claude client
"""

from claude_oauth_auth import ClaudeClient
from anthropic import APIError
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('claude_client.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ProductionClaudeClient:
    """
    Production-ready Claude client with logging, error handling, and monitoring
    """

    def __init__(self):
        """Initialize client with configuration"""
        self.client = None
        self.request_count = 0
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Claude client with proper error handling"""
        try:
            # Get API key from environment
            api_key = os.getenv("ANTHROPIC_API_KEY")

            if api_key:
                self.client = ClaudeClient(api_key=api_key)
                logger.info("Client initialized with API key")
            else:
                # Fall back to OAuth
                self.client = ClaudeClient()
                logger.info("Client initialized with OAuth")

        except Exception as e:
            logger.error(f"Failed to initialize client: {e}")
            raise

    def chat(self, prompt, max_tokens=1024, model="claude-3-5-sonnet-20241022"):
        """
        Send a chat message with logging and error handling

        Args:
            prompt: User prompt
            max_tokens: Maximum tokens in response
            model: Claude model to use

        Returns:
            Response text or None on error
        """
        self.request_count += 1
        request_id = self.request_count

        logger.info(f"[Request {request_id}] Sending prompt")

        try:
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}]
            )

            result = response.content[0].text
            logger.info(f"[Request {request_id}] Success")
            return result

        except APIError as e:
            logger.error(f"[Request {request_id}] API Error: {e}")
            return None

        except Exception as e:
            logger.error(f"[Request {request_id}] Unexpected error: {e}")
            return None

    def health_check(self):
        """
        Perform health check

        Returns:
            True if healthy, False otherwise
        """
        try:
            result = self.chat("Hello", max_tokens=10)
            return result is not None
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

# Example usage
if __name__ == "__main__":
    client = ProductionClaudeClient()

    # Health check
    if client.health_check():
        logger.info("System healthy")
    else:
        logger.error("System unhealthy")

    # Make a request
    response = client.chat("What is the capital of France?")
    if response:
        print(f"Response: {response}")
```

### 5.3 Docker Configuration

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Set environment
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["python", "production_client.py"]
```

Create `requirements.txt`:

```
claude-oauth-auth>=0.1.0
python-dotenv>=1.0.0
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  claude-app:
    build: .
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - APP_ENV=production
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
```

**Checkpoint**: You have a production-ready setup!

## Step 6: Testing Your Integration

### 6.1 Unit Tests

Create a file named `test_client.py`:

```python
"""
test_client.py - Unit tests for Claude integration
"""

import pytest
from claude_oauth_auth import ClaudeClient, UnifiedAuthManager

def test_client_initialization():
    """Test client can be initialized"""
    client = ClaudeClient()
    assert client is not None

def test_auth_manager():
    """Test authentication manager"""
    auth = UnifiedAuthManager()
    assert auth.has_credentials()
    assert auth.auth_method in ["oauth", "api_key"]

def test_simple_request():
    """Test simple API request"""
    client = ClaudeClient()
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say hi"}]
    )
    assert response is not None
    assert len(response.content) > 0
    assert response.content[0].text

def test_error_handling():
    """Test error handling with invalid input"""
    client = ClaudeClient()

    with pytest.raises(Exception):
        # This should fail - invalid model
        client.messages.create(
            model="invalid-model",
            max_tokens=10,
            messages=[{"role": "user", "content": "Test"}]
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 6.2 Run Tests

```bash
# Install pytest
pip install pytest

# Run tests
pytest test_client.py -v
```

**Expected Output:**
```
test_client.py::test_client_initialization PASSED
test_client.py::test_auth_manager PASSED
test_client.py::test_simple_request PASSED
test_client.py::test_error_handling PASSED

====== 4 passed in 2.34s ======
```

### 6.3 Integration Tests

Create a file named `integration_test.py`:

```python
"""
integration_test.py - Integration tests
"""

from claude_oauth_auth import ClaudeClient
import time

def test_conversation():
    """Test multi-turn conversation"""
    client = ClaudeClient()

    # First message
    response1 = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=50,
        messages=[{"role": "user", "content": "My name is Alice"}]
    )
    print(f"Response 1: {response1.content[0].text}")

    # Note: Each request is stateless, so context needs to be maintained
    # in the messages array for conversation context

    print("✓ Conversation test passed")

def test_rate_limiting():
    """Test handling of rate limits"""
    client = ClaudeClient()

    for i in range(5):
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=10,
                messages=[{"role": "user", "content": f"Test {i}"}]
            )
            print(f"Request {i}: Success")
            time.sleep(0.5)  # Be nice to the API
        except Exception as e:
            print(f"Request {i}: {e}")

    print("✓ Rate limiting test passed")

def test_long_response():
    """Test handling of long responses"""
    client = ClaudeClient()

    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": "Write a detailed explanation of OAuth 2.0"
        }]
    )

    assert len(response.content[0].text) > 100
    print(f"✓ Long response test passed ({len(response.content[0].text)} chars)")

if __name__ == "__main__":
    print("Running integration tests...\n")

    test_conversation()
    test_rate_limiting()
    test_long_response()

    print("\n✓ All integration tests passed!")
```

### 6.4 Load Testing

Create a file named `load_test.py`:

```python
"""
load_test.py - Simple load test
"""

from claude_oauth_auth import ClaudeClient
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

def make_request(request_id):
    """Make a single request"""
    client = ClaudeClient()
    start = time.time()

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            messages=[{"role": "user", "content": f"Request {request_id}"}]
        )
        elapsed = time.time() - start
        return {"id": request_id, "success": True, "time": elapsed}
    except Exception as e:
        elapsed = time.time() - start
        return {"id": request_id, "success": False, "time": elapsed, "error": str(e)}

def run_load_test(num_requests=10, max_workers=5):
    """Run load test"""
    print(f"Running load test: {num_requests} requests, {max_workers} concurrent workers")

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(make_request, i) for i in range(num_requests)]

        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            status = "✓" if result["success"] else "✗"
            print(f"{status} Request {result['id']}: {result['time']:.2f}s")

    total_time = time.time() - start_time

    # Calculate statistics
    successes = sum(1 for r in results if r["success"])
    failures = sum(1 for r in results if not r["success"])
    avg_time = sum(r["time"] for r in results) / len(results)

    print(f"\n=== Results ===")
    print(f"Total requests: {num_requests}")
    print(f"Successful: {successes}")
    print(f"Failed: {failures}")
    print(f"Average time: {avg_time:.2f}s")
    print(f"Total time: {total_time:.2f}s")
    print(f"Throughput: {num_requests / total_time:.2f} req/s")

if __name__ == "__main__":
    run_load_test(num_requests=10, max_workers=5)
```

**Checkpoint**: You can test your integration thoroughly!

## Next Steps

Congratulations! You've completed the tutorial. Here's what to explore next:

### 1. Advanced Features

- Read the [Advanced Guide](advanced.md) for:
  - Custom credential sources
  - Performance optimization
  - Advanced integration patterns

### 2. Production Deployment

- Review the [Migration Guide](migration.md) if migrating from other solutions
- Study the [Architecture Documentation](architecture.md) to understand internals
- Check the [FAQ](faq.md) for common questions

### 3. Real-World Examples

- Explore [Examples](examples.md) for:
  - Web framework integration (Flask, Django, FastAPI)
  - CLI tools
  - Background workers
  - Streaming responses

### 4. Best Practices

- Implement proper logging
- Set up monitoring and alerting
- Use environment-specific configurations
- Implement rate limiting
- Cache responses when appropriate

## Troubleshooting

### Problem: "No credentials found"

**Solution:**
```bash
# Check if Claude Code is installed and authenticated
ls ~/.config/claude/auth.json

# Or set API key
export ANTHROPIC_API_KEY="your-key"

# Verify
python -c "from claude_oauth_auth import get_auth_status; print(get_auth_status()['summary'])"
```

### Problem: "Token expired"

**Solution:**
Tokens are automatically refreshed. If this fails:
```bash
# Check token file
cat ~/.config/claude/auth.json

# Verify refresh token is present
python -c "from claude_oauth_auth import OAuthTokenManager; m = OAuthTokenManager(); print(m.get_valid_token())"
```

### Problem: "Rate limit exceeded"

**Solution:**
```python
import time

def rate_limited_request(prompt):
    time.sleep(1)  # Wait 1 second between requests
    client = ClaudeClient()
    return client.messages.create(...)
```

### Problem: Import errors

**Solution:**
```bash
# Ensure package is installed
pip install claude-oauth-auth

# Verify installation
pip show claude-oauth-auth

# Check Python version
python --version  # Should be 3.8+
```

### Need More Help?

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Review the [FAQ](faq.md)
3. Enable debug logging:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```
4. Open an issue on [GitHub](https://github.com/astoreyai/claude-oauth-auth/issues)

## Summary

You've learned:

- ✓ How to install claude-oauth-auth
- ✓ Making API calls to Claude
- ✓ Understanding authentication methods
- ✓ Handling errors properly
- ✓ Setting up production configuration
- ✓ Testing your integration

**You're ready to build with Claude!**
