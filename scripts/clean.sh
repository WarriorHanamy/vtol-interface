#!/bin/bash
# Clean build artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Remove build, log, and install directories
[ -d "${PROJECT_DIR}/build" ] && rm -rf "${PROJECT_DIR}/build"
[ -d "${PROJECT_DIR}/log" ] && rm -rf "${PROJECT_DIR}/log"
[ -d "${PROJECT_DIR}/install" ] && rm -rf "${PROJECT_DIR}/install"

echo "Cleaned build artifacts"
