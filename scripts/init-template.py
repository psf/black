#!/usr/bin/env python3
"""
Provenance Template Initialization Wizard

This script helps you customize the provenance-template for your own project.
It's idempotent - safe to run multiple times.

Usage:
    python scripts/init-template.py

What it does:
- Renames the package (demo_cli → your_package)
- Updates CLI command name (demo → your-command)
- Replaces placeholders (OWNER, repository name)
- Configures project metadata
- Optionally enables/disables distribution platforms
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def colored(text: str, color: str) -> str:
    """Add color to text."""
    return f"{color}{text}{Colors.END}"

def print_header(text: str) -> None:
    """Print a section header."""
    print("\n" + "=" * 70)
    print(colored(text, Colors.HEADER + Colors.BOLD))
    print("=" * 70 + "\n")

def print_success(text: str) -> None:
    """Print success message."""
    print(colored(f"✓ {text}", Colors.GREEN))

def print_warning(text: str) -> None:
    """Print warning message."""
    print(colored(f"⚠ {text}", Colors.YELLOW))

def print_error(text: str) -> None:
    """Print error message."""
    print(colored(f"✗ {text}", Colors.RED))

def print_info(text: str) -> None:
    """Print info message."""
    print(colored(f"ℹ {text}", Colors.CYAN))

# Repository root
REPO_ROOT = Path(__file__).parent.parent.resolve()

# Default/placeholder values to detect
DEFAULT_VALUES = {
    "package_name": "provenance-demo",
    "cli_command": "demo",
    "repo_owner": "OWNER",
    "repo_name": "provenance-template",
    "project_name": "Provenance Demo",
    "description": "Demo Secure CLI — reproducible & attestable release example",
}

def detect_current_config() -> Dict[str, str]:
    """Detect current configuration from pyproject.toml."""
    pyproject_path = REPO_ROOT / "pyproject.toml"

    if not pyproject_path.exists():
        print_error("pyproject.toml not found!")
        print_info(f"Expected location: {pyproject_path}")
        print_info("Make sure you're running this script from the repository root:")
        print(f"  cd {REPO_ROOT}")
        print("  python3 scripts/init-template.py")
        sys.exit(1)

    try:
        content = pyproject_path.read_text()
    except PermissionError:
        print_error(f"Permission denied reading {pyproject_path}")
        print_info("Check file permissions and try again")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to read pyproject.toml: {e}")
        sys.exit(1)

    config = {}

    # Extract package name
    if match := re.search(r'name\s*=\s*"([^"]+)"', content):
        config["package_name"] = match.group(1)

    # Extract description
    if match := re.search(r'description\s*=\s*"([^"]+)"', content):
        config["description"] = match.group(1)

    # Extract CLI command and package directory from scripts section
    # Format: cli-command = "package_dir.module:main"
    if match := re.search(r'\[project\.scripts\]\s*([a-z][a-z0-9-]*)\s*=\s*"([a-z_][a-z0-9_]*)', content):
        config["cli_command"] = match.group(1)
        config["package_dir"] = match.group(2)  # Actual directory name

    # Try to detect repo owner/name from URLs
    if match := re.search(r'github\.com/([^/]+)/([^/"]+)', content):
        config["repo_owner"] = match.group(1)
        config["repo_name"] = match.group(2)

    return config

def is_customized() -> Tuple[bool, List[str]]:
    """Check if template has been customized."""
    config = detect_current_config()
    unchanged = []

    for key, default_value in DEFAULT_VALUES.items():
        if key in config and config[key] == default_value:
            unchanged.append(key)

    return (len(unchanged) == 0, unchanged)

def prompt_with_default(prompt_text: str, default: str, required: bool = True) -> str:
    """Prompt user for input with a default value."""
    while True:
        user_input = input(f"{prompt_text} [{default}]: ").strip()

        if not user_input:
            if required and not default:
                print_warning("This field is required.")
                continue
            return default

        return user_input

def validate_package_name(name: str) -> bool:
    """Validate Python package name."""
    # Must be valid Python identifier
    if not re.match(r'^[a-z_][a-z0-9_]*$', name):
        print_error(f"Invalid package name: '{name}'")
        print_info("Package name requirements:")
        print("  • Must be lowercase")
        print("  • Start with letter or underscore")
        print("  • Contain only letters, numbers, and underscores")
        print("  • Examples: my_cli, secure_tool, cli_app")
        return False
    return True

def validate_cli_command(name: str) -> bool:
    """Validate CLI command name."""
    # Can contain hyphens, must be lowercase
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        print_error(f"Invalid CLI command: '{name}'")
        print_info("CLI command requirements:")
        print("  • Must be lowercase")
        print("  • Start with a letter")
        print("  • Contain only letters, numbers, and hyphens")
        print("  • Examples: my-cli, secure-tool, cli-app")
        return False
    return True

def get_project_config() -> Dict[str, str]:
    """Interactively gather project configuration."""
    print_header("PROJECT CONFIGURATION")

    current = detect_current_config()

    print_info("Current configuration:")
    for key, value in current.items():
        default_marker = " (default)" if DEFAULT_VALUES.get(key) == value else ""
        print(f"  {key}: {value}{default_marker}")

    print("\nEnter new values (press Enter to keep current):\n")

    config = {}

    # Package name
    while True:
        default_package = current.get("package_name", DEFAULT_VALUES["package_name"])
        user_input = input(f"Python package name [{default_package}]: ").strip()

        if not user_input:
            package_name = default_package
            config["package_name"] = package_name
            break
        elif validate_package_name(user_input):
            config["package_name"] = user_input
            break

    # CLI command
    while True:
        default_cli = current.get("cli_command", DEFAULT_VALUES["cli_command"])
        user_input = input(f"CLI command name [{default_cli}]: ").strip()

        if not user_input:
            cli_command = default_cli
            config["cli_command"] = cli_command
            break
        elif validate_cli_command(user_input):
            config["cli_command"] = user_input
            break

    # Repository owner
    config["repo_owner"] = prompt_with_default(
        "GitHub repository owner/organization",
        current.get("repo_owner", DEFAULT_VALUES["repo_owner"])
    )

    # Repository name
    config["repo_name"] = prompt_with_default(
        "GitHub repository name",
        current.get("repo_name", DEFAULT_VALUES["repo_name"])
    )

    # Project name
    config["project_name"] = prompt_with_default(
        "Project display name",
        config["cli_command"].replace("-", " ").title()
    )

    # Description
    config["description"] = prompt_with_default(
        "Project description",
        current.get("description", DEFAULT_VALUES["description"])
    )

    # Author (optional)
    try:
        git_user = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        git_user = ""

    config["author"] = prompt_with_default(
        "Author name (optional)",
        git_user or "",
        required=False
    )

    # Email (optional)
    try:
        git_email = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True,
            text=True,
            timeout=5
        ).stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        git_email = ""

    config["author_email"] = prompt_with_default(
        "Author email (optional)",
        git_email or "",
        required=False
    )

    return config

def confirm_changes(config: Dict[str, str]) -> bool:
    """Show summary and confirm changes."""
    print_header("CONFIGURATION SUMMARY")

    print("The following changes will be applied:\n")
    for key, value in config.items():
        if value:  # Only show non-empty values
            print(f"  {colored(key, Colors.BOLD)}: {value}")

    print("\nThis will update:")
    print("  • pyproject.toml")
    print("  • Source code directory structure")
    print("  • Documentation files")
    print("  • GitHub workflow files")
    print("  • Platform configuration files")

    print()
    response = input("Apply these changes? [y/N]: ").strip().lower()
    return response in ["y", "yes"]

def replace_in_file(file_path: Path, replacements: Dict[str, str]) -> bool:
    """Replace text in a file. Returns True if file was modified."""
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text()
    except PermissionError:
        print_warning(f"Permission denied reading {file_path.relative_to(REPO_ROOT)}")
        return False
    except UnicodeDecodeError:
        # Skip binary files
        return False
    except Exception as e:
        print_warning(f"Error reading {file_path.relative_to(REPO_ROOT)}: {e}")
        return False

    original = content

    for old, new in replacements.items():
        content = content.replace(old, new)

    if content != original:
        try:
            file_path.write_text(content)
            return True
        except PermissionError:
            print_error(f"Permission denied writing to {file_path.relative_to(REPO_ROOT)}")
            print_info("Check file permissions: chmod u+w " + str(file_path))
            return False
        except Exception as e:
            print_error(f"Error writing to {file_path.relative_to(REPO_ROOT)}: {e}")
            return False

    return False

def rename_package_directory(old_name: str, new_name: str) -> None:
    """Rename the package directory."""
    old_path = REPO_ROOT / "src" / old_name
    new_path = REPO_ROOT / "src" / new_name

    if not old_path.exists():
        print_warning(f"Source directory not found: {old_path.relative_to(REPO_ROOT)}")
        print_info("The package directory may have already been renamed or moved")
        return

    if old_path == new_path:
        print_info(f"Package directory name unchanged: {old_name}")
        return

    if new_path.exists():
        print_error(f"Target directory already exists: {new_path.relative_to(REPO_ROOT)}")
        print_info("Please manually resolve the conflict:")
        print(f"  • Remove or rename: {new_path}")
        print(f"  • Then run this wizard again")
        return

    try:
        old_path.rename(new_path)
        print_success(f"Renamed package directory: {old_name} → {new_name}")
    except PermissionError:
        print_error(f"Permission denied renaming directory")
        print_info(f"  From: {old_path.relative_to(REPO_ROOT)}")
        print_info(f"  To:   {new_path.relative_to(REPO_ROOT)}")
        print_info("Check directory permissions and try again")
    except Exception as e:
        print_error(f"Failed to rename directory: {e}")
        print_info("You may need to manually rename:")
        print(f"  mv {old_path} {new_path}")

def apply_configuration(config: Dict[str, str]) -> None:
    """Apply configuration changes across the repository."""
    print_header("APPLYING CHANGES")

    current = detect_current_config()

    # Build replacement map
    replacements = {}

    # Package name replacements
    if config["package_name"] != current.get("package_name"):
        replacements[current.get("package_name", DEFAULT_VALUES["package_name"])] = config["package_name"]
        replacements[current.get("package_name", DEFAULT_VALUES["package_name"]).replace("_", "-")] = config["package_name"].replace("_", "-")

    # CLI command replacements
    if config["cli_command"] != current.get("cli_command"):
        replacements[current.get("cli_command", DEFAULT_VALUES["cli_command"])] = config["cli_command"]

    # Repository owner/name replacements
    if config["repo_owner"] != current.get("repo_owner"):
        replacements[current.get("repo_owner", DEFAULT_VALUES["repo_owner"])] = config["repo_owner"]

    if config["repo_name"] != current.get("repo_name"):
        replacements[current.get("repo_name", DEFAULT_VALUES["repo_name"])] = config["repo_name"]

    # Description replacement
    if config["description"] != current.get("description"):
        replacements[current.get("description", DEFAULT_VALUES["description"])] = config["description"]

    # Files to update (in order of importance)
    files_to_update = [
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "README.md",
        REPO_ROOT / "CHANGELOG.md",
    ]

    # Add all Python files in src/
    src_dir = REPO_ROOT / "src"
    if src_dir.exists():
        files_to_update.extend(src_dir.rglob("*.py"))

    # Add all documentation files
    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        files_to_update.extend(docs_dir.rglob("*.md"))

    # Add workflow files
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if workflows_dir.exists():
        files_to_update.extend(workflows_dir.rglob("*.yml"))

    # Add platform config files
    packaging_dir = REPO_ROOT / "packaging"
    if packaging_dir.exists():
        files_to_update.extend(packaging_dir.rglob("*"))

    # Apply replacements
    modified_files = []
    for file_path in files_to_update:
        if file_path.is_file():
            if replace_in_file(file_path, replacements):
                modified_files.append(file_path.relative_to(REPO_ROOT))

    if modified_files:
        print_success(f"Updated {len(modified_files)} files")
        if len(modified_files) <= 20:  # Show list if reasonable
            for f in modified_files[:20]:
                print(f"  • {f}")
            if len(modified_files) > 20:
                print(f"  ... and {len(modified_files) - 20} more")

    # Rename package directory if needed
    if config["package_name"] != current.get("package_name"):
        # Use detected package_dir if available, otherwise convert package name
        old_dir_name = current.get("package_dir") or current.get("package_name", DEFAULT_VALUES["package_name"]).replace("-", "_")
        new_dir_name = config["package_name"].replace("-", "_")
        rename_package_directory(old_dir_name, new_dir_name)

    print_success("\nConfiguration applied successfully!")

def check_gh_cli() -> bool:
    """Check if GitHub CLI (gh) is installed."""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def list_github_secrets() -> Optional[List[str]]:
    """List GitHub secrets for the current repository."""
    try:
        result = subprocess.run(
            ["gh", "secret", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Parse output - format is "NAME\tUPDATED"
            secrets = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    secret_name = line.split("\t")[0]
                    secrets.append(secret_name)
            return secrets
        return None
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def configure_github_secrets(config: Dict[str, str]) -> None:
    """Guide user through GitHub secrets configuration."""
    print_header("GITHUB SECRETS CONFIGURATION")

    # Check if gh CLI is available
    if not check_gh_cli():
        print_warning("GitHub CLI (gh) is not installed or not in PATH")
        print("\nTo configure secrets, you need to install GitHub CLI:")
        print("\n  macOS:        brew install gh")
        print("  Linux:        See https://github.com/cli/cli/blob/trunk/docs/install_linux.md")
        print("  Windows:      winget install GitHub.cli")
        print("  Or visit:     https://cli.github.com/\n")
        print("After installing, authenticate with:")
        print("  gh auth login\n")
        print("Then run this wizard again or manually configure secrets:")
        print("  gh secret set SECRET_NAME\n")
        return

    # Check if authenticated
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            print_warning("Not authenticated with GitHub CLI")
            print("\nAuthenticate with GitHub:")
            print("  gh auth login")
            print("\nChoose:")
            print("  • GitHub.com (for public repositories)")
            print("  • Login with web browser (easiest)")
            print("  • HTTPS protocol")
            print("\nThen run this wizard again.\n")
            return
    except subprocess.TimeoutExpired:
        print_error("Timeout checking GitHub authentication")
        print_info("This might indicate a network issue or gh CLI problem")
        print("Try running manually: gh auth status")
        return

    # List existing secrets
    print_info("Checking existing secrets...")
    existing_secrets = list_github_secrets()

    if existing_secrets is None:
        print_warning("Could not list secrets")
        print_info("Common causes:")
        print("  • Not in a GitHub repository")
        print("  • No push access to the repository")
        print("  • Network connectivity issues")
        print("\nTry manually:")
        print("  gh secret list")
        return

    if existing_secrets:
        print_success(f"Found {len(existing_secrets)} existing secret(s):")
        for secret in existing_secrets:
            print(f"  • {secret}")
        print()
    else:
        print_info("No secrets configured yet.\n")

    # Platform-specific secrets
    platform_secrets = {
        "Homebrew": {
            "secrets": ["HOMEBREW_TAP_TOKEN"],
            "description": "Personal access token for Homebrew tap repository",
            "docs": "docs/distribution/quickstart/HOMEBREW.md"
        },
        "Chocolatey": {
            "secrets": ["CHOCOLATEY_API_KEY"],
            "description": "API key from chocolatey.org",
            "docs": "docs/distribution/quickstart/CHOCOLATEY.md"
        },
        "WinGet": {
            "secrets": ["WINGET_TOKEN"],
            "description": "GitHub token with workflow permissions",
            "docs": "docs/distribution/quickstart/WINGET.md"
        },
        "Snap": {
            "secrets": ["SNAPCRAFT_STORE_CREDENTIALS"],
            "description": "Credentials from snapcraft export-login",
            "docs": "docs/distribution/quickstart/SNAP.md"
        },
        "PyPI": {
            "secrets": ["PYPI_API_TOKEN"],
            "description": "API token from pypi.org",
            "docs": "docs/distribution/quickstart/PYPI.md"
        },
        "Docker/GHCR": {
            "secrets": ["GHCR_TOKEN"],
            "description": "GitHub token for container registry",
            "docs": "docs/distribution/quickstart/DOCKER.md"
        }
    }

    print("Would you like to configure secrets for distribution platforms?\n")
    print("Available platforms:")
    for i, (platform, info) in enumerate(platform_secrets.items(), 1):
        # Check if secrets already exist
        has_secrets = all(s in existing_secrets for s in info["secrets"])
        status = "✓ configured" if has_secrets else "not configured"
        print(f"  {i}. {platform} ({status})")
    print(f"  {len(platform_secrets) + 1}. Skip (configure later)\n")

    # Ask user which platforms to configure
    while True:
        choice = input("Enter platform number(s) to configure (comma-separated) or 'skip': ").strip().lower()

        if choice == "skip" or choice == str(len(platform_secrets) + 1):
            print_info("Skipping secrets configuration. You can configure them later.")
            return

        # Parse choices
        try:
            if "," in choice:
                choices = [int(c.strip()) for c in choice.split(",")]
            else:
                choices = [int(choice)]

            if all(1 <= c <= len(platform_secrets) for c in choices):
                break
            else:
                print_warning("Invalid choice. Please enter numbers 1-{} or 'skip'".format(len(platform_secrets) + 1))
        except ValueError:
            print_warning("Invalid input. Please enter numbers or 'skip'")

    # Configure selected platforms
    print()
    platforms_list = list(platform_secrets.items())
    for choice_num in choices:
        platform, info = platforms_list[choice_num - 1]
        print(colored(f"\n{platform}", Colors.BOLD))
        print(f"Description: {info['description']}")
        print(f"Documentation: {info['docs']}\n")

        for secret_name in info["secrets"]:
            if secret_name in existing_secrets:
                update = input(f"Secret {secret_name} already exists. Update? [y/N]: ").strip().lower()
                if update not in ["y", "yes"]:
                    print_info(f"Keeping existing {secret_name}")
                    continue

            print(f"\nSet {secret_name}:")
            print("  Enter the secret value when prompted by gh CLI")
            print(f"  (The value will be hidden for security)\n")

            try:
                # Use gh secret set with interactive input
                result = subprocess.run(
                    ["gh", "secret", "set", secret_name],
                    timeout=300  # 5 minutes timeout
                )
                if result.returncode == 0:
                    print_success(f"Secret {secret_name} configured successfully!")
                else:
                    print_error(f"Failed to configure {secret_name}")
            except subprocess.TimeoutExpired:
                print_error(f"Timeout while configuring {secret_name}")
            except KeyboardInterrupt:
                print_warning("\nSecret configuration cancelled")
                break

    print()
    print_success("Secrets configuration complete!")


def show_next_steps(config: Dict[str, str]) -> None:
    """Show next steps after configuration."""
    print_header("NEXT STEPS")

    print("Your template is now customized! Here's what to do next:\n")

    print(colored("1. Review Changes", Colors.BOLD))
    print("   git status")
    print("   git diff\n")

    print(colored("2. Test Your Package", Colors.BOLD))
    print(f"   uv run {config['cli_command']} --version")
    print(f"   uv run {config['cli_command']} hello world\n")

    print(colored("3. Run Tests", Colors.BOLD))
    print("   uv run pytest\n")

    print(colored("4. Update Your Code", Colors.BOLD))
    print(f"   • Add your logic to src/{config['package_name']}/")
    print("   • Update tests in tests/")
    print("   • Customize documentation in docs/\n")

    print(colored("5. Commit Changes", Colors.BOLD))
    print("   git add .")
    print(f"   git commit -m 'chore: Initialize template for {config['project_name']}'")
    print("   git push\n")

    print_info("For more help, see:")
    print("  • docs/contributing/DEVELOPER-GUIDE.md")
    print("  • docs/distribution/PLATFORM-SUPPORT.md")
    print("\nTo configure more secrets later, run: gh secret set SECRET_NAME")

def main() -> int:
    """Main entry point."""
    print_header("PROVENANCE TEMPLATE INITIALIZATION")

    print("This wizard will help you customize the provenance-template for your project.")
    print("It's safe to run multiple times - your current config will be detected.\n")

    # Check if already customized
    customized, unchanged = is_customized()

    if customized:
        print_success("Template is already customized!")
    else:
        print_warning(f"Template uses default values for: {', '.join(unchanged)}")

    print("\nPress Enter to continue, or Ctrl+C to exit...")
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        print("\n\nExiting.")
        return 0

    # Gather configuration
    config = get_project_config()

    # Confirm changes
    if not confirm_changes(config):
        print("\nNo changes made.")
        return 0

    # Apply configuration
    apply_configuration(config)

    # Configure GitHub secrets (optional)
    print("\n")
    configure_secrets = input("Would you like to configure GitHub secrets now? [y/N]: ").strip().lower()
    if configure_secrets in ["y", "yes"]:
        configure_github_secrets(config)
    else:
        print_info("Skipping secrets configuration. You can configure them later with: gh secret set SECRET_NAME")

    # Show next steps
    show_next_steps(config)

    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\n\nInterrupted. No changes made.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
