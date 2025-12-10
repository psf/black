#!/usr/bin/env bash
# Setup script for local configuration (no external accounts needed)
# This configures everything possible without GitHub secrets, PyPI accounts, etc.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Local Configuration Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Display tool versions from centralized config
if [ -f "config/tool-versions.yml" ]; then
    echo -e "${BLUE}## Tool Versions (from config/tool-versions.yml)${NC}"
    echo ""
    # Extract key versions using grep/sed (works without yaml parser)
    UV_VERSION=$(grep -A1 "^uv:" config/tool-versions.yml | grep "version:" | sed 's/.*version: "\(.*\)"/\1/')
    PIP_VERSION=$(grep -A1 "^pip:" config/tool-versions.yml | grep "version:" | sed 's/.*version: "\(.*\)"/\1/')
    PYTHON_DEFAULT=$(grep -A3 "^python:" config/tool-versions.yml | grep "default:" | sed 's/.*default: "\(.*\)"/\1/')

    echo "  • Python: $PYTHON_DEFAULT (default)"
    echo "  • uv: $UV_VERSION"
    echo "  • pip: $PIP_VERSION"
    echo ""
    echo -e "${GREEN}✅ Using centralized tool versions from config/tool-versions.yml${NC}"
    echo "   (Edit this file to update tool versions across all workflows and scripts)"
    echo ""
fi

# Get repository information from git remote or environment variables
GITHUB_OWNER="${GITHUB_OWNER:-}"
GITHUB_REPO="${GITHUB_REPO:-}"

if [ -z "$GITHUB_OWNER" ] || [ -z "$GITHUB_REPO" ]; then
    if git remote get-url origin >/dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        if [[ $REMOTE_URL =~ github\.com[:/]([^/]+)/([^/.]+) ]]; then
            GITHUB_OWNER="${BASH_REMATCH[1]}"
            GITHUB_REPO="${BASH_REMATCH[2]}"
            echo -e "${GREEN}✅ Detected repository from git remote: $GITHUB_OWNER/$GITHUB_REPO${NC}"
        fi
    fi
fi

# Fallback to default values if still not set
if [ -z "$GITHUB_OWNER" ]; then
    GITHUB_OWNER="hollowsunhc"
    echo -e "${YELLOW}⚠ GITHUB_OWNER not set, using default: $GITHUB_OWNER${NC}"
fi
if [ -z "$GITHUB_REPO" ]; then
    GITHUB_REPO="provenance-demo"
    echo -e "${YELLOW}⚠ GITHUB_REPO not set, using default: $GITHUB_REPO${NC}"
fi

echo ""
echo -e "${BLUE}## Updating Repository References${NC}"
echo ""

# Update hollowsunhc/provenance-demo placeholders in all files
echo "Updating hollowsunhc/provenance-demo → $GITHUB_OWNER/$GITHUB_REPO..."

