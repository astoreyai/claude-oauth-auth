# Contributing to claude-oauth-auth

First off, thank you for considering contributing to claude-oauth-auth! It's people like you that make this project such a great tool for the community.

## Welcome!

We love contributions from everyone. By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to Contribute

There are many ways to contribute to claude-oauth-auth:

- **Report bugs** - Help us identify issues and improve quality
- **Suggest features** - Share ideas for new functionality
- **Improve documentation** - Help others understand and use the package
- **Write code** - Fix bugs or implement new features
- **Review pull requests** - Help maintain code quality
- **Answer questions** - Help other users in discussions

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Getting Started

1. **Fork the repository** on GitHub

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/claude-oauth-auth.git
   cd claude-oauth-auth
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install in development mode** with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

## Development Workflow

### Making Changes

1. **Write your code** following our code style guidelines (see below)
2. **Add tests** for any new functionality
3. **Update documentation** if needed
4. **Run the test suite** to ensure everything works
5. **Commit your changes** with clear, descriptive messages

### Code Style Guidelines

We use automated tools to maintain consistent code quality:

#### Formatting with Ruff

```bash
# Check formatting
ruff check src tests

# Auto-fix issues
ruff check --fix src tests

# Format code
ruff format src tests
```

Our Ruff configuration:
- Line length: 100 characters
- Target: Python 3.8+
- Enforces: PEP 8, pyflakes, isort, and more

#### Type Checking with mypy

```bash
# Run type checker
mypy src
```

Our type checking standards:
- All functions must have type annotations
- No implicit `Any` types
- Strict optional checking enabled

### Testing Requirements

We maintain **95% code coverage** as a minimum standard.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=claude_oauth_auth --cov-report=html

# Run specific test file
pytest tests/test_oauth_manager.py

# Run with verbose output
pytest -v
```

#### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Use descriptive test names: `test_function_name_with_condition_expects_result`
- Test both success and failure cases
- Mock external dependencies (API calls, file I/O, etc.)
- Use fixtures for common test setup

Example test structure:
```python
def test_oauth_manager_initialization_with_valid_params_succeeds():
    """Test that OAuthManager initializes correctly with valid parameters."""
    manager = OAuthManager(
        client_id="test_id",
        client_secret="test_secret",
        redirect_uri="http://localhost:8080/callback"
    )
    assert manager.client_id == "test_id"
```

### Running the Full Test Suite

Before submitting a pull request:

```bash
# 1. Run linting
ruff check src tests

# 2. Run type checking
mypy src

# 3. Run tests with coverage
pytest --cov=claude_oauth_auth --cov-report=term --cov-fail-under=95

# 4. Check all Python versions (optional but recommended)
tox
```

## Pull Request Process

### Before Submitting

- [ ] All tests pass locally
- [ ] Code is formatted with ruff
- [ ] Type checking passes with mypy
- [ ] Test coverage is at least 95%
- [ ] Documentation is updated (if applicable)
- [ ] CHANGELOG.md is updated (see [RELEASING.md](../../RELEASING.md))

### Submitting Your PR

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Open a pull request** on GitHub

3. **Fill out the PR template** completely

4. **Wait for review** - maintainers will review your code and may request changes

5. **Address feedback** - make requested changes and push updates

6. **Get merged!** - once approved, a maintainer will merge your PR

### PR Guidelines

- **Keep PRs focused** - one feature or fix per PR
- **Write clear descriptions** - explain what and why, not just how
- **Link related issues** - use "Fixes #123" or "Relates to #456"
- **Keep commits clean** - squash unnecessary commits
- **Be responsive** - reply to comments and questions promptly
- **Be patient** - reviews may take a few days

## Commit Message Guidelines

We follow conventional commit format:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(oauth): add support for custom authorization endpoints

fix(auth): resolve token refresh race condition

docs(readme): update installation instructions
```

## Code Review Process

### What We Look For

- **Correctness** - Does it work as intended?
- **Tests** - Are there adequate tests?
- **Style** - Does it follow our guidelines?
- **Documentation** - Are changes documented?
- **Performance** - Are there any performance concerns?
- **Security** - Are there any security implications?

### Response Times

- Initial response: Within 3-5 business days
- Full review: Within 1-2 weeks (depending on complexity)
- We appreciate your patience!

## Documentation

### When to Update Docs

Update documentation when you:
- Add new features
- Change existing behavior
- Fix bugs that affect usage
- Improve error messages

### Documentation Types

- **README.md** - High-level overview and quick start
- **docs/** - Detailed guides and API reference
- **Docstrings** - In-code documentation
- **CHANGELOG.md** - Version history

### Docstring Format

We use Google-style docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description with more details about what the function does,
    any important behavior, or usage notes.

    Args:
        param1: Description of first parameter
        param2: Description of second parameter

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        RuntimeError: When operation fails

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

## Community Guidelines

### Be Respectful

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Getting Help

- **Questions?** Open a [GitHub Discussion](https://github.com/astoreyai/claude-oauth-auth/discussions)
- **Bug?** Open an [Issue](https://github.com/astoreyai/claude-oauth-auth/issues)
- **Security concern?** See [SECURITY.md](SECURITY.md)

### Recognition

Contributors are recognized in:
- GitHub contributor list
- CHANGELOG.md for significant contributions
- Release notes

## First Time Contributors

New to open source? Welcome! Here's how to get started:

1. Look for issues labeled `good first issue`
2. Read through this guide
3. Set up your development environment
4. Make a small change (fix a typo, improve docs)
5. Submit your first PR!

We're here to help. Don't hesitate to ask questions!

## Advanced Topics

### Release Process

See [RELEASING.md](../../RELEASING.md) for details on:
- Version numbering
- Release checklist
- Publishing to PyPI

### Architecture Decisions

For major changes:
1. Open an issue to discuss the proposal
2. Wait for feedback from maintainers
3. Create a design document if needed
4. Implement after approval

## License

By contributing to claude-oauth-auth, you agree that your contributions will be licensed under the MIT License.

## Questions?

Don't hesitate to reach out:
- Open a [Discussion](https://github.com/astoreyai/claude-oauth-auth/discussions)
- Comment on an existing [Issue](https://github.com/astoreyai/claude-oauth-auth/issues)

Thank you for contributing to claude-oauth-auth!
