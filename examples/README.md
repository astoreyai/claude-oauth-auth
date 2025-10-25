# Claude OAuth Auth - Examples

This directory contains production-ready integration examples for the `claude-oauth-auth` package. Each example demonstrates real-world usage patterns with complete, runnable code.

## Overview

All examples are fully functional and ready to run. Each subdirectory contains:
- Complete implementation code
- `requirements.txt` with all dependencies
- `README.md` with setup and usage instructions
- Proper error handling and logging
- Comments explaining key concepts

## Available Examples

### 1. Flask Web Application (`flask_app/`)
A complete Flask web application integrating Claude API with OAuth support.

**Features:**
- Request handlers for text generation
- Error handling and user feedback
- Streaming responses for long generations
- Session management
- Environment configuration

**Use Case:** Building web interfaces that interact with Claude API

### 2. FastAPI Application (`fastapi_app/`)
Modern async web application using FastAPI framework.

**Features:**
- Async handlers for better performance
- Dependency injection for authentication
- WebSocket streaming for real-time responses
- OpenAPI documentation
- Pydantic models for validation

**Use Case:** High-performance API services with Claude integration

### 3. CLI Tool (`cli_tool/`)
Production-ready command-line interface tool using Click.

**Features:**
- Interactive and non-interactive modes
- File input/output support
- Configuration management
- Progress indicators
- Rich terminal output

**Use Case:** Command-line automation and scripting

### 4. Batch Processor (`batch_processor/`)
Efficient batch processing of multiple prompts with concurrency.

**Features:**
- Thread pool for concurrent processing
- Progress tracking with tqdm
- Error recovery and retry logic
- Results export (JSON, CSV)
- Rate limiting

**Use Case:** Processing large datasets with Claude API

### 5. Jupyter Notebook (`jupyter/`)
Interactive notebook demonstrating Claude API usage.

**Features:**
- Cell-by-cell examples
- Visualizations of responses
- Authentication diagnostics
- Code examples with outputs
- Markdown explanations

**Use Case:** Exploratory analysis and prototyping

### 6. Testing Integration (`testing/`)
Comprehensive testing examples using pytest.

**Features:**
- Mock authentication for testing
- Reusable fixtures
- Integration test examples
- Test coverage setup
- CI/CD examples

**Use Case:** Testing applications that use Claude API

### 7. Docker Deployment (`docker/`)
Containerized application with OAuth credentials.

**Features:**
- Dockerfile for production deployment
- docker-compose for full stack
- Environment configuration
- Health checks
- Multi-stage builds

**Use Case:** Deploying Claude-powered applications

## Quick Start

Each example can be run independently. General steps:

1. **Navigate to example directory:**
   ```bash
   cd examples/flask_app  # or any other example
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up authentication:**

   Option A - Use Claude Code OAuth (automatic):
   ```bash
   # No setup needed if you have Claude Code installed
   ```

   Option B - Use API key:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-..."
   ```

   Option C - Use OAuth token:
   ```bash
   export ANTHROPIC_AUTH_TOKEN="sk-ant-oat01-..."
   ```

5. **Run the example:**
   ```bash
   # See individual example README for specific commands
   python app.py  # Flask
   uvicorn main:app  # FastAPI
   python claude_cli.py --help  # CLI
   # etc.
   ```

## Authentication Setup

All examples support multiple authentication methods:

### 1. Claude Code OAuth (Recommended)
If you have Claude Code installed, authentication is automatic:
```python
from claude_oauth_auth import ClaudeClient
client = ClaudeClient()  # Automatically finds OAuth token
```

### 2. API Key
Set environment variable or pass directly:
```python
client = ClaudeClient(api_key="sk-ant-api03-...")
```

### 3. OAuth Token
For Claude Max subscriptions:
```python
client = ClaudeClient(auth_token="sk-ant-oat01-...")
```

## Common Patterns

### Error Handling
```python
from claude_oauth_auth import ClaudeClient

try:
    client = ClaudeClient()
    response = client.generate("Hello, Claude!")
    print(response)
except ValueError as e:
    print(f"Authentication failed: {e}")
except RuntimeError as e:
    print(f"API call failed: {e}")
```

### Authentication Diagnostics
```python
from claude_oauth_auth import get_auth_status

# Check available authentication methods
status = get_auth_status()
print(status['summary'])
for method in status['available_methods']:
    print(f"  - {method}")
```

### Custom Model Configuration
```python
client = ClaudeClient(
    model="claude-sonnet-4-5-20250929",
    temperature=0.7,
    max_tokens=4096,
    verbose=True
)
```

## Project Structure

```
examples/
├── README.md                 # This file
├── flask_app/
│   ├── app.py
│   ├── requirements.txt
│   └── README.md
├── fastapi_app/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
├── cli_tool/
│   ├── claude_cli.py
│   ├── requirements.txt
│   └── README.md
├── batch_processor/
│   ├── processor.py
│   ├── requirements.txt
│   └── README.md
├── jupyter/
│   ├── claude_notebook.ipynb
│   └── README.md
├── testing/
│   ├── test_with_claude.py
│   ├── conftest.py
│   ├── requirements.txt
│   └── README.md
└── docker/
    ├── Dockerfile
    ├── docker-compose.yml
    ├── app.py
    ├── requirements.txt
    └── README.md
```

## Tips for Success

1. **Start Simple**: Begin with the Flask or CLI examples to understand basics
2. **Check Authentication**: Use `get_auth_status()` to debug credential issues
3. **Use Verbose Mode**: Enable `verbose=True` to see authentication details
4. **Handle Errors**: All examples show proper error handling patterns
5. **Read Comments**: Code comments explain key concepts and decisions

## Requirements

- Python 3.8 or higher
- `claude-oauth-auth` package installed
- Valid Anthropic credentials (API key or OAuth token)

## Support

For issues or questions:
- Check individual example READMEs for specific guidance
- Review main package documentation
- Check authentication with `get_auth_status()`
- Enable verbose mode for debugging

## Contributing

To add a new example:
1. Create a new subdirectory with descriptive name
2. Include complete, runnable code
3. Add `requirements.txt` with all dependencies
4. Write comprehensive `README.md`
5. Add entry to this main README
6. Test thoroughly

## License

All examples are provided under the MIT License, same as the main package.
