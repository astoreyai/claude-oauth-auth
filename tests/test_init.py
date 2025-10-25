"""
Tests for __init__.py module-level functions.

These tests cover the package-level convenience functions like
get_version() and get_package_info().
"""

import claude_oauth_auth


def test_get_version():
    """Test get_version() function."""
    version = claude_oauth_auth.get_version()

    assert isinstance(version, str)
    assert version == claude_oauth_auth.__version__
    assert len(version) > 0


def test_get_package_info():
    """Test get_package_info() function."""
    info = claude_oauth_auth.get_package_info()

    assert isinstance(info, dict)
    assert "name" in info
    assert "version" in info
    assert "author" in info
    assert "license" in info
    assert "description" in info
    assert "features" in info
    assert "public_api" in info

    # Check types
    assert isinstance(info["features"], list)
    assert isinstance(info["public_api"], list)

    # Check values
    assert info["name"] == "claude-oauth-auth"
    assert info["version"] == claude_oauth_auth.__version__
    assert len(info["features"]) > 0
    assert len(info["public_api"]) > 0

    # Check that OAuth support is mentioned
    assert any("oauth" in feature.lower() for feature in info["features"])
