# Template Initialization Wizard

The `init-template.py` script helps you customize the provenance-template for your own project through an interactive wizard.

## Features

- **Idempotent**: Safe to run multiple times - detects current configuration
- **Interactive**: Step-by-step prompts with validation
- **Comprehensive**: Updates all files across the repository
- **Safe**: Shows summary before applying changes
- **Validated**: Ensures package names and CLI commands are valid

## Usage

```bash
python3 scripts/init-template.py
```

## What It Does

The wizard will guide you through customizing:

### 1. Package Name
Your Python package/module name (e.g., `my_cli_tool`)
- Must be lowercase
- Start with letter or underscore
- Contain only letters, numbers, underscores

### 2. CLI Command
The command users will type (e.g., `my-tool`)
- Must be lowercase
- Start with letter
- Contain only letters, numbers, hyphens

### 3. Repository Information
- GitHub owner/organization
- Repository name

### 4. Project Metadata
- Display name
- Description
- Author (optional, defaults to git config)
- Email (optional, defaults to git config)

## Files Updated

The wizard updates placeholders across:
- `pyproject.toml` - Package configuration
- `src/` - Source code directory (renamed if needed)
- `docs/` - All documentation files
- `.github/workflows/` - CI/CD workflows
- `packaging/` - Platform-specific configurations

## Example Session

```
======================================================================
PROVENANCE TEMPLATE INITIALIZATION
======================================================================

This wizard will help you customize the provenance-template for your project.
It's safe to run multiple times - your current config will be detected.

✓ Template is already customized!

Press Enter to continue, or Ctrl+C to exit...

======================================================================
PROJECT CONFIGURATION
======================================================================

ℹ Current configuration:
  package_name: provenance-demo
  description: Minimal demo CLI with a hardened, reproducible, and attestable release pipeline.

Enter new values (press Enter to keep current):

Python package name [provenance-demo]: my_secure_cli
CLI command name [demo]: secure-cli
GitHub repository owner/organization [hollowsunhc]: myorg
GitHub repository name [provenance-template]: my-project
Project display name [Secure Cli]: My Secure CLI
Project description [Minimal demo CLI...]: A secure CLI tool with attestations
Author name (optional) [John Doe]:
Author email (optional) [john@example.com]:

======================================================================
CONFIGURATION SUMMARY
======================================================================

The following changes will be applied:

  package_name: my_secure_cli
  cli_command: secure-cli
  repo_owner: myorg
  repo_name: my-project
  project_name: My Secure CLI
  description: A secure CLI tool with attestations

This will update:
  • pyproject.toml
  • Source code directory structure
  • Documentation files
  • GitHub workflow files
  • Platform configuration files

Apply these changes? [y/N]: y

======================================================================
APPLYING CHANGES
======================================================================

✓ Updated 156 files
  • pyproject.toml
  • README.md
  • docs/distribution/PLATFORM-SUPPORT.md
  ... and 153 more

✓ Renamed package directory: provenance-demo → my_secure_cli

✅ Configuration applied successfully!

======================================================================
NEXT STEPS
======================================================================

Your template is now customized! Here's what to do next:

1. Review Changes
   git status
   git diff

2. Test Your Package
   uv run secure-cli --version
   uv run secure-cli hello world

3. Run Tests
   uv run pytest

4. Update Your Code
   • Add your logic to src/my_secure_cli/
   • Update tests in tests/
   • Customize documentation in docs/

5. Configure Distribution (Optional)
   • Set up platform-specific secrets in GitHub
   • Review .github/workflows/ for publishing workflows
   • Update packaging/ configs with your package details

6. Commit Changes
   git add .
   git commit -m 'chore: Initialize template for My Secure CLI'
   git push

ℹ For more help, see:
  • docs/contributing/DEVELOPER-GUIDE.md
  • docs/distribution/PLATFORM-SUPPORT.md
```

## Validation

The wizard validates:
- **Package names**: Must be valid Python identifiers
- **CLI commands**: Must be valid shell commands
- **No empty required fields**: Package name, CLI command, repo info

## Idempotent Behavior

The script detects your current configuration from `pyproject.toml`:
- Shows what's already customized
- Allows you to keep current values (press Enter)
- Only updates files that actually change
- Safe to run multiple times to refine configuration

## Troubleshooting

### Script Fails to Find pyproject.toml

**Error:**
```
✗ pyproject.toml not found!
ℹ Expected location: /path/to/provenance-template/pyproject.toml
```

**Solution:** Make sure you're running from the repository root:
```bash
cd /path/to/provenance-template
python3 scripts/init-template.py
```

### Package Name Validation Errors

**Error:**
```
✗ Invalid package name: 'my-cli'
ℹ Package name requirements:
  • Must be lowercase
  • Start with letter or underscore
  • Contain only letters, numbers, and underscores
  • Examples: my_cli, secure_tool, cli_app
```

**Solution:** Use underscores instead of hyphens in package names:
- ✗ Wrong: `my-cli`, `My_CLI`, `123_cli`
- ✓ Correct: `my_cli`, `secure_tool`, `cli_app`

