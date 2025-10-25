"""
FastAPI Application with Claude OAuth Integration

This example demonstrates a modern async FastAPI application integrating Claude API
with dependency injection, WebSocket streaming, and comprehensive API documentation.

Features:
- Async request handlers for better performance
- Dependency injection for authentication
- WebSocket streaming for real-time responses
- OpenAPI (Swagger) documentation
- Pydantic models for validation
- CORS support
- Health check endpoints

Run:
    uvicorn main:app --reload

Then visit:
    http://localhost:8000/docs (Swagger UI)
    http://localhost:8000/redoc (ReDoc)
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from claude_oauth_auth import ClaudeClient, get_auth_status


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Pydantic models for request/response validation
class GenerateRequest(BaseModel):
    """Request model for text generation."""

    prompt: str = Field(..., min_length=1, max_length=10000, description="The prompt to send to Claude")
    max_tokens: Optional[int] = Field(
        None, ge=1, le=8000, description="Maximum tokens to generate"
    )
    temperature: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Sampling temperature (0-1)"
    )
    system: Optional[str] = Field(None, description="Optional system prompt")

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Ensure prompt is not just whitespace."""
        if not v.strip():
            raise ValueError("Prompt cannot be empty or whitespace only")
        return v.strip()


class GenerateResponse(BaseModel):
    """Response model for text generation."""

    success: bool = Field(..., description="Whether the request succeeded")
    response: str = Field(..., description="Generated text from Claude")
    prompt: str = Field(..., description="The original prompt")
    model: str = Field(..., description="Claude model used")
    timestamp: str = Field(..., description="ISO 8601 timestamp")
    tokens_used: Optional[int] = Field(None, description="Approximate tokens used")


class ErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(False, description="Always false for errors")
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status: healthy or unhealthy")
    claude_client: str = Field(..., description="Claude client initialization status")
    auth_type: Optional[str] = Field(None, description="Authentication type in use")
    model: Optional[str] = Field(None, description="Claude model configured")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


class ChatMessage(BaseModel):
    """Chat message model."""

    message: str = Field(..., min_length=1, max_length=5000, description="Chat message")
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000, description="Max response tokens")


class ChatResponse(BaseModel):
    """Chat response model."""

    success: bool = True
    response: str
    message_count: int
    timestamp: str


