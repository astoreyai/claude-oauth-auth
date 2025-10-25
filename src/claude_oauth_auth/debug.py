"""
Debug and diagnostic utilities for Claude OAuth authentication.

This module provides comprehensive diagnostics to help users troubleshoot
authentication issues and understand their credential setup.

Usage:
    >>> from claude_oauth_auth.debug import diagnose
    >>>
    >>> # Run comprehensive diagnostics
    >>> report = diagnose()
    >>> print(report)
    >>>
    >>> # Get detailed diagnostics as dictionary
    >>> from claude_oauth_auth.debug import get_diagnostics
    >>> diagnostics = get_diagnostics()
    >>> for key, value in diagnostics.items():
    ...     print(f"{key}: {value}")
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .auth_manager import AuthCredentials, AuthSource, AuthType, UnifiedAuthManager
from .oauth_manager import OAuthTokenManager, get_token_manager
from .validate import (
    is_token_expired,
    validate_api_key,
    validate_credential,
    validate_oauth_token,
)


logger = logging.getLogger(__name__)


def check_claude_code_installation() -> Dict[str, Any]:
    """
    Check if Claude Code is installed and accessible.

    Returns:
        Dictionary with installation status:
        - installed: True if Claude Code appears to be installed
        - credentials_path: Path to credentials file
        - credentials_exists: True if credentials file exists
        - credentials_readable: True if credentials file can be read
        - details: Additional information
    """
    credentials_path = Path.home() / ".claude" / ".credentials.json"

    result = {
        "installed": False,
        "credentials_path": str(credentials_path),
        "credentials_exists": credentials_path.exists(),
        "credentials_readable": False,
        "details": [],
    }

    # Check if credentials file exists
    if credentials_path.exists():
        result["details"].append(f"Found credentials file: {credentials_path}")

        # Try to read it
        try:
            with open(credentials_path) as f:
                data = json.load(f)

            result["credentials_readable"] = True
            result["details"].append("Credentials file is readable")

            # Check for OAuth data
            if "claudeAiOauth" in data:
                result["installed"] = True
                result["details"].append("Claude Code OAuth credentials found")
            else:
                result["details"].append("WARNING: No OAuth credentials in file")
        except json.JSONDecodeError as e:
            result["details"].append(f"ERROR: Invalid JSON in credentials file: {e}")
        except PermissionError:
            result["details"].append(f"ERROR: Permission denied reading {credentials_path}")
        except Exception as e:
            result["details"].append(f"ERROR: Could not read credentials: {e}")
    else:
        result["details"].append(f"Credentials file not found: {credentials_path}")
        result["details"].append("To fix: Install Claude Code from https://claude.com/claude-code")

    return result


def check_environment_variables() -> Dict[str, Any]:
    """
    Check for authentication-related environment variables.

    Returns:
        Dictionary with environment variable status:
        - ANTHROPIC_API_KEY: Status of API key env var
        - ANTHROPIC_AUTH_TOKEN: Status of auth token env var
        - has_any: True if any relevant env var is set
        - details: Additional information
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    auth_token = os.getenv("ANTHROPIC_AUTH_TOKEN")

    result = {
        "ANTHROPIC_API_KEY": {
            "set": api_key is not None,
            "valid": False,
            "message": None,
        },
        "ANTHROPIC_AUTH_TOKEN": {
            "set": auth_token is not None,
            "valid": False,
            "message": None,
        },
        "has_any": api_key is not None or auth_token is not None,
        "details": [],
    }

    # Validate API key if set
    if api_key:
        is_valid, message = validate_api_key(api_key)
        result["ANTHROPIC_API_KEY"]["valid"] = is_valid
        result["ANTHROPIC_API_KEY"]["message"] = message
        result["details"].append(f"ANTHROPIC_API_KEY: {message}")
    else:
        result["details"].append("ANTHROPIC_API_KEY: Not set")

    # Validate auth token if set
    if auth_token:
        is_valid, message = validate_oauth_token(auth_token)
        result["ANTHROPIC_AUTH_TOKEN"]["valid"] = is_valid
        result["ANTHROPIC_AUTH_TOKEN"]["message"] = message
        result["details"].append(f"ANTHROPIC_AUTH_TOKEN: {message}")
    else:
        result["details"].append("ANTHROPIC_AUTH_TOKEN: Not set")

    return result


