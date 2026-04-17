#!/bin/bash
set -euo pipefail

# Only run in the Claude Code web sandbox.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

cd "$CLAUDE_PROJECT_DIR/gemini-image-mcp"

# Idempotent: skip if node_modules already has the MCP SDK.
if [ ! -d node_modules/@modelcontextprotocol/sdk ]; then
  npm install --no-audit --no-fund --loglevel=error
fi
