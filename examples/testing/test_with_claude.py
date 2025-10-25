"""
Testing Examples with Claude OAuth Auth

Demonstrates how to write tests for applications using Claude API,
including mocking, fixtures, and integration tests.

Features:
- Mock authentication for testing
- Reusable fixtures
- Integration test examples
- Test coverage examples
- CI/CD patterns

Run:
    pytest test_with_claude.py
    pytest test_with_claude.py -v
    pytest test_with_claude.py --cov
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from claude_oauth_auth import ClaudeClient, create_client, get_auth_status
from claude_oauth_auth.auth_manager import AuthCredentials, AuthType, AuthSource


# Example application function to test
def analyze_text(text: str, client: ClaudeClient) -> dict:
    """
    Example function that uses Claude to analyze text.

    Args:
        text: Text to analyze
        client: Claude client instance

    Returns:
        Analysis results
    """
    prompt = f"Analyze this text and provide sentiment, key topics, and summary:\n\n{text}"
    response = client.generate(prompt, max_tokens=500)
    return {
        "original_text": text,
        "analysis": response,
        "success": True
    }


def summarize_content(content: str, max_words: int = 100) -> str:
    """
    Example function that summarizes content using Claude.

    Args:
        content: Content to summarize
        max_words: Maximum words in summary

    Returns:
        Summary text
    """
    client = create_client()
    prompt = f"Summarize this in {max_words} words or less:\n\n{content}"
    return client.generate(prompt, max_tokens=max_words * 2)


class TestClaudeClientMocking:
    """Tests demonstrating how to mock ClaudeClient."""

    def test_mock_client_basic(self):
        """Test with basic mock client."""
        # Create mock client
        mock_client = Mock(spec=ClaudeClient)
        mock_client.generate.return_value = "Mocked response"

        # Use mock in function
        result = analyze_text("Test text", mock_client)

        # Verify
        assert result["success"] is True
        assert result["analysis"] == "Mocked response"
        mock_client.generate.assert_called_once()

    def test_mock_client_with_parameters(self):
        """Test mock verifying parameters."""
        mock_client = Mock(spec=ClaudeClient)
        mock_client.generate.return_value = "Analysis result"

        # Call function
        analyze_text("Sample text", mock_client)

        # Verify parameters
        call_args = mock_client.generate.call_args
        assert "Sample text" in call_args[0][0]  # Prompt contains text
        assert call_args[1]["max_tokens"] == 500

    def test_mock_client_side_effects(self):
        """Test mock with side effects for multiple calls."""
        mock_client = Mock(spec=ClaudeClient)
        mock_client.generate.side_effect = [
            "First response",
            "Second response",
            "Third response"
        ]

        # Make multiple calls
        assert analyze_text("Text 1", mock_client)["analysis"] == "First response"
        assert analyze_text("Text 2", mock_client)["analysis"] == "Second response"
        assert analyze_text("Text 3", mock_client)["analysis"] == "Third response"

    def test_mock_client_exception(self):
        """Test mock raising exception."""
        mock_client = Mock(spec=ClaudeClient)
        mock_client.generate.side_effect = RuntimeError("API Error")

        # Should raise exception
        with pytest.raises(RuntimeError, match="API Error"):
            analyze_text("Test", mock_client)


class TestClaudeClientPatching:
    """Tests demonstrating patching ClaudeClient."""

    @patch("claude_oauth_auth.ClaudeClient")
    def test_patch_client_creation(self, mock_client_class):
        """Test patching client creation."""
        # Setup mock
        mock_instance = Mock()
        mock_instance.generate.return_value = "Summary text"
        mock_client_class.return_value = mock_instance

        # This would normally create real client, but now uses mock
        result = summarize_content("Long content here...")

        # Verify
        assert result == "Summary text"
        mock_client_class.assert_called_once()

    @patch("claude_oauth_auth.create_client")
    def test_patch_create_client(self, mock_create):
        """Test patching create_client function."""
        mock_client = Mock()
        mock_client.generate.return_value = "Summary"
        mock_create.return_value = mock_client

        result = summarize_content("Content")

        assert result == "Summary"
        mock_create.assert_called_once()


class TestAuthenticationMocking:
    """Tests for mocking authentication."""

    @patch("claude_oauth_auth.auth_manager.UnifiedAuthManager")
    def test_mock_auth_discovery(self, mock_auth_manager):
        """Test mocking authentication discovery."""
        # Setup mock credentials
        mock_credentials = AuthCredentials(
            auth_type=AuthType.API_KEY,
            credential="sk-test-key",
            source=AuthSource.ENVIRONMENT_API_KEY,
            metadata={}
        )

        mock_manager_instance = Mock()
        mock_manager_instance.discover_credentials.return_value = mock_credentials
        mock_auth_manager.return_value = mock_manager_instance

        # This would normally discover real credentials
        # Now uses mocked credentials
        with patch("claude_oauth_auth.client.Anthropic"):
            client = ClaudeClient()
            assert client.credentials == mock_credentials

    @patch("claude_oauth_auth.get_auth_status")
    def test_mock_auth_status(self, mock_status):
        """Test mocking auth status."""
        mock_status.return_value = {
            "summary": "Mock auth available",
            "available_methods": ["mock_oauth"],
            "credentials_found": {
                "auth_type": "oauth_token",
                "source": "mock"
            }
        }

        status = get_auth_status()
        assert status["summary"] == "Mock auth available"
        assert "mock_oauth" in status["available_methods"]


class TestIntegrationExamples:
    """Integration test examples (require real credentials)."""

    @pytest.mark.integration
    def test_real_client_generation(self):
        """
        Integration test with real client.

        Marked as integration test - run with: pytest -m integration
        """
        try:
            client = ClaudeClient()
            response = client.generate("Say 'Hello, World!'", max_tokens=50)
            assert response is not None
            assert len(response) > 0
            assert isinstance(response, str)
        except ValueError:
            pytest.skip("No authentication credentials available")

    @pytest.mark.integration
    def test_real_client_parameters(self):
        """Test real client with different parameters."""
        try:
            client = ClaudeClient()

            # Test with different temperatures
            creative = client.generate("Tell a story", temperature=0.9, max_tokens=100)
            focused = client.generate("What is 2+2?", temperature=0.1, max_tokens=50)

            assert creative != focused
            assert len(creative) > len(focused)
        except ValueError:
            pytest.skip("No authentication credentials available")


class TestErrorHandling:
    """Tests for error handling."""

    def test_invalid_parameters(self):
        """Test client with invalid parameters."""
        mock_client = Mock(spec=ClaudeClient)
        mock_client.generate.side_effect = ValueError("Invalid temperature")

        with pytest.raises(ValueError, match="Invalid temperature"):
            analyze_text("Test", mock_client)

    def test_api_timeout(self):
        """Test handling API timeout."""
        mock_client = Mock(spec=ClaudeClient)
        mock_client.generate.side_effect = TimeoutError("Request timeout")

        with pytest.raises(TimeoutError):
            analyze_text("Test", mock_client)


# Pytest markers
pytestmark = [
    pytest.mark.unit,  # All tests in this file are unit tests
]


# Example of parameterized tests
@pytest.mark.parametrize("text,expected_length", [
    ("Short", 100),
    ("Medium length text here", 200),
    ("Very long text that needs more tokens" * 10, 500),
])
def test_text_length_handling(text, expected_length):
    """Test handling different text lengths."""
    mock_client = Mock(spec=ClaudeClient)
    mock_client.generate.return_value = "Analysis"

    result = analyze_text(text, mock_client)

    assert result["success"] is True
    # Verify appropriate max_tokens was used
    call_args = mock_client.generate.call_args
    assert call_args[1]["max_tokens"] == 500


# Example test with fixture from conftest.py
def test_with_fixture(mock_claude_client):
    """Test using fixture from conftest.py."""
    result = analyze_text("Test text", mock_claude_client)
    assert result["success"] is True


def test_with_client_fixture(client_fixture):
    """Test using client fixture."""
    response = client_fixture.generate("Hello")
    assert response == "Mocked response"


# Performance test example
@pytest.mark.slow
def test_batch_processing_performance(mock_claude_client):
    """Test performance of batch processing."""
    import time

    texts = [f"Text {i}" for i in range(100)]

    start = time.time()
    for text in texts:
        analyze_text(text, mock_claude_client)
    duration = time.time() - start

    # Should process 100 items quickly with mocks
    assert duration < 1.0  # Less than 1 second
    assert mock_claude_client.generate.call_count == 100
