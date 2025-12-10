# VM-Based Testing Infrastructure

This directory contains VM-based integration tests for Phase 2 distribution testing. The infrastructure ensures that VMs run **sequentially** (one at a time) and are **cleaned up immediately** after each test to free up disk space and resources.

## Key Features

### Sequential Execution
- **Lock mechanism** prevents multiple VM tests from running concurrently
- Only one VM test can acquire the lock at a time
- Other tests wait in queue (with timeout)
- Prevents resource exhaustion and conflicts

### Automatic Cleanup
- VMs are **deleted immediately** after each test completes
- `multipass purge` is run to free disk space
- No lingering VMs consuming resources
- Pre-flight checks remove any orphaned VMs

### Robust Error Handling
- VM launch retries (up to 3 attempts by default)
- Automatic cleanup on script exit (trap handlers)
- Clear error messages with suggestions
- Fail-fast on critical errors

## Architecture

### Core Components

1. **[vm-test-utils.sh](vm-test-utils.sh)** - Shared utilities library
   - Lock acquisition and release
   - VM lifecycle management (launch, cleanup)
   - Pre-flight checks
   - Retry logic

2. **[cleanup-vms.sh](cleanup-vms.sh)** - Standalone cleanup utility
   - Manual VM cleanup
   - Can be run independently
   - Supports `--all`, `--force`, `--list-only` flags

3. **Individual test scripts** - Updated to use utilities
   - [test-appimage-vm.sh](test-appimage-vm.sh)
   - [test-aur-vm.sh](test-aur-vm.sh)
   - [test-apt-repo-vm.sh](test-apt-repo-vm.sh)
   - [test-rpm-repo-vm.sh](test-rpm-repo-vm.sh)
   - etc.

4. **[comprehensive-vm-tests.sh](comprehensive-vm-tests.sh)** - Run all tests
   - Tests multiple distributions
   - Acquires global lock
   - Cleans up each VM immediately after testing

5. **[run-all-phase2-tests.sh](run-all-phase2-tests.sh)** - Master runner
   - Runs platform-specific tests
   - Sequential execution guaranteed by locks in individual scripts

## Usage

### Running Individual Tests

```bash
# Test AppImage on multiple distros
./scripts/phase2-testing/test-appimage-vm.sh

# Test AUR package build
./scripts/phase2-testing/test-aur-vm.sh

# Test APT repository
./scripts/phase2-testing/test-apt-repo-vm.sh
```

Each script will:
1. Acquire the VM test lock (wait if another test is running)
2. Run pre-flight checks
3. Launch a fresh VM
4. Run the test
5. Clean up the VM immediately
6. Release the lock

### Running Comprehensive Tests

```bash
# Run all VM-based distribution tests
./scripts/phase2-testing/comprehensive-vm-tests.sh
```

This will test all distribution methods sequentially, cleaning up after each one.

### Running Platform Tests

```bash
# Run specific platforms
./scripts/phase2-testing/run-all-phase2-tests.sh homebrew pypi

# Run all platforms
./scripts/phase2-testing/run-all-phase2-tests.sh --all

# Run with setup
./scripts/phase2-testing/run-all-phase2-tests.sh --setup apt rpm
```

### Manual Cleanup

If VMs get orphaned (e.g., script killed):

```bash
# List orphaned test VMs
./scripts/phase2-testing/cleanup-vms.sh --list-only

# Clean up test VMs (with confirmation)
./scripts/phase2-testing/cleanup-vms.sh

# Force cleanup without confirmation
./scripts/phase2-testing/cleanup-vms.sh --force

# Clean up ALL VMs (dangerous!)
./scripts/phase2-testing/cleanup-vms.sh --all --force
```

## Lock Mechanism

### How It Works

1. **Lock directory**: `/tmp/redoubt-vm-tests.lock.d`
2. **Mechanism**: Atomic directory creation (works on Linux and macOS)
3. **Timeout**: 300 seconds (5 minutes) by default
4. **Stale lock detection**: Automatically removes locks older than 1 hour or from dead processes
5. **Behavior**:
   - First test acquires lock immediately by creating directory
   - Subsequent tests wait for lock directory to be removed
   - If timeout expires, test fails with helpful message
   - Lock is cross-platform compatible (no `flock` required)

### Checking Lock Status

```bash
# Check if lock directory exists
ls -la /tmp/redoubt-vm-tests.lock.d

# See which process holds the lock
cat /tmp/redoubt-vm-tests.lock.d/pid  # Shows PID

# Check if that process is running
ps aux | grep <PID>

# Check lock age
stat -f %m /tmp/redoubt-vm-tests.lock.d  # macOS
stat -c %Y /tmp/redoubt-vm-tests.lock.d  # Linux
```

### Manually Releasing Lock

If a test crashes and doesn't release the lock:

```bash
# Remove lock directory
rm -rf /tmp/redoubt-vm-tests.lock.d

# Note: Stale locks are automatically detected and removed
# If lock is older than 1 hour or process is dead, it will be auto-removed
```

## Pre-flight Checks

Before each test run, the system performs these checks:

1. ✓ **Multipass installed** - Checks if `multipass` command exists
2. ✓ **Multipass running** - Verifies multipass daemon is active
3. ✓ **No lingering VMs** - Removes any orphaned test VMs
4. ✓ **Sufficient disk space** - Warns if less than 10GB free

If any check fails, the test aborts with a clear error message.

## Resource Management

### Disk Space

