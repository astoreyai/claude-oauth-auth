# FastAPI Application Example

A modern async FastAPI application demonstrating Claude API integration with dependency injection, WebSocket streaming, and comprehensive API documentation.

## Features

- **Async Handlers**: Non-blocking async operations for better performance
- **Dependency Injection**: Clean separation of concerns with FastAPI dependencies
- **WebSocket Streaming**: Real-time text generation over WebSocket
- **OpenAPI Documentation**: Auto-generated Swagger UI and ReDoc
- **Pydantic Validation**: Type-safe request/response models
- **CORS Support**: Cross-origin requests enabled
- **Error Handling**: Comprehensive exception handling

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

   **Option A: Claude Code OAuth (automatic)**
   ```bash
   # No setup needed if Claude Code is installed
   ```

   **Option B: API key**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-api03-..."
   ```

   **Option C: OAuth token**
   ```bash
   export ANTHROPIC_AUTH_TOKEN="sk-ant-oat01-..."
   ```

## Running the Application

### Development Mode

```bash
uvicorn main:app --reload
```

The app will start on http://localhost:8000

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Options:
- `--workers 4`: 4 worker processes for handling concurrent requests
- `--host 0.0.0.0`: Listen on all network interfaces
- `--port 8000`: Port number
- `--log-level info`: Logging level

### Configuration

Using environment variables:

```bash
export API_HOST="0.0.0.0"
export API_PORT="8000"
export API_RELOAD="False"
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

## API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
  - Interactive API documentation
  - Test endpoints directly in browser
  - See request/response schemas

- **ReDoc**: http://localhost:8000/redoc
  - Alternative documentation interface
  - Better for reading and understanding API

## Available Endpoints

### General

