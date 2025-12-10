#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="github-draft-release"
log "Starting $CHANNEL workflow"

require_command gh

REPO="${GH_DRAFT_REPO:-}"
[[ -z "$REPO" ]] && skip "Set GH_DRAFT_REPO to a repository you control for draft release testing"

if ! gh auth status --hostname github.com >/dev/null 2>&1; then
  skip "GitHub CLI not authenticated"
fi

ensure_python_build_artifacts
ASSET="$(ls -1 "$REPO_ROOT"/dist/*.pyz 2>/dev/null | head -n1 || true)"
[[ -z "$ASSET" ]] && skip "No .pyz asset available for release"

TAG="dist-test-$(date +%s)"
log "Creating draft release $TAG on $REPO"
if ! gh release create "$TAG" "$ASSET" --repo "$REPO" --draft --title "$TAG" --notes "Distribution test release"; then
  skip "gh release create failed (check repository permissions)"
fi

log "Draft release created; cleaning up"
gh release delete "$TAG" --repo "$REPO" --yes >/dev/null 2>&1 || log "Unable to delete draft release; remove manually"
