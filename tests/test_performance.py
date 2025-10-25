"""
Performance Benchmark Tests using pytest-benchmark

These tests integrate with pytest-benchmark for automated performance regression testing.
They establish performance baselines and can detect performance degradation in CI/CD.

Usage:
    # Run benchmarks
    pytest tests/test_performance.py --benchmark-only

    # Save baseline
    pytest tests/test_performance.py --benchmark-only --benchmark-save=baseline

    # Compare against baseline
    pytest tests/test_performance.py --benchmark-only --benchmark-compare=baseline

    # Generate histogram
    pytest tests/test_performance.py --benchmark-only --benchmark-histogram

Requirements:
    pip install pytest-benchmark
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from claude_oauth_auth import ClaudeClient
from claude_oauth_auth.auth_manager import UnifiedAuthManager
from claude_oauth_auth.oauth_manager import OAuthTokenManager


# Fixtures for test credentials


@pytest.fixture
def test_api_key():
    """Test API key for benchmarking."""
    return "sk-ant-api03-test-key-for-benchmarking-purposes-only"


@pytest.fixture
def test_oauth_credentials():
    """Create temporary OAuth credentials for testing."""
    expires_at = int((datetime.now().timestamp() + (30 * 24 * 60 * 60)) * 1000)
    return {
        "claudeAiOauth": {
            "accessToken": "sk-ant-oat01-test-token-for-benchmarking",
            "refreshToken": "sk-ant-ort01-test-refresh-token",
            "expiresAt": expires_at,
            "scopes": ["user:inference", "user:profile"],
            "subscriptionType": "max"
        }
    }


@pytest.fixture
def oauth_credentials_file(test_oauth_credentials):
    """Create temporary OAuth credentials file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cred_file = Path(tmpdir) / ".credentials.json"
        cred_file.write_text(json.dumps(test_oauth_credentials))
        yield cred_file


# Credential Discovery Benchmarks


def test_bench_explicit_api_key_discovery(benchmark, test_api_key):
    """Benchmark credential discovery with explicit API key."""
    def discover():
        manager = UnifiedAuthManager(api_key=test_api_key, verbose=False)
        return manager.discover_credentials()

    result = benchmark(discover)
    assert result.credential == test_api_key


def test_bench_env_var_discovery(benchmark, test_api_key):
    """Benchmark credential discovery from environment variable."""
    os.environ["ANTHROPIC_API_KEY"] = test_api_key

    try:
        def discover():
            manager = UnifiedAuthManager(verbose=False)
            return manager.discover_credentials()

        result = benchmark(discover)
        assert result.credential == test_api_key
    finally:
        os.environ.pop("ANTHROPIC_API_KEY", None)


def test_bench_oauth_file_parsing_cold(benchmark, oauth_credentials_file):
    """Benchmark OAuth credential file parsing (cold start)."""
    def parse_cold():
        manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
        manager._load_credentials(force_reload=True)
        return manager

    benchmark(parse_cold)


def test_bench_oauth_file_parsing_warm(benchmark, oauth_credentials_file):
    """Benchmark OAuth credential file parsing (warm/cached)."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()  # Prime cache

    def parse_warm():
        return manager._load_credentials(force_reload=False)

    benchmark(parse_warm)


# Client Initialization Benchmarks


def test_bench_client_init_explicit_key(benchmark, test_api_key):
    """Benchmark ClaudeClient initialization with explicit API key."""
    def create_client():
        return ClaudeClient(api_key=test_api_key)

    client = benchmark(create_client)
    assert client.credentials.credential == test_api_key


def test_bench_client_init_env_var(benchmark, test_api_key):
    """Benchmark ClaudeClient initialization from environment variable."""
    os.environ["ANTHROPIC_API_KEY"] = test_api_key

    try:
        def create_client():
            return ClaudeClient()

        client = benchmark(create_client)
        assert client.credentials.credential == test_api_key
    finally:
        os.environ.pop("ANTHROPIC_API_KEY", None)


def test_bench_auth_manager_only(benchmark, test_api_key):
    """Benchmark just auth manager creation (no full client)."""
    def create_manager():
        manager = UnifiedAuthManager(api_key=test_api_key, verbose=False)
        return manager.discover_credentials()

    benchmark(create_manager)


# OAuth Operations Benchmarks


def test_bench_oauth_is_available(benchmark, oauth_credentials_file):
    """Benchmark OAuth availability check."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()  # Prime cache

    def check_available():
        return manager.is_oauth_available()

    result = benchmark(check_available)
    assert result is True


def test_bench_oauth_is_expired(benchmark, oauth_credentials_file):
    """Benchmark token expiration check."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()  # Prime cache

    def check_expired():
        return manager.is_token_expired()

    result = benchmark(check_expired)
    assert result is False


def test_bench_oauth_get_token(benchmark, oauth_credentials_file):
    """Benchmark getting OAuth access token."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()  # Prime cache

    def get_token():
        return manager.get_access_token()

    token = benchmark(get_token)
    assert token is not None
    assert token.startswith("sk-ant-oat01-")


