# Phase 2 Testing Scripts

Automated scripts for testing package manager installations without public release.

## Overview

Phase 2 testing allows you to test the complete installation experience using package managers (Homebrew, PyPI, Docker, Snap, APT, RPM, Scoop) before publishing to official registries.

Each platform has:

1. **Setup script** - Creates private infrastructure and uploads your package
2. **Test script** - Creates a fresh VM and tests the installation

## Quick Start

### Run All Tests

```bash
# Setup and test all platforms
./run-all-phase2-tests.sh --setup --all

# Test specific platforms
./run-all-phase2-tests.sh --setup homebrew pypi docker
```

### Individual Platform Testing

```bash
# 1. Setup infrastructure and upload package
./setup-homebrew-tap.sh

# 2. Test in fresh VM
./test-homebrew-tap-vm.sh
```

## Available Platforms

| Platform | Setup Script | Test Script | Infrastructure Created |
|----------|-------------|-------------|----------------------|
| **Homebrew** | `setup-homebrew-tap.sh` | `test-homebrew-tap-vm.sh` | `OWNER/homebrew-tap` repo |
| **PyPI** | `setup-test-pypi.sh` | `test-test-pypi-vm.sh` | Package on test.pypi.org |
| **Docker** | `setup-docker-registry.sh` | `test-docker-registry-vm.sh` | `ghcr.io/OWNER/redoubt:test-*` |
| **Snap** | `setup-snap-edge.sh` | `test-snap-edge-vm.sh` | Edge channel on Snap Store |
| **APT** | `setup-apt-repo.sh` | `test-apt-repo-vm.sh` | `OWNER/apt-repo` (GitHub Pages) |
| **RPM** | `setup-rpm-repo.sh` | `test-rpm-repo-vm.sh` | `OWNER/rpm-repo` (GitHub Pages) |
| **Scoop** | `setup-scoop-bucket.sh` | *(manual)* | `OWNER/scoop-bucket` repo |

## Prerequisites

### General Requirements

- **multipass** - For creating test VMs
  - macOS: `brew install multipass`
  - Linux: `sudo snap install multipass`
- **gh** - GitHub CLI (for repository management)
  - `brew install gh` or `sudo apt install gh`
  - Run `gh auth login` to authenticate

### Platform-Specific Requirements

#### Homebrew

- No additional requirements (uses gh CLI)

#### PyPI

- **twine** - For uploading to Test PyPI

  ```bash
  pip install twine
  ```

- **Test PyPI account** - Register at <https://test.pypi.org>

#### Docker

- **docker** - Docker Desktop or Docker Engine
- **Authenticated with GHCR**

  ```bash
  gh auth token | docker login ghcr.io -u USERNAME --password-stdin
  ```

#### Snap

- **snapcraft** - Snap packaging tool

  ```bash
  sudo snap install snapcraft --classic
  snapcraft login
  ```

- **Registered snap name** - Register at <https://snapcraft.io>

#### APT

- **dpkg-deb** - Debian package tools
  - Ubuntu/Debian: `sudo apt install dpkg-dev`
  - macOS: `brew install dpkg`

#### RPM

- **rpmbuild** - RPM build tools
  - Fedora/RHEL: `sudo dnf install rpm-build`
  - Ubuntu/Debian: `sudo apt install rpm`
  - macOS: `brew install rpm`
- **createrepo_c** - Repository metadata generation
  - Fedora/RHEL: `sudo dnf install createrepo_c`
  - Ubuntu/Debian: `sudo apt install createrepo-c`
  - macOS: `brew install createrepo_c`

#### Scoop

- No additional requirements (setup only, manual Windows testing)

## Detailed Platform Guides

### Homebrew (macOS/Linux)

```bash
# 1. Setup private tap
./setup-homebrew-tap.sh
# - Creates OWNER/homebrew-tap repository
# - Builds provenance-demo.pyz
# - Creates test release in main repo
# - Updates Formula/redoubt.rb with SHA256
# - Pushes to tap repo

# 2. Test installation in VM
./test-homebrew-tap-vm.sh
# - Creates Ubuntu VM
# - Installs Homebrew
# - Adds your private tap: brew tap OWNER/tap
# - Installs: brew install redoubt
# - Tests: redoubt --version, redoubt hello, redoubt verify
```

