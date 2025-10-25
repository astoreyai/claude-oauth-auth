"""
Containerized Flask Application with Claude OAuth

A simple Flask app designed to run in Docker with Claude API integration.
Demonstrates best practices for containerizing Claude-powered applications.
"""

import logging
import os
from datetime import datetime

from flask import Flask, jsonify, request

from claude_oauth_auth import ClaudeClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Initialize Claude client
try:
    claude_client = ClaudeClient(verbose=True)
    logger.info("Claude client initialized successfully")
except ValueError as e:
    logger.error(f"Failed to initialize Claude client: {e}")
    claude_client = None


@app.route("/")
def home():
    """Home endpoint with API info."""
    return jsonify({
        "name": "Claude OAuth Demo - Docker",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "generate": "/api/generate",
        }
    })


@app.route("/health")
def health():
    """Health check endpoint for Docker health checks."""
    if claude_client is None:
        return jsonify({
            "status": "unhealthy",
            "claude_client": "not initialized",
            "timestamp": datetime.utcnow().isoformat()
        }), 503

    try:
        auth_info = claude_client.get_auth_info()
        return jsonify({
            "status": "healthy",
            "claude_client": "initialized",
            "auth_type": auth_info["auth_type"],
            "timestamp": datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 503


@app.route("/api/generate", methods=["POST"])
def generate():
    """Generate text using Claude API."""
    if claude_client is None:
        return jsonify({
            "error": "Claude client not initialized",
            "success": False
        }), 503

    data = request.get_json() or {}
    prompt = data.get("prompt", "").strip()

    if not prompt:
        return jsonify({
            "error": "Prompt is required",
            "success": False
        }), 400

    try:
        response = claude_client.generate(
            prompt,
            max_tokens=data.get("max_tokens", 1000)
        )

        return jsonify({
            "success": True,
            "response": response,
            "prompt": prompt,
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        return jsonify({
            "error": str(e),
            "success": False
        }), 500


if __name__ == "__main__":
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", 8000))

    logger.info(f"Starting Flask app on {host}:{port}")

    if claude_client:
        auth_info = claude_client.get_auth_info()
        logger.info(f"Using {auth_info['auth_type']} from {auth_info['source']}")

    app.run(host=host, port=port, debug=False)
