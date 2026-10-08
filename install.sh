#!/usr/bin/env bash
# Orchestra Plugin Installer for Antigravity

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="$(which python3 || which python || echo "")"

if [ -z "$PYTHON_BIN" ]; then
  echo "Error: Python 3 is required to install Orchestra." >&2
  exit 1
fi

"$PYTHON_BIN" "$SCRIPT_DIR/scripts/install.py" "$@"