- **GET /** - API information and endpoint list
  ```bash
  curl http://localhost:8000/
  ```

### Monitoring

- **GET /health** - Health check endpoint
  ```bash
  curl http://localhost:8000/health
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
  curl http://localhost:8000/auth-status
  ```

### Claude API

- **POST /api/generate** - Generate text
  ```bash
  curl -X POST http://localhost:8000/api/generate \
    -H "Content-Type: application/json" \
    -d '{
      "prompt": "Explain async programming in Python",
      "max_tokens": 500,
      "temperature": 0.7
    }'
  ```

  Response:
  ```json
  {
    "success": true,
    "response": "Async programming in Python...",
    "prompt": "Explain async programming in Python",
    "model": "claude-sonnet-4-5-20250929",
    "timestamp": "2025-10-24T12:00:00",
    "tokens_used": 234
  }
  ```

- **POST /api/chat** - Chat with context
  ```bash
  curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{
      "message": "What is FastAPI?",
      "max_tokens": 1000
    }'
  ```

- **POST /api/stream** - Streaming response
  ```bash
  curl -X POST http://localhost:8000/api/stream \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Write a story about AI"}' \
    --no-buffer
  ```

## WebSocket Usage

### Python Client

```python
import asyncio
import json
import websockets

async def test_websocket():
    uri = "ws://localhost:8000/ws/generate"
    async with websockets.connect(uri) as websocket:
        # Send request
        await websocket.send(json.dumps({
            "prompt": "Explain WebSockets",
            "max_tokens": 200
        }))

        # Receive response
        response = await websocket.recv()
        data = json.loads(response)
        print(data["response"])

asyncio.run(test_websocket())
```

### JavaScript Client

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/generate');

ws.onopen = () => {
  ws.send(JSON.stringify({
    prompt: 'What are WebSockets?',
    max_tokens: 300
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data.response);
};
```

## Usage Examples

### Python with httpx

```python
import httpx
import asyncio

async def generate_text():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/generate",
            json={
                "prompt": "What is machine learning?",
                "max_tokens": 500,
                "temperature": 0.7
            }
        )
        data = response.json()
        print(data["response"])

asyncio.run(generate_text())
```

### Python with requests (sync)

```python
import requests

response = requests.post(
    "http://localhost:8000/api/generate",
    json={
        "prompt": "Explain neural networks",
        "max_tokens": 400
    }
)
print(response.json()["response"])
```

### JavaScript with fetch

```javascript
async function generateText() {
  const response = await fetch('http://localhost:8000/api/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      prompt: 'What is deep learning?',
      max_tokens: 500
    })
  });

  const data = await response.json();
  console.log(data.response);
}
```

### Streaming Example

```python
import requests

response = requests.post(
    "http://localhost:8000/api/stream",
    json={"prompt": "Tell me a story about robots"},
    stream=True
)

for line in response.iter_lines():
    if line:
        decoded_line = line.decode('utf-8')
        if decoded_line.startswith('data: '):
            chunk = decoded_line[6:]  # Remove 'data: ' prefix
            if chunk != '[DONE]':
                print(chunk, end='', flush=True)
```

## Request/Response Models

### GenerateRequest

```python
{
  "prompt": "string (1-10000 chars, required)",
  "max_tokens": "integer (1-8000, optional)",
  "temperature": "float (0.0-1.0, optional)",
  "system": "string (optional system prompt)"
}
```

### GenerateResponse

```python
{
  "success": true,
  "response": "string (generated text)",
  "prompt": "string (original prompt)",
  "model": "string (model name)",
  "timestamp": "string (ISO 8601)",
  "tokens_used": "integer (approximate)"
}
```

### ErrorResponse

```python
{
  "success": false,
  "error": "string (error message)",
  "detail": "string (optional details)",
  "timestamp": "string (ISO 8601)"
}
```

## Dependency Injection

The app uses FastAPI's dependency injection for clean code:

```python
from fastapi import Depends
from claude_oauth_auth import ClaudeClient

def get_claude_client() -> ClaudeClient:
    """Dependency that provides Claude client."""
    if claude_client is None:
        raise HTTPException(status_code=503)
    return claude_client

@app.post("/api/generate")
async def generate(
    request: GenerateRequest,
    client: ClaudeClient = Depends(get_claude_client)
):
    # Use client here
    response = await loop.run_in_executor(
        None, lambda: client.generate(request.prompt)
    )
    return {"response": response}
```

## CORS Configuration

CORS is enabled for all origins by default. For production, restrict to specific origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Specific methods
    allow_headers=["*"],
)
```

## Error Handling

The app includes comprehensive error handling:

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Service Unavailable

```json
{
  "success": false,
  "error": "Claude client not initialized. Check authentication credentials.",
  "timestamp": "2025-10-24T12:00:00"
}
```

### Internal Server Error

```json
{
  "success": false,
  "error": "Internal server error",
  "detail": "Specific error details...",
  "timestamp": "2025-10-24T12:00:00"
}
```

## Production Deployment

### Using Gunicorn with Uvicorn Workers

```bash
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Environment Variables for Production

```bash
export API_HOST="0.0.0.0"
export API_PORT="8000"
export API_RELOAD="False"
export ANTHROPIC_API_KEY="sk-ant-api03-..."
```

### Security Considerations

1. **Restrict CORS**: Set specific allowed origins
2. **Rate Limiting**: Add rate limiting middleware
3. **API Keys**: Implement API key authentication for endpoints
4. **HTTPS**: Deploy behind reverse proxy with SSL
5. **Validation**: Validate all inputs (Pydantic handles this)

## Testing

### Test Health Endpoint

```bash
curl http://localhost:8000/health | jq
```

### Test Generation

```bash
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello Claude"}' | jq
```

### Test WebSocket

```bash
# Install websocat: https://github.com/vi/websocat
echo '{"prompt": "Hello", "max_tokens": 50}' | \
  websocat ws://localhost:8000/ws/generate
```

## Performance Tips

1. **Use async/await**: All I/O operations should be async
2. **Worker processes**: Use multiple workers for CPU-bound tasks
3. **Connection pooling**: Reuse HTTP connections
4. **Caching**: Cache common responses
5. **Rate limiting**: Prevent API abuse

## Customization

### Add Custom Endpoint

```python
@app.post("/custom/analyze")
async def analyze_text(
    text: str,
    client: ClaudeClient = Depends(get_claude_client)
):
    # Custom analysis logic
    prompt = f"Analyze this text: {text}"
    response = await loop.run_in_executor(
        None, lambda: client.generate(prompt)
    )
    return {"analysis": response}
```

### Add Middleware

```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## Troubleshooting

### Issue: "Claude client not initialized"

**Solution:**
1. Check authentication credentials
2. Enable verbose mode in ClaudeClient initialization
3. Check `/auth-status` endpoint for details

### Issue: WebSocket connection fails

**Solution:**
1. Ensure WebSocket support is installed: `pip install websockets`
2. Check firewall settings
3. Verify WebSocket URL uses `ws://` not `http://`

### Issue: Slow response times

**Solution:**
1. Increase worker processes
2. Use async operations properly
3. Reduce `max_tokens` for faster responses
4. Implement caching for common requests

## Next Steps

- Add authentication middleware
- Implement rate limiting
- Add request logging
- Create admin endpoints
- Add response caching
- Implement background tasks

## License

MIT License - see main package for details.