### CLI Command Validation Errors

**Error:**
```
✗ Invalid CLI command: 'my_cli'
ℹ CLI command requirements:
  • Must be lowercase
  • Start with a letter
  • Contain only letters, numbers, and hyphens
  • Examples: my-cli, secure-tool, cli-app
```

**Solution:** Use hyphens instead of underscores in CLI commands:
- ✗ Wrong: `my_cli`, `My-CLI`, `123-cli`
- ✓ Correct: `my-cli`, `secure-tool`, `cli-app`

### GitHub CLI Not Installed

**Error:**
```
⚠ GitHub CLI (gh) is not installed or not in PATH
```

**Solution:** Install GitHub CLI:
```bash
# macOS
brew install gh

# Linux (Debian/Ubuntu)
sudo apt install gh

# Windows
winget install GitHub.cli

# Or visit: https://cli.github.com/
```

Then authenticate:
```bash
gh auth login
```

### Not Authenticated with GitHub

**Error:**
```
⚠ Not authenticated with GitHub CLI
```

**Solution:** Authenticate with GitHub:
```bash
gh auth login
```

Choose:
- GitHub.com (for public repositories)
- Login with web browser (easiest)
- HTTPS protocol

### Cannot List Secrets

**Error:**
```
⚠ Could not list secrets
```

**Common causes:**
- Not in a GitHub repository
- No push access to the repository
- Network connectivity issues

**Solution:**
```bash
# Test manually
gh secret list

# If that fails, check authentication
gh auth status

# Re-authenticate if needed
gh auth login
```

### Permission Denied Errors

**Error:**
```
✗ Permission denied writing to pyproject.toml
```

**Solution:** Fix file permissions:
```bash
chmod u+w pyproject.toml
# or
chmod -R u+w .
```

### Target Directory Already Exists

**Error:**
```
✗ Target directory already exists: src/my_new_package
ℹ Please manually resolve the conflict:
  • Remove or rename: src/my_new_package
  • Then run this wizard again
```

**Solution:** Remove or rename the conflicting directory:
```bash
# Remove if it's empty
rm -rf src/my_new_package

# Or rename to backup
mv src/my_new_package src/my_new_package.backup
```

Then run the wizard again.

## Frequently Asked Questions

### Can I run the wizard multiple times?

Yes! The wizard is idempotent - it detects your current configuration and allows you to update values. It's safe to run as many times as needed.

### What if I make a mistake?

Before applying changes, the wizard shows a summary and asks for confirmation. If you haven't confirmed yet, just press `Ctrl+C` to exit. If you've already applied changes, you can:
1. Use `git diff` to see what changed
2. Use `git restore .` to revert if not committed
3. Run the wizard again to fix values

### Do I need to configure secrets immediately?

No, secrets configuration is optional. You can skip it during the wizard and configure them later:
```bash
gh secret set SECRET_NAME
```

### Which platforms require secrets?

- **Homebrew**: `HOMEBREW_TAP_TOKEN` (for tap repository)
- **Chocolatey**: `CHOCOLATEY_API_KEY` (from chocolatey.org)
- **WinGet**: `WINGET_TOKEN` (GitHub token with workflow permissions)
- **Snap**: `SNAPCRAFT_STORE_CREDENTIALS` (from snapcraft export-login)
- **PyPI**: `PYPI_API_TOKEN` (from pypi.org)
- **Docker/GHCR**: `GHCR_TOKEN` (GitHub token for container registry)

See [Platform Status](../docs/distribution/PLATFORM-STATUS.md) for complete details.

### What's the difference between package name and CLI command?

- **Package name**: Python module name (use underscores: `my_cli`)
- **CLI command**: What users type in terminal (use hyphens: `my-cli`)

Example:
```python
# Package name: my_secure_cli
from my_secure_cli import main

# CLI command: my-secure-cli
$ my-secure-cli --version
```

## Advanced Usage

### Non-Interactive Mode
Currently, the script requires interactive input. For CI/CD automation, use the shell script instead:
```bash
./scripts/setup_local_config.sh
```

### Partial Updates
You can run the wizard multiple times to update specific values:
1. Run the wizard
2. Keep most values unchanged (press Enter)
3. Update only what you want to change

## Comparison with setup_local_config.sh

| Feature | init-template.py | setup_local_config.sh |
|---------|------------------|----------------------|
| Interactive | ✅ Yes | ❌ No |
| Idempotent | ✅ Yes | ⚠️  Partial |
| Validation | ✅ Yes | ❌ No |
| Package renaming | ✅ Yes | ❌ No |
| Shows summary | ✅ Yes | ❌ No |
| Detects current config | ✅ Yes | ❌ No |
| CI/CD friendly | ⚠️  Planned | ✅ Yes |

**Recommendation**: Use `init-template.py` for initial setup and customization. Use `setup_local_config.sh` for quick repository URL updates in CI/CD.
