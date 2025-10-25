"""
Test suite for claude-oauth-auth package.

This package contains comprehensive tests for OAuth token management,
unified authentication, and Claude SDK client functionality.

Test Modules:
- conftest.py: Shared pytest fixtures and configuration
- test_oauth_manager.py: OAuth token management tests (39 tests)
- test_auth_manager.py: Unified authentication manager tests (37 tests)
- test_client.py: Claude SDK client tests (34 tests)
- test_integration.py: End-to-end integration tests (19 tests)

Total: 129 tests covering all components with 95%+ coverage target.

Usage:
    pytest                           # Run all tests
    pytest -v                        # Verbose output
    pytest -m "not integration"      # Skip integration tests
    pytest --cov=claude_oauth_auth   # Run with coverage
"""

__version__ = "0.1.0"
