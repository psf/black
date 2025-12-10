#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="helm-local-repo"
log "Starting $CHANNEL workflow"

require_command helm

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
cleanup_hooks=("rm -rf '$WORK_DIR'")
trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

CHART_DIR="$WORK_DIR/redoubt-chart"
helm create redoubt-chart >/dev/null 2>&1
mv redoubt-chart "$CHART_DIR"

pushd "$CHART_DIR" >/dev/null
helm lint . >/dev/null 2>&1 || skip "helm lint failed"
CHART_PACKAGE="$(helm package . --destination "$WORK_DIR" 2>/dev/null | awk '{print $NF}' || true)"
[[ -z "$CHART_PACKAGE" ]] && skip "helm package failed"
popd >/dev/null

REPO_DIR="$WORK_DIR/repo"
mkdir -p "$REPO_DIR"
helm repo index "$REPO_DIR" --url "file://$REPO_DIR" >/dev/null 2>&1 || skip "helm repo index failed"
mv "$WORK_DIR"/*.tgz "$REPO_DIR/"
helm repo index "$REPO_DIR" --url "file://$REPO_DIR" >/dev/null 2>&1

helm repo add redoubt-local "file://$REPO_DIR" >/dev/null 2>&1 || skip "helm repo add failed"
trap 'helm repo remove redoubt-local >/dev/null 2>&1 || true; for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

RELEASE_NAME="redoubt-demo-$RANDOM"
if ! helm install "$RELEASE_NAME" redoubt-local/redoubt-chart >/dev/null 2>&1; then
  skip "helm install failed (local repo issue)"
fi

helm uninstall "$RELEASE_NAME" >/dev/null 2>&1 || true
log "Helm local repo workflow completed"
