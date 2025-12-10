# Testing Structure - Phase 1 vs Phase 2

## Clear Distinction

### Phase 1: Host-Based Testing (macOS + Docker fallback)

**Directory:** `scripts/phase1-testing/`

**What it is:**

- Fast tests that run on your **local machine** (macOS, Linux, or Windows)
- Uses **Docker containers** as fallback for Linux-specific tools
- **Smart skipping** when tools unavailable (CI-friendly)

**Platform Coverage:**

- ✅ macOS native tools (Homebrew, etc.)
- ✅ Linux tools via Docker (APT, RPM, Snap, Flatpak)
- ✅ Cross-platform tools (Python, Go, Node, Ruby, Rust)
- ✅ Windows tools via PowerShell (if installed)

**Time:** 10-60 seconds
**Skips:** 67% (without all tools), 0-15% (with all tools)

**Use for:**

- Development iteration
- CI/CD pull request checks
- Quick validation

**Run:**

```bash
# Quick run (accepts skips)
./scripts/phase1-testing/run-all.sh

# Zero-skip run (builds artifacts, activates PATHs)
./scripts/phase1-testing/run-all-no-skips.sh
```

---

### Phase 2: Individual VM Testing (0% Skips Guaranteed)

**Directory:** `scripts/phase2-testing/`

**What it is:**

- Each distribution method tested in **its own fresh VM**
- Complete isolation - no cross-contamination
- Installs **only** what's needed per test
- **Zero skips** - everything runs in proper environment

**How it works:**

```
Test 1: apt-debian
  → Launch fresh Ubuntu 22.04 VM
  → Install Python + pip + venv
  → Test .pyz installation
  → Verify it works
  → Destroy VM

Test 2: rpm-fedora
  → Launch fresh Fedora VM
  → Install Python + dnf tools
  → Test .rpm installation
  → Verify it works
  → Destroy VM

... 12 more tests, each in its own VM
```

**Time:** 30-60 minutes
**Skips:** 0% (guaranteed)

**Use for:**

- Pre-release validation
- Certification/compliance
- Final verification before publishing

**Run:**

```bash
./scripts/phase2-testing/comprehensive-vm-tests.sh
```

---

## Comparison Table

| Aspect | Phase 1 (Host + Docker) | Phase 2 (Individual VMs) |
|--------|-------------------------|--------------------------|
| **Location** | `scripts/phase1-testing/` | `scripts/phase2-testing/` |
| **Method** | Local machine + Docker fallback | Fresh VM per test |
| **Platforms** | 18 distribution methods | 14 distribution methods |
| **Isolation** | Shared host, Docker containers | Complete (1 VM per test) |
| **Skip Rate** | 67% (no tools) / 15% (with tools) | 0% (guaranteed) |
| **Speed** | 10-60 seconds | 30-60 minutes |
| **Resources** | Low (host + Docker) | High (14 VMs) |
| **Use Case** | Development, CI/CD | Pre-release, certification |

---

## File Structure

```
scripts/
├── phase1-testing/              # Phase 1: Fast host-based tests
│   ├── run-all.sh              # Main runner (accepts skips)
│   ├── run-all-no-skips.sh     # Enhanced runner (activates PATHs)
│   ├── common.sh               # Shared utilities
│   ├── apt-local-repo.sh       # APT test (Docker)
│   ├── rpm-local-repo.sh       # RPM test (Docker)
│   ├── snap-dry-run.sh         # Snap test (Docker fallback)
│   ├── flatpak-local-repo.sh   # Flatpak test (Docker fallback)
│   ├── docker-local-registry.sh # Docker test
│   ├── homebrew-local-tap.sh   # Homebrew test
│   ├── pip-test-index.sh       # PyPI test
│   ├── npm-local-registry.sh   # npm test
│   ├── cargo-local-registry.sh # Cargo test
│   ├── go-module-replace.sh    # Go test
│   ├── rubygems-local-server.sh # Ruby test
│   ├── conda-local-channel.sh  # Conda test
│   ├── helm-local-repo.sh      # Helm test
│   ├── terraform-local-module.sh # Terraform test
│   ├── github-draft-release.sh # GitHub test
│   ├── chocolatey-local-feed.ps1 # Chocolatey (Windows)
│   └── winget-local-manifest.ps1 # Winget (Windows)
│
└── phase2-testing/              # Phase 2: Individual VM tests
    ├── comprehensive-vm-tests.sh # Master runner (0% skips)
    ├── run-all-phase2-tests.sh   # Original Phase 2 runner
    ├── setup-*.sh                # Setup scripts for private repos
    └── test-*-vm.sh              # Individual VM test scripts
```

---

## When to Use Each Phase

### During Development

```bash
# Use Phase 1 for fast feedback
./scripts/phase1-testing/run-all.sh  # 10 seconds
```

### Before Committing

```bash
# Use Phase 1 with tools installed
./scripts/install-all-distribution-tools.sh  # One-time
source ~/.cargo/env && export PATH="$HOME/miniconda/bin:$PATH"
./scripts/phase1-testing/run-all.sh  # ~60 seconds
```

### Before Releases

```bash
# Use Phase 2 for complete validation
./scripts/phase2-testing/comprehensive-vm-tests.sh  # 30-60 minutes
```

### In CI/CD

```yaml
# Pull Requests: Fast Phase 1
- run: ./scripts/phase1-testing/run-all.sh

# Releases: Thorough Phase 2
- run: ./scripts/phase2-testing/comprehensive-vm-tests.sh
  if: github.event_name == 'release'
```

---

## Key Insight: macOS as Universal Test Platform

**Your observation:**
> "By having a single VM running Ubuntu, we could test snap, flatpak and snapcraft...
> It's actually a good idea to run all those steps from macOS"

**✅ CORRECT! And we implemented it!**

### Phase 1 on macOS Now Tests

**Native:**

- Homebrew, Python, Go, Node, Ruby, Rust, Docker, Helm, Terraform, gh CLI

**Via Docker:**

- APT/Debian ✅
- RPM/Fedora ✅
- Snap ✅ (NEW!)
- Flatpak ✅ (NEW!)

**Result:** macOS can test **15/18 distribution methods** (83%)!

The 3 remaining are Windows-only (Chocolatey, Winget on native Windows - not via PowerShell emulation).

---

## Summary

### Phase 1: `scripts/phase1-testing/`

- **Purpose:** Fast iteration on local machine
- **Method:** Host-based + Docker fallback
- **Skip Rate:** 67% (no tools) → 15% (with tools)
- **Time:** 10-60 seconds

### Phase 2: `scripts/phase2-testing/`

- **Purpose:** Complete validation with zero skips
- **Method:** Individual VMs per distribution method
- **Skip Rate:** 0% (guaranteed)
- **Time:** 30-60 minutes

**Best practice: Use Phase 1 for development, Phase 2 for releases.** 🎯
