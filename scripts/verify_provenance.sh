#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <tag> <OWNER> <REPO> [artifact]" >&2; exit 1
fi
TAG="$1"; OWNER="$2"; REPO="$3"; ARTIFACT="${4:-client.pyz}"
BASE="https://github.com/${OWNER}/${REPO}/releases/download/${TAG}"
command -v gh >/dev/null || { echo "Install GitHub CLI"; exit 2; }

tmpfile="$(mktemp)"; trap 'rm -f "$tmpfile"' EXIT
curl -sSLo "$tmpfile" "${BASE}/${ARTIFACT}"
gh attestation verify "$tmpfile" --repo "${OWNER}/${REPO}"

if command -v cosign >/dev/null; then
  curl -sSLo SHA256SUMS "${BASE}/SHA256SUMS"
  curl -sSLo SHA256SUMS.bundle "${BASE}/SHA256SUMS.bundle"
  COSIGN_EXPERIMENTAL=1 cosign verify-blob \
    --bundle SHA256SUMS.bundle \
    --certificate-oidc-issuer https://token.actions.githubusercontent.com \
    --certificate-identity "https://github.com/${OWNER}/${REPO}/.github/workflows/Secure Release@refs/tags/${TAG}" \
    SHA256SUMS
  echo "✅ cosign bundle verified"
else
  echo "cosign not found; skipped cosign verification"
fi
echo "✅ provenance verified"
