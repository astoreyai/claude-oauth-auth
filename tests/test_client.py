"""
Unit Tests for ClaudeClient

Tests the Claude SDK client with OAuth and API key support, including
initialization, message generation, and authentication integration.

Test Coverage:
- Client initialization with different auth methods
- Message generation with API mocking
- Parameter overrides
- Authentication info retrieval
- Error handling
- Backward compatibility
- Verbose mode

Usage:
    pytest tests/test_client.py -v
    pytest tests/test_client.py::TestClientInitialization -v
"""

from unittest.mock import MagicMock, patch

import pytest

from claude_oauth_auth.auth_manager import AuthType
from claude_oauth_auth.client import ClaudeClient, create_client


class TestClientInitialization:
    """Test ClaudeClient initialization."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_initialization_with_api_key(self, mock_anthropic, clean_env):
        """Test client initialization with API key."""
        client = ClaudeClient(api_key="sk-ant-api03-test")

        assert client.model == "claude-sonnet-4-5-20250929"
        assert client.temperature == 0.7
        assert client.max_tokens == 4096

        # Should have called Anthropic with api_key
        mock_anthropic.assert_called_once()
        call_kwargs = mock_anthropic.call_args[1]
        assert "api_key" in call_kwargs

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_initialization_with_oauth(self, mock_anthropic, clean_env):
        """Test client initialization with OAuth token."""
        ClaudeClient(auth_token="sk-ant-oat01-test")

        # Should have called Anthropic with auth_token
        mock_anthropic.assert_called_once()
        call_kwargs = mock_anthropic.call_args[1]
        assert "auth_token" in call_kwargs

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_initialization_auto_discovery(self, mock_anthropic, clean_env):
        """Test client initialization with auto credential discovery."""
        clean_env.setenv("ANTHROPIC_API_KEY", "sk-ant-api03-env-key")

        ClaudeClient()

        # Should have discovered credentials
        mock_anthropic.assert_called_once()

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_custom_model(self, mock_anthropic, clean_env):
        """Test client initialization with custom model."""
        client = ClaudeClient(api_key="sk-ant-api03-test", model="claude-opus-4")

        assert client.model == "claude-opus-4"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_custom_temperature(self, mock_anthropic, clean_env):
        """Test client initialization with custom temperature."""
        client = ClaudeClient(api_key="sk-ant-api03-test", temperature=0.5)

        assert client.temperature == 0.5

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_custom_max_tokens(self, mock_anthropic, clean_env):
        """Test client initialization with custom max_tokens."""
        client = ClaudeClient(api_key="sk-ant-api03-test", max_tokens=2000)

        assert client.max_tokens == 2000

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_all_custom_parameters(self, mock_anthropic, clean_env):
        """Test client initialization with all custom parameters."""
        client = ClaudeClient(
            api_key="sk-ant-api03-test", model="claude-opus-4", temperature=0.9, max_tokens=8000
        )

        assert client.model == "claude-opus-4"
        assert client.temperature == 0.9
        assert client.max_tokens == 8000


class TestMessageGeneration:
    """Test message generation functionality."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_simple_message(self, mock_anthropic, clean_env):
        """Test generating a simple message."""
        # Setup mock
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Hello from Claude!")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")
        response = client.generate("Say hello")

        assert response == "Hello from Claude!"
        mock_client.messages.create.assert_called_once()

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_with_system_message(self, mock_anthropic, clean_env):
        """Test generating with system message."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")
        client.generate("User message", system="You are a helpful assistant")

        # Check system parameter was passed
        call_kwargs = mock_client.messages.create.call_args[1]
        assert "system" in call_kwargs
        assert call_kwargs["system"] == "You are a helpful assistant"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_with_temperature_override(self, mock_anthropic, clean_env):
        """Test generating with temperature override."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test", temperature=0.7)
        client.generate("Test", temperature=0.9)

        # Check temperature was overridden
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["temperature"] == 0.9

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_with_max_tokens_override(self, mock_anthropic, clean_env):
        """Test generating with max_tokens override."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test", max_tokens=4096)
        client.generate("Test", max_tokens=2000)

        # Check max_tokens was overridden
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["max_tokens"] == 2000

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_with_model_override(self, mock_anthropic, clean_env):
        """Test generating with model override."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")
        client.generate("Test", model="claude-opus-4")

        # Check model was overridden
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-opus-4"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_preserves_defaults(self, mock_anthropic, clean_env):
        """Test that generate uses client defaults when not overridden."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(
            api_key="sk-ant-api03-test", model="claude-opus-4", temperature=0.5, max_tokens=2000
        )
        client.generate("Test")

        # Check defaults were used
        call_kwargs = mock_client.messages.create.call_args[1]
        assert call_kwargs["model"] == "claude-opus-4"
        assert call_kwargs["temperature"] == 0.5
        assert call_kwargs["max_tokens"] == 2000


class TestAuthenticationInfo:
    """Test authentication information retrieval."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_get_auth_info_with_api_key(self, mock_anthropic, clean_env):
        """Test get_auth_info with API key."""
        client = ClaudeClient(api_key="sk-ant-api03-test")
        info = client.get_auth_info()

        assert isinstance(info, dict)
        assert info["auth_type"] == "api_key"
        assert info["source"] == "explicit_api_key_parameter"
        assert "credential_prefix" in info
        assert info["model"] == "claude-sonnet-4-5-20250929"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_get_auth_info_with_oauth(self, mock_anthropic, clean_env):
        """Test get_auth_info with OAuth token."""
        client = ClaudeClient(auth_token="sk-ant-oat01-test")
        info = client.get_auth_info()

        assert info["auth_type"] == "oauth_token"
        assert info["source"] == "explicit_auth_token_parameter"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_get_auth_info_includes_model(self, mock_anthropic, clean_env):
        """Test that auth info includes current model."""
        client = ClaudeClient(api_key="sk-ant-api03-test", model="claude-opus-4")
        info = client.get_auth_info()

        assert info["model"] == "claude-opus-4"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_get_full_auth_status(self, mock_anthropic, clean_env):
        """Test get_full_auth_status method."""
        client = ClaudeClient(api_key="sk-ant-api03-test")
        status = client.get_full_auth_status()

        assert isinstance(status, dict)
        assert "is_valid" in status
        assert "summary" in status
        assert status["is_valid"] is True


