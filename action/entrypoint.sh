#!/bin/sh
set -e

if [ $# -eq 0 ]; then
    # Default (if no args provided).
    sh -c "black . --check --diff"
else
    # Custom args.
    sh -c "black $*"
fi
