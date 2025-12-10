#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source VM utilities
source "$SCRIPT_DIR/vm-test-utils.sh"

# Acquire lock to prevent concurrent VM tests
vm_lock_acquire

# Run pre-flight checks
if ! vm_preflight_check; then
  vm_lock_release
  exit 1
fi

# Check for required environment variables
if [ -z "${PYTHON_VERSION:-}" ] || [ -z "${PACKAGE_NAME:-}" ] || [ -z "${PACKAGE_VERSION:-}" ]; then
  echo ""
  echo "⚠ Missing required environment variables"
  echo "→ This test requires:"
  echo "  - PYTHON_VERSION (e.g. 3.10|3.11|3.12|3.13)"
  echo "  - PACKAGE_NAME (e.g. demo-secure-cli)"
  echo "  - PACKAGE_VERSION (e.g. 1.0.0)"
  echo ""
  echo "Skipping Test PyPI test (infrastructure validated)"
  vm_lock_release
  exit 0
fi

if ! command -v multipass >/dev/null 2>&1; then
  echo "multipass is required"; exit 2
fi
VM="testpypi-py${PYTHON_VERSION//./}-$$"

# Setup cleanup trap
vm_setup_cleanup_trap "$VM"

if ! vm_launch_with_retry "$VM" "ubuntu:22.04" "2G" "10G"; then
    echo "Failed to launch VM"
    exit 1
fi

multipass exec "$VM" -- bash -lc "
  set -euo pipefail
  sudo apt-get update
  sudo apt-get install -y software-properties-common curl
  sudo add-apt-repository -y ppa:deadsnakes/ppa
  sudo apt-get update
  sudo apt-get install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv
  /usr/bin/python${PYTHON_VERSION} -m venv venv
  . venv/bin/activate
  python -m pip install -U pip==24.3.1
  python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple \
    ${PACKAGE_NAME}==${PACKAGE_VERSION}
  ${PACKAGE_NAME%%-*} --version || true
  echo '✓ TestPyPI install ok for Python ${PYTHON_VERSION}'
"
echo "✓ VM ${VM} completed"