class TestErrorHandling:
    """Test error handling in client."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_api_error(self, mock_anthropic, clean_env):
        """Test handling of API errors during generation."""
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")

        with pytest.raises(Exception) as exc_info:
            client.generate("Test")

        assert "API Error" in str(exc_info.value)

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_empty_response(self, mock_anthropic, clean_env):
        """Test handling of empty response from API."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = []
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")

        # Should handle empty content gracefully - raises RuntimeError with context
        with pytest.raises(RuntimeError):
            client.generate("Test")

    def test_client_no_credentials_error(self, clean_env, tmp_path, monkeypatch):
        """Test client initialization fails without credentials."""
        monkeypatch.setattr("claude_oauth_auth.auth_manager.Path.home", lambda: tmp_path)

        with pytest.raises(ValueError) as exc_info:
            ClaudeClient()

        assert "No Anthropic API credentials found" in str(exc_info.value)


class TestVerboseMode:
    """Test verbose logging functionality."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_verbose_mode_initialization(self, mock_anthropic, clean_env, caplog):
        """Test verbose mode during initialization."""
        import logging

        caplog.set_level(logging.INFO)

        ClaudeClient(api_key="sk-ant-api03-test", verbose=True)

        # Should have logged authentication details
        assert len(caplog.records) > 0

    @patch("claude_oauth_auth.client.Anthropic")
    def test_non_verbose_mode(self, mock_anthropic, clean_env, caplog):
        """Test non-verbose mode produces minimal logging."""
        import logging

        caplog.set_level(logging.INFO)

        ClaudeClient(api_key="sk-ant-api03-test", verbose=False)

        # Should have minimal logging


class TestBackwardCompatibility:
    """Test backward compatibility with older API versions."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_v1_compatible_initialization(self, mock_anthropic, clean_env):
        """Test that v1 usage patterns still work."""
        # Old v1 patterns
        ClaudeClient()  # Auto-discovery
        client2 = ClaudeClient(api_key="sk-ant-api03-test")
        client3 = ClaudeClient(
            api_key="sk-ant-api03-test", model="claude-opus-4", temperature=0.5, max_tokens=2000
        )

        # All should initialize successfully
        assert client2.model == "claude-sonnet-4-5-20250929"
        assert client3.model == "claude-opus-4"
        assert client3.temperature == 0.5

    @patch("claude_oauth_auth.client.Anthropic")
    def test_generate_v1_compatible(self, mock_anthropic, clean_env):
        """Test that v1 generate patterns still work."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")

        # Old v1 patterns
        response1 = client.generate("Simple prompt")
        response2 = client.generate("Prompt", temperature=0.9)
        response3 = client.generate("Prompt", model="claude-opus-4", max_tokens=2000)

        assert all([response1, response2, response3])


class TestConvenienceFunctions:
    """Test module-level convenience functions."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_create_client_function(self, mock_anthropic, clean_env):
        """Test create_client convenience function."""
        client = create_client(api_key="sk-ant-api03-test")

        assert isinstance(client, ClaudeClient)
        assert client.credentials.auth_type == AuthType.API_KEY

    @patch("claude_oauth_auth.client.Anthropic")
    def test_create_client_with_oauth(self, mock_anthropic, clean_env):
        """Test create_client with OAuth."""
        client = create_client(auth_token="sk-ant-oat01-test")

        assert client.credentials.auth_type == AuthType.OAUTH_TOKEN

    @patch("claude_oauth_auth.client.Anthropic")
    def test_create_client_with_options(self, mock_anthropic, clean_env):
        """Test create_client with custom options."""
        client = create_client(api_key="sk-ant-api03-test", model="claude-opus-4", temperature=0.8)

        assert client.model == "claude-opus-4"
        assert client.temperature == 0.8


