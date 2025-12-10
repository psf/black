#!/usr/bin/env bash
# Demonstration script to show VM test infrastructure working
# This is a minimal test that doesn't require actual build artifacts

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source VM utilities
source "$SCRIPT_DIR/vm-test-utils.sh"


echo "=== VM Test Infrastructure Demo ==="
echo ""
echo "This demo will:"
echo "  1. Acquire the VM test lock"
echo "  2. Run pre-flight checks"
echo "  3. Launch a minimal Ubuntu VM"
echo "  4. Run a simple test inside the VM"
echo "  5. Clean up the VM immediately"
echo "  6. Release the lock"
echo ""
echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
sleep 5

# Acquire lock to prevent concurrent VM tests
vm_lock_acquire

# Run pre-flight checks
if ! vm_preflight_check; then
  vm_lock_release
  exit 1
fi

# Create a test VM
VM_NAME="demo-vm-test-$$"

echo ""
echo "=== Launching Test VM ==="
echo "VM Name: $VM_NAME"
echo ""

# Setup cleanup trap
vm_setup_cleanup_trap "$VM_NAME"

# Launch VM with retries
if ! vm_launch_with_retry "$VM_NAME" "22.04" "1G" "5G" "1" "2"; then
    echo "ERROR: Failed to launch VM"
    vm_lock_release
    exit 1
fi

echo ""
echo "=== Running Test Commands in VM ==="
echo ""

# Run simple tests
echo "Testing basic commands..."
multipass exec "$VM_NAME" -- bash -c "
  echo '→ Checking OS version:'
  cat /etc/os-release | grep PRETTY_NAME
  echo ''
  echo '→ Checking available disk space:'
  df -h / | grep -v Filesystem
  echo ''
  echo '→ Checking memory:'
  free -h | grep Mem
  echo ''
  echo '→ Testing Python availability:'
  python3 --version
  echo ''
  echo '✓ All basic tests passed!'
"

echo ""
echo "=== Cleaning Up VM ==="
echo "The VM will be deleted immediately to free resources..."
echo ""

# VM will be cleaned up by the trap handler when script exits

echo "✓ Demo completed successfully!"
echo ""
echo "Key features demonstrated:"
echo "  ✓ Lock mechanism (prevented concurrent tests)"
echo "  ✓ Pre-flight checks (verified multipass & disk space)"
echo "  ✓ VM launch with retries"
echo "  ✓ Sequential execution (one VM at a time)"
echo "  ✓ Automatic cleanup (VM will be deleted on exit)"
