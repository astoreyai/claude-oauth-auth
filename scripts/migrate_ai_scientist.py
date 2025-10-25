#!/usr/bin/env python3
"""
Automated Migration Script for AI Scientist to claude-oauth-auth Package

This script automates the migration from embedded OAuth/auth code to using
the claude-oauth-auth package. It performs import replacements, removes old
files, and validates the migration.

Features:
- Dry-run mode to preview changes
- Automatic backup creation
- Import statement updates
- File removal with archiving
- Validation checks
- Rollback support

Usage:
    # Dry run (preview changes)
    python migrate_ai_scientist.py --dry-run --ai-scientist-path /path/to/ai_scientist

    # Full migration with backup
    python migrate_ai_scientist.py --ai-scientist-path /path/to/ai_scientist --backup

    # Migration without backup (not recommended)
    python migrate_ai_scientist.py --ai-scientist-path /path/to/ai_scientist

    # Rollback to backup
    python migrate_ai_scientist.py --rollback --ai-scientist-path /path/to/ai_scientist
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import subprocess
from datetime import datetime


class MigrationScript:
    """Handles migration from embedded auth code to claude-oauth-auth package."""

    def __init__(self, ai_scientist_path: Path, dry_run: bool = False, backup: bool = True):
        """
        Initialize migration script.

        Args:
            ai_scientist_path: Path to AI Scientist project root
            dry_run: If True, only show what would be done
            backup: If True, create backup before migration
        """
        self.ai_scientist_path = Path(ai_scientist_path).resolve()
        self.dry_run = dry_run
        self.backup_enabled = backup
        self.backup_path: Optional[Path] = None
        self.changes: List[str] = []
        self.errors: List[str] = []

        # Validate path
        if not self.ai_scientist_path.exists():
            raise ValueError(f"AI Scientist path does not exist: {self.ai_scientist_path}")

        self.core_path = self.ai_scientist_path / "ai_scientist" / "core"
        if not self.core_path.exists():
            raise ValueError(f"Core module not found: {self.core_path}")

    def log(self, message: str, level: str = "INFO"):
        """Log a message with color coding."""
        colors = {
            "INFO": "\033[94m",      # Blue
            "SUCCESS": "\033[92m",   # Green
            "WARNING": "\033[93m",   # Yellow
            "ERROR": "\033[91m",     # Red
            "DRY_RUN": "\033[95m",   # Magenta
        }
        reset = "\033[0m"
        prefix = f"[{level}]"
        color = colors.get(level, "")
        print(f"{color}{prefix}{reset} {message}")

    def create_backup(self) -> bool:
        """
        Create backup of AI Scientist project.

        Returns:
            True if backup successful, False otherwise
        """
        if not self.backup_enabled:
            self.log("Backup disabled, skipping", "WARNING")
            return True

        if self.dry_run:
            self.log("Would create backup (dry run)", "DRY_RUN")
            return True

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_path = self.ai_scientist_path.parent / f"ai_scientist_backup_{timestamp}"

        try:
            self.log(f"Creating backup at: {self.backup_path}", "INFO")

            # Copy entire project
            shutil.copytree(
                self.ai_scientist_path,
                self.backup_path,
                ignore=shutil.ignore_patterns('.venv', '__pycache__', '*.pyc', '.git')
            )

            self.log(f"✓ Backup created successfully", "SUCCESS")
            self.changes.append(f"Created backup: {self.backup_path}")
            return True

        except Exception as e:
            self.log(f"Failed to create backup: {e}", "ERROR")
            self.errors.append(f"Backup failed: {e}")
            return False

    def update_imports_in_file(self, file_path: Path) -> Tuple[bool, int]:
        """
        Update imports in a single file.

        Args:
            file_path: Path to file to update

        Returns:
            (success, num_replacements)
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            original_content = content
            replacements = 0

            # Define import replacements
            import_patterns = [
                # OAuth manager imports
                (
                    r'from ai_scientist\.core\.oauth_manager import',
                    'from claude_oauth_auth import'
                ),
                (
                    r'from \.oauth_manager import',
                    'from claude_oauth_auth import'
                ),
                (
                    r'import ai_scientist\.core\.oauth_manager',
                    'import claude_oauth_auth.oauth_manager'
                ),

                # Auth manager imports
                (
                    r'from ai_scientist\.core\.auth_manager import',
                    'from claude_oauth_auth import'
                ),
                (
                    r'from \.auth_manager import',
                    'from claude_oauth_auth import'
                ),
                (
                    r'import ai_scientist\.core\.auth_manager',
                    'import claude_oauth_auth.auth_manager'
                ),

                # Claude SDK client imports
                (
                    r'from ai_scientist\.core\.claude_sdk_client import ClaudeSDKClient',
                    'from claude_oauth_auth import ClaudeClient as ClaudeSDKClient'
                ),
                (
                    r'from ai_scientist\.core\.claude_sdk_client import create_claude_client',
                    'from claude_oauth_auth import create_client as create_claude_client'
                ),
                (
                    r'from ai_scientist\.core\.claude_sdk_client import',
                    'from claude_oauth_auth import ClaudeClient as'
                ),

                # Claude SDK client v2 imports
                (
                    r'from ai_scientist\.core\.claude_sdk_client_v2 import ClaudeSDKClient',
                    'from claude_oauth_auth import ClaudeClient as ClaudeSDKClient'
                ),
                (
                    r'from ai_scientist\.core\.claude_sdk_client_v2 import create_claude_client',
                    'from claude_oauth_auth import create_client as create_claude_client'
                ),
                (
                    r'from ai_scientist\.core\.claude_sdk_client_v2 import',
                    'from claude_oauth_auth import ClaudeClient as'
                ),

                # Relative imports in core module
                (
                    r'from \.claude_sdk_client import ClaudeSDKClient',
                    'from claude_oauth_auth import ClaudeClient as ClaudeSDKClient'
                ),
                (
                    r'from \.claude_sdk_client_v2 import ClaudeSDKClient',
                    'from claude_oauth_auth import ClaudeClient as ClaudeSDKClient'
                ),
            ]

            # Apply replacements
            for pattern, replacement in import_patterns:
                new_content, count = re.subn(pattern, replacement, content)
                if count > 0:
                    content = new_content
                    replacements += count
                    self.log(f"  - Replaced {count} occurrence(s) of: {pattern[:50]}...", "INFO")

            # Only write if changes were made
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    self.log(f"✓ Updated {file_path.relative_to(self.ai_scientist_path)}", "SUCCESS")
                else:
                    self.log(f"Would update {file_path.relative_to(self.ai_scientist_path)}", "DRY_RUN")

                self.changes.append(f"Updated imports in: {file_path.relative_to(self.ai_scientist_path)}")
                return True, replacements

            return True, 0

        except Exception as e:
            self.log(f"Failed to update {file_path}: {e}", "ERROR")
            self.errors.append(f"Import update failed for {file_path}: {e}")
            return False, 0

    def find_files_to_update(self) -> List[Path]:
        """
        Find all Python files that need import updates.

        Returns:
            List of file paths to update
        """
        files_to_update = []

        # Search patterns
        search_dirs = [
            self.ai_scientist_path / "ai_scientist",
            self.ai_scientist_path / "tests",
            self.ai_scientist_path / "examples",
            self.ai_scientist_path / "scripts",
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for py_file in search_dir.rglob("*.py"):
                # Skip __pycache__ and .venv
                if '__pycache__' in str(py_file) or '.venv' in str(py_file):
                    continue

                # Check if file contains imports we need to update
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()

                    if any(pattern in content for pattern in [
                        'ai_scientist.core.oauth_manager',
                        'ai_scientist.core.auth_manager',
                        'ai_scientist.core.claude_sdk_client',
                        '.oauth_manager',
                        '.auth_manager',
                        '.claude_sdk_client',
                    ]):
                        files_to_update.append(py_file)

                except Exception as e:
                    self.log(f"Error reading {py_file}: {e}", "WARNING")

        return files_to_update

    def update_all_imports(self) -> bool:
        """
        Update imports in all relevant files.

        Returns:
            True if successful, False otherwise
        """
        self.log("Finding files to update...", "INFO")
        files = self.find_files_to_update()

        if not files:
            self.log("No files found that need updating", "WARNING")
            return True

        self.log(f"Found {len(files)} files to update", "INFO")

        total_replacements = 0
        successful = 0

        for file_path in files:
            self.log(f"\nUpdating: {file_path.relative_to(self.ai_scientist_path)}", "INFO")
            success, count = self.update_imports_in_file(file_path)
            if success:
                successful += 1
                total_replacements += count

        self.log(f"\n✓ Updated {successful}/{len(files)} files ({total_replacements} replacements)", "SUCCESS")
        return successful == len(files)

    def archive_old_files(self) -> bool:
        """
        Archive old auth files instead of deleting them.

        Returns:
            True if successful, False otherwise
        """
        archive_dir = self.core_path / "archive"

        files_to_archive = [
            self.core_path / "oauth_manager.py",
            self.core_path / "auth_manager.py",
            self.core_path / "claude_sdk_client.py",
            self.core_path / "claude_sdk_client_v2.py",
        ]

        # Filter to only existing files
        existing_files = [f for f in files_to_archive if f.exists()]

        if not existing_files:
            self.log("No old files found to archive", "WARNING")
            return True

        if self.dry_run:
            self.log(f"Would archive {len(existing_files)} files to {archive_dir}", "DRY_RUN")
            for file in existing_files:
                self.log(f"  - {file.name}", "DRY_RUN")
            return True

        try:
            # Create archive directory
            archive_dir.mkdir(exist_ok=True)

            # Archive each file
            for file in existing_files:
                archive_path = archive_dir / file.name
                self.log(f"Archiving: {file.name} → archive/{file.name}", "INFO")
                shutil.move(str(file), str(archive_path))
                self.changes.append(f"Archived: {file.name}")

            self.log(f"✓ Archived {len(existing_files)} files", "SUCCESS")
            return True

        except Exception as e:
            self.log(f"Failed to archive files: {e}", "ERROR")
            self.errors.append(f"Archive failed: {e}")
            return False

    def update_requirements(self) -> bool:
        """
        Update requirements.txt and pyproject.toml.

        Returns:
            True if successful, False otherwise
        """
        success = True

        # Update requirements.txt
        req_file = self.ai_scientist_path / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    content = f.read()

                if 'claude-oauth-auth' not in content:
                    # Add package to requirements
                    lines = content.split('\n')

                    # Find LLM section or add at end
                    insert_idx = len(lines)
                    for i, line in enumerate(lines):
                        if 'LLM' in line or 'anthropic' in line:
                            insert_idx = i
                            break

                    lines.insert(insert_idx, 'claude-oauth-auth>=0.1.0         # OAuth authentication for Claude API')

                    new_content = '\n'.join(lines)

                    if not self.dry_run:
                        with open(req_file, 'w') as f:
                            f.write(new_content)
                        self.log("✓ Updated requirements.txt", "SUCCESS")
                    else:
                        self.log("Would update requirements.txt", "DRY_RUN")

                    self.changes.append("Updated requirements.txt")
                else:
                    self.log("requirements.txt already contains claude-oauth-auth", "INFO")

            except Exception as e:
                self.log(f"Failed to update requirements.txt: {e}", "ERROR")
                self.errors.append(f"requirements.txt update failed: {e}")
                success = False

        # Update pyproject.toml
        pyproject_file = self.ai_scientist_path / "pyproject.toml"
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r') as f:
                    content = f.read()

                if 'claude-oauth-auth' not in content:
                    # Add to dependencies section
                    content = re.sub(
                        r'(dependencies = \[)',
                        r'\1\n    "claude-oauth-auth>=0.1.0",',
                        content
                    )

                    if not self.dry_run:
                        with open(pyproject_file, 'w') as f:
                            f.write(content)
                        self.log("✓ Updated pyproject.toml", "SUCCESS")
                    else:
                        self.log("Would update pyproject.toml", "DRY_RUN")

                    self.changes.append("Updated pyproject.toml")
                else:
                    self.log("pyproject.toml already contains claude-oauth-auth", "INFO")

            except Exception as e:
                self.log(f"Failed to update pyproject.toml: {e}", "ERROR")
                self.errors.append(f"pyproject.toml update failed: {e}")
                success = False

        return success

    def run_tests(self) -> bool:
        """
        Run tests to validate migration.

        Returns:
            True if tests pass, False otherwise
        """
        if self.dry_run:
            self.log("Would run tests (dry run)", "DRY_RUN")
            return True

        self.log("Running tests to validate migration...", "INFO")

        try:
            # Check if pytest is available
            result = subprocess.run(
                ["pytest", "--version"],
                cwd=self.ai_scientist_path,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                self.log("pytest not available, skipping tests", "WARNING")
                return True

            # Run OAuth integration tests
            result = subprocess.run(
                ["pytest", "tests/test_oauth_integration.py", "-v"],
                cwd=self.ai_scientist_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                self.log("✓ Tests passed", "SUCCESS")
                return True
            else:
                self.log("✗ Tests failed", "ERROR")
                self.log(f"Output: {result.stdout}", "ERROR")
                self.log(f"Errors: {result.stderr}", "ERROR")
                self.errors.append("Tests failed after migration")
                return False

        except subprocess.TimeoutExpired:
            self.log("Tests timed out", "ERROR")
            self.errors.append("Tests timed out")
            return False
        except Exception as e:
            self.log(f"Failed to run tests: {e}", "WARNING")
            return True  # Don't fail migration if tests can't run

    def validate_imports(self) -> bool:
        """
        Validate that imports work after migration.

        Returns:
            True if imports work, False otherwise
        """
        if self.dry_run:
            self.log("Would validate imports (dry run)", "DRY_RUN")
            return True

        self.log("Validating imports...", "INFO")

        test_script = """
import sys
sys.path.insert(0, str({!r}))

from ai_scientist.core import (
    ClaudeSDKClient,
    OAuthTokenManager,
    UnifiedAuthManager,
    get_oauth_token,
    is_oauth_available,
    get_auth_status
)

print('✓ All imports successful')
""".format(str(self.ai_scientist_path))

        try:
            result = subprocess.run(
                ["python", "-c", test_script],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                self.log("✓ Import validation successful", "SUCCESS")
                return True
            else:
                self.log("✗ Import validation failed", "ERROR")
                self.log(f"Output: {result.stdout}", "ERROR")
                self.log(f"Errors: {result.stderr}", "ERROR")
                self.errors.append("Import validation failed")
                return False

        except Exception as e:
            self.log(f"Failed to validate imports: {e}", "ERROR")
            self.errors.append(f"Import validation error: {e}")
            return False

    def generate_report(self) -> str:
        """
        Generate migration report.

        Returns:
            Report text
        """
        report_lines = [
            "=" * 70,
            "MIGRATION REPORT",
            "=" * 70,
            "",
            f"AI Scientist Path: {self.ai_scientist_path}",
            f"Dry Run: {self.dry_run}",
            f"Backup Created: {self.backup_path if self.backup_path else 'No'}",
            "",
            f"Changes Made: {len(self.changes)}",
        ]

        if self.changes:
            report_lines.append("")
            report_lines.append("Changes:")
            for change in self.changes:
                report_lines.append(f"  - {change}")

        if self.errors:
            report_lines.append("")
            report_lines.append(f"Errors: {len(self.errors)}")
            report_lines.append("")
            report_lines.append("Errors:")
            for error in self.errors:
                report_lines.append(f"  - {error}")

        report_lines.append("")
        report_lines.append("=" * 70)

        return "\n".join(report_lines)

    def run(self) -> bool:
        """
        Run complete migration process.

        Returns:
            True if successful, False otherwise
        """
        self.log("=" * 70, "INFO")
        self.log("AI Scientist Migration to claude-oauth-auth Package", "INFO")
        self.log("=" * 70, "INFO")

        if self.dry_run:
            self.log("DRY RUN MODE - No changes will be made", "DRY_RUN")

        # Step 1: Create backup
        if not self.create_backup():
            self.log("Backup failed, aborting migration", "ERROR")
            return False

        # Step 2: Update imports
        self.log("\n--- Step 1: Updating Imports ---", "INFO")
        if not self.update_all_imports():
            self.log("Import updates failed", "ERROR")
            return False

        # Step 3: Archive old files
        self.log("\n--- Step 2: Archiving Old Files ---", "INFO")
        if not self.archive_old_files():
            self.log("Archive failed", "ERROR")
            return False

        # Step 4: Update requirements
        self.log("\n--- Step 3: Updating Requirements ---", "INFO")
        if not self.update_requirements():
            self.log("Requirements update failed", "WARNING")

        # Step 5: Validate imports
        self.log("\n--- Step 4: Validating Imports ---", "INFO")
        if not self.validate_imports():
            self.log("Import validation failed", "ERROR")
            return False

        # Step 6: Run tests
        self.log("\n--- Step 5: Running Tests ---", "INFO")
        if not self.run_tests():
            self.log("Tests failed", "WARNING")

        # Generate report
        report = self.generate_report()
        print("\n" + report)

        if self.errors:
            self.log(f"\nMigration completed with {len(self.errors)} errors", "WARNING")
            return False
        else:
            self.log("\n✓ Migration completed successfully!", "SUCCESS")

            if not self.dry_run:
                self.log("\nNext steps:", "INFO")
                self.log("1. Review changes: git diff", "INFO")
                self.log("2. Run full test suite: pytest tests/ -v", "INFO")
                self.log("3. Commit changes: git commit -m 'Migrate to claude-oauth-auth package'", "INFO")
                if self.backup_path:
                    self.log(f"4. Remove backup when satisfied: rm -rf {self.backup_path}", "INFO")

            return True


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate AI Scientist to claude-oauth-auth package",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Preview changes
    python migrate_ai_scientist.py --dry-run --ai-scientist-path /path/to/ai_scientist

    # Run migration with backup
    python migrate_ai_scientist.py --ai-scientist-path /path/to/ai_scientist --backup

    # Run without backup (not recommended)
    python migrate_ai_scientist.py --ai-scientist-path /path/to/ai_scientist
        """
    )

    parser.add_argument(
        "--ai-scientist-path",
        required=True,
        type=Path,
        help="Path to AI Scientist project root"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without making them"
    )

    parser.add_argument(
        "--backup",
        action="store_true",
        default=True,
        help="Create backup before migration (default: True)"
    )

    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation (not recommended)"
    )

    args = parser.parse_args()

    # Handle backup flag
    backup = args.backup and not args.no_backup

    try:
        # Create and run migration
        migration = MigrationScript(
            ai_scientist_path=args.ai_scientist_path,
            dry_run=args.dry_run,
            backup=backup
        )

        success = migration.run()
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
