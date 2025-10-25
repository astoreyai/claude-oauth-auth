# AI Scientist Migration Guide

**Migration from Embedded Auth Code to `claude-oauth-auth` Package**

**Version**: 0.1.0
**Status**: Phase 5 - Integration Planning
**Target**: AI Scientist v0.1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Benefits of Migration](#benefits-of-migration)
3. [Pre-Migration Checklist](#pre-migration-checklist)
4. [Step-by-Step Migration](#step-by-step-migration)
5. [Before/After Examples](#beforeafter-examples)
6. [Testing the Migration](#testing-the-migration)
7. [Rollback Procedure](#rollback-procedure)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The AI Scientist project originally implemented OAuth authentication and Claude SDK client functionality directly in its codebase. This code has now been extracted into the `claude-oauth-auth` package for better maintainability, reusability, and testing.

### What's Being Migrated

**Modules to be replaced:**
- `ai_scientist/core/oauth_manager.py` → `claude_oauth_auth.oauth_manager`
- `ai_scientist/core/auth_manager.py` → `claude_oauth_auth.auth_manager`
- `ai_scientist/core/claude_sdk_client.py` → `claude_oauth_auth.client`

**Files affected:**
- `ai_scientist/core/__init__.py` - Update imports
- `tests/test_oauth_integration.py` - Update test imports
- `examples/tot_with_real_claude.py` - Update example imports
- `scripts/validate_claude_sdk.py` - Update validation imports
- Documentation files - Update code examples

### Migration Timeline

**Estimated time**: 2-4 hours
- Phase 1: Install package (5 min)
- Phase 2: Update imports (30 min)
- Phase 3: Run tests (30 min)
- Phase 4: Remove old code (15 min)
- Phase 5: Final validation (30 min)
- Buffer: 1-2 hours for troubleshooting

---

## Benefits of Migration

### 1. **Reduced Codebase Complexity**
- **Before**: ~2,500 lines of authentication code in AI Scientist
- **After**: Single dependency, ~50 lines of import statements
- **Benefit**: Easier to maintain core AI Scientist functionality

### 2. **Improved Testability**
- Dedicated test suite in package (95%+ coverage)
- CI/CD pipeline for auth code
- Isolated testing of authentication logic

### 3. **Better Documentation**
- Comprehensive API documentation
- Interactive examples
- Troubleshooting guides
- Version-specific migration guides

### 4. **Faster Bug Fixes**
- Centralized bug tracking
- Dedicated package maintenance
- Independent release cycle
- Quick security patches

### 5. **Shared Improvements**
- Other projects benefit from improvements
- Community contributions
- Industry best practices
- Enhanced error messages

### 6. **Simplified Dependency Management**
- Single version number to track
- Clear compatibility matrix
- Semantic versioning
- Automatic dependency updates

---

## Pre-Migration Checklist

Before starting the migration, ensure:

### Environment Requirements
- [ ] Python 3.9+ installed (AI Scientist requires 3.9+)
- [ ] Virtual environment activated
- [ ] Git repository in clean state (no uncommitted changes)
- [ ] All tests currently passing

### Backup and Safety
- [ ] Create backup branch: `git checkout -b backup/pre-oauth-migration`
- [ ] Tag current version: `git tag pre-oauth-migration-$(date +%Y%m%d)`
- [ ] Document current test results
- [ ] Export current authentication configuration

### Verification
```bash
# Check Python version
python --version  # Should be 3.9+

# Check current tests pass
cd /home/aaron/projects/ai_scientist
source .venv/bin/activate
pytest tests/test_oauth_integration.py -v

# Check git status
git status  # Should show clean working tree

# Create backup
git checkout -b backup/pre-oauth-migration
git tag pre-oauth-migration-$(date +%Y%m%d)
```

---

## Step-by-Step Migration

### Step 1: Install the Package (Dual Installation)

First, install the package **alongside** existing code (not replacing it yet):

```bash
cd /home/aaron/projects/ai_scientist

# Activate virtual environment
source .venv/bin/activate

# Install claude-oauth-auth package
pip install -e /home/aaron/projects/claude-oauth-auth

# Verify installation
python -c "import claude_oauth_auth; print(f'✓ Installed version {claude_oauth_auth.__version__}')"
```

**Expected output:**
```
✓ Installed version 0.1.0
```

### Step 2: Update Core Module Imports

Update `ai_scientist/core/__init__.py`:

**Before:**
```python
# OAuth and Authentication Support
from .oauth_manager import (
    OAuthTokenManager,
    get_oauth_token,
    is_oauth_available,
    get_oauth_info,
    get_token_manager
)

from .auth_manager import (
    UnifiedAuthManager,
    AuthType,
    AuthSource,
    AuthCredentials,
    discover_credentials,
    get_auth_status,
    create_anthropic_client
)

from .claude_sdk_client_v2 import (
    ClaudeSDKClient,
    create_claude_client
)
```

**After:**
```python
# OAuth and Authentication Support (from package)
from claude_oauth_auth import (
    # OAuth Manager
    OAuthTokenManager,
    get_oauth_token,
    is_oauth_available,
    get_oauth_info,
    get_token_manager,
    # Auth Manager
    UnifiedAuthManager,
    AuthType,
    AuthSource,
    AuthCredentials,
    discover_credentials,
    get_auth_status,
    create_anthropic_client,
    # Client
    ClaudeClient as ClaudeSDKClient,  # Alias for compatibility
    create_client as create_claude_client  # Alias for compatibility
)
```

### Step 3: Update Test Imports

Update `tests/test_oauth_integration.py`:

**Before:**
```python
from ai_scientist.core.oauth_manager import (
    OAuthTokenManager,
    get_oauth_token,
    is_oauth_available,
    get_oauth_info,
    get_token_manager
)
from ai_scientist.core.auth_manager import (
    UnifiedAuthManager,
    AuthType,
    AuthSource,
    AuthCredentials,
    discover_credentials,
    get_auth_status
)
from ai_scientist.core.claude_sdk_client_v2 import (
    ClaudeSDKClient,
    create_claude_client
)
```

**After:**
```python
from claude_oauth_auth import (
    OAuthTokenManager,
    get_oauth_token,
    is_oauth_available,
    get_oauth_info,
    get_token_manager,
    UnifiedAuthManager,
    AuthType,
    AuthSource,
    AuthCredentials,
    discover_credentials,
    get_auth_status,
    ClaudeClient as ClaudeSDKClient,
    create_client as create_claude_client
)
```

### Step 4: Update Example Scripts

Update `examples/tot_with_real_claude.py`:

**Before:**
```python
from ai_scientist.core.claude_sdk_client import ClaudeSDKClient
```

**After:**
```python
from claude_oauth_auth import ClaudeClient as ClaudeSDKClient
```

### Step 5: Update Validation Scripts

Update `scripts/validate_claude_sdk.py` and `scripts/quick_validation.py`:

**Before:**
```python
from ai_scientist.core.claude_sdk_client import ClaudeSDKClient
```

**After:**
```python
from claude_oauth_auth import ClaudeClient as ClaudeSDKClient
```

### Step 6: Run Automated Migration Script

For bulk updates across all files, use the migration script:

```bash
cd /home/aaron/projects/ai_scientist

# Run in dry-run mode first
python /home/aaron/projects/claude-oauth-auth/scripts/migrate_ai_scientist.py \
    --dry-run \
    --ai-scientist-path /home/aaron/projects/ai_scientist

# Review changes, then run for real
python /home/aaron/projects/claude-oauth-auth/scripts/migrate_ai_scientist.py \
    --ai-scientist-path /home/aaron/projects/ai_scientist \
    --backup
```

### Step 7: Run Tests

```bash
cd /home/aaron/projects/ai_scientist
source .venv/bin/activate

# Run OAuth integration tests
pytest tests/test_oauth_integration.py -v

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=ai_scientist --cov-report=html
```

**Expected results:**
- All tests should pass
- Coverage should remain at 90%+
- No import errors

### Step 8: Remove Old Code Files

Only after tests pass, remove the old embedded code:

```bash
# Create backup first
mkdir -p ai_scientist/core/archive
mv ai_scientist/core/oauth_manager.py ai_scientist/core/archive/
mv ai_scientist/core/auth_manager.py ai_scientist/core/archive/
mv ai_scientist/core/claude_sdk_client.py ai_scientist/core/archive/
mv ai_scientist/core/claude_sdk_client_v2.py ai_scientist/core/archive/

# Or delete (only if backup exists)
# rm ai_scientist/core/oauth_manager.py
# rm ai_scientist/core/auth_manager.py
# rm ai_scientist/core/claude_sdk_client.py
# rm ai_scientist/core/claude_sdk_client_v2.py
```

### Step 9: Update Requirements

Update `requirements.txt`:

**Before:**
```txt
# LLM Integrations (Optional - for non-Claude Code mode)
# anthropic>=0.7.0               # Anthropic API (optional)
```

**After:**
```txt
# LLM Integrations and Authentication
claude-oauth-auth>=0.1.0         # OAuth authentication for Claude API
```

Update `pyproject.toml`:

**Before:**
```toml
dependencies = [
    "requests>=2.31.0",
    "pypdf>=3.17.0",
    # ... other deps
]
```

**After:**
```toml
dependencies = [
    "requests>=2.31.0",
    "pypdf>=3.17.0",
    "claude-oauth-auth>=0.1.0",
    # ... other deps
]
```

### Step 10: Final Validation

```bash
# Run all tests
pytest tests/ -v

# Validate imports
python -c "from ai_scientist.core import ClaudeSDKClient; print('✓ Imports work')"

# Test OAuth discovery
python -c "from ai_scientist.core import get_auth_status; print(get_auth_status())"

# Run example
python examples/tot_with_real_claude.py
```

---

## Before/After Examples

### Example 1: Basic Client Creation

**Before:**
```python
from ai_scientist.core.claude_sdk_client import ClaudeSDKClient

# Create client with automatic OAuth discovery
client = ClaudeSDKClient()
response = client.generate("Hello, Claude!")
```

**After:**
```python
from claude_oauth_auth import ClaudeClient

# Same API, different import
client = ClaudeClient()
response = client.generate("Hello, Claude!")

# Or use alias for backward compatibility
from ai_scientist.core import ClaudeSDKClient  # Re-exported from package
client = ClaudeSDKClient()
```

### Example 2: OAuth Token Management

**Before:**
```python
from ai_scientist.core.oauth_manager import get_oauth_token, is_oauth_available

if is_oauth_available():
    token = get_oauth_token()
    print(f"Using OAuth token: {token[:15]}...")
```

**After:**
```python
from claude_oauth_auth import get_oauth_token, is_oauth_available

# Identical API
if is_oauth_available():
    token = get_oauth_token()
    print(f"Using OAuth token: {token[:15]}...")
```

### Example 3: Authentication Discovery

**Before:**
```python
from ai_scientist.core.auth_manager import UnifiedAuthManager, AuthType

manager = UnifiedAuthManager(verbose=True)
creds = manager.discover_credentials()

if creds.auth_type == AuthType.OAUTH_TOKEN:
    print("Using Claude Max subscription")
```

**After:**
```python
from claude_oauth_auth import UnifiedAuthManager, AuthType

# Identical API
manager = UnifiedAuthManager(verbose=True)
creds = manager.discover_credentials()

if creds.auth_type == AuthType.OAUTH_TOKEN:
    print("Using Claude Max subscription")
```

### Example 4: Direct Anthropic Client Creation

**Before:**
```python
from ai_scientist.core.auth_manager import create_anthropic_client

# Auto-discover credentials and create client
client = create_anthropic_client()
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**After:**
```python
from claude_oauth_auth import create_anthropic_client

# Identical API
client = create_anthropic_client()
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Example 5: Test Fixtures

**Before:**
```python
from ai_scientist.core.oauth_manager import OAuthTokenManager

@pytest.fixture
def oauth_manager(mock_credentials_file):
    return OAuthTokenManager(credentials_path=mock_credentials_file)
```

**After:**
```python
from claude_oauth_auth import OAuthTokenManager

# Identical API
@pytest.fixture
def oauth_manager(mock_credentials_file):
    return OAuthTokenManager(credentials_path=mock_credentials_file)
```

---

## Testing the Migration

### Unit Tests

```bash
cd /home/aaron/projects/ai_scientist

# Test OAuth manager functionality
pytest tests/test_oauth_integration.py::TestOAuthTokenManager -v

# Test auth manager functionality
pytest tests/test_oauth_integration.py::TestUnifiedAuthManager -v

# Test client functionality
pytest tests/test_oauth_integration.py::TestClaudeSDKClient -v
```

### Integration Tests

```bash
# Test full workflow
pytest tests/test_oauth_integration.py -v -m "integration"

# Test with real credentials (optional)
pytest tests/test_oauth_integration.py -v --run-real
```

### Manual Testing

```python
# Test 1: Import verification
python -c "
from ai_scientist.core import (
    ClaudeSDKClient,
    OAuthTokenManager,
    UnifiedAuthManager,
    get_oauth_token,
    is_oauth_available
)
print('✓ All imports successful')
"

# Test 2: OAuth discovery
python -c "
from ai_scientist.core import get_auth_status
status = get_auth_status()
print(status['summary'])
"

# Test 3: Client creation
python -c "
from ai_scientist.core import ClaudeSDKClient
client = ClaudeSDKClient()
print(f'✓ Client created: {client}')
"
```

### Regression Testing

Run the full AI Scientist test suite to ensure no regressions:

```bash
# Run all tests with coverage
pytest tests/ -v --cov=ai_scientist --cov-report=html

# Check coverage report
open htmlcov/index.html  # Or: firefox htmlcov/index.html
```

**Success criteria:**
- All tests pass
- Coverage remains ≥90%
- No new errors or warnings
- Example scripts run successfully

---

## Rollback Procedure

If you encounter issues during migration, follow these steps to rollback:

### Immediate Rollback (Before Removing Old Files)

If old files still exist:

```bash
cd /home/aaron/projects/ai_scientist

# Uninstall package
pip uninstall claude-oauth-auth -y

# Revert import changes
git checkout ai_scientist/core/__init__.py
git checkout tests/test_oauth_integration.py
git checkout examples/tot_with_real_claude.py

# Verify rollback
pytest tests/test_oauth_integration.py -v
```

### Full Rollback (After Removing Old Files)

If old files were archived or deleted:

```bash
cd /home/aaron/projects/ai_scientist

# Option 1: Restore from archive
mv ai_scientist/core/archive/*.py ai_scientist/core/

# Option 2: Restore from git
git checkout backup/pre-oauth-migration

# Option 3: Restore from tag
git checkout pre-oauth-migration-$(date +%Y%m%d)

# Uninstall package
pip uninstall claude-oauth-auth -y

# Verify rollback
pytest tests/test_oauth_integration.py -v
```

### Partial Rollback (Keep Package, Revert Imports)

If you want to keep the package installed but revert to old code:

```bash
# Restore old files from archive
mv ai_scientist/core/archive/*.py ai_scientist/core/

# Revert imports in __init__.py
git checkout ai_scientist/core/__init__.py

# Package remains installed but unused
# This allows gradual migration
```

---

## Troubleshooting

### Issue 1: Import Errors

**Symptom:**
```python
ImportError: cannot import name 'ClaudeSDKClient' from 'ai_scientist.core'
```

**Solution:**
```bash
# Verify package is installed
pip list | grep claude-oauth-auth

# Reinstall if needed
pip install -e /home/aaron/projects/claude-oauth-auth

# Check imports
python -c "import claude_oauth_auth; print(claude_oauth_auth.__version__)"
```

### Issue 2: Tests Failing

**Symptom:**
```
tests/test_oauth_integration.py::test_oauth_token_discovery FAILED
```

**Solution:**
```bash
# Run in verbose mode to see details
pytest tests/test_oauth_integration.py::test_oauth_token_discovery -vv

# Check if old modules are still being imported
python -c "
import ai_scientist.core.oauth_manager as om
print(om.__file__)  # Should be from package, not local
"

# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

### Issue 3: Name Conflicts

**Symptom:**
```python
AttributeError: module 'ai_scientist.core' has no attribute 'ClaudeSDKClient'
```

**Solution:**

Check `ai_scientist/core/__init__.py` has correct aliases:

```python
from claude_oauth_auth import (
    ClaudeClient as ClaudeSDKClient,  # ← Note the alias
    create_client as create_claude_client
)

__all__ = [
    "ClaudeSDKClient",  # ← Must be in __all__
    "create_claude_client",
    # ... other exports
]
```

### Issue 4: Credential Discovery Issues

**Symptom:**
```
ValueError: No Anthropic API credentials found
```

**Solution:**
```python
# Debug credential discovery
from claude_oauth_auth import diagnose
diagnose()

# Check specific sources
from claude_oauth_auth import get_auth_status
status = get_auth_status()
print(status['summary'])
print("Available methods:", status['available_methods'])
```

### Issue 5: Version Compatibility

**Symptom:**
```
TypeError: __init__() got an unexpected keyword argument 'verbose'
```

**Solution:**
```bash
# Check package version
python -c "import claude_oauth_auth; print(claude_oauth_auth.__version__)"

# Update to latest version
pip install --upgrade -e /home/aaron/projects/claude-oauth-auth

# Check API compatibility
python -c "
from claude_oauth_auth import UnifiedAuthManager
import inspect
print(inspect.signature(UnifiedAuthManager.__init__))
"
```

---

## Post-Migration Checklist

After successful migration:

- [ ] All tests passing
- [ ] Coverage at 90%+
- [ ] Old code files archived or removed
- [ ] Requirements updated
- [ ] Documentation updated
- [ ] Commit changes with clear message
- [ ] Tag new version
- [ ] Update CHANGELOG.md

```bash
# Commit migration
git add .
git commit -m "Migrate to claude-oauth-auth package

- Replace embedded OAuth/auth code with package
- Update all imports across codebase
- Remove old oauth_manager.py, auth_manager.py, claude_sdk_client*.py
- Update requirements.txt and pyproject.toml
- All tests passing, coverage maintained at 90%+

Migration completed successfully using claude-oauth-auth v0.1.0"

# Tag version
git tag ai-scientist-v0.1.0-with-oauth-package

# Push changes (if ready)
# git push origin main --tags
```

---

## Additional Resources

- **Package Documentation**: `/home/aaron/projects/claude-oauth-auth/README.md`
- **API Reference**: `/home/aaron/projects/claude-oauth-auth/docs/API.md`
- **Example Integration**: `/home/aaron/projects/claude-oauth-auth/examples/ai_scientist_integration/`
- **Migration Script**: `/home/aaron/projects/claude-oauth-auth/scripts/migrate_ai_scientist.py`
- **Rollout Plan**: `/home/aaron/projects/claude-oauth-auth/AI_SCIENTIST_ROLLOUT.md`

---

## Support

If you encounter issues not covered in this guide:

1. Check package documentation
2. Run diagnostic: `python -m claude_oauth_auth diagnose`
3. Review examples: `/home/aaron/projects/claude-oauth-auth/examples/`
4. Check for similar issues in package tests
5. Consult rollout plan for phased migration approach

---

**Migration Guide Version**: 1.0.0
**Last Updated**: 2025-10-24
**Package Version**: claude-oauth-auth v0.1.0
**Target Project**: AI Scientist v0.1.0
