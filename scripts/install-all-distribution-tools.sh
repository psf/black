#!/usr/bin/env bash
# Auto-install ALL distribution testing prerequisites
# This eliminates skipped tests in Phase 1 by installing everything locally

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BOLD}${BLUE}║     Distribution Testing Tools - Auto Installer                   ║${NC}"
echo -e "${BOLD}${BLUE}║     Installs ALL prerequisites for Phase 1 testing                ║${NC}"
echo -e "${BOLD}${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Darwin*)    PLATFORM="macos";;
    Linux*)     PLATFORM="linux";;
    CYGWIN*|MINGW*|MSYS*) PLATFORM="windows";;
    *)          PLATFORM="unknown";;
esac

echo -e "\n${BLUE}Detected platform: ${BOLD}$PLATFORM${NC}\n"

# Check for package manager
if [ "$PLATFORM" = "macos" ]; then
    if ! command -v brew >/dev/null 2>&1; then
        echo -e "${RED}Error: Homebrew not found. Install from https://brew.sh${NC}"
        exit 1
    fi
    PKG_MGR="brew install"
elif [ "$PLATFORM" = "linux" ]; then
    if command -v apt-get >/dev/null 2>&1; then
        PKG_MGR="sudo apt-get install -y"
    elif command -v dnf >/dev/null 2>&1; then
        PKG_MGR="sudo dnf install -y"
    elif command -v yum >/dev/null 2>&1; then
        PKG_MGR="sudo yum install -y"
    else
        echo -e "${RED}Error: No supported package manager found${NC}"
        exit 1
    fi
else
    echo -e "${RED}Error: Unsupported platform${NC}"
    exit 1
fi

# Install function
install_tool() {
    local tool=$1
    local install_cmd=$2

    echo -e "${YELLOW}→ Installing $tool...${NC}"
    if command -v "$tool" >/dev/null 2>&1; then
        echo -e "${GREEN}  ✓ $tool already installed${NC}"
        return 0
    fi

    if eval "$install_cmd"; then
        echo -e "${GREEN}  ✓ $tool installed successfully${NC}"
    else
        echo -e "${RED}  ✗ Failed to install $tool${NC}"
    fi
}

# ═══════════════════════════════════════════════════════════════════
# Core Tools
# ═══════════════════════════════════════════════════════════════════
echo -e "${BOLD}Installing Core Tools...${NC}"

if [ "$PLATFORM" = "macos" ]; then
    install_tool "python3" "brew install python3"
    install_tool "docker" "brew install --cask docker"
    install_tool "git" "brew install git"
fi

# ═══════════════════════════════════════════════════════════════════
# Language Package Managers
# ═══════════════════════════════════════════════════════════════════
echo -e "\n${BOLD}Installing Language Package Managers...${NC}"

# Cargo (Rust)
if ! command -v cargo >/dev/null 2>&1; then
    # Check if cargo directory already exists
    if [ -d "$HOME/.cargo" ]; then
        echo -e "${GREEN}  ✓ Cargo already installed (found $HOME/.cargo)${NC}"
        echo -e "${YELLOW}    Add to PATH: source \$HOME/.cargo/env${NC}"
    else
        echo -e "${YELLOW}→ Installing Cargo (Rust)...${NC}"
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source "$HOME/.cargo/env" 2>/dev/null || true
        echo -e "${GREEN}  ✓ Cargo installed successfully${NC}"
    fi
else
    echo -e "${GREEN}  ✓ cargo already available in PATH${NC}"
fi

# Go
if [ "$PLATFORM" = "macos" ]; then
    install_tool "go" "brew install go"
elif [ "$PLATFORM" = "linux" ]; then
    if ! command -v go >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing Go...${NC}"
        wget https://go.dev/dl/go1.21.5.linux-amd64.tar.gz -O /tmp/go.tar.gz
        sudo rm -rf /usr/local/go
        sudo tar -C /usr/local -xzf /tmp/go.tar.gz
        echo 'export PATH=$PATH:/usr/local/go/bin' >> "$HOME/.profile"
    fi
fi

# Node.js / npm
if [ "$PLATFORM" = "macos" ]; then
    install_tool "node" "brew install node"
elif [ "$PLATFORM" = "linux" ]; then
    if ! command -v node >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing Node.js...${NC}"
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        $PKG_MGR nodejs
    fi
fi

# Ruby
if [ "$PLATFORM" = "macos" ]; then
    install_tool "ruby" "brew install ruby"
elif [ "$PLATFORM" = "linux" ]; then
    $PKG_MGR ruby ruby-dev
fi

# ═══════════════════════════════════════════════════════════════════
# System Package Managers
# ═══════════════════════════════════════════════════════════════════
echo -e "\n${BOLD}Installing System Package Managers...${NC}"

if [ "$PLATFORM" = "macos" ]; then
    # Homebrew already installed (checked above)
    echo -e "${GREEN}  ✓ Homebrew already available${NC}"
fi

# Conda
if ! command -v conda >/dev/null 2>&1; then
    # Check if miniconda directory already exists
    if [ -d "$HOME/miniconda" ]; then
        echo -e "${GREEN}  ✓ Conda already installed (found $HOME/miniconda)${NC}"
        echo -e "${YELLOW}    Add to PATH: export PATH=\"\$HOME/miniconda/bin:\$PATH\"${NC}"
    else
        echo -e "${YELLOW}→ Installing Conda (Miniconda)...${NC}"
        if [ "$PLATFORM" = "macos" ]; then
            curl -o /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
        else
            curl -o /tmp/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
        fi
        bash /tmp/miniconda.sh -b -p "$HOME/miniconda"
        echo 'export PATH="$HOME/miniconda/bin:$PATH"' >> "$HOME/.profile"
        echo -e "${GREEN}  ✓ Conda installed successfully${NC}"
    fi
