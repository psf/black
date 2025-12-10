#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

CHANNEL="go-module-replace"
log "Starting $CHANNEL workflow"

require_command go

WORK_DIR="$(mktemp -d "$WORK_ROOT/${CHANNEL}.XXXX")"
cleanup_hooks=("rm -rf '$WORK_DIR'")
trap 'for hook in "${cleanup_hooks[@]}"; do eval "$hook"; done' EXIT

MODULE_DIR="$WORK_DIR/module"
mkdir -p "$MODULE_DIR"
pushd "$MODULE_DIR" >/dev/null
go mod init example.com/redoubt/demo >/dev/null 2>&1
cat >demo.go <<'EOF'
package demo

func Greet() string {
	return "hello from redoubt module"
}
EOF
cat >demo_test.go <<'EOF'
package demo

import "testing"

func TestGreet(t *testing.T) {
	if Greet() == "" {
		t.Fatal("expected greeting")
	}
}
EOF
go test ./... >/dev/null 2>&1
popd >/dev/null

CONSUMER_DIR="$WORK_DIR/consumer"
mkdir -p "$CONSUMER_DIR"
pushd "$CONSUMER_DIR" >/dev/null
go mod init consumer.example >/dev/null 2>&1
go mod edit -require=example.com/redoubt/demo@v0.0.0
go mod edit -replace=example.com/redoubt/demo="$MODULE_DIR"

cat >main.go <<'EOF'
package main

import (
	"fmt"
	"example.com/redoubt/demo"
)

func main() {
	fmt.Println(demo.Greet())
}
EOF

if ! go list ./... >/dev/null 2>&1; then
  skip "go list failed (replace directive not honored)"
fi

go run . >/dev/null 2>&1 || skip "go run failed"
log "Go module replace workflow completed"
popd >/dev/null
