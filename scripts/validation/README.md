# Platform Validation Scripts

This directory contains standalone validation scripts for all distribution platforms supported by provenance-demo.

## Overview

Each validation script performs comprehensive checks to ensure the platform installation is working correctly:

- ✅ Platform/tool availability
- ✅ Command existence and accessibility
- ✅ Version information
- ✅ Basic functionality tests
- ✅ Verify command availability
- ✅ Platform-specific checks (checksums, signatures, etc.)

## Scripts

### Individual Platform Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `validate-pypi.sh` | PyPI | Validates pip/uv installations |
| `validate-pipx.sh` | pipx | Validates pipx isolated installations |
| `validate-pyz.sh` | .pyz | Validates direct .pyz file execution |
| `validate-github-releases.sh` | GitHub Releases | Validates downloaded release artifacts |
| `validate-homebrew.sh` | Homebrew | Validates Homebrew package installations |
| `validate-snap.sh` | Snap | Validates Snap package installations |
| `validate-docker.sh` | Docker/OCI | Validates Docker container images |

### Master Script

| Script | Description |
|--------|-------------|
| `validate-all.sh` | Master script that runs all platform validations with comprehensive reporting |

## Usage

### Individual Platform Validation

Run a specific platform validation:

```bash
# PyPI validation
./validate-pypi.sh

# pipx validation
./validate-pipx.sh

# .pyz validation
./validate-pyz.sh

# GitHub Releases validation
./validate-github-releases.sh

# Homebrew validation
./validate-homebrew.sh

# Snap validation
./validate-snap.sh

# Docker validation
./validate-docker.sh
```

### Master Script Validation

#### Validate All Platforms

```bash
./validate-all.sh
```

#### Validate Specific Platforms

```bash
# Validate only PyPI and Docker
./validate-all.sh --platforms=pypi,docker

# Validate package managers
./validate-all.sh --platforms=pipx,homebrew,snap
```

#### Continue on Error

By default, the master script stops on the first failure. Use `--continue-on-error` to test all platforms:

```bash
./validate-all.sh --continue-on-error
```

#### Verbose Mode

Show detailed output from each validation:

```bash
./validate-all.sh --verbose
```

#### Combined Options

```bash
./validate-all.sh --platforms=pypi,pipx,homebrew --continue-on-error --verbose
```

## Exit Codes

All scripts use standard exit codes:

- `0` - All validation checks passed
- `1` - One or more validation checks failed

## Prerequisites

### Platform-Specific Requirements

Each validation script requires the corresponding platform to be installed:

| Script | Requires |
|--------|----------|
| `validate-pypi.sh` | `pip` or `uv`, `provenance-demo` installed via PyPI |
| `validate-pipx.sh` | `pipx`, `provenance-demo` installed via pipx |
| `validate-pyz.sh` | Python 3.10+, `provenance-demo.pyz` file in current directory |
| `validate-github-releases.sh` | Downloaded release artifacts in current directory |
| `validate-homebrew.sh` | Homebrew, `provenance-demo` installed via brew |
| `validate-snap.sh` | `snapd`, `provenance-demo` snap installed |
| `validate-docker.sh` | Docker daemon, `ghcr.io/hollowsunhc/provenance-demo` image |

### Optional Tools

For enhanced validation (signatures, checksums):

- `cosign` - For Sigstore signature verification
- `sha256sum` - For checksum verification (usually pre-installed)
- `gh` - For GitHub CLI operations

## Examples

### Validate After Installation

After installing via PyPI:

```bash
pip install provenance-demo
./validate-pypi.sh
```

After installing via pipx:

```bash
pipx install provenance-demo
./validate-pipx.sh
```

### Validate Downloaded Release

After downloading from GitHub Releases:

```bash
gh release download v0.1.0 --repo hollowsunhc/provenance-template
cd v0.1.0/
../scripts/validation/validate-github-releases.sh
```

### Validate Multiple Platforms

Test all installed platforms:

```bash
./validate-all.sh --continue-on-error
```

### CI/CD Integration

Use in GitHub Actions:

