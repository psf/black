#!/usr/bin/env bash
set -euo pipefail
: "${GPG_KEY_NAME:?Set GPG_KEY_NAME (uid) for signing}"

RPM_DIR="${1:-dist/rpm}"
PUBKEY_OUT="${2:-$RPM_DIR/RELEASE-GPG-KEY}"

# Configure rpmsign to call gpg with loopback pinentry; passphrase via env RPMSIGN_PASSPHRASE
cat > "$HOME/.rpmmacros" <<EOF
%_signature gpg
%_gpg_name $GPG_KEY_NAME
%_gpg_digest_algo sha256
%_gpg_path $HOME/.gnupg
%_gpg_sign_cmd %{__gpg} gpg --batch --no-verbose --no-armor \
  --pinentry-mode loopback --passphrase-fd 0 \
  --digest-algo sha256 --sign --detach-sign --local-user "%_gpg_name}" \
  --output %{__signature_filename} %{__plaintext_filename}
EOF

export RPMSIGN_PASSPHRASE="${GPG_PASSPHRASE:-}"

sign_one() {
  local rpm="$1"
  # Skip if already signed
  if rpm -qp --qf '%{SIGPGP:pgpsig}\n' "$rpm" 2>/dev/null | grep -q "Key ID"; then
    echo "⊙ Already signed: $rpm"
    return 0
  fi
  if [[ -n "${RPMSIGN_PASSPHRASE:-}" ]]; then
    echo "${RPMSIGN_PASSPHRASE}" | rpmsign --addsign "$rpm"
  else
    rpmsign --addsign "$rpm"
  fi
}

find "$RPM_DIR" -name "*.rpm" -print0 | while IFS= read -r -d '' f; do
  sign_one "$f"
done

gpg --export --armor "$GPG_KEY_NAME" > "$PUBKEY_OUT"
echo "✓ RPMs signed; pubkey at $PUBKEY_OUT"
