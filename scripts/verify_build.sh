#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <tag> <OWNER> <REPO> [artifact]" >&2; exit 1
fi
TAG="$1"; OWNER="$2"; REPO="$3"; ARTIFACT="${4:-client.pyz}"
BASE="https://github.com/${OWNER}/${REPO}/releases/download/${TAG}"

git fetch --tags
git checkout --quiet "$TAG"

export TZ=UTC LC_ALL=C LANG=C PYTHONHASHSEED=0
export SOURCE_DATE_EPOCH="$(git log -1 --pretty=%ct)"
umask 0022

python3 -m venv .venv
source .venv/bin/activate
./scripts/build_pyz.sh
sha256sum dist/* > local.SHA256SUMS

curl -sSLo "release.${ARTIFACT}" "${BASE}/${ARTIFACT}"
curl -sSLo release.SHA256SUMS "${BASE}/SHA256SUMS"

LOCAL_HASH="$(grep -m1 -Eo '^[0-9a-f]{64}' local.SHA256SUMS || true)"
REL_HASH="$(grep "  ${ARTIFACT}$" release.SHA256SUMS | awk '{print $1}' || true)"

if [[ -z "$LOCAL_HASH" || -z "$REL_HASH" ]]; then
  echo "Could not find comparable hashes." >&2; exit 2
fi
[[ "$LOCAL_HASH" == "$REL_HASH" ]] && echo "✅ MATCH" && exit 0
echo "❌ MISMATCH"; echo "Local: $LOCAL_HASH"; echo "Release: $REL_HASH"; exit 3