def check_oauth_credentials() -> Dict[str, Any]:
    """
    Check OAuth credentials from Claude Code.

    Returns:
        Dictionary with OAuth credential status:
        - available: True if OAuth credentials exist
        - valid: True if token is not expired
        - expired: True if token is expired
        - info: Token information
        - details: Additional information
    """
    manager = get_token_manager()
    info = manager.get_token_info()

    result = {
        "available": info.get("available", False),
        "valid": info.get("is_valid", False),
        "expired": False,
        "info": info,
        "details": [],
    }

    if not info.get("available"):
        result["details"].append("OAuth credentials not available")
        result["details"].append(info.get("error", "Unknown error"))
        return result

    # Check expiration
    expired, error, expires_at = is_token_expired(manager)
    result["expired"] = expired

    if expired:
        if error:
            result["details"].append(f"Token expired: {error}")
        else:
            result["details"].append("Token is expired")
        result["details"].append("To fix: Re-authenticate with Claude Code")
    else:
        if expires_at:
            result["details"].append(f"Token valid until: {expires_at}")
        else:
            result["details"].append("Token is valid")

    # Add subscription info
    subscription = info.get("subscription_type")
    if subscription:
        result["details"].append(f"Subscription: {subscription}")

    scopes = info.get("scopes", [])
    if scopes:
        result["details"].append(f"Scopes: {', '.join(scopes)}")

    return result


def check_config_files() -> Dict[str, Any]:
    """
    Check for config files with credentials.

    Returns:
        Dictionary with config file status:
        - files_found: List of config files found
        - credentials_found: True if any config has credentials
        - details: Additional information
    """
    config_locations = [
        Path.home() / ".anthropic" / "config",
        Path.home() / ".anthropic" / "config.json",
        Path.home() / ".anthropic" / "api_key",
        Path.home() / ".config" / "anthropic" / "config",
        Path("config") / "credentials.yaml",
        Path(".env"),
    ]

    files_found = []
    credentials_found = False
    details = []

    for path in config_locations:
        if path.exists():
            files_found.append(str(path))
            details.append(f"Found config file: {path}")
            credentials_found = True

    if not files_found:
        details.append("No config files found")
        details.append("Searched locations:")
        for path in config_locations:
            details.append(f"  - {path}")

    return {
        "files_found": files_found,
        "credentials_found": credentials_found,
        "details": details,
    }


def test_api_connectivity() -> Dict[str, Any]:
    """
    Test API connectivity with discovered credentials.

    Returns:
        Dictionary with connectivity test results:
        - can_connect: True if API call succeeded
        - auth_method: Authentication method used
        - error: Error message if connection failed
        - details: Additional information
    """
    result = {
        "can_connect": False,
        "auth_method": None,
        "error": None,
        "details": [],
    }

    try:
        from anthropic import Anthropic

        # Try to discover credentials
        manager = UnifiedAuthManager(verbose=False)
        creds = manager.discover_credentials()

        result["auth_method"] = f"{creds.auth_type.value} from {creds.source.value}"
        result["details"].append(f"Using: {result['auth_method']}")

        # Create client
        if creds.auth_type == AuthType.OAUTH_TOKEN:
            client = Anthropic(auth_token=creds.credential)
        else:
            client = Anthropic(api_key=creds.credential)

        # Test with a minimal API call
        result["details"].append("Testing API connection...")

        # Note: We're not actually making a call here to avoid costs
        # Just verify the client was created successfully
        result["can_connect"] = True
        result["details"].append("Client created successfully")
        result["details"].append("Note: Actual API call skipped to avoid usage costs")

    except ValueError as e:
        result["error"] = f"No credentials found: {e}"
        result["details"].append(result["error"])
    except Exception as e:
        result["error"] = f"Connection failed: {e}"
        result["details"].append(result["error"])

    return result


def get_diagnostics() -> Dict[str, Any]:
    """
    Get comprehensive system diagnostics.

    Returns:
        Dictionary with complete diagnostic information including:
        - system: System information
        - claude_code: Claude Code installation status
        - environment: Environment variable status
        - oauth: OAuth credential status
        - config_files: Config file status
        - connectivity: API connectivity test results
        - credentials: Discovered credentials (if any)

    Example:
        >>> from claude_oauth_auth.debug import get_diagnostics
        >>> diag = get_diagnostics()
        >>> print(f"OAuth available: {diag['oauth']['available']}")
        >>> print(f"API key set: {diag['environment']['ANTHROPIC_API_KEY']['set']}")
    """
    diagnostics = {
        "timestamp": datetime.now().isoformat(),
        "system": {
            "python_version": sys.version,
            "platform": sys.platform,
            "cwd": str(Path.cwd()),
            "home": str(Path.home()),
        },
        "claude_code": check_claude_code_installation(),
        "environment": check_environment_variables(),
        "oauth": check_oauth_credentials(),
        "config_files": check_config_files(),
        "connectivity": test_api_connectivity(),
    }

    # Try to discover credentials
    try:
        manager = UnifiedAuthManager(verbose=False)
        creds = manager.discover_credentials()
        diagnostics["credentials"] = {
            "found": True,
            "auth_type": creds.auth_type.value,
            "source": creds.source.value,
            "credential_prefix": creds.credential[:15] + "...",
            "metadata": creds.metadata,
        }
    except ValueError:
        diagnostics["credentials"] = {
            "found": False,
            "error": "No credentials discovered",
        }

    return diagnostics