else
    echo -e "${GREEN}  ✓ conda already available in PATH${NC}"
fi

# Snap (Linux only)
if [ "$PLATFORM" = "linux" ]; then
    if ! command -v snap >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing Snapd...${NC}"
        $PKG_MGR snapd
        sudo systemctl enable --now snapd.socket
    fi
fi

# Flatpak (Linux only)
if [ "$PLATFORM" = "linux" ]; then
    if ! command -v flatpak >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing Flatpak...${NC}"
        $PKG_MGR flatpak
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# Cloud/Infrastructure Tools
# ═══════════════════════════════════════════════════════════════════
echo -e "\n${BOLD}Installing Cloud/Infrastructure Tools...${NC}"

if [ "$PLATFORM" = "macos" ]; then
    install_tool "helm" "brew install helm"
    install_tool "terraform" "brew install terraform"
elif [ "$PLATFORM" = "linux" ]; then
    # Helm
    if ! command -v helm >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing Helm...${NC}"
        curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
    fi

    # Terraform
    if ! command -v terraform >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing Terraform...${NC}"
        wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip -O /tmp/terraform.zip
        unzip -o /tmp/terraform.zip -d /tmp/
        sudo mv /tmp/terraform /usr/local/bin/
    fi
fi

# GitHub CLI
if [ "$PLATFORM" = "macos" ]; then
    install_tool "gh" "brew install gh"
elif [ "$PLATFORM" = "linux" ]; then
    if ! command -v gh >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing GitHub CLI...${NC}"
        type -p curl >/dev/null || $PKG_MGR curl
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
        echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
        sudo apt update
        $PKG_MGR gh
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# Build Tools
# ═══════════════════════════════════════════════════════════════════
echo -e "\n${BOLD}Installing Build Tools...${NC}"

# Snapcraft (Linux only)
if [ "$PLATFORM" = "linux" ]; then
    if ! command -v snapcraft >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing Snapcraft...${NC}"
        sudo snap install snapcraft --classic
    fi
fi

# PowerShell
if [ "$PLATFORM" = "macos" ]; then
    install_tool "pwsh" "brew install --cask powershell"
elif [ "$PLATFORM" = "linux" ]; then
    if ! command -v pwsh >/dev/null 2>&1; then
        echo -e "${YELLOW}→ Installing PowerShell...${NC}"
        wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O /tmp/packages-microsoft-prod.deb
        sudo dpkg -i /tmp/packages-microsoft-prod.deb
        sudo apt-get update
        $PKG_MGR powershell
    fi
fi

# ═══════════════════════════════════════════════════════════════════
# VM/Container Tools
# ═══════════════════════════════════════════════════════════════════
echo -e "\n${BOLD}Installing VM/Container Tools...${NC}"

if [ "$PLATFORM" = "macos" ]; then
    install_tool "multipass" "brew install --cask multipass"
fi

# ═══════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════
echo -e "\n${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BOLD}${BLUE}                    INSTALLATION COMPLETE                          ${NC}"
echo -e "${BOLD}${BLUE}═══════════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BOLD}Installed Tools:${NC}"

tools=(
    "python3:Python"
    "docker:Docker"
    "cargo:Rust/Cargo"
    "go:Go"
    "node:Node.js/npm"
    "ruby:Ruby/gem"
    "conda:Conda"
    "snap:Snap"
    "flatpak:Flatpak"
    "helm:Helm"
    "terraform:Terraform"
    "gh:GitHub CLI"
    "snapcraft:Snapcraft"
    "pwsh:PowerShell"
    "multipass:Multipass"
)

for tool_info in "${tools[@]}"; do
    IFS=':' read -r cmd name <<< "$tool_info"
    if command -v "$cmd" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name"
    elif [[ "$cmd" == "cargo" && -d "$HOME/.cargo" ]]; then
        echo -e "  ${GREEN}✓${NC} $name (installed, needs PATH: source ~/.cargo/env)"
    elif [[ "$cmd" == "conda" && -d "$HOME/miniconda" ]]; then
        echo -e "  ${GREEN}✓${NC} $name (installed, needs PATH: export PATH=\$HOME/miniconda/bin:\$PATH)"
    else
        echo -e "  ${YELLOW}⊘${NC} $name (not available)"
    fi
done

echo -e "\n${BOLD}${GREEN}You can now run Phase 1 tests with minimal skips:${NC}"
echo -e "  ${BLUE}./scripts/distribution-testing/run-all.sh${NC}"

echo -e "\n${BOLD}${YELLOW}Note: Some tools need PATH activation. Run these commands:${NC}"
if [ -d "$HOME/.cargo" ] && ! command -v cargo >/dev/null 2>&1; then
    echo -e "  ${BLUE}source ~/.cargo/env${NC}  # Activate Cargo"
fi
if [ -d "$HOME/miniconda" ] && ! command -v conda >/dev/null 2>&1; then
    echo -e "  ${BLUE}export PATH=\"\$HOME/miniconda/bin:\$PATH\"${NC}  # Activate Conda"
fi

echo -e "\n${BOLD}${CYAN}Or simply restart your terminal to auto-load all tools.${NC}"
echo ""
