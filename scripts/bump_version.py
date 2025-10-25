#!/usr/bin/env python3
"""
Version Bumping Script for claude-oauth-auth

This script automates the version bumping process:
1. Updates version in pyproject.toml
2. Updates version in __init__.py
3. Updates CHANGELOG.md with new version section
4. Optionally creates git commit and tag

Usage:
    ./scripts/bump_version.py patch    # 0.1.0 -> 0.1.1
    ./scripts/bump_version.py minor    # 0.1.0 -> 0.2.0
    ./scripts/bump_version.py major    # 0.1.0 -> 1.0.0
    ./scripts/bump_version.py --version 1.0.0  # Specific version

Options:
    --no-commit         Skip git commit and tag
    --no-changelog      Skip CHANGELOG.md update
    --dry-run          Show what would be done without making changes
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple


class VersionBumper:
    """Handles version bumping for the project."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.pyproject_path = project_root / "pyproject.toml"
        self.init_path = project_root / "src" / "claude_oauth_auth" / "__init__.py"
        self.changelog_path = project_root / "CHANGELOG.md"

    def get_current_version(self) -> str:
        """Extract current version from pyproject.toml."""
        content = self.pyproject_path.read_text()
        match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
        if not match:
            raise ValueError("Could not find version in pyproject.toml")
        return match.group(1)

    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """Parse version string into (major, minor, patch)."""
        match = re.match(r"^(\d+)\.(\d+)\.(\d+)$", version)
        if not match:
            raise ValueError(f"Invalid version format: {version}")
        return tuple(map(int, match.groups()))

    def bump_version(self, current: str, bump_type: str) -> str:
        """Bump version based on type (major, minor, patch)."""
        major, minor, patch = self.parse_version(current)

        if bump_type == "major":
            return f"{major + 1}.0.0"
        elif bump_type == "minor":
            return f"{major}.{minor + 1}.0"
        elif bump_type == "patch":
            return f"{major}.{minor}.{patch + 1}"
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

    def update_pyproject(self, old_version: str, new_version: str, dry_run: bool = False) -> None:
        """Update version in pyproject.toml."""
        content = self.pyproject_path.read_text()
        old_pattern = f'version = "{old_version}"'
        new_pattern = f'version = "{new_version}"'

        if old_pattern not in content:
            raise ValueError(f"Could not find '{old_pattern}' in pyproject.toml")

        new_content = content.replace(old_pattern, new_pattern)

        if dry_run:
            print(f"[DRY RUN] Would update {self.pyproject_path}")
            print(f"  {old_pattern} -> {new_pattern}")
        else:
            self.pyproject_path.write_text(new_content)
            print(f"✅ Updated {self.pyproject_path}")

    def update_init(self, old_version: str, new_version: str, dry_run: bool = False) -> None:
        """Update version in __init__.py."""
        content = self.init_path.read_text()
        old_pattern = f'__version__ = "{old_version}"'
        new_pattern = f'__version__ = "{new_version}"'

        if old_pattern not in content:
            raise ValueError(f"Could not find '{old_pattern}' in {self.init_path}")

        new_content = content.replace(old_pattern, new_pattern)

        if dry_run:
            print(f"[DRY RUN] Would update {self.init_path}")
            print(f"  {old_pattern} -> {new_pattern}")
        else:
            self.init_path.write_text(new_content)
            print(f"✅ Updated {self.init_path}")

    def update_changelog(self, new_version: str, dry_run: bool = False) -> None:
        """Update CHANGELOG.md with new version section."""
        if not self.changelog_path.exists():
            print(f"⚠️  {self.changelog_path} not found, skipping")
            return

        content = self.changelog_path.read_text()
        today = datetime.now().strftime("%Y-%m-%d")

        # Find the [Unreleased] section
        unreleased_pattern = r"## \[Unreleased\].*?(?=\n## \[|$)"
        unreleased_match = re.search(unreleased_pattern, content, re.DOTALL)

        if not unreleased_match:
            print("⚠️  No [Unreleased] section found in CHANGELOG.md, skipping")
            return

        unreleased_section = unreleased_match.group(0)

        # Create new version section
        new_version_section = f"## [{new_version}] - {today}"

        # Replace [Unreleased] with new version and create new [Unreleased]
        new_unreleased = """## [Unreleased]

### Added
- Features to be added

### Changed
- Changes to be made

### Fixed
- Bugs to be fixed

"""
        # Replace the old [Unreleased] header with new version
        updated_section = unreleased_section.replace("## [Unreleased]", new_version_section)

        # Insert new [Unreleased] section at the top
        new_content = content.replace(unreleased_section, new_unreleased + "\n" + updated_section)

        # Update the comparison links at the bottom
        # Find existing link pattern
        link_pattern = r"\[Unreleased\]: (https://github\.com/[^/]+/[^/]+)/compare/v([^.]+\.[^.]+\.[^.]+)\.\.\.HEAD"
        link_match = re.search(link_pattern, new_content)

        if link_match:
            repo_url = link_match.group(1)
            last_version = link_match.group(2)

            # Create new links
            new_unreleased_link = f"[Unreleased]: {repo_url}/compare/v{new_version}...HEAD"
            new_version_link = f"[{new_version}]: {repo_url}/compare/v{last_version}...v{new_version}"

            # Replace old unreleased link and add new version link
            old_link = link_match.group(0)
            new_content = new_content.replace(
                old_link, new_unreleased_link + "\n" + new_version_link
            )

        if dry_run:
            print(f"[DRY RUN] Would update {self.changelog_path}")
            print(f"  Would add section: {new_version_section}")
        else:
            self.changelog_path.write_text(new_content)
            print(f"✅ Updated {self.changelog_path}")

    def create_git_commit_and_tag(
        self, version: str, dry_run: bool = False
    ) -> None:
        """Create git commit and tag for the version bump."""
        files_to_commit = [
            "pyproject.toml",
            "src/claude_oauth_auth/__init__.py",
            "CHANGELOG.md",
        ]

        commit_message = f"chore: release v{version}"
        tag_message = f"Release version {version}"

        if dry_run:
            print(f"[DRY RUN] Would create git commit and tag:")
            print(f"  git add {' '.join(files_to_commit)}")
            print(f'  git commit -m "{commit_message}"')
            print(f'  git tag -a v{version} -m "{tag_message}"')
            return

        try:
            # Add files
            subprocess.run(
                ["git", "add"] + files_to_commit,
                check=True,
                cwd=self.project_root,
            )

            # Commit
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                check=True,
                cwd=self.project_root,
            )

            # Tag
            subprocess.run(
                ["git", "tag", "-a", f"v{version}", "-m", tag_message],
                check=True,
                cwd=self.project_root,
            )

            print(f"✅ Created git commit and tag v{version}")
            print(f"\n📌 Next steps:")
            print(f"  1. Review changes: git show HEAD")
            print(f"  2. Push to remote: git push origin main v{version}")
            print(f"  3. Monitor workflow: https://github.com/astoreyai/claude-oauth-auth/actions")

        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
            print("   You may need to commit and tag manually")
            sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Bump version for claude-oauth-auth",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s patch              # 0.1.0 -> 0.1.1
  %(prog)s minor              # 0.1.0 -> 0.2.0
  %(prog)s major              # 0.1.0 -> 1.0.0
  %(prog)s --version 1.0.0    # Set specific version
  %(prog)s patch --dry-run    # See what would happen
        """,
    )

    parser.add_argument(
        "bump_type",
        nargs="?",
        choices=["major", "minor", "patch"],
        help="Type of version bump",
    )
    parser.add_argument(
        "--version",
        help="Set specific version instead of bumping",
    )
    parser.add_argument(
        "--no-commit",
        action="store_true",
        help="Skip git commit and tag",
    )
    parser.add_argument(
        "--no-changelog",
        action="store_true",
        help="Skip CHANGELOG.md update",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    # Validate arguments
    if not args.version and not args.bump_type:
        parser.error("Must specify either bump_type or --version")

    # Find project root (directory containing pyproject.toml)
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    if not (project_root / "pyproject.toml").exists():
        print("❌ Could not find pyproject.toml in project root")
        sys.exit(1)

    bumper = VersionBumper(project_root)

    try:
        # Get current version
        current_version = bumper.get_current_version()
        print(f"📦 Current version: {current_version}")

        # Determine new version
        if args.version:
            new_version = args.version
            # Validate version format
            bumper.parse_version(new_version)
        else:
            new_version = bumper.bump_version(current_version, args.bump_type)

        print(f"🎯 New version: {new_version}")

        if args.dry_run:
            print("\n🔍 DRY RUN MODE - No changes will be made\n")

        # Confirm if not dry run
        if not args.dry_run:
            response = input(f"\nProceed with version bump {current_version} → {new_version}? [y/N] ")
            if response.lower() != "y":
                print("❌ Cancelled")
                sys.exit(0)

        # Update files
        print("\n📝 Updating files...")
        bumper.update_pyproject(current_version, new_version, args.dry_run)
        bumper.update_init(current_version, new_version, args.dry_run)

        if not args.no_changelog:
            bumper.update_changelog(new_version, args.dry_run)

        # Create git commit and tag
        if not args.no_commit and not args.dry_run:
            print("\n🔧 Creating git commit and tag...")
            bumper.create_git_commit_and_tag(new_version, args.dry_run)

        print("\n✨ Version bump complete!")

        if args.dry_run:
            print("\n💡 Run without --dry-run to apply changes")
        elif args.no_commit:
            print("\n📌 Next steps:")
            print("  1. Review changes: git diff")
            print(f"  2. Commit: git commit -m 'chore: release v{new_version}'")
            print(f"  3. Tag: git tag v{new_version}")
            print(f"  4. Push: git push origin main v{new_version}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
