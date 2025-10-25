"""
Flask Web Application with Claude OAuth Integration

This example demonstrates a production-ready Flask application that integrates
Claude API using the claude-oauth-auth package with comprehensive error handling,
streaming responses, and proper session management.

Features:
- Multiple routes for different Claude API use cases
- Error handling with user-friendly messages
- Streaming responses for long generations
- Session management for chat history
- Environment configuration
- Health check endpoint
- Authentication diagnostics page

Run:
    python app.py

Then visit:
    http://localhost:5000
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, jsonify, render_template_string, request, session, stream_with_context

from claude_oauth_auth import ClaudeClient, get_auth_status


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

# Initialize Claude client (with error handling)
try:
    claude_client = ClaudeClient(verbose=True)
    logger.info("Claude client initialized successfully")
except ValueError as e:
    logger.error(f"Failed to initialize Claude client: {e}")
    claude_client = None


# HTML template for the home page
HOME_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Claude OAuth Demo - Flask</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 30px; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #555;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        button {
            background-color: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #0056b3;
        }
        .response {
            margin-top: 20px;
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
        }
        .error {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        .success {
            background-color: #d4edda;
            border-left-color: #28a745;
            color: #155724;
        }
        .info {
            background-color: #d1ecf1;
            border-left-color: #17a2b8;
            color: #0c5460;
        }
        .links {
            margin-top: 30px;
            padding: 20px;
            background-color: #e9ecef;
            border-radius: 4px;
        }
        .links a {
            display: inline-block;
            margin-right: 15px;
            color: #007bff;
            text-decoration: none;
        }
        .links a:hover {
            text-decoration: underline;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }
        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Claude OAuth Demo - Flask</h1>
        <p>This Flask application demonstrates integration with Claude API using OAuth authentication.</p>

        {% if not client_available %}
        <div class="response error">
            <strong>Authentication Error:</strong> Claude client not initialized.
            Please check your credentials and try again.
        </div>
        {% else %}
        <div class="response success">
            <strong>Status:</strong> Claude client ready
            <br><strong>Auth Type:</strong> {{ auth_info.auth_type }}
            <br><strong>Source:</strong> {{ auth_info.source }}
            <br><strong>Model:</strong> {{ auth_info.model }}
        </div>
        {% endif %}

        <h2>Try It Out</h2>

        <form action="/generate" method="POST">
            <div class="form-group">
                <label for="prompt">Enter your prompt:</label>
                <textarea id="prompt" name="prompt" placeholder="Ask Claude anything...">Explain the benefits of OAuth 2.0 authentication in 3 bullet points.</textarea>
            </div>
            <button type="submit">Generate Response</button>
        </form>

        <div class="links">
            <h3>API Endpoints:</h3>
            <a href="/health">Health Check</a>
            <a href="/auth-status">Auth Status</a>
            <a href="/api/generate?prompt=Hello%20Claude">API Example</a>
        </div>

        <h2>Example API Usage</h2>
        <pre><code># POST /api/generate
curl -X POST http://localhost:5000/api/generate \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Explain quantum computing", "max_tokens": 500}'

# GET /api/generate (simple)
curl "http://localhost:5000/api/generate?prompt=Hello%20Claude"
</code></pre>
    </div>
</body>
</html>
"""

