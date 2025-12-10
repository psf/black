#!/usr/bin/env bash
#
# Generate GPG signing key for package repositories (APT, RPM)
# This script should be run ONCE offline/locally, then the key exported for CI use
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${BLUE}  GPG Key Generation for Package Signing${NC}"
echo -e "${BOLD}${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Check if GPG is installed
if ! command -v gpg &> /dev/null; then
    echo -e "${RED}✗ GPG is not installed${NC}"
    echo ""
    echo "Install GPG:"
    echo "  macOS:  brew install gnupg"
    echo "  Ubuntu: apt-get install gnupg"
    exit 1
fi

echo -e "${GREEN}✓ GPG is installed: $(gpg --version | head -n1)${NC}"
echo ""

# Get repository information
OWNER="${OWNER:-OWNER}"
REPO="${REPO:-REPO}"
PACKAGE_NAME="${PACKAGE_NAME:-redoubt}"

# Prompt for key information
echo -e "${BOLD}Key Configuration:${NC}"
echo ""
read -p "Package name (default: $PACKAGE_NAME): " INPUT_PACKAGE
PACKAGE_NAME="${INPUT_PACKAGE:-$PACKAGE_NAME}"

read -p "Your name (default: Release Manager): " INPUT_NAME
KEY_NAME="${INPUT_NAME:-Release Manager}"

read -p "Your email (default: noreply@example.com): " INPUT_EMAIL
KEY_EMAIL="${INPUT_EMAIL:-noreply@example.com}"

read -p "Key validity (default: 2y): " INPUT_EXPIRY
KEY_EXPIRY="${INPUT_EXPIRY:-2y}"

read -s -p "Passphrase (leave empty for no passphrase - NOT RECOMMENDED): " INPUT_PASSPHRASE
echo ""
if [ -z "$INPUT_PASSPHRASE" ]; then
    echo -e "${YELLOW}⚠ Warning: Generating key without passphrase${NC}"
    read -p "Are you sure? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        echo "Aborted."
        exit 1
    fi
    USE_PASSPHRASE=false
else
    USE_PASSPHRASE=true
fi

echo ""
echo -e "${BOLD}Generating GPG key with:${NC}"
echo "  Name:     $KEY_NAME ($PACKAGE_NAME Release Key)"
echo "  Email:    $KEY_EMAIL"
echo "  Validity: $KEY_EXPIRY"
echo "  Passphrase: $([ "$USE_PASSPHRASE" = true ] && echo 'Yes' || echo 'No (insecure)')"
echo ""

# Create GPG key generation config
KEY_CONFIG_FILE="$(mktemp)"
trap "rm -f $KEY_CONFIG_FILE" EXIT

if [ "$USE_PASSPHRASE" = true ]; then
    cat > "$KEY_CONFIG_FILE" <<EOF
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $KEY_NAME
Name-Comment: $PACKAGE_NAME Release Key
Name-Email: $KEY_EMAIL
Expire-Date: $KEY_EXPIRY
Passphrase: $INPUT_PASSPHRASE
%commit
%echo GPG key generated successfully
EOF
else
    cat > "$KEY_CONFIG_FILE" <<EOF
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: $KEY_NAME
Name-Comment: $PACKAGE_NAME Release Key
Name-Email: $KEY_EMAIL
Expire-Date: $KEY_EXPIRY
%no-protection
%commit
%echo GPG key generated successfully
EOF
fi

echo -e "${BLUE}→ Generating GPG key (this may take a minute)...${NC}"
gpg --batch --generate-key "$KEY_CONFIG_FILE" 2>&1 | grep -v "^gpg:"

echo -e "${GREEN}✓ GPG key generated${NC}"
echo ""

# Get the key ID
KEY_ID_FULL="$KEY_NAME ($PACKAGE_NAME Release Key) <$KEY_EMAIL>"
KEY_ID=$(gpg --list-keys "$KEY_ID_FULL" | grep -A 1 "^pub" | tail -n 1 | awk '{print $1}')

echo -e "${BOLD}Key Information:${NC}"
gpg --list-keys "$KEY_ID_FULL"
echo ""

# Create output directory
OUTPUT_DIR="$REPO_ROOT/gpg-keys"
mkdir -p "$OUTPUT_DIR"

# Export public key
PUBLIC_KEY_FILE="$OUTPUT_DIR/release-public-key.asc"
gpg --armor --export "$KEY_ID_FULL" > "$PUBLIC_KEY_FILE"
echo -e "${GREEN}✓ Public key exported: $PUBLIC_KEY_FILE${NC}"

