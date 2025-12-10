#!/usr/bin/env bash
set -euo pipefail

KEY_NAME="${1:-Release Key (Redoubt Test)}"
KEY_DIR="${2:-$HOME/.gnupg-redoubt-test}"

if [[ -d "$KEY_DIR" ]]; then
  echo "Test keyring already exists at $KEY_DIR"; exit 0
fi

export GNUPGHOME="$KEY_DIR"
mkdir -p "$GNUPGHOME"; chmod 700 "$GNUPGHOME"

cat > "$GNUPGHOME/gen-key-config" <<EOF
Key-Type: RSA
Key-Length: 4096
Name-Real: $KEY_NAME
Name-Email: noreply@example.com
Expire-Date: 1y
%no-protection
%commit
EOF

gpg --batch --generate-key "$GNUPGHOME/gen-key-config"
rm -f "$GNUPGHOME/gen-key-config"

echo "✓ Test GPG key generated in $KEY_DIR"
echo "Export priv: gpg --export-secret-keys --armor > test-key.asc"
echo "Use keyring: export GNUPGHOME=$KEY_DIR"
