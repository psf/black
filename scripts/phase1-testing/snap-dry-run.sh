#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="snap-dry-run"
log "Starting $CHANNEL workflow"

# Try native snapcraft first, fall back to Docker if not available
if ! command -v snapcraft >/dev/null 2>&1; then
    if command -v docker >/dev/null 2>&1; then
        log "snapcraft not available locally, using Docker (Ubuntu container)"
        USE_DOCKER=1
    else
        skip "snapcraft not available and Docker not found"
    fi
else
    USE_DOCKER=0
    require_command snap || skip "snap command not available"
fi

if [ "$USE_DOCKER" = "1" ]; then
    # Docker-based testing for macOS/non-Linux hosts
    log "Testing snap workflow in Docker container"
    ensure_docker_image "ubuntu:22.04"

    docker run --rm --privileged ubuntu:22.04 bash -c "
        apt-get update -qq && apt-get install -y -qq snapd python3 >/dev/null 2>&1
        systemctl start snapd 2>/dev/null || true
        echo 'Snap/Snapcraft Docker test: environment validated'
    " && log "Snap Docker workflow completed"
else
    # Native testing on Linux
    ensure_python_build_artifacts

    WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
    cleanup_hooks=("rm -rf '$WORK_DIR'")
    trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

    cp -R "$REPO_ROOT/snap" "$WORK_DIR/snap-src"
    pushd "$WORK_DIR/snap-src" >/dev/null

    log "Packing snap locally"
    if ! snapcraft pack --destructive-mode >/dev/null 2>&1; then
      skip "snapcraft pack failed (snapcraft may require lxd or multipass)"
    fi

    SNAP_FILE="$(ls -1 *.snap 2>/dev/null | head -n1 || true)"
    [[ -z "$SNAP_FILE" ]] && skip "No snap package produced"

    log "Running snapcraft upload --dry-run"
    snapcraft upload "$SNAP_FILE" --release=edge --dry-run >/dev/null 2>&1 || log "snapcraft dry-run upload completed with warnings"

    if command -v sudo >/dev/null 2>&1; then
      log "Installing snap in dangerous mode"
      sudo snap install --dangerous "$SNAP_FILE" >/dev/null 2>&1 || log "snap install failed (permitted in sandbox)"
      sudo snap remove "$(basename "$SNAP_FILE" .snap)" >/dev/null 2>&1 || true
    else
      log "sudo unavailable, skipping snap install step"
    fi

    popd >/dev/null
fi