# Export private key (for CI/CD)
PRIVATE_KEY_FILE="$OUTPUT_DIR/release-private-key.asc"
if [ "$USE_PASSPHRASE" = true ]; then
    echo "$INPUT_PASSPHRASE" | gpg --batch --yes --passphrase-fd 0 --pinentry-mode loopback \
        --armor --export-secret-keys "$KEY_ID_FULL" > "$PRIVATE_KEY_FILE"
else
    gpg --batch --yes --armor --export-secret-keys "$KEY_ID_FULL" > "$PRIVATE_KEY_FILE"
fi
echo -e "${GREEN}✓ Private key exported: $PRIVATE_KEY_FILE${NC}"

# Export private key as base64 (for GitHub Secrets)
PRIVATE_KEY_B64_FILE="$OUTPUT_DIR/release-private-key.b64"
base64 < "$PRIVATE_KEY_FILE" > "$PRIVATE_KEY_B64_FILE"
echo -e "${GREEN}✓ Private key (base64) exported: $PRIVATE_KEY_B64_FILE${NC}"

# Create fingerprint file
FINGERPRINT=$(gpg --fingerprint "$KEY_ID_FULL" | grep -A 1 "Key fingerprint" | tail -n 1 | tr -d ' ')
echo "$FINGERPRINT" > "$OUTPUT_DIR/key-fingerprint.txt"
echo -e "${GREEN}✓ Key fingerprint saved: $OUTPUT_DIR/key-fingerprint.txt${NC}"

echo ""
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BOLD}${GREEN}  GPG Key Generated Successfully!${NC}"
echo -e "${BOLD}${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

echo -e "${BOLD}Next Steps:${NC}"
echo ""
echo -e "${BOLD}1. Add GitHub Secrets for CI/CD:${NC}"
echo ""
echo "   Go to: https://github.com/$OWNER/$REPO/settings/secrets/actions"
echo ""
echo "   Add these secrets:"
echo -e "   ${YELLOW}GPG_PRIVATE_KEY${NC}  = $(cat "$PRIVATE_KEY_B64_FILE")"
if [ "$USE_PASSPHRASE" = true ]; then
    echo -e "   ${YELLOW}GPG_PASSPHRASE${NC}  = $INPUT_PASSPHRASE"
fi
echo -e "   ${YELLOW}GPG_KEY_NAME${NC}    = $KEY_ID_FULL"
echo ""

echo -e "${BOLD}2. Publish Public Key:${NC}"
echo ""
echo "   The public key needs to be accessible to users for package verification:"
echo ""
echo "   For APT repository:"
echo "     - Copy $PUBLIC_KEY_FILE to your apt-repo/keys/ directory"
echo "     - Users will run:"
echo "       curl -fsSL https://YOUR_DOMAIN/apt-repo/keys/release-public-key.asc | sudo apt-key add -"
echo ""
echo "   For RPM repository:"
echo "     - Copy $PUBLIC_KEY_FILE to your rpm-repo/ directory"
echo "     - Users will run:"
echo "       sudo rpm --import https://YOUR_DOMAIN/rpm-repo/release-public-key.asc"
echo ""

echo -e "${BOLD}3. Security:${NC}"
echo ""
echo -e "   ${RED}⚠ IMPORTANT:${NC} Keep these files secure:"
echo "     - $PRIVATE_KEY_FILE"
echo "     - $PRIVATE_KEY_B64_FILE"
if [ "$USE_PASSPHRASE" = true ]; then
    echo "     - The passphrase you entered"
fi
echo ""
echo "   These files are in .gitignore and should NEVER be committed to git."
echo "   Store them in a secure location (password manager, encrypted vault, etc.)"
echo ""

echo -e "${BOLD}4. Test Signing:${NC}"
echo ""
echo "   Set environment variables:"
echo "     export GPG_KEY_NAME='$KEY_ID_FULL'"
if [ "$USE_PASSPHRASE" = true ]; then
    echo "     export GPG_PASSPHRASE='$INPUT_PASSPHRASE'"
fi
echo ""
echo "   Test APT signing:"
echo "     ./scripts/release/sign-apt-repo.sh dist/deb-repo"
echo ""
echo "   Test RPM signing:"
echo "     ./scripts/release/sign-rpm.sh dist/rpm"
echo ""

echo -e "${BOLD}5. Key Rotation (in $KEY_EXPIRY):${NC}"
echo ""
echo "   Before key expiry:"
echo "     - Generate new key with this script"
echo "     - Publish both old and new public keys"
echo "     - Sign repos with both keys for one release cycle"
echo "     - Remove old key after deprecation window"
echo ""

echo -e "${GREEN}✓ Setup complete!${NC}"
