#!/bin/sh
# This script runs at n8n startup to import workflows.
# n8n CLI commands are available in the container.

echo "[n8n-init] Importing workflows..."

for f in /workflows/*.json; do
  if [ -f "$f" ]; then
    echo "[n8n-init] Importing $f..."
    n8n import:workflow --input="$f" 2>/dev/null || echo "[n8n-init] Warning: could not import $f (may already exist)"
  fi
done

echo "[n8n-init] Workflow import complete."
