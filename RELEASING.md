# Release Process

This document describes the process for releasing new versions of claude-oauth-auth.

## Table of Contents

- [Version Numbering](#version-numbering)
- [Release Types](#release-types)
- [Pre-Release Checklist](#pre-release-checklist)
- [Release Steps](#release-steps)
- [Post-Release Steps](#post-release-steps)
- [Emergency Releases](#emergency-releases)
- [Release Automation](#release-automation)

## Version Numbering

We follow [Semantic Versioning](https://semver.org/) (SemVer):

```
MAJOR.MINOR.PATCH
```

- **MAJOR** - Incompatible API changes
- **MINOR** - New functionality (backwards-compatible)
- **PATCH** - Bug fixes (backwards-compatible)

### Examples

- `0.1.0` → `0.1.1` - Bug fix release
- `0.1.0` → `0.2.0` - New features, no breaking changes
- `0.9.0` → `1.0.0` - First stable release, possible breaking changes
- `1.2.3` → `2.0.0` - Breaking changes in stable version

### Pre-1.0 Versions

During pre-1.0 development (0.x.y):
- Breaking changes can occur in MINOR versions
- We'll clearly document all breaking changes
- Users should expect some instability

### Version 1.0 and Beyond

Once we reach 1.0:
- MAJOR version changes indicate breaking changes
- We'll maintain backwards compatibility within major versions
- Deprecation warnings before removal

## Release Types

### Patch Release (0.1.0 → 0.1.1)

**When:**
- Bug fixes
- Documentation updates
- Performance improvements (without API changes)
- Dependency updates (patch versions)

**Frequency:** As needed

### Minor Release (0.1.0 → 0.2.0)

**When:**
- New features (backwards-compatible)
- Deprecations (with warnings)
- Dependency updates (minor versions)
- Significant documentation additions

**Frequency:** Monthly or as needed

### Major Release (0.9.0 → 1.0.0)

**When:**
- Breaking API changes
- Removal of deprecated features
- Major architectural changes
- Dependency updates (major versions)

**Frequency:** Infrequent, well-planned

## Pre-Release Checklist

Before starting a release, ensure:

- [ ] All target issues/PRs are merged
- [ ] All tests pass on main branch
- [ ] No known critical bugs
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is up to date
- [ ] Version numbers are consistent
- [ ] Security vulnerabilities are addressed

## Release Steps

### 1. Prepare the Release

#### Update Version Number

Update version in `pyproject.toml`:

```toml
[project]
name = "claude-oauth-auth"
version = "0.2.0"  # Update this
```

#### Update CHANGELOG.md

Move items from `[Unreleased]` to the new version:

```markdown
## [0.2.0] - 2025-11-15

### Added
- New feature A (#42)
- New feature B (#45)

### Changed
- Improved error handling (#50)

### Fixed
- Bug fix (#44)
```

Add the release link at the bottom:

```markdown
[0.2.0]: https://github.com/astoreyai/claude-oauth-auth/compare/v0.1.0...v0.2.0
```

#### Review Documentation

Ensure all documentation is current:

```bash
# Check README.md
# Check docs/ directory
# Verify code examples work
# Update API documentation if needed
```

### 2. Create Release Branch

```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Create release branch
git checkout -b release/v0.2.0

# Commit version updates
git add pyproject.toml CHANGELOG.md
git commit -m "chore: prepare release v0.2.0"

# Push release branch
git push origin release/v0.2.0
```

### 3. Run Final Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run full test suite
pytest --cov=claude_oauth_auth --cov-fail-under=95

# Run linting
ruff check src tests

# Run type checking
mypy src

# Test across Python versions (if tox is configured)
tox

# Test package build
python -m build
pip install dist/claude_oauth_auth-0.2.0-py3-none-any.whl
```

### 4. Create Pull Request

Create a PR from `release/v0.2.0` to `main`:

- Title: "Release v0.2.0"
- Description: Summary of changes from CHANGELOG
- Label: `release`
- Request review from maintainers

### 5. Merge and Tag

Once approved:

```bash
# Merge to main
git checkout main
git merge release/v0.2.0
git push origin main

# Create and push tag
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0

# Delete release branch (optional)
git branch -d release/v0.2.0
git push origin --delete release/v0.2.0
```

### 6. Build and Publish to PyPI

#### Build Distribution

```bash
# Ensure build tools are installed
pip install --upgrade build twine

# Build distribution packages
python -m build

# Verify build
ls -la dist/
# Should see:
# - claude_oauth_auth-0.2.0-py3-none-any.whl
# - claude_oauth_auth-0.2.0.tar.gz
```

#### Test on PyPI Test Server (Optional but Recommended)

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ claude-oauth-auth==0.2.0

# Verify it works
python -c "from claude_oauth_auth import ClaudeOAuthClient; print('Success!')"
```

#### Publish to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# Enter credentials when prompted
# Or use API token: __token__ / your-api-token

# Verify on PyPI
# Visit: https://pypi.org/project/claude-oauth-auth/
```

#### Using API Tokens (Recommended)

Set up PyPI API token:

```bash
# Create ~/.pypirc
cat > ~/.pypirc << EOF
[pypi]
username = __token__
password = pypi-YOUR-API-TOKEN-HERE

[testpypi]
username = __token__
password = pypi-YOUR-TESTPYPI-TOKEN-HERE
EOF

chmod 600 ~/.pypirc

# Now upload without entering credentials
python -m twine upload dist/*
```

### 7. Create GitHub Release

On GitHub:

1. Go to [Releases](https://github.com/astoreyai/claude-oauth-auth/releases)
2. Click "Draft a new release"
3. Select tag: `v0.2.0`
4. Release title: `v0.2.0`
5. Description: Copy from CHANGELOG.md
6. Attach build artifacts (optional)
7. Check "Set as the latest release"
8. Click "Publish release"

Or use GitHub CLI:

```bash
# Install gh CLI if needed
# https://cli.github.com/

# Create release
gh release create v0.2.0 \
  --title "v0.2.0" \
  --notes-file <(sed -n '/## \[0.2.0\]/,/## \[/p' CHANGELOG.md | head -n -1) \
  dist/*
```

## Post-Release Steps

### 1. Verify Release

```bash
# Test PyPI installation
pip install --upgrade claude-oauth-auth

# Verify version
python -c "import claude_oauth_auth; print(claude_oauth_auth.__version__)"

# Test basic functionality
python -c "from claude_oauth_auth import ClaudeOAuthClient"
```

### 2. Update Documentation

If using ReadTheDocs or similar:
- Trigger documentation build
- Verify latest version shows correctly
- Check that examples work

### 3. Announce Release

Consider announcing via:

- [ ] GitHub Discussions
- [ ] Twitter/X (if applicable)
- [ ] Reddit communities (r/Python, relevant subreddits)
- [ ] Email to users mailing list (if exists)
- [ ] Blog post (if applicable)

Example announcement:

```markdown
📢 claude-oauth-auth v0.2.0 is now available!

🎉 What's new:
- Feature A for improved OAuth flows
- Feature B for better error handling
- Performance improvements

📦 Install: pip install --upgrade claude-oauth-auth
📖 Docs: https://github.com/astoreyai/claude-oauth-auth
🔗 Release: https://github.com/astoreyai/claude-oauth-auth/releases/tag/v0.2.0

Thank you to all contributors! 🙏
```

### 4. Monitor for Issues

After release:
- Watch GitHub issues for bug reports
- Monitor PyPI download stats
- Check for installation problems
- Be ready for hotfix if needed

### 5. Prepare for Next Release

```bash
# Update CHANGELOG.md
# Add [Unreleased] section
# Update version comparison link

git checkout main
git pull origin main

# Edit CHANGELOG.md to add:
## [Unreleased]

### Added
- Features to be added

### Changed
- Changes to be made

# Commit
git add CHANGELOG.md
git commit -m "chore: prepare for next release"
git push origin main
```

## Emergency Releases

For critical bugs or security issues:

### Hotfix Process

1. **Create hotfix branch from tag:**
   ```bash
   git checkout -b hotfix/v0.2.1 v0.2.0
   ```

2. **Make minimal fix:**
   ```bash
   # Fix the critical issue
   # Update tests
   # Update CHANGELOG.md
   ```

3. **Fast-track release:**
   ```bash
   # Update version to 0.2.1
   # Run tests
   # Commit and tag
   git commit -m "fix: critical security issue"
   git tag v0.2.1
   ```

4. **Merge to main:**
   ```bash
   git checkout main
   git merge hotfix/v0.2.1
   git push origin main v0.2.1
   ```

5. **Release immediately:**
   ```bash
   python -m build
   python -m twine upload dist/*
   gh release create v0.2.1 --title "v0.2.1 (Hotfix)"
   ```

6. **Announce urgently** if security-related

## Release Automation

### Future Improvements

Consider setting up:

- **GitHub Actions** for automated builds
- **Automated version bumping** with tools like `bump2version`
- **Automatic PyPI publishing** on tag creation
- **Automated changelog generation** from commit messages
- **Release draft automation**

### Example GitHub Action (Future)

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Build
        run: |
          pip install build
          python -m build
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          password: ${{ secrets.PYPI_API_TOKEN }}
      - name: Create GitHub Release
        uses: softprops/action-gh-release@v1
        with:
          files: dist/*
```

## Questions?

If you have questions about the release process:
- Open a [Discussion](https://github.com/astoreyai/claude-oauth-auth/discussions)
- Contact maintainers
- Refer to [CONTRIBUTING.md](.github/CONTRIBUTING.md)

---

**Last Updated**: October 2025
