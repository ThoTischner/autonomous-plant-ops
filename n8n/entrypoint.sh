#!/bin/sh
set -e

# Import workflows before n8n starts
echo "[n8n-init] Importing workflows..."
for f in /workflows/*.json; do
  if [ -f "$f" ]; then
    echo "[n8n-init] Importing $f..."
    n8n import:workflow --input="$f" 2>&1 || echo "[n8n-init] Warning: could not import $f"
  fi
done

# Activate/publish each workflow individually
echo "[n8n-init] Publishing workflows..."
n8n publish:workflow --id=1 2>&1 || echo "[n8n-init] Warning: could not publish workflow 1"
n8n publish:workflow --id=2 2>&1 || echo "[n8n-init] Warning: could not publish workflow 2"

echo "[n8n-init] Starting n8n..."
exec n8n start