**What users will do:**

```bash
brew tap OWNER/tap
brew install redoubt
```

---

### PyPI (Python Packages)

```bash
# 1. Upload to Test PyPI
./setup-test-pypi.sh
# - Builds wheel and sdist
# - Uploads to test.pypi.org
# - Tests installation from Test PyPI

# 2. Test in fresh VM
./test-test-pypi-vm.sh
# - Creates Ubuntu VM
# - Installs Python and pip
# - Installs from Test PyPI
# - Tests commands
```

**What users will do:**

```bash
pip install --index-url https://test.pypi.org/simple/ provenance-demo
```

---

### Docker (Container Registry)

```bash
# 1. Push to GHCR
./setup-docker-registry.sh
# - Builds Docker image
# - Tags as ghcr.io/OWNER/redoubt:test-VERSION
# - Pushes to GitHub Container Registry
# - Tests locally

# 2. Test pull from registry
./test-docker-registry-vm.sh
# - Creates Ubuntu VM
# - Installs Docker
# - Pulls from GHCR
# - Runs container tests
```

**What users will do:**

```bash
docker pull ghcr.io/OWNER/redoubt:test-VERSION
docker run ghcr.io/OWNER/redoubt:test-VERSION --version
```

---

### Snap (Linux)

```bash
# 1. Upload to edge channel
./setup-snap-edge.sh
# - Builds .pyz
# - Builds snap package
# - Uploads to Snap Store edge channel
# - Tests local installation

# 2. Test from edge channel
./test-snap-edge-vm.sh
# - Creates Ubuntu VM
# - Waits for snapd
# - Installs from edge: snap install provenance-demo --edge
# - Tests commands
```

**What users will do:**

```bash
sudo snap install provenance-demo --edge
```

---

### APT (Debian/Ubuntu)

```bash
# 1. Setup private APT repository
./setup-apt-repo.sh
# - Builds .deb package
# - Creates OWNER/apt-repo repository
# - Generates Packages index
# - Publishes to GitHub Pages
# - Waits for deployment

# 2. Test installation
./test-apt-repo-vm.sh
# - Creates Ubuntu VM
# - Adds APT repository
# - Installs: apt install redoubt
# - Tests commands
```

**What users will do:**

```bash
echo "deb [trusted=yes] https://OWNER.github.io/apt-repo stable main" | sudo tee /etc/apt/sources.list.d/redoubt.list
sudo apt update
sudo apt install redoubt
```

---

### RPM (Fedora/RHEL/CentOS)

```bash
# 1. Setup private RPM repository
./setup-rpm-repo.sh
# - Builds .rpm package
# - Creates OWNER/rpm-repo repository
# - Generates repository metadata
# - Publishes to GitHub Pages

# 2. Test installation
./test-rpm-repo-vm.sh
# - Creates Fedora or Ubuntu VM (with DNF)
# - Adds RPM repository
# - Installs: dnf install redoubt
# - Tests commands
```

**What users will do:**

```bash
sudo curl -fsSL https://OWNER.github.io/rpm-repo/redoubt.repo -o /etc/yum.repos.d/redoubt.repo
sudo dnf install redoubt
```

---

### Scoop (Windows)

```bash
# 1. Setup private bucket (macOS/Linux)
./setup-scoop-bucket.sh
# - Creates OWNER/scoop-bucket repository
# - Builds provenance-demo.pyz
# - Creates test release
# - Generates Scoop manifest with SHA256
# - Pushes to bucket repo

# 2. Manual testing in Windows
# Open PowerShell on Windows VM:
scoop bucket add OWNER https://github.com/OWNER/scoop-bucket
scoop install redoubt
redoubt --version
```

**Note:** Automated Windows VM testing not yet implemented. Use manual testing in Windows VM or physical Windows machine.

