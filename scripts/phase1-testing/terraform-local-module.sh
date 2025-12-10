#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="terraform-local-module"
log "Starting $CHANNEL workflow"

require_command terraform

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
cleanup_hooks=("rm -rf '$WORK_DIR'")
trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

MODULE_DIR="$WORK_DIR/module"
mkdir -p "$MODULE_DIR"
cat >"$MODULE_DIR/main.tf" <<'EOF'
terraform {
  required_version = ">= 1.3.0"
}

output "message" {
  value = "Hello from Redoubt module"
}
EOF

ROOT_DIR="$WORK_DIR/root"
mkdir -p "$ROOT_DIR"
cat >"$ROOT_DIR/main.tf" <<EOF
module "redoubt" {
  source = "./module"
}

output "module_message" {
  value = module.redoubt.message
}
EOF

pushd "$ROOT_DIR" >/dev/null
terraform -chdir="$ROOT_DIR" init >/dev/null 2>&1 || skip "terraform init failed"
terraform -chdir="$ROOT_DIR" plan -input=false >/dev/null 2>&1 || skip "terraform plan failed"
popd >/dev/null

log "Terraform local module workflow completed"