```yaml
- name: Validate PyPI Installation
  run: |
    pip install provenance-demo
    ./scripts/validation/validate-pypi.sh

- name: Validate All Platforms
  run: ./scripts/validation/validate-all.sh --continue-on-error
```

## Output Examples

### Individual Script Success

```
=== PyPI Installation Validation ===
✓ Command found
✓ Version: provenance-demo 0.1.0
✓ Basic functionality works
✓ Verify command available

✅ All validation checks passed!
Installation is working correctly.
```

### Individual Script Failure

```
=== PyPI Installation Validation ===
❌ provenance-demo command not found
```

### Master Script Summary

```
╔════════════════════════════════════════════════════════════════╗
║                    VALIDATION SUMMARY                          ║
╚════════════════════════════════════════════════════════════════╝

Platform              Result
────────────────────────────────────────────────────────────────
pypi                 ✓ PASSED
pipx                 ✓ PASSED
pyz                  ⊘ SKIPPED
github-releases      ✓ PASSED
homebrew             ✗ FAILED
snap                 ⊘ SKIPPED
docker               ✓ PASSED

────────────────────────────────────────────────────────────────
Total:   7
Passed:  4
Failed:  1
Skipped: 2
────────────────────────────────────────────────────────────────
```

## Troubleshooting

### Script Not Found

If you get "command not found":

```bash
# Make scripts executable
chmod +x scripts/validation/*.sh

# Or run with bash explicitly
bash scripts/validation/validate-pypi.sh
```

### Platform Not Available

If a platform isn't available on your system, the validation will fail. This is expected behavior.

To test only available platforms:

```bash
./validate-all.sh --continue-on-error
```

### Permission Denied (Docker)

For Docker validation without sudo:

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### snapd Not Running

For Snap validation:

```bash
# Start snapd service
sudo systemctl start snapd
sudo systemctl enable snapd
```

## Development

### Adding a New Platform

To add validation for a new platform:

1. Create `validate-{platform}.sh` following the existing pattern
2. Add proper shebang and `set -e`
3. Implement comprehensive checks
4. Add to `ALL_PLATFORMS` array in `validate-all.sh`
5. Update this README

### Script Template

```bash
#!/bin/bash
set -e

echo "=== Platform Name Validation ==="

# Check if platform tool is installed
if ! command -v platform-tool &> /dev/null; then
    echo "❌ platform-tool not found"
    exit 1
fi
echo "✓ Platform tool found"

# Check if package is installed
if ! command -v provenance-demo &> /dev/null; then
    echo "❌ provenance-demo command not found"
    exit 1
fi
echo "✓ Command found"

# Check version
VERSION=$(provenance-demo --version 2>&1)
if [[ -z "$VERSION" ]]; then
    echo "❌ Version check failed"
    exit 1
fi
echo "✓ Version: $VERSION"

# Test basic functionality
OUTPUT=$(provenance-demo hello "Test" 2>&1)
if [[ "$OUTPUT" != *"Hello, Test"* ]]; then
    echo "❌ Basic functionality test failed"
    exit 1
fi
echo "✓ Basic functionality works"

# Check if verify command exists
if ! provenance-demo verify --help &> /dev/null; then
    echo "❌ Verify command not available"
    exit 1
fi
echo "✓ Verify command available"

echo ""
echo "✅ All validation checks passed!"
echo "Installation is working correctly."
```

## Related Documentation

- [Platform Status](../../docs/distribution/PLATFORM-STATUS.md) - Complete platform support matrix
- [Quickstart Guides](../../docs/distribution/quickstart/) - Installation instructions for each platform
- [Phase 1 Testing](../phase1-testing/) - Automated platform testing
- [Phase 2 Testing](../phase2-testing/) - Comprehensive integration testing

## Support

For issues with validation scripts:

1. Ensure the platform is properly installed
2. Check that `provenance-demo` is accessible
3. Review the [Troubleshooting](#troubleshooting) section
4. Open an issue at [GitHub Issues](https://github.com/hollowsunhc/provenance-demo/issues)

---

**Last Updated:** 2025-11-01
**Maintainer:** provenance-demo team
