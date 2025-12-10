#!/usr/bin/env bash
set -euo pipefail
: "${GPG_KEY_NAME:?Set GPG_KEY_NAME (uid) for signing}"

REPO_DIR="${1:-dist/deb-repo}"
cd "$REPO_DIR"

# Expect ./dists/.../Release already built
export GPG_TTY="$(tty || true)"

if [[ -n "${GPG_PASSPHRASE:-}" ]]; then
  # InRelease
  echo "$GPG_PASSPHRASE" | gpg --batch --yes --passphrase-fd 0 --pinentry-mode loopback \
    --local-user "$GPG_KEY_NAME" --clearsign -o InRelease Release
  # Release.gpg
  echo "$GPG_PASSPHRASE" | gpg --batch --yes --passphrase-fd 0 --pinentry-mode loopback \
    --local-user "$GPG_KEY_NAME" --detach-sign -o Release.gpg Release
else
  gpg --batch --yes --local-user "$GPG_KEY_NAME" --clearsign -o InRelease Release
  gpg --batch --yes --local-user "$GPG_KEY_NAME" --detach-sign -o Release.gpg Release
fi

mkdir -p keys
gpg --export --armor "$GPG_KEY_NAME" > keys/release.pub.asc
echo "✓ APT repo signed; pubkey at $REPO_DIR/keys/release.pub.asc"
