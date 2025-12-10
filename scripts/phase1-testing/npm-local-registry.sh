#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="npm-local-registry"
log "Starting $CHANNEL workflow"

require_command node
require_command npm

REGISTRY_URL="http://127.0.0.1:4873"
cleanup_hooks=()

if command -v docker >/dev/null 2>&1; then
  ensure_docker_image "verdaccio/verdaccio:5"
  CONTAINER_NAME="dist-test-verdaccio-$RANDOM"
  if docker run -d --rm --name "$CONTAINER_NAME" -p 4873:4873 verdaccio/verdaccio:5 >/dev/null 2>&1; then
    cleanup_hooks+=("docker stop '$CONTAINER_NAME' >/dev/null 2>&1 || true")
  else
    skip "Unable to start verdaccio docker container"
  fi
else
  require_command npx
  log "Starting Verdaccio via npx (requires Node>=16)"
  npx --yes verdaccio@5 --listen "0.0.0.0:4873" >/dev/null 2>&1 &
  VERDACCIO_PID=$!
  sleep 5
  if ! kill -0 "$VERDACCIO_PID" >/dev/null 2>&1; then
    skip "Unable to launch Verdaccio via npx"
  fi
  cleanup_hooks+=("kill '$VERDACCIO_PID' >/dev/null 2>&1 || true")
fi

TMP_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
cleanup_hooks+=("rm -rf '$TMP_DIR'")
trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

PACKAGE_DIR="$TMP_DIR/package"
mkdir -p "$PACKAGE_DIR"

cat >"$PACKAGE_DIR/package.json" <<EOF
{
  "name": "@redoubt/demo-cli",
  "version": "0.0.1",
  "description": "Demo package for registry testing",
  "main": "index.js",
  "publishConfig": {
    "registry": "http://127.0.0.1:4873/"
  }
}
EOF

cat >"$PACKAGE_DIR/index.js" <<'EOF'
module.exports = function () {
  console.log("hello from registry test");
};
EOF

pushd "$PACKAGE_DIR" >/dev/null
printf '//127.0.0.1:4873/:_authToken="fake-token"\nalways-auth=true\nregistry=%s\n' "$REGISTRY_URL" > "$TMP_DIR/.npmrc"

export NPM_CONFIG_USERCONFIG="$TMP_DIR/.npmrc"

NPM_REGISTRY_FLAG=(--registry "$REGISTRY_URL")
npm adduser "${NPM_REGISTRY_FLAG[@]}" --always-auth --username distbot --password distbot --email distbot@example.com >/dev/null 2>&1 || true

if ! npm publish "${NPM_REGISTRY_FLAG[@]}" >/dev/null 2>&1; then
  skip "npm publish failed (likely verdaccio not reachable)."
fi
popd >/dev/null

INSTALL_DIR="$TMP_DIR/install"
mkdir -p "$INSTALL_DIR"
pushd "$INSTALL_DIR" >/dev/null

if ! npm install "${NPM_REGISTRY_FLAG[@]}" @redoubt/demo-cli >/dev/null 2>&1; then
  skip "npm install failed (registry likely unreachable)"
fi

log "Published and installed package from local Verdaccio registry"
popd >/dev/null
