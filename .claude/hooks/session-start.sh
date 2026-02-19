#!/bin/bash
set -euo pipefail

# Only run in remote (Claude Code on the web) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

# --- Python dependencies ---
echo "Installing Python dependencies..."
pip install --prefer-binary "${PROJECT_DIR}[dev]" --quiet

# Export PYTHONPATH so imports resolve correctly
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PYTHONPATH=\"${PROJECT_DIR}\"" >> "$CLAUDE_ENV_FILE"
fi

# --- Node.js / Next.js dependencies ---
if [ -f "${PROJECT_DIR}/web/package.json" ]; then
  echo "Installing Node.js dependencies..."
  npm install --prefix "${PROJECT_DIR}/web" --no-audit --no-fund
fi

echo "Session start hook completed successfully."
