#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="apt-local-repo"
log "Starting $CHANNEL workflow"

require_command docker
ensure_docker_image "debian:stable-slim"

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

docker run --rm -v "$WORK_DIR":/work debian:stable-slim bash -eu <<'EOF'
apt-get update >/dev/null
apt-get install -y --no-install-recommends dpkg-dev >/dev/null
mkdir -p /work/pkg/DEBIAN
cat >/work/pkg/DEBIAN/control <<CTL
Package: redoubt-demo
Version: 0.0.1
Section: base
Priority: optional
Architecture: all
Maintainer: Redoubt <dist@example.com>
Description: Demo package for local apt repository
CTL

mkdir -p /work/pkg/usr/bin
cat >/work/pkg/usr/bin/redoubt-demo <<'BIN'
#!/usr/bin/env bash
echo "Redoubt apt demo"
BIN
chmod +x /work/pkg/usr/bin/redoubt-demo

dpkg-deb --build /work/pkg /work/redoubt-demo_0.0.1_all.deb >/dev/null

mkdir -p /work/repo
cp /work/redoubt-demo_0.0.1_all.deb /work/repo/
cd /work/repo
dpkg-scanpackages . /dev/null > Packages
apt-ftparchive release . > Release

echo "deb [trusted=yes] file:/work/repo ./" > /etc/apt/sources.list.d/redoubt.list
apt-get update >/dev/null
apt-get install -y redoubt-demo >/dev/null

redoubt-demo
EOF

log "APT local repository workflow completed"
