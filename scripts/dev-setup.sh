#!/bin/bash
#
# dev-setup.sh: Comprehensive development environment setup script
#
# This script ensures a consistent and complete development environment is set up
# with a single command. It is idempotent and can be run safely multiple times.

set -e # Exit immediately if a command exits with a non-zero status.

# --- Helper Functions ---

# Print a message in a consistent format
info() {
    echo -e "\033[34m[INFO]\033[0m $1"
}

# Print a success message
success() {
    echo -e "\033[32m[SUCCESS]\033[0m $1"
}

# Print a warning message
warning() {
    echo -e "\033[33m[WARNING]\033[0m $1"
}

# Check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# --- Main Setup Logic ---

info "Starting development environment setup..."

# 1. Check for essential tools
info "Checking for required tools (git, python3, uv)..."
if ! command_exists git; then
    warning "Git is not installed. Please install it to continue."
    exit 1
fi

if ! command_exists python3; then
    warning "Python 3 is not installed. Please install it to continue."
    exit 1
fi

if ! command_exists uv; then
    info "'uv' is not found. Installing it via pip..."
    python3 -m pip install uv==0.5.11
    # Add uv to PATH for the current session if it's not there already
    if ! command_exists uv; then
        export PATH="$HOME/.local/bin:$PATH"
        if ! command_exists uv; then
            warning "Failed to add uv to PATH. Please add it manually."
            exit 1
        fi
    fi
fi
success "All required tools are available."

# 2. Set up Python virtual environment
VENV_DIR=".venv"
if [ ! -d "$VENV_DIR" ]; then
    info "Creating Python virtual environment in '$VENV_DIR'..."
    python3 -m venv "$VENV_DIR"
    success "Virtual environment created."
else
    info "Virtual environment already exists."
fi

# Activate the virtual environment for the rest of the script
source "$VENV_DIR/bin/activate"

# 3. Install dependencies
info "Installing project dependencies using uv..."
uv pip install -e ".[dev]"
success "Dependencies installed."

# 4. Install pre-commit hooks
info "Installing pre-commit hooks..."
if command_exists pre-commit; then
    pre-commit install
    pre-commit install --hook-type commit-msg
    success "Pre-commit hooks installed."
else
    warning "'pre-commit' command not found. Skipping hook installation."
fi

# 5. Create local .env file if it doesn't exist
if [ ! -f ".env" ]; then
    info "Creating .env file from .env.example..."
    cp .env.example .env
    success ".env file created. You may need to customize it."
else
    info ".env file already exists."
fi

# --- Finalization ---

success "Development environment setup is complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "Common commands:"
echo "  make test       - Run tests"
echo "  make format     - Format code"
echo "  make lint       - Run linters"
echo "  make build      - Build the project"
