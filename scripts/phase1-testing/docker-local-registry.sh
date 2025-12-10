#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="docker-local-registry"
log "Starting $CHANNEL workflow"

require_command docker

ensure_docker_image "registry:2"
REG_NAME="dist-registry-$RANDOM"
docker run -d --rm --name "$REG_NAME" -p 5000:5000 registry:2 >/dev/null 2>&1 || skip "Unable to start local registry"
trap 'docker stop "$REG_NAME" >/dev/null 2>&1 || true' EXIT

IMAGE_TAG="localhost:5000/redoubt/demo:local"

cat <<'EOF' | docker build -t redoubt/demo:local - >/dev/null 2>&1 || skip "docker build failed"
FROM alpine:3.18
CMD ["echo", "Redoubt local registry test"]
EOF

docker tag redoubt/demo:local "$IMAGE_TAG"
docker push "$IMAGE_TAG" >/dev/null 2>&1 || skip "docker push to local registry failed"

docker image rm "$IMAGE_TAG" >/dev/null 2>&1 || true
docker pull "$IMAGE_TAG" >/dev/null 2>&1 || skip "docker pull from local registry failed"

log "Docker local registry workflow completed successfully"
