# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered agent for monitoring industrial systems and autonomously detecting, preventing, and fixing failures in real time. Uses a local LLM (Ollama) for reasoning, n8n for orchestration, and a React dashboard for visualization.

## Docker-Only Policy

**EVERYTHING runs in Docker containers.** This is a hard rule for the entire project:

- **Development**: All services run via `docker compose up --build`
- **Testing**: All tests run inside Docker containers via `Dockerfile.test` per service
- **CI/CD**: GitHub Actions pipeline builds and runs everything in Docker — no host-level Python, Node, or npm installs
- **Linting/Type-checking**: ruff, mypy, tsc all run inside their respective test containers
- **Integration tests**: Run in a dedicated container connected to the Docker network

**Never** install Python packages, Node modules, or any other dependencies directly on the host. Always use Docker.

```bash
# Run unit tests for a service (in Docker)
docker build -f sensor-simulator/Dockerfile.test -t sensor-simulator-test sensor-simulator/
docker run --rm sensor-simulator-test pytest tests/ -v

# Run all tests (in Docker)
docker compose -f docker-compose.yml -f docker-compose.test.yml up --build --abort-on-container-exit

# Lint a service (in Docker)
docker build -f llm-agent/Dockerfile.test -t llm-agent-test llm-agent/
docker run --rm llm-agent-test ruff check src/
```

## Architecture

6 Docker services connected via `plant-net` bridge network:

| Service | Port | Tech |
|---|---|---|
| sensor-simulator | 8001 | Python/FastAPI — generates sensor data for 3 equipments |
| llm-agent | 8002 | Python/FastAPI + Ollama SDK — LLM-based anomaly analysis |
| n8n | 5678 | n8n (Docker) — orchestrates 5s monitoring loop |
| dashboard-api | 8003 | Python/FastAPI + SSE — event store & streaming |
| dashboard-frontend | 5173 | React/Vite/TypeScript/Tailwind/Recharts/Framer Motion |
| ollama | 11434 | Local LLM runtime (llama3.1:8b) |

## Build & Run

```bash
# Full stack (everything in Docker)
docker compose up --build

# Pull LLM model (first time, runs inside Ollama container)
docker compose exec ollama ollama pull llama3.1:8b

# One-click setup
./scripts/setup.sh
```

## Testing (all in Docker)

```bash
# Unit tests per service
docker build -f sensor-simulator/Dockerfile.test -t test sensor-simulator/ && docker run --rm test
docker build -f llm-agent/Dockerfile.test -t test llm-agent/ && docker run --rm test
docker build -f dashboard/api/Dockerfile.test -t test dashboard/api/ && docker run --rm test

# Frontend type check
docker build -f dashboard/frontend/Dockerfile.test -t test dashboard/frontend/ && docker run --rm test

# All tests + integration
docker compose -f docker-compose.yml -f docker-compose.test.yml up --build --abort-on-container-exit

# Linting (in Docker)
docker run --rm test ruff check src/
docker run --rm test mypy src/ --ignore-missing-imports
```

## Key Endpoints

- `GET localhost:8001/sensors/latest` — current sensor readings
- `GET localhost:8001/sensors/history/{id}` — sensor history
- `POST localhost:8001/actions/execute` — execute corrective actions
- `POST localhost:8001/scenarios/trigger` — trigger failure scenarios
- `GET localhost:8001/scenarios/list` — list available scenarios
- `POST localhost:8002/agent/analyze` — LLM analysis
- `POST localhost:8003/events` — push events
- `GET localhost:8003/events` — get events
- `GET localhost:8003/events/stream` — SSE stream

## CI/CD

GitHub Actions pipeline at `.github/workflows/ci.yml`:
- 6 parallel jobs, all running in Docker containers
- Per-service: build Dockerfile.test → ruff → mypy → pytest
- Frontend: tsc --noEmit + production build
- Full docker-compose build + health checks
- Integration tests over Docker network

## Project Structure

```
sensor-simulator/     Python/FastAPI — 3 equipments, 4 scenarios
llm-agent/            Python/FastAPI — Ollama integration, prompt engineering
dashboard/api/        Python/FastAPI — Event store + SSE streaming
dashboard/frontend/   React/TypeScript — Real-time industrial dashboard
n8n/workflows/        n8n workflow JSON files
scripts/              Setup and demo scripts
tests/                Integration tests (Docker-based)
```
