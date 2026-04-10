#!/bin/bash
# Build all fixture repos into a temp directory and run the test suite.
# Usage: tests/run_tests.sh [pytest options...]
set -e
cd "$(dirname "$0")"

WORK_DIR=$(mktemp -d)
trap "rm -rf $WORK_DIR" EXIT
mkdir "$WORK_DIR/fixtures"

for script in fixtures/*.sh; do
    echo "Building fixture: $script"
    bash "$script" "$WORK_DIR"
done

PYTHONDONTWRITEBYTECODE=1 exec python3 -m pytest . --work-dir="$WORK_DIR" -o "cache_dir=$WORK_DIR/.pytest_cache" "$@"
