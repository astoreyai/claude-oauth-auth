"""
Command-line interface for Claude OAuth authentication.

This module provides a CLI for checking authentication status, testing connections,
and running diagnostics.

Usage:
    # Show authentication status
    python -m claude_oauth_auth status

    # Test API connection
    python -m claude_oauth_auth test

    # Run full diagnostics
    python -m claude_oauth_auth diagnose

    # Show configuration
    python -m claude_oauth_auth config

    # Export diagnostics to file
    python -m claude_oauth_auth export --output diagnostics.json

Example:
    $ python -m claude_oauth_auth status
    Authentication Status
    =====================
    Status: Valid
    Type: oauth_token
    Source: claude_code_oauth_credentials
    ...
"""

import argparse
import sys
from typing import List, Optional

from .auth_manager import get_auth_status
from .debug import diagnose, export_diagnostics, get_diagnostics
from .oauth_manager import get_oauth_info, is_oauth_available
from .validate import validate_credential


def cmd_status(args: argparse.Namespace) -> int:
    """
    Show authentication status.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("Authentication Status")
    print("=" * 80)
    print()

    try:
        status = get_auth_status()

        print(f"Status: {'✓ Valid' if status['is_valid'] else '✗ No credentials found'}")

        if status['is_valid']:
            print(f"Type: {status['auth_type']}")
            print(f"Source: {status['source']}")
            print()

            # Show OAuth info if using OAuth
            if status['oauth_info']:
                oauth = status['oauth_info']
                print("OAuth Information:")
                print(f"  Valid: {'Yes' if oauth['is_valid'] else 'No'}")
                if oauth.get('subscription_type'):
                    print(f"  Subscription: {oauth['subscription_type']}")
                if oauth.get('expires_at'):
                    print(f"  Expires: {oauth['expires_at']}")
                if oauth.get('scopes'):
                    print(f"  Scopes: {', '.join(oauth['scopes'])}")
                print()

        print("Available Authentication Methods:")
        if status['available_methods']:
            for method in status['available_methods']:
                print(f"  ✓ {method}")
        else:
            print("  None found")
        print()

        if status['error']:
            print("Error:")
            print(status['error'])
            print()
            return 1

        return 0

    except Exception as e:
        print(f"Error checking authentication status: {e}")
        return 1


def cmd_test(args: argparse.Namespace) -> int:
    """
    Test API connection.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("Testing API Connection")
    print("=" * 80)
    print()

    try:
        from .auth_manager import UnifiedAuthManager
        from anthropic import Anthropic

        # Try to discover and use credentials
        manager = UnifiedAuthManager(verbose=args.verbose)
        creds = manager.discover_credentials()

        print(f"Using: {creds.auth_type.value} from {creds.source.value}")

        # Validate credential format
        is_valid, message, cred_type = validate_credential(creds.credential)
        print(f"Validation: {message}")

        if not is_valid:
            print()
            print("✗ Credential validation failed")
            return 1

        # Create client (but don't make API call to avoid costs)
        print()
        print("Creating Anthropic client...")

        if creds.auth_type.value == "oauth_token":
            client = Anthropic(auth_token=creds.credential)
        else:
            client = Anthropic(api_key=creds.credential)

        print("✓ Client created successfully")
        print()
        print("Note: Actual API call skipped to avoid usage costs.")
        print("To test a real API call, use the Python API directly:")
        print()
        print("  from claude_oauth_auth import ClaudeClient")
        print("  client = ClaudeClient()")
        print("  response = client.generate('Hello!')")
        print()

        return 0

    except ValueError as e:
        print(f"✗ No credentials found:")
        print(f"  {e}")
        print()
        print("Run 'python -m claude_oauth_auth diagnose' for more details.")
        return 1
    except Exception as e:
        print(f"✗ Error: {e}")
        return 1