# Update workflows
for file in .github/workflows/*.yml; do
    if [ -f "$file" ]; then
        sed -i.bak "s/OWNER\/REPO/$GITHUB_OWNER\/$GITHUB_REPO/g" "$file"
        rm "${file}.bak"
        echo "  ✓ $(basename $file)"
    fi
done

# Update documentation and packaging files
for file in README.md SUPPLY-CHAIN.md QUICK-START.md DEVELOPER_GUIDE.md SECURITY.md packaging/aur/PKGBUILD; do
    if [ -f "$file" ]; then
        sed -i.bak "s/hollowsunhc\/provenance-demo-/$GITHUB_OWNER\/$GITHUB_REPO/g" "$file"
        sed -i.bak "s/OWNER\/tap/$GITHUB_OWNER\/tap/g" "$file"
        rm "${file}.bak"
        echo "  ✓ $file"
    fi
done

# Update scripts
for file in scripts/*.sh; do
    if [ -f "$file" ]; then
        sed -i.bak "s/OWNER\/REPO/$GITHUB_OWNER\/$GITHUB_REPO/g" "$file"
        rm "${file}.bak"
        echo "  ✓ $(basename $file)"
    fi
done

echo ""
echo -e "${BLUE}## Customizing Package Metadata${NC}"
echo ""

# Get package name
CURRENT_NAME=$(grep '^name = ' pyproject.toml | cut -d'"' -f2)
echo "Current package name: $CURRENT_NAME"
if [ -n "${CLI_PACKAGE_NAME}" ]; then
    NEW_NAME="${CLI_PACKAGE_NAME}"
    echo -e "${GREEN}✅ Using package name from environment: $NEW_NAME${NC}"
else
    read -p "Enter new package name (or press Enter to keep '$CURRENT_NAME'): " NEW_NAME_INPUT
    NEW_NAME=${NEW_NAME_INPUT:-$CURRENT_NAME}
fi

if [ "$NEW_NAME" != "$CURRENT_NAME" ]; then
    sed -i.bak "s/name = \"$CURRENT_NAME\"/name = \"$NEW_NAME\"/" pyproject.toml
    rm pyproject.toml.bak
    echo -e "${GREEN}  ✓ Updated package name to: $NEW_NAME${NC}"
fi

# Get author name
CURRENT_AUTHOR=$(grep 'authors = ' pyproject.toml | cut -d'"' -f2)
if [ "$CURRENT_AUTHOR" = "Your Name" ]; then
    AUTHOR_NAME="${AUTHOR_NAME:-}"
    AUTHOR_EMAIL="${AUTHOR_EMAIL:-}"

    if [ -z "$AUTHOR_NAME" ] || [ -z "$AUTHOR_EMAIL" ]; then
        # Try to get from git config
        GIT_NAME=$(git config user.name 2>/dev/null || echo "")
        GIT_EMAIL=$(git config user.email 2>/dev/null || echo "")

        if [ -n "$GIT_NAME" ] && [ -n "$GIT_EMAIL" ]; then
            AUTHOR_NAME="$GIT_NAME"
            AUTHOR_EMAIL="$GIT_EMAIL"
            echo -e "${GREEN}✅ Detected git user for author info: $AUTHOR_NAME <$AUTHOR_EMAIL>${NC}"
        else
            AUTHOR_NAME="Your Name" # Fallback default
            AUTHOR_EMAIL="your.email@example.com" # Fallback default
            echo -e "${YELLOW}⚠ Author name/email not set, using defaults: $AUTHOR_NAME <$AUTHOR_EMAIL>${NC}"
        fi
    else
        echo -e "${GREEN}✅ Using author info from environment: $AUTHOR_NAME <$AUTHOR_EMAIL>${NC}"
    fi
    sed -i.bak "s/authors = \[{name = \"Your Name\"}\]/authors = [{name = \"$AUTHOR_NAME\", email = \"$AUTHOR_EMAIL\"}]/" pyproject.toml
    rm pyproject.toml.bak
    echo -e "${GREEN}  ✓ Updated author info${NC}"
fi

# Update CLI entry point name
CURRENT_CLI=$(grep '^\[project.scripts\]' -A 1 pyproject.toml | tail -1 | cut -d' ' -f1)
echo "Current CLI command: $CURRENT_CLI"
if [ -n "${CLI_COMMAND_NAME}" ]; then
    NEW_CLI="${CLI_COMMAND_NAME}"
    echo -e "${GREEN}✅ Using CLI command name from environment: $NEW_CLI${NC}"
else
    read -p "Enter new CLI command name (or press Enter to keep '$CURRENT_CLI'): " NEW_CLI_INPUT
    NEW_CLI=${NEW_CLI_INPUT:-$CURRENT_CLI}
fi

if [ "$NEW_CLI" != "$CURRENT_CLI" ]; then
    sed -i.bak "s/^$CURRENT_CLI = /$NEW_CLI = /" pyproject.toml
    rm pyproject.toml.bak
    echo -e "${GREEN}  ✓ Updated CLI command to: $NEW_CLI${NC}"
fi

if [ "$NEW_CLI" != "$CURRENT_CLI" ]; then
    sed -i.bak "s/^$CURRENT_CLI = /$NEW_CLI = /" pyproject.toml
    rm pyproject.toml.bak
    echo -e "${GREEN}  ✓ Updated CLI command to: $NEW_CLI${NC}"
fi

echo ""
echo -e "${BLUE}## Setting Up Pre-commit Hooks${NC}"
echo ""

# Install pre-commit if not available
if ! command -v pre-commit &> /dev/null; then
    echo "Installing pre-commit..."
    pip3 install pre-commit
fi

# Install hooks
echo "Installing pre-commit hooks..."
pre-commit install
echo -e "${GREEN}  ✓ Pre-commit hooks installed${NC}"

# Generate secrets baseline
if command -v detect-secrets &> /dev/null; then
    echo "Generating secrets baseline..."
    detect-secrets scan > .secrets.baseline 2>/dev/null || true
    echo -e "${GREEN}  ✓ Secrets baseline created${NC}"
else
    echo -e "${YELLOW}  ⚠ detect-secrets not installed (optional)${NC}"
    echo "    Install: pip install detect-secrets"
fi

echo ""
echo -e "${BLUE}## Building Artifacts${NC}"
echo ""

# Build .pyz
if [ -x scripts/build_pyz.sh ]; then
    echo "Building .pyz artifact..."
    ./scripts/build_pyz.sh
    echo -e "${GREEN}  ✓ .pyz built: dist/provenance-demo.pyz${NC}"
else
    echo -e "${YELLOW}  ⚠ Build script not executable${NC}"
    chmod +x scripts/build_pyz.sh
    ./scripts/build_pyz.sh
    echo -e "${GREEN}  ✓ .pyz built: dist/provenance-demo.pyz${NC}"
fi

# Build wheel and sdist
if command -v python3 &> /dev/null; then
    echo "Building wheel and sdist..."
    python3 -m pip install --user build >/dev/null 2>&1 || true
    python3 -m build
    echo -e "${GREEN}  ✓ Wheel and sdist built${NC}"
fi

echo ""
echo -e "${BLUE}## Creating Distribution Configurations${NC}"
echo ""

# Create homebrew-tap directory structure (local only, for testing)
mkdir -p packaging/homebrew-tap/Formula
cat > packaging/homebrew-tap/Formula/client.rb <<EOF
# Homebrew Formula for $NEW_NAME
# This is a template - customize for your needs

class Client < Formula
  desc "$NEW_NAME - Secure CLI with reproducible releases"
  homepage "https://github.com/$GITHUB_OWNER/$GITHUB_REPO"
  url "https://github.com/$GITHUB_OWNER/$GITHUB_REPO/releases/download/v0.1.0/provenance-demo.pyz"
  sha256 "REPLACE_WITH_ACTUAL_SHA256"
  license "MIT"

  def install
    bin.install "provenance-demo.pyz" => "$NEW_CLI"
  end

  test do
    system "#{bin}/$NEW_CLI", "--version"
  end
end
EOF
echo -e "${GREEN}  ✓ Created Homebrew formula template: packaging/homebrew-tap/Formula/client.rb${NC}"
echo "    Note: Update SHA256 and version after first release"

# Create snap directory structure (for future use)
mkdir -p snap
cat > packaging/snap/snapcraft.yaml <<EOF
name: $NEW_NAME
base: core22
version: '0.1.0'
summary: Secure CLI with reproducible releases
description: |
  $NEW_NAME is a Python CLI application with a production-grade
  secure release pipeline including reproducible builds, SBOM generation,
  and cryptographic signatures.

grade: stable
confinement: strict

apps:
  $NEW_CLI:
    command: bin/provenance-demo.pyz
    plugs:
      - home
      - network

parts:
  cli:
    plugin: dump
    source: dist/
    organize:
      'provenance-demo.pyz': bin/provenance-demo.pyz
    stage:
      - bin/provenance-demo.pyz
EOF
echo -e "${GREEN}  ✓ Created Snap configuration: packaging/snap/snapcraft.yaml${NC}"

# Create .env.example (but not .env)
cat > .env.example <<EOF
# Example environment configuration
# Copy to .env and customize (DO NOT commit .env)

# GitHub Configuration
GITHUB_REPO=$GITHUB_OWNER/$GITHUB_REPO

# Optional: Homebrew Tap
HOMEBREW_TAP=$GITHUB_OWNER/tap

# Optional: PyPI Package Name
PYPI_PACKAGE=$NEW_NAME

# GitHub Tokens (DO NOT commit actual tokens)
# TAP_PUSH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# WINGET_GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# PYPI_TOKEN=pypi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EOF
echo -e "${GREEN}  ✓ Created .env.example${NC}"

echo ""
echo -e "${BLUE}## Running Tests${NC}"
echo ""

# Run fast tests
echo "Running test suite..."
if command -v pytest &> /dev/null; then
    pytest tests/ -m "not slow and not integration and not published" -q
    echo -e "${GREEN}  ✓ Tests passed${NC}"
else
    echo -e "${YELLOW}  ⚠ pytest not installed${NC}"
    echo "    Install: pip install pytest pyyaml"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ Local Configuration Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

echo "Summary:"
echo "  • Repository: $GITHUB_OWNER/$GITHUB_REPO"
echo "  • Package: $NEW_NAME"
echo "  • CLI command: $NEW_CLI"
echo "  • Artifacts built: dist/"
echo "  • Pre-commit hooks: installed"
echo "  • Distribution configs: created"
echo ""

echo "Next steps:"
echo ""
echo "1. Review and commit changes:"
echo "   git add ."
echo "   git commit -m 'Configure repository for $GITHUB_OWNER/$GITHUB_REPO'"
echo ""
echo "2. Test your CLI:"
echo "   ./dist/provenance-demo.pyz --version"
echo "   ./dist/provenance-demo.pyz YourName"
echo ""
echo "3. Optional - Set up external services:"
echo "   • Create homebrew-tap repository: $GITHUB_OWNER/homebrew-tap"
echo "   • Configure GitHub secrets (see COMPLETE-SECURITY-CHECKLIST.md)"
echo "   • Set up PyPI account (see DEVELOPER_GUIDE.md)"
echo ""
echo "4. When ready, create first release:"
echo "   git tag v0.1.0"
echo "   git push origin v0.1.0"
echo ""
echo "See QUICK-START.md for detailed next steps."
echo ""
