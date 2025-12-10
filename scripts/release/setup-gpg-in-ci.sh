#!/usr/bin/env bash
set -euo pipefail

: "${GPG_PRIVATE_KEY:?Base64-encoded armored private key required}"
: "${GPG_KEY_NAME:?User ID (uid) of the key required}"
GNUPGHOME="${GNUPGHOME:-$HOME/.gnupg}"; export GNUPGHOME
mkdir -p "$GNUPGHOME"; chmod 700 "$GNUPGHOME"

# Import private key
echo "$GPG_PRIVATE_KEY" | base64 -d | gpg --batch --yes --import

# Force loopback pinentry (works on Actions/CI, headless)
echo "pinentry-mode loopback" > "$GNUPGHOME/gpg.conf"
echo "allow-loopback-pinentry" > "$GNUPGHOME/gpg-agent.conf"
gpgconf --kill gpg-agent || true

# Optional: list keys for debugging (non-secret)
gpg --list-keys "$GPG_KEY_NAME" || { echo "Key not found"; exit 1; }

echo "✓ GPG CI setup complete (loopback pinentry enabled)"