class TestResponseHandling:
    """Test response handling and parsing."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_response_text_extraction(self, mock_anthropic, clean_env):
        """Test extracting text from response."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Test response text")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")
        response = client.generate("Test")

        assert response == "Test response text"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_response_with_multiple_content_blocks(self, mock_anthropic, clean_env):
        """Test response with multiple content blocks."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="First block"), MagicMock(text="Second block")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")
        response = client.generate("Test")

        # Should return first content block
        assert response == "First block"


class TestParameterValidation:
    """Test parameter validation."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_temperature_range_validation(self, mock_anthropic, clean_env):
        """Test temperature parameter range validation."""
        # Valid temperatures should work
        client1 = ClaudeClient(api_key="sk-ant-api03-test", temperature=0.0)
        client2 = ClaudeClient(api_key="sk-ant-api03-test", temperature=1.0)

        assert client1.temperature == 0.0
        assert client2.temperature == 1.0

    @patch("claude_oauth_auth.client.Anthropic")
    def test_max_tokens_positive_validation(self, mock_anthropic, clean_env):
        """Test max_tokens must be positive."""
        # Positive values should work
        client = ClaudeClient(api_key="sk-ant-api03-test", max_tokens=100)
        assert client.max_tokens == 100

    @patch("claude_oauth_auth.client.Anthropic")
    def test_model_string_validation(self, mock_anthropic, clean_env):
        """Test model must be a string."""
        client = ClaudeClient(api_key="sk-ant-api03-test", model="claude-opus-4")
        assert isinstance(client.model, str)


class TestClientState:
    """Test client state management."""

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_credentials_immutable(self, mock_anthropic, clean_env):
        """Test that client credentials are set at initialization."""
        client = ClaudeClient(api_key="sk-ant-api03-test")

        # Credentials should be set
        assert client.credentials is not None
        assert client.credentials.credential == "sk-ant-api03-test"

    @patch("claude_oauth_auth.client.Anthropic")
    def test_client_multiple_generate_calls(self, mock_anthropic, clean_env):
        """Test multiple generate calls on same client."""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Response")]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        client = ClaudeClient(api_key="sk-ant-api03-test")

        # Multiple calls should work
        client.generate("Test 1")
        client.generate("Test 2")
        client.generate("Test 3")

        assert mock_client.messages.create.call_count == 3