def cmd_diagnose(args: argparse.Namespace) -> int:
    """
    Run full diagnostics.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        report = diagnose(
            verbose=args.verbose,
            redact_credentials=not args.show_credentials
        )
        print(report)
        return 0

    except Exception as e:
        print(f"Error running diagnostics: {e}")
        return 1


def cmd_config(args: argparse.Namespace) -> int:
    """
    Show configuration and credential sources.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("Configuration")
    print("=" * 80)
    print()

    from pathlib import Path
    import os

    # Show credential sources
    print("Credential Sources (in priority order):")
    print()

    sources = [
        ("1. Explicit parameters", "api_key= or auth_token= in constructor", None),
        ("2. ANTHROPIC_AUTH_TOKEN", "Environment variable", os.getenv("ANTHROPIC_AUTH_TOKEN")),
        ("3. ANTHROPIC_API_KEY", "Environment variable", os.getenv("ANTHROPIC_API_KEY")),
        ("4. Claude Code OAuth", "~/.claude/.credentials.json",
         str(Path.home() / ".claude" / ".credentials.json")),
        ("5. Config files", "~/.anthropic/config, etc.", None),
    ]

    for name, description, value in sources:
        print(f"{name}")
        print(f"  Description: {description}")
        if value is not None:
            if name.startswith("2.") or name.startswith("3."):
                # Environment variable
                print(f"  Set: {'Yes' if value else 'No'}")
            elif name.startswith("4."):
                # File path
                exists = Path(value).exists()
                print(f"  Path: {value}")
                print(f"  Exists: {'Yes' if exists else 'No'}")
        print()

    # Show OAuth status
    print("OAuth Status:")
    if is_oauth_available():
        oauth_info = get_oauth_info()
        print(f"  Available: Yes")
        print(f"  Valid: {'Yes' if oauth_info['is_valid'] else 'No'}")
        if oauth_info.get('subscription_type'):
            print(f"  Subscription: {oauth_info['subscription_type']}")
    else:
        print(f"  Available: No")
    print()

    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """
    Export diagnostics to file.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        filepath = export_diagnostics(
            output_file=args.output,
            redact_credentials=not args.show_credentials
        )
        print(f"Diagnostics exported to: {filepath}")
        return 0

    except Exception as e:
        print(f"Error exporting diagnostics: {e}")
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """
    Validate a credential.

    Args:
        args: Command arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print("Validating Credential")
    print("=" * 80)
    print()

    credential = args.credential

    is_valid, message, cred_type = validate_credential(credential)

    print(f"Credential Type: {cred_type or 'Unknown'}")
    print(f"Valid: {'Yes' if is_valid else 'No'}")
    print(f"Message: {message}")
    print()

    if not is_valid:
        from .validate import get_validation_hints
        hints = get_validation_hints(credential)
        print("Hints:")
        print(hints)
        print()
        return 1

    return 0


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="claude-oauth-auth",
        description="Claude OAuth authentication CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check authentication status
  python -m claude_oauth_auth status

  # Test API connection
  python -m claude_oauth_auth test

  # Run diagnostics
  python -m claude_oauth_auth diagnose

  # Show configuration
  python -m claude_oauth_auth config

  # Export diagnostics
  python -m claude_oauth_auth export --output report.json

  # Validate a credential
  python -m claude_oauth_auth validate sk-ant-api03-...

For more information, visit: https://github.com/astoreyai/claude-oauth-auth
        """
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Status command
    status_parser = subparsers.add_parser(
        "status",
        help="Show authentication status"
    )
    status_parser.set_defaults(func=cmd_status)

    # Test command
    test_parser = subparsers.add_parser(
        "test",
        help="Test API connection"
    )
    test_parser.set_defaults(func=cmd_test)

    # Diagnose command
    diagnose_parser = subparsers.add_parser(
        "diagnose",
        help="Run full diagnostics"
    )
    diagnose_parser.add_argument(
        "--show-credentials",
        action="store_true",
        help="Show credential values (WARNING: sensitive information)"
    )
    diagnose_parser.set_defaults(func=cmd_diagnose)

    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Show configuration"
    )
    config_parser.set_defaults(func=cmd_config)

    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export diagnostics to file"
    )
    export_parser.add_argument(
        "-o", "--output",
        help="Output file path (default: diagnostics-{timestamp}.json)"
    )
    export_parser.add_argument(
        "--show-credentials",
        action="store_true",
        help="Include credential values (WARNING: sensitive information)"
    )
    export_parser.set_defaults(func=cmd_export)

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate a credential"
    )
    validate_parser.add_argument(
        "credential",
        help="Credential to validate (API key or OAuth token)"
    )
    validate_parser.set_defaults(func=cmd_validate)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return 0

    # Run the command
    try:
        return args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
