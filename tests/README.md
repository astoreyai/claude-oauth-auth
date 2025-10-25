# Test Suite Documentation

Comprehensive test suite for the `claude-oauth-auth` package.

## Overview

The test suite is organized into focused test modules with 95%+ coverage target:

- **conftest.py** - Shared pytest fixtures and configuration
- **test_oauth_manager.py** - OAuth token management tests
- **test_auth_manager.py** - Unified authentication manager tests
- **test_client.py** - Claude SDK client tests
- **test_integration.py** - End-to-end integration tests

## Quick Start

### Run All Tests

```bash
# Run all tests (except real API tests)
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=claude_oauth_auth --cov-report=html
```

### Run Specific Test Modules

```bash
# Test OAuth manager only
pytest tests/test_oauth_manager.py -v

# Test authentication manager only
pytest tests/test_auth_manager.py -v

# Test client only
pytest tests/test_client.py -v

# Test integration scenarios only
pytest tests/test_integration.py -v
```

### Run Specific Test Classes

```bash
# Test specific class
pytest tests/test_oauth_manager.py::TestOAuthManagerInitialization -v

# Test specific test
pytest tests/test_client.py::TestClientInitialization::test_client_initialization_with_api_key -v
```

### Test by Markers

```bash
# Run only unit tests (exclude integration)
pytest -v -m "not integration"

# Run only integration tests
pytest -v -m integration

# Run tests requiring real credentials (use with caution)
pytest -v -m real
```

## Test Organization

### Unit Tests

Unit tests focus on individual components in isolation with mocked dependencies:

- **test_oauth_manager.py** - 15 test classes, 60+ tests
  - Initialization and configuration
  - Credentials loading and parsing
  - Token validation and expiration
  - Thread safety
  - Error handling

- **test_auth_manager.py** - 12 test classes, 50+ tests
  - Authentication priority and precedence
  - Credential discovery from multiple sources
  - Environment variable handling
  - Config file parsing
  - Status reporting

- **test_client.py** - 11 test classes, 45+ tests
  - Client initialization
  - Message generation
  - Parameter overrides
  - Authentication integration
  - Error handling

### Integration Tests

Integration tests verify end-to-end workflows across multiple components:

- **test_integration.py** - 8 test classes, 25+ tests
  - Complete OAuth workflow
  - Complete API key workflow
  - Cross-component integration
  - Error propagation
  - Thread safety
  - Real credentials (optional)

## Test Fixtures

### Available Fixtures (from conftest.py)

#### Credential Fixtures

- `mock_credentials_file` - Valid OAuth credentials file
- `expired_credentials_file` - Expired OAuth credentials file
- `mock_api_key_config` - API key configuration file
- `invalid_json_file` - Corrupted credentials file
- `mock_multiple_credentials` - Multiple credential sources

#### Environment Fixtures

- `clean_env` - Clean environment variables
- `temp_credentials_dir` - Temporary credentials directory

#### Client Fixtures

- `mock_anthropic_client` - Mocked Anthropic client with responses

### Using Fixtures

```python
def test_something(mock_credentials_file, clean_env):
    """Test using fixtures."""
    manager = OAuthTokenManager(credentials_path=mock_credentials_file)
    # Test code here
```

## Coverage Requirements

### Target: 95%+ Coverage

The test suite maintains a minimum coverage threshold of 95%:

```bash
# Run tests with coverage check (fails if < 95%)
pytest --cov=claude_oauth_auth --cov-fail-under=95
```

### Generate Coverage Reports

```bash
# HTML report (viewable in browser)
pytest --cov=claude_oauth_auth --cov-report=html
open htmlcov/index.html

# Terminal report with missing lines
pytest --cov=claude_oauth_auth --cov-report=term-missing

# XML report (for CI/CD)
pytest --cov=claude_oauth_auth --cov-report=xml
```

### Coverage Configuration

Coverage settings are in `pyproject.toml`:

- Source: `claude_oauth_auth` package
- Branch coverage: Enabled
- Omit: Tests, cache, site-packages
- Exclude: Pragma comments, abstract methods, TYPE_CHECKING blocks

## Tox Environments

### Available Environments

```bash
# Test across Python versions
tox -e py38,py39,py310,py311,py312

# Run linting
tox -e lint

# Run type checking
tox -e type

# Run tests with coverage
tox -e coverage

# Build documentation
tox -e docs

# Run all checks
tox
```

### Tox Commands

```bash
# List available environments
tox -l

# Run specific environment
tox -e py311

# Run with specific pytest args
tox -e py311 -- tests/test_client.py -v

# Skip missing Python interpreters
tox --skip-missing-interpreters
```

