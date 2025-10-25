# Testing Integration Example

Comprehensive testing examples using pytest with mocking, fixtures, and integration tests.

## Features

- Mock authentication for testing
- Reusable fixtures
- Integration test examples
- Test coverage setup
- Parameterized tests
- CI/CD patterns

## Installation

```bash
pip install -r requirements.txt
```

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Run only unit tests
pytest -m unit

# Run integration tests (requires credentials)
pytest --run-integration

# Run specific test file
pytest test_with_claude.py

# Run specific test
pytest test_with_claude.py::TestClaudeClientMocking::test_mock_client_basic
```

## Test Organization

### Unit Tests
- Mock Claude client for fast, isolated tests
- Test application logic without API calls
- Run by default

### Integration Tests
- Test with real Claude API
- Require authentication credentials
- Run with `--run-integration` flag
- Marked with `@pytest.mark.integration`

## Fixtures

Available fixtures in `conftest.py`:
- `mock_claude_client`: Basic mock client
- `client_fixture`: Configured mock client
- `sample_prompts`: Test prompts
- `sample_responses`: Test responses

## License

MIT License - see main package for details.
