# autonomous-plant-ops

KI-gestützte autonome Überwachung industrieller Anlagen. Dieses Chart deployt die fünf Anwendungs-Services und optional Ollama in ein Kubernetes-Cluster.

## TL;DR

```bash
helm repo add autonomous-plant-ops https://thotischner.github.io/autonomous-plant-ops
helm install plant-ops autonomous-plant-ops/autonomous-plant-ops
```

## Voraussetzungen

- Kubernetes ≥ 1.23
- Helm ≥ 3.8
- Ein nginx-Ingress-Controller (wenn `ingress.enabled=true`)
- Erreichbarer Ollama-Endpoint (extern) **oder** genügend Cluster-Ressourcen für In-Cluster-Ollama

## Services

| Service | Port | Typ |
|---|---|---|
| sensor-simulator | 8001 | Deployment + Service |
| llm-agent | 8002 | Deployment + Service |
| orchestrator | – | Deployment (Loop, kein Service, fix 1 Replica) |
| dashboard-api | 8003 | Deployment + Service |
| dashboard-frontend | 80 | Deployment + Service (Ingress-Backend) |
| ollama | 11434 | optional, nur bei `ollama.mode=in-cluster` |

## Ollama-Modus

```bash
# Extern (Default)
helm install plant-ops . --set ollama.external.host=http://my-ollama:11434

# Im Cluster
helm install plant-ops . --set ollama.mode=in-cluster

# Im Cluster mit GPU
helm install plant-ops . \
  --set ollama.mode=in-cluster \
  --set ollama.inCluster.gpu.enabled=true
```

Bei In-Cluster-Ollama muss das Modell einmalig gepullt werden:

```bash
kubectl exec deploy/ollama -- ollama pull llama3.2:3b
```

## Wichtige Werte

| Schlüssel | Default | Beschreibung |
|---|---|---|
| `image.registry` | `ghcr.io/thotischner/` | Registry-Präfix (für lokale Builds `""`) |
| `image.tag` | `latest` | Image-Tag aller Services |
| `ollama.mode` | `external` | `external` oder `in-cluster` |
| `ollama.external.host` | `http://host.docker.internal:11434` | Externer Ollama-Endpoint |
| `ollama.inCluster.persistence.size` | `20Gi` | PVC-Größe für Modelle |
| `ollama.inCluster.gpu.enabled` | `false` | GPU-Limit + NodeSelector/Tolerations |
| `ingress.enabled` | `true` | nginx-Ingress aufs Frontend |
| `ingress.host` | `plant-ops.local` | Hostname |

Vollständige Liste in [`values.yaml`](values.yaml); Validierung über [`values.schema.json`](values.schema.json).

## Hinweise

- **Service-Namen sind fix** (entsprechen den Compose-Namen), damit die im Code/in `nginx.conf` hartkodierten URLs unverändert funktionieren — nicht umbenennen.
- **Orchestrator nicht hochskalieren** — mehrere Replicas würden Fehlszenarien doppelt triggern.
- **SSE** — Der Ingress setzt `proxy-buffering: off` und lange Timeouts, damit `/events/stream` offen bleibt.
