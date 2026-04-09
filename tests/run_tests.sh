#!/bin/bash
# Build all fixture repos and run the test suite.
# Usage: tests/run_tests.sh [pytest options...]
set -e
cd "$(dirname "$0")"

for script in fixtures/*.sh; do
    echo "Building fixture: $script"
    bash "$script"
done

exec python3 -m pytest . "$@"