---

## Master Test Runner

The `run-all-phase2-tests.sh` script orchestrates testing across all platforms:

### Usage

```bash
./run-all-phase2-tests.sh [OPTIONS] [PLATFORMS]

Options:
  --setup              Run setup scripts before tests
  --all                Run all platform tests
  -h, --help           Show help message

Platforms:
  homebrew, pypi, docker, snap, apt, rpm
```

### Examples

```bash
# Run all tests with setup
./run-all-phase2-tests.sh --setup --all

# Test specific platforms with setup
./run-all-phase2-tests.sh --setup homebrew docker snap

# Test only (assumes setup already done)
./run-all-phase2-tests.sh pypi apt rpm

# Get help
./run-all-phase2-tests.sh --help
```

### Output

The master runner provides:

- Colored output for each platform
- Timing for each test
- Summary statistics
- Pass/fail/skip status

Example output:

```
╔════════════════════════════════════════════════════════════════════╗
║         Redoubt Phase 2 Testing - Master Test Runner              ║
╚════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Testing: Homebrew Tap
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Running setup: setup-homebrew-tap.sh
...
✓ Homebrew Tap test passed (45s)

╔════════════════════════════════════════════════════════════════════╗
║                     Phase 2 Testing Summary                        ║
╚════════════════════════════════════════════════════════════════════╝

Test Results:
  ✓ Homebrew Tap: PASSED (45s)
  ✓ Test PyPI: PASSED (38s)
  ✓ Docker GHCR: PASSED (52s)

Statistics:
  Total tests:    3
  Passed:         3
  Failed:         0
  Skipped:        0

All tests passed! 🎉
```

## Troubleshooting

### Common Issues

#### "multipass not found"

```bash
# macOS
brew install multipass

# Linux
sudo snap install multipass
```

#### "gh: command not found"

```bash
brew install gh  # or sudo apt install gh
gh auth login
```

#### GitHub API rate limit

If you hit rate limits, authenticate with GitHub CLI:

```bash
gh auth login
```

#### VM creation fails

```bash
# Check multipass status
multipass list

# Delete stale VMs
multipass delete --all --purge

# Restart multipass
multipass restart
```

#### Docker login fails

```bash
# Login to GHCR
gh auth token | docker login ghcr.io -u YOUR_USERNAME --password-stdin
```

#### Test PyPI upload fails

Make sure you've registered at <https://test.pypi.org> and configured `~/.pypirc`:

```ini
[testpypi]
username = __token__
password = pypi-...
```

### Platform-Specific Issues

#### Homebrew: Formula not found after setup

- Wait a few seconds for GitHub to propagate the push
- Check that Formula/redoubt.rb exists in your tap repo
- Verify the tap was added: `brew tap`

#### Snap: Upload fails

- Ensure you're logged in: `snapcraft login`
- Verify snap name is registered: `snapcraft list-registered`
- Check snap store status: <https://snapcraft.io>

#### APT/RPM: GitHub Pages not deployed

- Wait 1-2 minutes after push for GitHub Pages to deploy
- Check GitHub Pages settings in repository
- Verify Pages source is set to main branch

## Next Steps

After Phase 2 testing passes:

1. **Review test results** - Ensure all platforms install correctly
2. **Manual testing** - Test on actual systems (not just VMs)
3. **Beta testing** - Share private repos/registries with testers
4. **Proceed to Phase 3** - Publish to official registries

See [TESTING-APPROACHES.md](../../TESTING-APPROACHES.md) for complete testing strategy.

## Contributing

To add a new platform to Phase 2 testing:

1. Create `setup-PLATFORM.sh` script
2. Create `test-PLATFORM-vm.sh` script
3. Add platform to `run-all-phase2-tests.sh`
4. Update this README
5. Update TESTING-APPROACHES.md

Example platforms to add:

- Chocolatey (Windows)
- WinGet (Windows)
- Flatpak (Linux)
- AppImage (Linux)
- AUR (Arch Linux)
- Nix/nixpkgs