Each VM typically uses:
- **Base image**: ~500MB - 1GB (cached)
- **VM disk**: 10GB allocated (thin provisioned)
- **Actual usage**: 2-5GB per VM

The infrastructure ensures:
- VMs are deleted immediately after use
- `multipass purge` frees up space
- Pre-flight checks warn about low disk space

### Memory

Default VM allocation:
- **Memory**: 2GB per VM
- **CPUs**: 2 cores

Only **one VM runs at a time**, so peak memory usage is consistent.

### Best Practices

1. **Run tests sequentially** - Don't try to parallelize VM tests
2. **Monitor disk space** - Keep at least 20GB free
3. **Clean up regularly** - Run `cleanup-vms.sh` periodically
4. **Check for orphaned VMs** - If tests fail, verify no VMs are lingering

## Troubleshooting

### Problem: "Failed to acquire VM test lock"

**Cause**: Another VM test is running or a previous test didn't release the lock

**Solution**:
```bash
# Check for running VM tests
ps aux | grep "test.*vm.sh"

# If no tests running, remove lock manually
rm /tmp/redoubt-vm-tests.lock
```

### Problem: "Low disk space" warning

**Cause**: Less than 10GB disk space available

**Solution**:
```bash
# Clean up test VMs
./scripts/phase2-testing/cleanup-vms.sh --force

# Purge multipass images
multipass purge

# Check disk space
df -h /
```

### Problem: VM launch keeps failing

**Cause**: Network issues, multipass daemon problems, or resource constraints

**Solution**:
```bash
# Check multipass status
multipass version

# Restart multipass daemon (macOS)
sudo launchctl stop com.canonical.multipassd
sudo launchctl start com.canonical.multipassd

# Check available images
multipass find

# Check system resources
top
df -h
```

### Problem: Tests timing out

**Cause**: VM operations taking longer than expected

**Solution**:
- Increase timeout in lock acquisition (edit `vm-test-utils.sh`)
- Check network connectivity
- Verify multipass isn't rate-limited

### Problem: Orphaned VMs consuming resources

**Cause**: Test script killed before cleanup could run

**Solution**:
```bash
# List all VMs
multipass list

# Clean up all test VMs
./scripts/phase2-testing/cleanup-vms.sh --force

# Or manually
multipass delete <vm-name>
multipass purge
```

## CI/CD Integration

### GitHub Actions

The VM test infrastructure can be used in CI, but note:

- GitHub-hosted runners **don't support nested virtualization**
- You need **self-hosted runners** with multipass installed
- Or use **Docker-based tests** instead (see [integration-tests.yml](../../.github/workflows/integration-tests.yml))

### Self-Hosted Runners

To use VM tests in CI:

1. Set up self-hosted runner with multipass
2. Ensure sufficient disk space (100GB+ recommended)
3. Add cleanup as a post-run step
4. Monitor for orphaned VMs

Example workflow:

```yaml
jobs:
  vm-tests:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4

      - name: Clean up any orphaned VMs
        run: ./scripts/phase2-testing/cleanup-vms.sh --force

      - name: Run VM tests
        run: ./scripts/phase2-testing/comprehensive-vm-tests.sh

      - name: Cleanup after tests
        if: always()
        run: ./scripts/phase2-testing/cleanup-vms.sh --force
```

## Advanced Usage

### Custom Lock Timeout

```bash
# Set custom timeout (in seconds)
VM_LOCK_TIMEOUT=600 ./scripts/phase2-testing/test-appimage-vm.sh
```

### Custom Lock File Location

```bash
# Use different lock file
VM_LOCK_FILE=/tmp/my-custom-lock.lock ./scripts/phase2-testing/test-aur-vm.sh
```

### Adjusting VM Resources

Edit the script or utility functions to change VM specs:

```bash
# In vm-test-utils.sh or individual scripts
vm_launch_with_retry "$NAME" "$IMAGE" "4G" "20G" "4"  # 4GB RAM, 20GB disk, 4 CPUs
```

## Development

### Adding New VM Tests

When creating a new VM test script:

1. Source the utilities:
   ```bash
   source "$SCRIPT_DIR/vm-test-utils.sh"
   ```

2. Initialize lock:
   ```bash
   vm_lock_init
   vm_lock_acquire
   ```

3. Run pre-flight checks:
   ```bash
   if ! vm_preflight_check; then
       vm_lock_release
       exit 1
   fi
   ```

4. Setup cleanup trap:
   ```bash
   vm_setup_cleanup_trap "$VM_NAME"
   ```

5. Launch VM with retry:
   ```bash
   vm_launch_with_retry "$VM_NAME" "$IMAGE" "2G" "10G"
   ```

6. Run your tests...

7. The trap handler will automatically clean up on exit

### Testing the Infrastructure

```bash
# Test lock mechanism (run in two terminals)
# Terminal 1:
./scripts/phase2-testing/test-appimage-vm.sh

# Terminal 2 (while first is running):
./scripts/phase2-testing/test-aur-vm.sh
# Should see "Waiting for other VM tests to complete..."
```

## Summary

The VM testing infrastructure provides:

✅ **Sequential execution** - One VM at a time via lock mechanism
✅ **Immediate cleanup** - VMs deleted right after tests
✅ **Resource efficiency** - No lingering VMs consuming disk/memory
✅ **Robust error handling** - Retries and cleanup on failure
✅ **Pre-flight checks** - Catch issues before tests run
✅ **Easy cleanup** - Standalone utility for manual cleanup

This ensures reliable, reproducible VM-based testing without resource exhaustion.