## Writing New Tests

### Test Structure

Follow this structure for new tests:

```python
"""
Module docstring explaining what is tested.

Test Coverage:
- Feature 1
- Feature 2
- Edge cases

Usage:
    pytest tests/test_new_module.py -v
"""

import pytest
from claude_oauth_auth import SomeClass


class TestFeatureGroup:
    """Test a specific feature group."""

    def test_basic_functionality(self):
        """Test basic functionality with descriptive docstring."""
        # Arrange
        obj = SomeClass()

        # Act
        result = obj.method()

        # Assert
        assert result == expected_value

    def test_error_case(self):
        """Test error handling."""
        obj = SomeClass()

        with pytest.raises(ValueError) as exc_info:
            obj.method_that_fails()

        assert "expected error message" in str(exc_info.value)

    def test_with_fixture(self, mock_credentials_file):
        """Test using a fixture."""
        obj = SomeClass(credentials_path=mock_credentials_file)
        assert obj.credentials is not None
```

### Test Naming Conventions

- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestOAuthManager`)
- Test functions: `test_*` (e.g., `test_load_credentials_success`)
- Use descriptive names that explain what is tested

### Markers

Mark tests appropriately:

```python
@pytest.mark.unit
def test_unit_test():
    """Unit test marker (optional, default)."""
    pass

@pytest.mark.integration
def test_integration():
    """Integration test - tests multiple components."""
    pass

@pytest.mark.real
def test_with_real_api():
    """Requires real API credentials - use cautiously."""
    pass
```

### Mocking Best Practices

```python
from unittest.mock import Mock, MagicMock, patch

# Mock external dependencies
@patch('claude_oauth_auth.client.Anthropic')
def test_with_mock(mock_anthropic):
    """Test with mocked Anthropic client."""
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client

    # Test code using mocked client
```

## Continuous Integration

### GitHub Actions Integration

The test suite integrates with GitHub Actions:

```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: |
    pytest --cov=claude_oauth_auth --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

### Pre-commit Hooks

Set up pre-commit hooks for local testing:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Troubleshooting

### Tests Failing Locally

1. **Check Python version**: Ensure you're using Python 3.8+
   ```bash
   python --version
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Clear pytest cache**:
   ```bash
   pytest --cache-clear
   ```

4. **Check environment variables**:
   ```bash
   # Ensure test environment is clean
   unset ANTHROPIC_API_KEY
   unset ANTHROPIC_AUTH_TOKEN
   ```

### Coverage Issues

1. **Identify missing coverage**:
   ```bash
   pytest --cov=claude_oauth_auth --cov-report=term-missing
   ```

2. **Focus on specific module**:
   ```bash
   pytest --cov=claude_oauth_auth.oauth_manager --cov-report=term-missing
   ```

3. **Check excluded lines** in `pyproject.toml`:
   - Pragma comments: `# pragma: no cover`
   - Abstract methods
   - TYPE_CHECKING blocks

### Tox Issues

1. **Missing Python versions**:
   ```bash
   # Skip missing interpreters
   tox --skip-missing-interpreters
   ```

2. **Rebuild environments**:
   ```bash
   tox -r  # Recreate environments
   ```

3. **Clear tox cache**:
   ```bash
   rm -rf .tox/
   ```

## Performance Testing

### Measure Test Execution Time

```bash
# Show slowest tests
pytest --durations=10

# Show all test durations
pytest --durations=0
```

### Parallel Test Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Best Practices

### Do's

✅ Write clear, descriptive test names
✅ Use fixtures for reusable test data
✅ Mock external dependencies (APIs, file system when appropriate)
✅ Test both success and error paths
✅ Keep tests independent and isolated
✅ Aim for 95%+ coverage
✅ Document complex test scenarios

### Don'ts

❌ Don't test external APIs without mocking (except in @real tests)
❌ Don't share state between tests
❌ Don't use hardcoded credentials
❌ Don't skip error handling tests
❌ Don't test implementation details
❌ Don't commit coverage reports to git

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [tox documentation](https://tox.wiki/)
- [Python testing best practices](https://docs.python-guide.org/writing/tests/)

## Contributing

When adding new tests:

1. Follow existing test structure
2. Add appropriate docstrings
3. Use available fixtures
4. Maintain 95%+ coverage
5. Run all tests before committing:
   ```bash
   pytest -v
   tox -e lint,type,coverage
   ```

## License

Tests are part of the claude-oauth-auth package and follow the same MIT license.
