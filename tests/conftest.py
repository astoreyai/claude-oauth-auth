"""
Pytest Configuration and Fixtures for claude-oauth-auth

This module provides shared fixtures for all test modules:
- Mock credentials files (valid and expired)
- Mock API key configurations
- Environment variable cleanup
- Mock Anthropic client
- Temporary file handling

Usage:
    Fixtures are automatically available to all test files in the tests/ directory.
    Simply add the fixture name as a parameter to any test function.

Example:
    def test_something(mock_credentials_file, clean_env):
        # Test with mocked credentials and clean environment
        pass
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_credentials_file(tmp_path: Path) -> Path:
    """
    Create a mock Claude Code credentials file with valid OAuth token.

    Returns:
        Path: Path to the temporary credentials file

    File Structure:
        ~/.claude/.credentials.json with valid claudeAiOauth section
    """
    credentials_dir = tmp_path / ".claude"
    credentials_dir.mkdir()

    credentials_file = credentials_dir / ".credentials.json"

    # Create mock credentials with future expiration
    expires_at = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
    credentials = {
        "claudeAiOauth": {
            "accessToken": "sk-ant-oat01-test-token-12345",
            "refreshToken": "sk-ant-ort01-test-refresh-12345",
            "expiresAt": expires_at,
            "scopes": ["user:inference", "user:profile"],
            "subscriptionType": "max",
        }
    }

    with open(credentials_file, "w") as f:
        json.dump(credentials, f)

    return credentials_file


@pytest.fixture
def expired_credentials_file(tmp_path: Path) -> Path:
    """
    Create a mock Claude Code credentials file with expired OAuth token.

    Returns:
        Path: Path to the temporary credentials file with expired token

    File Structure:
        ~/.claude/.credentials.json with expired claudeAiOauth section
    """
    credentials_dir = tmp_path / ".claude"
    credentials_dir.mkdir()

    credentials_file = credentials_dir / ".credentials.json"

    # Create expired credentials (1 day in the past)
    expires_at = int((datetime.now() - timedelta(days=1)).timestamp() * 1000)
    credentials = {
        "claudeAiOauth": {
            "accessToken": "sk-ant-oat01-expired-token",
            "refreshToken": "sk-ant-ort01-expired-refresh",
            "expiresAt": expires_at,
            "scopes": ["user:inference", "user:profile"],
            "subscriptionType": "max",
        }
    }

    with open(credentials_file, "w") as f:
        json.dump(credentials, f)

    return credentials_file


@pytest.fixture
def mock_api_key_config(tmp_path: Path) -> Path:
    """
    Create a mock Anthropic API key configuration file.

    Returns:
        Path: Path to the temporary config file

    File Structure:
        ~/.anthropic/config with [default] section containing api_key
    """
    config_dir = tmp_path / ".anthropic"
    config_dir.mkdir()

    config_file = config_dir / "config"

    with open(config_file, "w") as f:
        f.write("[default]\n")
        f.write("api_key = sk-ant-api03-test-api-key\n")

    return config_file


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> pytest.MonkeyPatch:
    """
    Clean environment of all Anthropic-related variables.

    Returns:
        MonkeyPatch: The monkeypatch object for additional modifications

    Removed Variables:
        - ANTHROPIC_API_KEY
        - ANTHROPIC_AUTH_TOKEN
        - CLAUDE_USE_SUBSCRIPTION
        - CLAUDE_CODE_ENTRYPOINT
        - CLAUDE_BYPASS_BALANCE_CHECK
    """
    env_vars = [
        "ANTHROPIC_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_USE_SUBSCRIPTION",
        "CLAUDE_CODE_ENTRYPOINT",
        "CLAUDE_BYPASS_BALANCE_CHECK",
    ]

    for var in env_vars:
        monkeypatch.delenv(var, raising=False)

    return monkeypatch


@pytest.fixture
def mock_anthropic_client() -> MagicMock:
    """
    Create a mock Anthropic client for testing.

    Returns:
        MagicMock: Mocked Anthropic client with messages.create method

    Example:
        def test_client(mock_anthropic_client):
            client = mock_anthropic_client
            response = client.messages.create(...)
            assert response.content[0].text == "Mocked response"
    """
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Mocked response from Claude")]
    mock_response.id = "msg_test_12345"
    mock_response.model = "claude-sonnet-4-5-20250929"
    mock_response.role = "assistant"
    mock_response.stop_reason = "end_turn"
    mock_response.usage = MagicMock(input_tokens=10, output_tokens=20)

    mock_client.messages.create.return_value = mock_response

    return mock_client


@pytest.fixture
def temp_credentials_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Create a temporary directory for credentials storage.

    Yields:
        Path: Path to temporary credentials directory

    Cleanup:
        Automatically cleaned up after test completion
    """
    creds_dir = tmp_path / ".claude"
    creds_dir.mkdir(parents=True, exist_ok=True)
    yield creds_dir


@pytest.fixture
def invalid_json_file(tmp_path: Path) -> Path:
    """
    Create a credentials file with invalid JSON.

    Returns:
        Path: Path to file with malformed JSON

    Purpose:
        Test error handling for corrupted credentials files
    """
    credentials_dir = tmp_path / ".claude"
    credentials_dir.mkdir()

    invalid_file = credentials_dir / ".credentials.json"
    with open(invalid_file, "w") as f:
        f.write("{invalid json content")

    return invalid_file


@pytest.fixture
def mock_multiple_credentials(tmp_path: Path) -> dict:
    """
    Create multiple credential sources for priority testing.

    Returns:
        dict: Dictionary containing paths to different credential sources
            - oauth_file: OAuth credentials file
            - api_key_file: API key config file
            - env_vars: Dictionary of environment variables to set

    Purpose:
        Test authentication priority and credential discovery
    """
    # Create OAuth credentials
    oauth_dir = tmp_path / ".claude"
    oauth_dir.mkdir()
    oauth_file = oauth_dir / ".credentials.json"

    expires_at = int((datetime.now() + timedelta(days=1)).timestamp() * 1000)
    oauth_creds = {
        "claudeAiOauth": {
            "accessToken": "sk-ant-oat01-oauth-token",
            "refreshToken": "sk-ant-ort01-oauth-refresh",
            "expiresAt": expires_at,
            "scopes": ["user:inference"],
            "subscriptionType": "pro",
        }
    }

    with open(oauth_file, "w") as f:
        json.dump(oauth_creds, f)

    # Create API key config
    api_key_dir = tmp_path / ".anthropic"
    api_key_dir.mkdir()
    api_key_file = api_key_dir / "config"

    with open(api_key_file, "w") as f:
        f.write("[default]\n")
        f.write("api_key = sk-ant-api03-config-key\n")

    return {
        "oauth_file": oauth_file,
        "api_key_file": api_key_file,
        "env_vars": {
            "ANTHROPIC_API_KEY": "sk-ant-api03-env-key",
            "ANTHROPIC_AUTH_TOKEN": "sk-ant-oat01-env-token",
        },
        "home_dir": tmp_path,
    }


@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset singleton instances between tests.

    Purpose:
        Ensures each test starts with clean state for singleton managers

    Note:
        This is autouse=True, so it runs automatically for every test
    """
    # Reset the OAuth manager singleton before each test
    import claude_oauth_auth.oauth_manager as oauth_mod

    oauth_mod._default_manager = None

    yield

    # Reset the OAuth manager singleton after each test
    oauth_mod._default_manager = None


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "real: mark test as requiring real API credentials")
