"""
Pytest Configuration and Shared Fixtures

This file contains pytest configuration and fixtures that can be used
across all test files in this directory.
"""

import pytest
from unittest.mock import Mock

from claude_oauth_auth import ClaudeClient


@pytest.fixture
def mock_claude_client():
    """
    Fixture providing a mock Claude client.

    Returns:
        Mock ClaudeClient instance with standard responses
    """
    mock_client = Mock(spec=ClaudeClient)
    mock_client.generate.return_value = "Mocked response"
    mock_client.model = "claude-sonnet-4-5-20250929"
    mock_client.temperature = 0.7
    mock_client.max_tokens = 4096

    # Mock auth info
    mock_client.get_auth_info.return_value = {
        "auth_type": "api_key",
        "source": "mock",
        "model": "claude-sonnet-4-5-20250929",
        "credential_prefix": "sk-mock-key..."
    }

    return mock_client


@pytest.fixture
def client_fixture():
    """
    Fixture providing a configured mock client.

    This fixture demonstrates setting up a client with specific behavior.
    """
    mock_client = Mock(spec=ClaudeClient)
    mock_client.generate.return_value = "Mocked response"

    # Configure mock to track calls
    mock_client.generate.call_count = 0

    def generate_wrapper(*args, **kwargs):
        mock_client.generate.call_count += 1
        return "Mocked response"

    mock_client.generate.side_effect = generate_wrapper

    return mock_client


@pytest.fixture
def sample_prompts():
    """Fixture providing sample prompts for testing."""
    return [
        "What is Python?",
        "Explain machine learning",
        "Write a haiku about programming"
    ]


@pytest.fixture
def sample_responses():
    """Fixture providing sample responses for testing."""
    return [
        "Python is a high-level programming language...",
        "Machine learning is a subset of AI...",
        "Code flows like water\nFunctions dance in harmony\nBugs flee at first light"
    ]


# Configure pytest markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test (requires credentials)"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


# Configure test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""
    for item in items:
        # Auto-mark integration tests to skip by default
        if "integration" in item.keywords:
            if not config.getoption("--run-integration"):
                item.add_marker(pytest.mark.skip(reason="Integration test - use --run-integration to run"))


def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests (requires real credentials)"
    )
