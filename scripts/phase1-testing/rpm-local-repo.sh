#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="rpm-local-repo"
log "Starting $CHANNEL workflow"

require_command docker
ensure_docker_image "fedora:40"

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
trap 'rm -rf "$WORK_DIR"' EXIT

docker run --rm -v "$WORK_DIR":/work fedora:40 bash -eu <<'EOF'
dnf install -y rpm-build createrepo_c >/dev/null

RPMBUILD=/root/rpmbuild
mkdir -p $RPMBUILD/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

cat >/root/rpmbuild/SPECS/redoubt-demo.spec <<'SPEC'
Name:           redoubt-demo
Version:        0.0.1
Release:        1%{?dist}
Summary:        Demo RPM for local repo testing

License:        MIT
URL:            https://example.com/redoubt
Source0:        redoubt-demo.sh

BuildArch:      noarch

%description
Simple demo package for local RPM repo validation.

%install
install -D -m755 %{SOURCE0} %{buildroot}%{_bindir}/redoubt-demo

%files
%{_bindir}/redoubt-demo

%changelog
* Thu Jan 01 1970 Redoubt <dist@example.com> 0.0.1-1
- initial package
SPEC

cat >/root/rpmbuild/SOURCES/redoubt-demo.sh <<'BIN'
#!/usr/bin/env bash
echo "Redoubt RPM demo"
BIN

rpmbuild -bb /root/rpmbuild/SPECS/redoubt-demo.spec >/dev/null

mkdir -p /work/repo
cp $RPMBUILD/RPMS/noarch/*.rpm /work/repo/
createrepo_c /work/repo >/dev/null

cat >/etc/yum.repos.d/redoubt.repo <<'REPO'
[redoubt-local]
name=Redoubt Local Repo
baseurl=file:///work/repo
enabled=1
gpgcheck=0
REPO

dnf install -y redoubt-demo >/dev/null
redoubt-demo
EOF

log "RPM local repository workflow completed"
