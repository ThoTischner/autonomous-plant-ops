#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "  Autonomous Plant Ops — Setup"
echo "========================================="
echo ""

cd "$PROJECT_DIR"

# Build and start all services
echo "[1/3] Building and starting all services..."
docker compose up --build -d

echo ""
echo "[2/3] Waiting for services to be ready..."
sleep 5

# Wait for Ollama to be ready and pull model
echo "[3/3] Pulling LLM model (llama3.1:8b) — this may take a while on first run..."
docker compose exec ollama ollama pull llama3.1:8b || echo "WARNING: Could not pull model. You may need to run: docker compose exec ollama ollama pull llama3.1:8b"

echo ""
echo "========================================="
echo "  All services are running!"
echo "========================================="
echo ""
echo "  Sensor Simulator:  http://localhost:8001"
echo "  LLM Agent:         http://localhost:8002"
echo "  n8n Orchestrator:  http://localhost:5678"
echo "  Dashboard API:     http://localhost:8003"
echo "  Dashboard UI:      http://localhost:5173"
echo ""
echo "  Next steps:"
echo "  1. Open n8n at http://localhost:5678"
echo "  2. Import workflow from n8n/workflows/main-monitoring-loop.json"
echo "  3. Activate the workflow"
echo "  4. Open Dashboard at http://localhost:5173"
echo "  5. Trigger a scenario:"
echo "     curl -X POST http://localhost:8001/scenarios/trigger \\"
echo "       -H 'Content-Type: application/json' \\"
echo "       -d '{\"scenario\": \"thermal_runaway\"}'"
echo ""
