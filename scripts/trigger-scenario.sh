#!/usr/bin/env bash
set -euo pipefail

SCENARIO="${1:-thermal_runaway}"
EQUIPMENT_ID="${2:-}"

echo "Triggering scenario: $SCENARIO"

BODY="{\"scenario\": \"$SCENARIO\""
if [ -n "$EQUIPMENT_ID" ]; then
    BODY="$BODY, \"equipment_id\": \"$EQUIPMENT_ID\""
fi
BODY="$BODY}"

curl -s -X POST http://localhost:8001/scenarios/trigger \
    -H "Content-Type: application/json" \
    -d "$BODY" | python3 -m json.tool 2>/dev/null || echo "$BODY"

echo ""
echo "Available scenarios:"
curl -s http://localhost:8001/scenarios/list | python3 -m json.tool 2>/dev/null || true
