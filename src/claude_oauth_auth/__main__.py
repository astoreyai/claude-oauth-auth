"""
Main entry point for claude-oauth-auth CLI.

This allows running the CLI via:
    python -m claude_oauth_auth [command]
"""

import sys

from .cli import main


if __name__ == "__main__":
    sys.exit(main())
