#!/usr/bin/env python3
"""
Standalone troubleshooting script for Claude OAuth authentication.

This script can be run independently to diagnose authentication issues
and generate a support report that's safe to share (redacts credentials).

Usage:
    # Run diagnostics
    python scripts/troubleshoot.py

    # Save report to file
    python scripts/troubleshoot.py --output report.txt

    # Include credentials (for your eyes only!)
    python scripts/troubleshoot.py --show-credentials

    # Export as JSON
    python scripts/troubleshoot.py --json --output report.json
"""

import argparse
import json
import sys
from pathlib import Path

# Add src to path to import from claude_oauth_auth
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from claude_oauth_auth.debug import diagnose, export_diagnostics, get_diagnostics
    from claude_oauth_auth.validate import validate_credential
except ImportError as e:
    print("Error: Could not import claude_oauth_auth module.")
    print(f"Details: {e}")
    print()
    print("Make sure you're running this from the project root:")
    print("  python scripts/troubleshoot.py")
    print()
    print("Or install the package first:")
    print("  pip install -e .")
    sys.exit(1)


def main():
    """Main entry point for troubleshooting script."""
    parser = argparse.ArgumentParser(
        description="Troubleshoot Claude OAuth authentication issues",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run diagnostics and print to console
  python scripts/troubleshoot.py

  # Save report to file
  python scripts/troubleshoot.py --output report.txt

  # Export as JSON
  python scripts/troubleshoot.py --json --output diagnostics.json

  # Include credentials (WARNING: sensitive!)
  python scripts/troubleshoot.py --show-credentials

This script generates a comprehensive diagnostic report including:
  - System information
  - Claude Code installation status
  - Environment variables
  - OAuth credentials
  - Config files
  - API connectivity test
  - Actionable recommendations

The report is safe to share by default (credentials are redacted).
        """
    )

    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: print to console)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Export as JSON instead of text report"
    )

    parser.add_argument(
        "--show-credentials",
        action="store_true",
        help="Include credential values (WARNING: sensitive information!)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    # Print header
    print()
    print("=" * 80)
    print("Claude OAuth Auth - Troubleshooting Script")
    print("=" * 80)
    print()

    if args.show_credentials:
        print("WARNING: Credentials will be included in output!")
        print("Do NOT share this output publicly.")
        print()

    # Run diagnostics
    try:
        if args.json:
            # Export as JSON
            if args.output:
                filepath = export_diagnostics(
                    output_file=args.output,
                    redact_credentials=not args.show_credentials
                )
                print(f"✓ Diagnostics exported to: {filepath}")
            else:
                diagnostics = get_diagnostics()
                if args.show_credentials:
                    print(json.dumps(diagnostics, indent=2, default=str))
                else:
                    # Redact credentials
                    if diagnostics['credentials'].get('credential_prefix'):
                        diagnostics['credentials']['credential_prefix'] = "[REDACTED]"
                    print(json.dumps(diagnostics, indent=2, default=str))
        else:
            # Generate text report
            report = diagnose(
                verbose=args.verbose,
                redact_credentials=not args.show_credentials
            )

            if args.output:
                # Write to file
                with open(args.output, 'w') as f:
                    f.write(report)
                print(f"✓ Report saved to: {args.output}")
                print()
                print("You can share this report when asking for support.")
                if not args.show_credentials:
                    print("(Credentials are redacted for safety)")
            else:
                # Print to console
                print(report)

        print()
        print("=" * 80)
        print()
        print("Need help?")
        print("  - Documentation: https://github.com/astoreyai/claude-oauth-auth")
        print("  - Issues: https://github.com/astoreyai/claude-oauth-auth/issues")
        print()

        return 0

    except Exception as e:
        print()
        print(f"✗ Error running diagnostics: {e}")
        print()
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