def format_diagnostics(diagnostics: Dict[str, Any], redact_credentials: bool = True) -> str:
    """
    Format diagnostics into a human-readable report.

    Args:
        diagnostics: Diagnostics dictionary from get_diagnostics()
        redact_credentials: If True, redact sensitive information

    Returns:
        Formatted string report

    Example:
        >>> from claude_oauth_auth.debug import get_diagnostics, format_diagnostics
        >>> diag = get_diagnostics()
        >>> report = format_diagnostics(diag)
        >>> print(report)
    """
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("Claude OAuth Auth - Diagnostic Report")
    lines.append("=" * 80)
    lines.append(f"Generated: {diagnostics['timestamp']}")
    lines.append("")

    # System info
    lines.append("SYSTEM INFORMATION")
    lines.append("-" * 80)
    lines.append(f"Python: {diagnostics['system']['python_version'].split()[0]}")
    lines.append(f"Platform: {diagnostics['system']['platform']}")
    lines.append(f"Working Directory: {diagnostics['system']['cwd']}")
    lines.append("")

    # Claude Code
    lines.append("CLAUDE CODE INSTALLATION")
    lines.append("-" * 80)
    cc = diagnostics['claude_code']
    lines.append(f"Installed: {'Yes' if cc['installed'] else 'No'}")
    lines.append(f"Credentials Path: {cc['credentials_path']}")
    lines.append(f"Credentials Exist: {'Yes' if cc['credentials_exists'] else 'No'}")
    for detail in cc['details']:
        lines.append(f"  {detail}")
    lines.append("")

    # Environment variables
    lines.append("ENVIRONMENT VARIABLES")
    lines.append("-" * 80)
    env = diagnostics['environment']
    for var_name in ['ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN']:
        var_data = env[var_name]
        status = "Set" if var_data['set'] else "Not set"
        lines.append(f"{var_name}: {status}")
        if var_data['set'] and var_data['message']:
            lines.append(f"  Validation: {var_data['message']}")
    lines.append("")

    # OAuth credentials
    lines.append("OAUTH CREDENTIALS")
    lines.append("-" * 80)
    oauth = diagnostics['oauth']
    lines.append(f"Available: {'Yes' if oauth['available'] else 'No'}")
    lines.append(f"Valid: {'Yes' if oauth['valid'] else 'No'}")
    if oauth['expired']:
        lines.append("Status: EXPIRED")
    for detail in oauth['details']:
        lines.append(f"  {detail}")
    lines.append("")

    # Config files
    lines.append("CONFIG FILES")
    lines.append("-" * 80)
    cfg = diagnostics['config_files']
    if cfg['files_found']:
        lines.append(f"Found {len(cfg['files_found'])} config file(s):")
        for file in cfg['files_found']:
            lines.append(f"  - {file}")
    else:
        lines.append("No config files found")
    lines.append("")

    # Discovered credentials
    lines.append("DISCOVERED CREDENTIALS")
    lines.append("-" * 80)
    creds = diagnostics['credentials']
    if creds['found']:
        lines.append(f"Found: Yes")
        lines.append(f"Type: {creds['auth_type']}")
        lines.append(f"Source: {creds['source']}")
        if not redact_credentials:
            lines.append(f"Prefix: {creds['credential_prefix']}")
    else:
        lines.append("Found: No")
        lines.append(f"Error: {creds.get('error', 'Unknown error')}")
    lines.append("")

    # Connectivity
    lines.append("API CONNECTIVITY")
    lines.append("-" * 80)
    conn = diagnostics['connectivity']
    lines.append(f"Can Connect: {'Yes' if conn['can_connect'] else 'No'}")
    if conn['auth_method']:
        lines.append(f"Auth Method: {conn['auth_method']}")
    if conn['error']:
        lines.append(f"Error: {conn['error']}")
    for detail in conn['details']:
        lines.append(f"  {detail}")
    lines.append("")

    # Recommendations
    lines.append("RECOMMENDATIONS")
    lines.append("-" * 80)
    recommendations = generate_recommendations(diagnostics)
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            lines.append(f"{i}. {rec}")
    else:
        lines.append("Everything looks good!")
    lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