# Global client instance (initialized in lifespan)
claude_client: Optional[ClaudeClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan context manager for startup and shutdown.

    This initializes the Claude client on startup and cleans up on shutdown.
    """
    global claude_client

    # Startup
    logger.info("Starting FastAPI application...")
    try:
        claude_client = ClaudeClient(verbose=True)
        logger.info("Claude client initialized successfully")
    except ValueError as e:
        logger.error(f"Failed to initialize Claude client: {e}")
        claude_client = None

    yield

    # Shutdown
    logger.info("Shutting down FastAPI application...")
    claude_client = None


# Create FastAPI app with lifespan
app = FastAPI(
    title="Claude OAuth Demo - FastAPI",
    description="Modern async API for Claude AI with OAuth authentication",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection for Claude client
def get_claude_client() -> ClaudeClient:
    """
    Dependency that provides the Claude client.

    Raises:
        HTTPException: If client is not initialized
    """
    if claude_client is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Claude client not initialized. Check authentication credentials.",
        )
    return claude_client


# Routes
@app.get("/", tags=["General"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "name": "Claude OAuth Demo - FastAPI",
        "version": "1.0.0",
        "description": "Modern async API for Claude AI with OAuth authentication",
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "auth_status": "/auth-status",
            "generate": "/api/generate",
            "chat": "/api/chat",
            "stream": "/api/stream",
            "websocket": "ws://localhost:8000/ws/generate",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["Monitoring"])
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Health status including Claude client state
    """
    if claude_client is None:
        return {
            "status": "unhealthy",
            "claude_client": "not initialized",
            "timestamp": datetime.utcnow().isoformat(),
        }

    try:
        auth_info = claude_client.get_auth_info()
        return {
            "status": "healthy",
            "claude_client": "initialized",
            "auth_type": auth_info["auth_type"],
            "model": auth_info["model"],
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "claude_client": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@app.get("/auth-status", tags=["Monitoring"])
async def auth_status() -> Dict[str, Any]:
    """
    Get comprehensive authentication status.

    Returns:
        Detailed authentication information
    """
    try:
        status = get_auth_status()
        return {
            "success": True,
            "status": status,
            "client_initialized": claude_client is not None,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting auth status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post(
    "/api/generate",
    response_model=GenerateResponse,
    responses={
        503: {"model": ErrorResponse, "description": "Service unavailable"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
    tags=["Claude API"],
)
async def generate(
    request: GenerateRequest, client: ClaudeClient = Depends(get_claude_client)
) -> Dict[str, Any]:
    """
    Generate text using Claude API.

    This endpoint accepts a prompt and optional parameters, returning generated text.

    Args:
        request: Generation request with prompt and parameters
        client: Claude client (injected)

    Returns:
        Generated text response

    Raises:
        HTTPException: If generation fails
    """
    try:
        # Build kwargs for optional parameters
        kwargs = {}
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.temperature is not None:
            kwargs["temperature"] = request.temperature
        if request.system is not None:
            kwargs["system"] = request.system

        # Generate response (run in thread pool to avoid blocking)
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: client.generate(request.prompt, **kwargs)
        )

        return {
            "success": True,
            "response": response,
            "prompt": request.prompt,
            "model": client.model,
            "timestamp": datetime.utcnow().isoformat(),
            "tokens_used": len(response.split()),  # Approximate
        }

    except Exception as e:
        logger.error(f"Error generating response: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}",
        )


@app.post("/api/chat", response_model=ChatResponse, tags=["Claude API"])
async def chat(
    message: ChatMessage,
    client: ClaudeClient = Depends(get_claude_client),
    chat_history: List[Dict[str, str]] = [],
) -> Dict[str, Any]:
    """
    Chat with Claude maintaining conversation context.

    Note: In a real application, you'd want to store chat history
    in a database or session store, not as a function parameter.

    Args:
        message: Chat message
        client: Claude client (injected)
        chat_history: Conversation history (in production, use session/database)

    Returns:
        Chat response
    """
    try:
        # Add user message to history
        chat_history.append({"role": "user", "content": message.message})

        # Build context from recent history (last 10 messages)
        context_messages = chat_history[-10:]
        context_prompt = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in context_messages]
        )

        # Generate response
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: client.generate(
                context_prompt + "\nassistant:", max_tokens=message.max_tokens
            ),
        )

        # Add response to history
        chat_history.append({"role": "assistant", "content": response})

        return {
            "success": True,
            "response": response,
            "message_count": len(chat_history),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@app.post("/api/stream", tags=["Claude API"])
async def stream_generate(
    request: GenerateRequest, client: ClaudeClient = Depends(get_claude_client)
) -> StreamingResponse:
    """
    Stream generated text in chunks for better UX on long responses.

    This simulates streaming by generating the full response and sending
    it in chunks. For true streaming, you'd need to use Claude's streaming API.

    Args:
        request: Generation request
        client: Claude client (injected)

    Returns:
        Streaming response with text chunks
    """

    async def generate_chunks() -> AsyncGenerator[str, None]:
        """Generate response in chunks."""
        try:
            # Build kwargs
            kwargs = {}
            if request.max_tokens is not None:
                kwargs["max_tokens"] = request.max_tokens
            if request.temperature is not None:
                kwargs["temperature"] = request.temperature
            if request.system is not None:
                kwargs["system"] = request.system

            # Generate full response
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: client.generate(request.prompt, **kwargs)
            )

            # Stream in chunks (simulated)
            chunk_size = 50  # characters per chunk
            for i in range(0, len(response), chunk_size):
                chunk = response[i : i + chunk_size]
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.05)  # Small delay for streaming effect

            yield "data: [DONE]\n\n"

        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            yield f"data: Error: {str(e)}\n\n"

    return StreamingResponse(generate_chunks(), media_type="text/event-stream")


@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time text generation.

    Client sends JSON: {"prompt": "...", "max_tokens": 100}
    Server responds with generated text

    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()

    try:
        if claude_client is None:
            await websocket.send_json(
                {"error": "Claude client not initialized", "success": False}
            )
            await websocket.close()
            return

        while True:
            # Receive message
            data = await websocket.receive_json()

            prompt = data.get("prompt", "").strip()
            if not prompt:
                await websocket.send_json({"error": "Prompt is required", "success": False})
                continue

            # Build kwargs
            kwargs = {}
            if "max_tokens" in data:
                kwargs["max_tokens"] = data["max_tokens"]
            if "temperature" in data:
                kwargs["temperature"] = data["temperature"]

            try:
                # Send status
                await websocket.send_json({"status": "generating", "prompt": prompt})

                # Generate response (in thread pool)
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, lambda: claude_client.generate(prompt, **kwargs)
                )

                # Send response
                await websocket.send_json(
                    {
                        "success": True,
                        "response": response,
                        "prompt": prompt,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

            except Exception as e:
                logger.error(f"Error in WebSocket generation: {e}")
                await websocket.send_json({"error": str(e), "success": False})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close()
        except Exception:
            pass


# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Any, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with custom format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Any, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        },
    )


if __name__ == "__main__":
    import uvicorn

    # Configuration
    host = os.environ.get("API_HOST", "0.0.0.0")
    port = int(os.environ.get("API_PORT", 8000))
    reload = os.environ.get("API_RELOAD", "True").lower() == "true"

    logger.info(f"Starting FastAPI app on {host}:{port}")
    logger.info(f"Reload mode: {reload}")

    uvicorn.run("main:app", host=host, port=port, reload=reload)