def test_bench_oauth_get_token_info(benchmark, oauth_credentials_file):
    """Benchmark getting comprehensive token info."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()  # Prime cache

    def get_info():
        return manager.get_token_info()

    info = benchmark(get_info)
    assert info["available"] is True
    assert info["is_valid"] is True


# Client Method Benchmarks


def test_bench_client_get_auth_info(benchmark, test_api_key):
    """Benchmark getting client auth info."""
    client = ClaudeClient(api_key=test_api_key)

    def get_auth_info():
        return client.get_auth_info()

    info = benchmark(get_auth_info)
    assert info["auth_type"] == "api_key"


def test_bench_client_get_full_status(benchmark, test_api_key):
    """Benchmark getting full authentication status."""
    client = ClaudeClient(api_key=test_api_key)

    def get_status():
        return client.get_full_auth_status()

    status = benchmark(get_status)
    assert status["is_valid"] is True


# Composite Operations Benchmarks


def test_bench_full_client_workflow(benchmark, test_api_key):
    """Benchmark complete client creation and usage workflow."""
    def workflow():
        # Create client
        client = ClaudeClient(api_key=test_api_key)

        # Get auth info
        auth_info = client.get_auth_info()

        # Get full status
        status = client.get_full_auth_status()

        return client, auth_info, status

    client, auth_info, status = benchmark(workflow)
    assert auth_info["auth_type"] == "api_key"
    assert status["is_valid"] is True


def test_bench_oauth_complete_validation(benchmark, oauth_credentials_file):
    """Benchmark complete OAuth validation workflow."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)

    def validate_oauth():
        # Check availability
        is_available = manager.is_oauth_available()

        # Check expiration
        is_expired = manager.is_token_expired()

        # Get token
        token = manager.get_access_token()

        # Get info
        info = manager.get_token_info()

        return is_available, is_expired, token, info

    is_available, is_expired, token, info = benchmark(validate_oauth)
    assert is_available is True
    assert is_expired is False
    assert token is not None
    assert info["is_valid"] is True


# Performance Regression Tests


def test_bench_client_init_under_100ms(benchmark, test_api_key):
    """Ensure client initialization stays under 100ms (performance regression test)."""
    def create_client():
        return ClaudeClient(api_key=test_api_key)

    stats = benchmark(create_client)

    # Assert performance target
    # Note: This is a soft target; actual time depends on hardware
    # We're checking mean time is reasonable
    assert stats.stats.mean < 0.1, f"Client init too slow: {stats.stats.mean*1000:.2f}ms"


def test_bench_oauth_validation_under_1ms(benchmark, oauth_credentials_file):
    """Ensure OAuth validation stays under 1ms (performance regression test)."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()  # Prime cache

    def validate():
        return manager.is_token_expired()

    stats = benchmark(validate)

    # Assert performance target (cached operations should be very fast)
    # This is lenient; cached operations should be microseconds
    assert stats.stats.mean < 0.001, f"OAuth validation too slow: {stats.stats.mean*1000:.2f}ms"


def test_bench_credential_discovery_under_50ms(benchmark, test_api_key):
    """Ensure credential discovery stays under 50ms (performance regression test)."""
    def discover():
        manager = UnifiedAuthManager(api_key=test_api_key, verbose=False)
        return manager.discover_credentials()

    stats = benchmark(discover)

    # Assert performance target
    assert stats.stats.mean < 0.05, f"Credential discovery too slow: {stats.stats.mean*1000:.2f}ms"


# Benchmark Groups


@pytest.mark.benchmark(group="discovery")
def test_bench_group_discovery_explicit(benchmark, test_api_key):
    """Discovery benchmark group - explicit key."""
    def discover():
        manager = UnifiedAuthManager(api_key=test_api_key, verbose=False)
        return manager.discover_credentials()

    benchmark(discover)


@pytest.mark.benchmark(group="discovery")
def test_bench_group_discovery_env(benchmark, test_api_key):
    """Discovery benchmark group - environment variable."""
    os.environ["ANTHROPIC_API_KEY"] = test_api_key

    try:
        def discover():
            manager = UnifiedAuthManager(verbose=False)
            return manager.discover_credentials()

        benchmark(discover)
    finally:
        os.environ.pop("ANTHROPIC_API_KEY", None)


@pytest.mark.benchmark(group="oauth")
def test_bench_group_oauth_available(benchmark, oauth_credentials_file):
    """OAuth benchmark group - availability check."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()

    def check():
        return manager.is_oauth_available()

    benchmark(check)


@pytest.mark.benchmark(group="oauth")
def test_bench_group_oauth_expired(benchmark, oauth_credentials_file):
    """OAuth benchmark group - expiration check."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()

    def check():
        return manager.is_token_expired()

    benchmark(check)


@pytest.mark.benchmark(group="oauth")
def test_bench_group_oauth_get_token(benchmark, oauth_credentials_file):
    """OAuth benchmark group - get token."""
    manager = OAuthTokenManager(credentials_path=oauth_credentials_file)
    manager._load_credentials()

    def get():
        return manager.get_access_token()

    benchmark(get)


@pytest.mark.benchmark(group="client_init")
def test_bench_group_client_explicit(benchmark, test_api_key):
    """Client init benchmark group - explicit key."""
    def create():
        return ClaudeClient(api_key=test_api_key)

    benchmark(create)


@pytest.mark.benchmark(group="client_init")
def test_bench_group_client_env(benchmark, test_api_key):
    """Client init benchmark group - environment variable."""
    os.environ["ANTHROPIC_API_KEY"] = test_api_key

    try:
        def create():
            return ClaudeClient()

        benchmark(create)
    finally:
        os.environ.pop("ANTHROPIC_API_KEY", None)