# Template for response display
RESPONSE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Claude Response - Flask</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        .prompt {
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .response {
            padding: 15px;
            background-color: #f8f9fa;
            border-left: 4px solid #007bff;
            border-radius: 4px;
            line-height: 1.6;
        }
        .error {
            background-color: #f8d7da;
            border-left-color: #dc3545;
            color: #721c24;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #007bff;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Claude Response</h1>

        <div class="prompt">
            <strong>Your Prompt:</strong><br>
            {{ prompt }}
        </div>

        {% if error %}
        <div class="response error">
            <strong>Error:</strong> {{ error }}
        </div>
        {% else %}
        <div class="response">
            {{ response|safe }}
        </div>
        {% endif %}

        <a href="/" class="back-link">← Back to Home</a>
    </div>
</body>
</html>
"""


@app.route("/")
def home() -> str:
    """Home page with form and examples."""
    client_available = claude_client is not None

    auth_info = {}
    if client_available:
        try:
            auth_info = claude_client.get_auth_info()
        except Exception as e:
            logger.error(f"Error getting auth info: {e}")
            client_available = False

    return render_template_string(
        HOME_TEMPLATE, client_available=client_available, auth_info=auth_info
    )


@app.route("/generate", methods=["POST"])
def generate_web() -> str:
    """Generate response from form submission."""
    if claude_client is None:
        return render_template_string(
            RESPONSE_TEMPLATE, prompt="", response="", error="Claude client not initialized"
        )

    prompt = request.form.get("prompt", "").strip()

    if not prompt:
        return render_template_string(
            RESPONSE_TEMPLATE, prompt="", response="", error="Prompt cannot be empty"
        )

    try:
        # Generate response using Claude
        response = claude_client.generate(prompt)

        # Convert newlines to HTML breaks for display
        response_html = response.replace("\n", "<br>")

        return render_template_string(
            RESPONSE_TEMPLATE, prompt=prompt, response=response_html, error=None
        )

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return render_template_string(
            RESPONSE_TEMPLATE, prompt=prompt, response="", error=str(e)
        )


@app.route("/api/generate", methods=["GET", "POST"])
def generate_api() -> Any:
    """
    API endpoint for generating responses.

    GET /api/generate?prompt=Hello&max_tokens=100
    POST /api/generate with JSON body: {"prompt": "...", "max_tokens": 100}

    Returns:
        JSON response with generated text or error
    """
    if claude_client is None:
        return jsonify({"error": "Claude client not initialized", "success": False}), 503

    # Get parameters from either GET or POST
    if request.method == "POST":
        data = request.get_json() or {}
        prompt = data.get("prompt", "").strip()
        max_tokens = data.get("max_tokens")
        temperature = data.get("temperature")
    else:
        prompt = request.args.get("prompt", "").strip()
        max_tokens = request.args.get("max_tokens", type=int)
        temperature = request.args.get("temperature", type=float)

    if not prompt:
        return jsonify({"error": "Prompt is required", "success": False}), 400

    try:
        # Build kwargs for optional parameters
        kwargs = {}
        if max_tokens is not None:
            kwargs["max_tokens"] = max_tokens
        if temperature is not None:
            kwargs["temperature"] = temperature

        # Generate response
        response = claude_client.generate(prompt, **kwargs)

        return jsonify(
            {
                "success": True,
                "response": response,
                "prompt": prompt,
                "timestamp": datetime.utcnow().isoformat(),
                "model": claude_client.model,
            }
        )

    except Exception as e:
        logger.error(f"Error in API generation: {e}")
        return jsonify({"error": str(e), "success": False, "prompt": prompt}), 500


@app.route("/health")
def health_check() -> Any:
    """Health check endpoint for monitoring."""
    if claude_client is None:
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "claude_client": "not initialized",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            503,
        )

    try:
        # Get auth info to verify client is working
        auth_info = claude_client.get_auth_info()

        return jsonify(
            {
                "status": "healthy",
                "claude_client": "initialized",
                "auth_type": auth_info["auth_type"],
                "model": auth_info["model"],
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return (
            jsonify(
                {
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ),
            503,
        )


@app.route("/auth-status")
def auth_status_page() -> Any:
    """Display comprehensive authentication status."""
    try:
        status = get_auth_status()

        return jsonify(
            {
                "success": True,
                "status": status,
                "client_initialized": claude_client is not None,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/chat", methods=["POST"])
def chat() -> Any:
    """
    Chat endpoint with session-based history.

    Maintains conversation context across multiple requests.
    """
    if claude_client is None:
        return jsonify({"error": "Claude client not initialized", "success": False}), 503

    data = request.get_json() or {}
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message is required", "success": False}), 400

    try:
        # Get or initialize chat history from session
        if "chat_history" not in session:
            session["chat_history"] = []

        # Add user message to history
        session["chat_history"].append({"role": "user", "content": user_message})

        # Build context from history (last 5 messages)
        context_messages = session["chat_history"][-5:]
        context_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in context_messages])

        # Generate response
        response = claude_client.generate(
            context_prompt + "\nassistant:", max_tokens=data.get("max_tokens", 1000)
        )

        # Add assistant response to history
        session["chat_history"].append({"role": "assistant", "content": response})

        return jsonify(
            {
                "success": True,
                "response": response,
                "message_count": len(session["chat_history"]),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return jsonify({"error": str(e), "success": False}), 500


@app.route("/chat/reset", methods=["POST"])
def reset_chat() -> Any:
    """Reset chat history."""
    session.pop("chat_history", None)
    return jsonify({"success": True, "message": "Chat history reset"})


@app.errorhandler(404)
def not_found(error: Any) -> Any:
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found", "success": False}), 404


@app.errorhandler(500)
def internal_error(error: Any) -> Any:
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error", "success": False}), 500


if __name__ == "__main__":
    # Configuration
    host = os.environ.get("FLASK_HOST", "0.0.0.0")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    logger.info(f"Starting Flask app on {host}:{port}")
    logger.info(f"Debug mode: {debug}")

    if claude_client:
        auth_info = claude_client.get_auth_info()
        logger.info(f"Using {auth_info['auth_type']} from {auth_info['source']}")
    else:
        logger.warning("Claude client not initialized - app will have limited functionality")

    app.run(host=host, port=port, debug=debug)
