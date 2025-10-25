# Installation Guide

Complete guide to installing and setting up `claude-oauth-auth`.

## Requirements

- **Python**: 3.8 or higher
- **pip**: Latest version recommended
- **Operating System**: Linux, macOS, or Windows

## Installation Methods

### Standard Installation

Install the latest stable version from PyPI:

```bash
pip install claude-oauth-auth
```

This installs the core package with all required dependencies.

### Development Installation

For development work, install with development dependencies:

```bash
pip install claude-oauth-auth[dev]
```

This includes:
- Testing tools (pytest, pytest-cov)
- Code quality tools (ruff, mypy)
- Security scanners (bandit, safety)

### Documentation Tools

To build documentation locally:

```bash
pip install claude-oauth-auth[docs]
```

This includes:
- MkDocs and MkDocs Material theme
- MkDocstrings for API documentation

### Benchmark Tools

For performance testing:

```bash
pip install claude-oauth-auth[benchmark]
```

This includes:
- pytest-benchmark
- memory-profiler
- psutil

### All Optional Dependencies

Install everything:

```bash
pip install claude-oauth-auth[all]
```

## Installation from Source

### For Development

Clone the repository and install in development mode:

```bash
# Clone the repository
git clone https://github.com/astoreyai/claude-oauth-auth.git
cd claude-oauth-auth

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"
```

### For Production from Source

```bash
# Clone the repository
git clone https://github.com/astoreyai/claude-oauth-auth.git
cd claude-oauth-auth

# Build and install
pip install .
```

## Virtual Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate

# Install package
pip install claude-oauth-auth
```

### Using conda

```bash
# Create conda environment
conda create -n claude-auth python=3.11

# Activate environment
conda activate claude-auth

# Install package
pip install claude-oauth-auth
```

### Using poetry

```bash
# Initialize poetry project
poetry init

# Add dependency
poetry add claude-oauth-auth

# Install
poetry install
```

## Verifying Installation

### Check Installation

```bash
# Check if package is installed
pip show claude-oauth-auth

# Check version
python -c "import claude_oauth_auth; print(claude_oauth_auth.__version__)"
```

### Test Import

```python
# Test basic import
from claude_oauth_auth import UnifiedAuthManager, ClaudeClient

# Verify installation
import claude_oauth_auth
print(f"Installed version: {claude_oauth_auth.__version__}")
```

### Run Quick Test

```python
from claude_oauth_auth import UnifiedAuthManager

# Check if credentials are available
auth = UnifiedAuthManager()
print(f"Credentials available: {auth.has_credentials()}")
print(f"Authentication method: {auth.auth_method}")
```

## Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade claude-oauth-auth
```

### Upgrade to Specific Version

```bash
pip install claude-oauth-auth==0.1.0
```

### Check for Updates

```bash
pip list --outdated | grep claude-oauth-auth
```

## Uninstalling

```bash
pip uninstall claude-oauth-auth
```

## Common Installation Issues

### Issue: Permission Denied

**Solution**: Use `--user` flag or virtual environment

```bash
# Install for current user only
pip install --user claude-oauth-auth

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install claude-oauth-auth
```

### Issue: Python Version Too Old

**Error**: `Requires-Python >=3.8`

**Solution**: Upgrade Python

```bash
# Check current version
python --version

# Upgrade Python using your system's package manager
# Ubuntu/Debian
sudo apt update && sudo apt install python3.11

# macOS with Homebrew
brew install python@3.11

# Or use pyenv
pyenv install 3.11.0
pyenv global 3.11.0
```

### Issue: Missing Dependencies

**Solution**: Reinstall with all dependencies

```bash
pip install --force-reinstall --no-cache-dir claude-oauth-auth
```

### Issue: Import Error After Installation

**Solution**: Ensure you're in the correct environment

```bash
# Check which Python is being used
which python

# Check if package is installed
pip list | grep claude-oauth-auth

# Reinstall if necessary
pip uninstall claude-oauth-auth
pip install claude-oauth-auth
```

## Platform-Specific Notes

### Linux

Standard installation should work on all distributions:

```bash
pip install claude-oauth-auth
```

### macOS

May need to install Python 3 first:

```bash
# Using Homebrew
brew install python3
pip3 install claude-oauth-auth
```

### Windows

Use Command Prompt or PowerShell:

```cmd
python -m pip install claude-oauth-auth
```

For development on Windows, ensure you have:
- Visual Studio Build Tools (for some dependencies)
- Git for Windows

## Docker Installation

Use the package in a Docker container:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install package
RUN pip install claude-oauth-auth

# Copy your application
COPY . .

CMD ["python", "your_app.py"]
```

Build and run:

```bash
docker build -t my-claude-app .
docker run -e ANTHROPIC_API_KEY=your_key my-claude-app
```

## Requirements Files

### For Production

Create `requirements.txt`:

```
claude-oauth-auth>=0.1.0
```

Install:

```bash
pip install -r requirements.txt
```

### For Development

Create `requirements-dev.txt`:

```
claude-oauth-auth[dev]>=0.1.0
```

Install:

```bash
pip install -r requirements-dev.txt
```

## Next Steps

After installation:

1. **Configure Credentials**: See [Authentication Guide](authentication.md)
2. **Quick Start**: Follow the [Quick Start Guide](quickstart.md)
3. **Complete Tutorial**: Try the [Tutorial](tutorial.md)
4. **Read Documentation**: Check the [User Guide](guide.md)

## Getting Help

If you encounter installation issues:

- Check the [Troubleshooting Guide](troubleshooting.md)
- Search [GitHub Issues](https://github.com/astoreyai/claude-oauth-auth/issues)
- Open a new issue with your system details and error message
