# Flask Web Application Example

A production-ready Flask web application demonstrating Claude API integration with OAuth authentication.

## Features

- **Multiple Routes**: Web UI, REST API, health checks, and auth diagnostics
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Session Management**: Chat history with conversation context
- **API Endpoints**: RESTful API for programmatic access
- **Health Checks**: Monitoring endpoint for deployment
- **Auto-Discovery**: Automatic OAuth/API key detection

## Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up authentication:**

   The application supports multiple authentication methods (in priority order):

   **Option A: Claude Code OAuth (automatic)**
   ```bash
   # No setup needed if Claude Code is installed
   # Credentials automatically discovered from ~/.claude/.credentials.json
   ```

   **Option B: Environment variable (API key)**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-..."
   ```

   **Option C: Environment variable (OAuth token)**
   ```bash
   export ANTHROPIC_AUTH_TOKEN="sk-ant-oat01-..."
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

The app will start on http://localhost:5000

### Production Mode

Using Gunicorn (recommended for production):

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Options:
- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `--timeout 120`: Increase timeout for long Claude API calls

### Configuration

Configure using environment variables:

```bash
# Flask configuration
export FLASK_HOST="0.0.0.0"
export FLASK_PORT="5000"
export FLASK_DEBUG="False"
export SECRET_KEY="your-secret-key-here"

# Claude API (if not using auto-discovery)
export ANTHROPIC_API_KEY="sk-ant-api03-..."
# OR
export ANTHROPIC_AUTH_TOKEN="sk-ant-oat01-..."
```

Using `.env` file (with python-dotenv):

```env
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
SECRET_KEY=your-secret-key-here
ANTHROPIC_API_KEY=sk-ant-api03-...
```

## Available Endpoints

### Web Interface

- **GET /** - Home page with interactive form
- **POST /generate** - Generate response from form submission

### REST API

- **GET /api/generate** - Generate response (query params)
  ```bash
  curl "http://localhost:5000/api/generate?prompt=Hello%20Claude&max_tokens=100"
  ```

- **POST /api/generate** - Generate response (JSON body)
  ```bash
  curl -X POST http://localhost:5000/api/generate \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Explain OAuth 2.0", "max_tokens": 500}'
  ```

### Chat API

- **POST /chat** - Send message with conversation context
  ```bash
  curl -X POST http://localhost:5000/chat \
    -H "Content-Type: application/json" \
    -H "Cookie: session=..." \
    -d '{"message": "Tell me about Python"}'
  ```

- **POST /chat/reset** - Clear chat history
  ```bash
  curl -X POST http://localhost:5000/chat/reset
  ```

### Monitoring

- **GET /health** - Health check endpoint
  ```bash
  curl http://localhost:5000/health
  ```

  Response:
  ```json
  {
    "status": "healthy",
    "claude_client": "initialized",
    "auth_type": "oauth_token",
    "model": "claude-sonnet-4-5-20250929",
    "timestamp": "2025-10-24T12:00:00"
  }
  ```

- **GET /auth-status** - Detailed authentication status
  ```bash
  curl http://localhost:5000/auth-status
  ```

## Usage Examples

### Web Interface

1. Open http://localhost:5000 in your browser
2. Enter your prompt in the text area
3. Click "Generate Response"
4. View the response

### API Usage (Python)

```python
import requests

# Simple GET request
response = requests.get(
    "http://localhost:5000/api/generate",
    params={"prompt": "Explain machine learning"}
)
print(response.json()["response"])

# POST request with options
response = requests.post(
    "http://localhost:5000/api/generate",
    json={
        "prompt": "Write a haiku about programming",
        "max_tokens": 100,
        "temperature": 0.9
    }
)
print(response.json()["response"])
```

### API Usage (JavaScript)

```javascript
// Fetch API
fetch('http://localhost:5000/api/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    prompt: 'Explain quantum computing',
    max_tokens: 500
  })
})
  .then(res => res.json())
  .then(data => console.log(data.response));
```

### Chat with Context

```python
import requests

session = requests.Session()

# First message
response = session.post(
    "http://localhost:5000/chat",
    json={"message": "What is Python?"}
)
print(response.json()["response"])

# Follow-up (maintains context)
response = session.post(
    "http://localhost:5000/chat",
    json={"message": "What are its main features?"}
)
print(response.json()["response"])

# Reset conversation
session.post("http://localhost:5000/chat/reset")
```

## Error Handling

The application handles various error scenarios:

### Authentication Errors

If credentials are not found:
```json
{
  "error": "Claude client not initialized",
  "success": false
}
```

**Solution:** Set up authentication using one of the methods above.

### API Errors

If the Claude API call fails:
```json
{
  "error": "Claude API call failed: ...",
  "success": false,
  "prompt": "your prompt here"
}
```

### Validation Errors

If prompt is missing:
```json
{
  "error": "Prompt is required",
  "success": false
}
```

## Production Deployment

### Using Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with 4 workers
gunicorn -w 4 \
  --bind 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - \
  app:app
```

### Using Docker

See the `../docker/` example for containerized deployment.

### Environment Variables for Production

```bash
export FLASK_DEBUG=False
export SECRET_KEY="$(openssl rand -hex 32)"
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### Security Considerations

1. **Change secret key**: Use a strong random secret key in production
2. **Use HTTPS**: Deploy behind a reverse proxy with SSL
3. **Rate limiting**: Add rate limiting for API endpoints
4. **Input validation**: Validate and sanitize all user inputs
5. **Secure credentials**: Never commit credentials to version control

## Customization

### Change Claude Model

Edit `app.py`:
```python
claude_client = ClaudeClient(
    model="claude-opus-4-20250514",  # Use a different model
    temperature=0.8,
    max_tokens=2000
)
```

### Add Custom Routes

```python
@app.route("/custom")
def custom_route():
    # Your custom logic
    response = claude_client.generate("Custom prompt")
    return jsonify({"response": response})
```

### Add Middleware

```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
```

## Troubleshooting

### Issue: "Claude client not initialized"

**Cause:** No authentication credentials found.

**Solution:**
1. Check if Claude Code is installed and authenticated
2. Set `ANTHROPIC_API_KEY` or `ANTHROPIC_AUTH_TOKEN` environment variable
3. Run with verbose mode to see auth discovery:
   ```python
   claude_client = ClaudeClient(verbose=True)
   ```

### Issue: "Connection timeout"

**Cause:** Claude API call taking too long.

**Solution:**
- Increase timeout in production server:
  ```bash
  gunicorn --timeout 180 app:app
  ```
- Reduce `max_tokens` for faster responses

### Issue: "Rate limit exceeded"

**Cause:** Too many requests to Claude API.

**Solution:**
- Implement rate limiting
- Cache common responses
- Use queuing for batch requests

## Testing

Run the application and test endpoints:

```bash
# Start the app
python app.py

# In another terminal, test endpoints
curl http://localhost:5000/health
curl "http://localhost:5000/api/generate?prompt=Hello"

# Check auth status
curl http://localhost:5000/auth-status | jq
```

## Next Steps

- Add user authentication
- Implement rate limiting
- Add request logging
- Create admin dashboard
- Add response caching
- Implement streaming responses

## License

MIT License - see main package for details.