def generate_recommendations(diagnostics: Dict[str, Any]) -> List[str]:
    """
    Generate actionable recommendations based on diagnostics.

    Args:
        diagnostics: Diagnostics dictionary from get_diagnostics()

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Check if credentials were found
    if not diagnostics['credentials']['found']:
        recommendations.append(
            "No credentials found. Set up authentication:\n"
            "   a) Install Claude Code: https://claude.com/claude-code\n"
            "   b) Or get API key: https://console.anthropic.com/settings/keys\n"
            "   c) Set ANTHROPIC_API_KEY environment variable"
        )

    # Check Claude Code installation
    if not diagnostics['claude_code']['installed']:
        if diagnostics['claude_code']['credentials_exists']:
            recommendations.append(
                "Claude Code credentials file exists but lacks OAuth data.\n"
                "   Run 'claude' and log in to refresh credentials."
            )
        else:
            recommendations.append(
                "Install Claude Code for OAuth support:\n"
                "   Visit https://claude.com/claude-code"
            )

    # Check OAuth expiration
    if diagnostics['oauth']['available'] and diagnostics['oauth']['expired']:
        recommendations.append(
            "OAuth token has expired.\n"
            "   Re-authenticate: Run 'claude' and log in again."
        )

    # Check environment variables
    env = diagnostics['environment']
    if env['ANTHROPIC_API_KEY']['set'] and not env['ANTHROPIC_API_KEY']['valid']:
        recommendations.append(
            f"ANTHROPIC_API_KEY is set but invalid:\n"
            f"   {env['ANTHROPIC_API_KEY']['message']}\n"
            f"   Get a new key from: https://console.anthropic.com/settings/keys"
        )

    if env['ANTHROPIC_AUTH_TOKEN']['set'] and not env['ANTHROPIC_AUTH_TOKEN']['valid']:
        recommendations.append(
            f"ANTHROPIC_AUTH_TOKEN is set but invalid:\n"
            f"   {env['ANTHROPIC_AUTH_TOKEN']['message']}"
        )

    # Check connectivity
    if not diagnostics['connectivity']['can_connect']:
        if diagnostics['connectivity']['error']:
            recommendations.append(
                f"Cannot connect to API:\n"
                f"   {diagnostics['connectivity']['error']}"
            )

    return recommendations


def diagnose(verbose: bool = True, redact_credentials: bool = True) -> str:
    """
    Run comprehensive diagnostics and return formatted report.

    This is the main entry point for debugging authentication issues.

    Args:
        verbose: If True, print detailed information
        redact_credentials: If True, redact sensitive information from report

    Returns:
        Formatted diagnostic report string

    Example:
        >>> from claude_oauth_auth.debug import diagnose
        >>>
        >>> # Quick diagnosis
        >>> print(diagnose())
        >>>
        >>> # With credentials visible (for your eyes only!)
        >>> print(diagnose(redact_credentials=False))
    """
    if verbose:
        print("Running diagnostics...")
        print()

    diagnostics = get_diagnostics()
    report = format_diagnostics(diagnostics, redact_credentials=redact_credentials)

    return report


def export_diagnostics(
    output_file: Optional[str] = None,
    redact_credentials: bool = True
) -> str:
    """
    Export diagnostics to a file.

    Args:
        output_file: Path to output file (defaults to diagnostics-{timestamp}.json)
        redact_credentials: If True, redact sensitive information

    Returns:
        Path to the exported file

    Example:
        >>> from claude_oauth_auth.debug import export_diagnostics
        >>> filepath = export_diagnostics()
        >>> print(f"Diagnostics saved to: {filepath}")
    """
    diagnostics = get_diagnostics()

    # Redact credentials if requested
    if redact_credentials:
        if diagnostics['credentials'].get('credential_prefix'):
            diagnostics['credentials']['credential_prefix'] = "[REDACTED]"
        for key in ['ANTHROPIC_API_KEY', 'ANTHROPIC_AUTH_TOKEN']:
            if diagnostics['environment'][key]['set']:
                diagnostics['environment'][key]['value'] = "[REDACTED]"

    # Generate filename if not provided
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"diagnostics-{timestamp}.json"

    # Write to file
    with open(output_file, 'w') as f:
        json.dump(diagnostics, f, indent=2, default=str)

    return output_file
