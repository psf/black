#!/bin/bash

# This script checks the configuration of the Provenance Demo.
# It verifies that essential files exist and are correctly configured.

set -euo pipefail

REPO_ROOT=$(dirname "$(dirname "$(realpath "$0")")")
cd "$REPO_ROOT"

GREEN="\033[0;32m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
BLUE="\033[0;34m"
NC="\033[0m"

# Function to check if a command exists
command_exists () {
  command -v "$1" >/dev/null 2>&1
}

# Function to log messages
log_info () {
  echo -e "${BLUE}[INFO]${NC} $1"
}

log_success () {
  echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn () {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error () {
  echo -e "${RED}[ERROR]${NC} $1"
}

# Function to run a check
run_check () {
  local name="$1"
  local check_cmd="$2"
  local help_text="$3"

  log_info "Checking: $name"
  if eval "$check_cmd"; then
    log_success "  ✓ $name is configured."
  else
    log_warn "  ✗ $name is NOT configured. $help_text"
    # Optionally, you could exit here or collect failures
  fi
}

log_info "Starting configuration checks..."

# Check essential files
run_check \
  "pyproject.toml exists" \
  "test -f pyproject.toml" \
  "Please ensure pyproject.toml is in the root directory."

run_check \
  "action.yml exists" \
  "test -f action.yml" \
  "Please ensure action.yml is in the root directory."

run_check \
  "Makefile exists" \
  "test -f Makefile" \
  "Please ensure Makefile is in the root directory."

run_check \
  "justfile exists" \
  "test -f justfile" \
  "Please ensure justfile is in the root directory."

run_check \
  "flake.nix exists" \
  "test -f flake.nix" \
  "Please ensure flake.nix is in the root directory."

# Check scripts directory
run_check \
  "scripts directory exists" \
  "test -d scripts" \
  "Please ensure the scripts directory exists."

# Check src directory
run_check \
  "src directory exists" \
  "test -d src" \
  "Please ensure the src directory exists."

# Check tests directory
run_check \
  "tests directory exists" \
  "test -d tests" \
  "Please ensure the tests directory exists."

# Check docs directory
run_check \
  "docs directory exists" \
  "test -d docs" \
  "Please ensure the docs directory exists."

# Check .github workflows
run_check \
  ".github/workflows directory exists" \
  "test -d .github/workflows" \
  "Please ensure the .github/workflows directory exists."

# Check pre-commit config
run_check \
  ".pre-commit-config.yaml exists" \
  "test -f .pre-commit-config.yaml" \
  "Please ensure .pre-commit-config.yaml is in the root directory."

# Check .env.example
run_check \
  ".env.example exists" \
  "test -f .env.example" \
  "Please ensure .env.example is in the root directory."

# Check distribution configurations (optional, but recommended)
log_info "Checking optional distribution configurations..."

# Check Homebrew configuration
run_check \
  "Homebrew formula config" \
  "test -d packaging/homebrew-tap/Formula" \
  "To enable: Create packaging/homebrew-tap/Formula/client.rb (see DEVELOPER_GUIDE.md)"

# Check Snap configuration
run_check \
  "Snap package config" \
  "test -f packaging/snap/snapcraft.yaml" \
  "To enable: Create packaging/snap/snapcraft.yaml (see DEVELOPER_GUIDE.md)"

# Check Debian configuration
run_check \
  "Debian package config" \
  "test -f packaging/debian/control && test -f packaging/debian/rules" \
  "To enable: Create packaging/debian/control and packaging/debian/rules (see DEVELOPER_GUIDE.md)"

# Check RPM configuration
run_check \
  "RPM package config" \
  "test -f packaging/rpm/redoubt.spec" \
  "To enable: Create packaging/rpm/redoubt.spec (see DEVELOPER_GUIDE.md)"

# Check Flatpak configuration
run_check \
  "Flatpak package config" \
  "test -f packaging/flatpak/com.OWNER.Redoubt.yml" \
  "To enable: Create packaging/flatpak/com.OWNER.Redoubt.yml (see DEVELOPER_GUIDE.md)"

# Check AppImage configuration
run_check \
  "AppImage config" \
  "test -f packaging/appimage/AppImageBuilder.yml" \
  "To enable: Create packaging/appimage/AppImageBuilder.yml (see DEVELOPER_GUIDE.md)"

# Check Chocolatey configuration
run_check \
  "Chocolatey package config" \
  "test -f packaging/chocolatey/redoubt.nuspec" \
  "To enable: Create packaging/chocolatey/redoubt.nuspec (see DEVELOPER_GUIDE.md)"

# Check Scoop configuration
run_check \
  "Scoop package config" \
  "test -f packaging/scoop/redoubt.json" \
  "To enable: Create packaging/scoop/redoubt.json (see DEVELOPER_GUIDE.md)"

# Check WinGet configuration
run_check \
  "WinGet package config" \
  "test -f packaging/winget/manifests/OWNER.redoubt.yaml" \
  "To enable: Create packaging/winget/manifests/OWNER.redoubt.yaml (see DEVELOPER_GUIDE.md)"

# Check AUR configuration
run_check \
  "AUR package config" \
  "test -f packaging/aur/PKGBUILD" \
  "To enable: Create packaging/aur/PKGBUILD (see DEVELOPER_GUIDE.md)"

log_success "All configuration checks completed."
