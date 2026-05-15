# autonomous-plant-ops

KI-gestuetzte autonome Ueberwachung industrieller Anlagen — Sensor Simulator, LLM Agent, Orchestrator, Dashboard API/Frontend und optional Ollama.

![Version: 0.2.1](https://img.shields.io/badge/Version-0.2.1-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.0.1](https://img.shields.io/badge/AppVersion-1.0.1-informational?style=flat-square)

## Installation

```bash
helm repo add autonomous-plant-ops https://thotischner.github.io/autonomous-plant-ops
helm repo update
helm install plant-ops autonomous-plant-ops/autonomous-plant-ops
```

Ollama-Modus wählen (Standard: externer Endpoint):

```bash
# Ollama im Cluster (optional mit GPU)
helm install plant-ops autonomous-plant-ops/autonomous-plant-ops \
  --set ollama.mode=in-cluster \
  --set ollama.inCluster.gpu.enabled=true
```

Bei `ollama.mode=in-cluster` das Modell einmalig pullen:

```bash
kubectl exec deploy/ollama -- ollama pull llama3.2:3b
```

## Betriebshinweise

- Service-Namen sind fix (Inter-Service-URLs hängen daran) — nicht umbenennen.
- `services.orchestrator.replicas` muss `1` bleiben.
- Ingress hält den SSE-Stream `/events/stream` offen (Annotations in `values`).
- Images sind auf `Chart.AppVersion` gepinnt und Multi-Arch (amd64/arm64).

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| image.registry | string | `"ghcr.io/thotischner/"` | Registry-Präfix inkl. abschließendem Slash. Leer (`""`) für lokale Builds. |
| image.tag | string | `""` | Image-Tag. Leer = gepinnt auf `Chart.AppVersion` (empfohlen, reproduzierbar). Für Dev z. B. `main`. |
| image.pullPolicy | string | `"IfNotPresent"` | Image pull policy. |
| imagePullSecrets | list | `[]` | Pull-Secrets für private Registries. |
| services | object | siehe Felder unten | Anwendungs-Services. Die Keys werden 1:1 als Kubernetes-Service-Namen verwendet (nicht umbenennen — Inter-Service-URLs sind darauf angewiesen). |
| services.sensor-simulator.image | string | `"autonomous-plant-ops/sensor-simulator"` | Image-Repository (wird mit `image.registry` und Tag kombiniert). |
| services.sensor-simulator.replicas | int | `1` | Replica-Anzahl. |
| services.sensor-simulator.port | int | `8001` | Container-/Service-Port. |
| services.sensor-simulator.healthPath | string | `"/health"` | HTTP-Pfad für Readiness/Liveness-Probe. |
| services.sensor-simulator.env | object | `{"EQUIPMENT_FILE":"/data/equipment.json"}` | Umgebungsvariablen. |
| services.sensor-simulator.persistence | object | `{"enabled":true,"mountPath":"/data","size":"1Gi","storageClass":""}` | Persistente Equipment-Definition (PVC). `enabled: false` = ephemer. |
| services.sensor-simulator.resources | object | `{}` | Ressourcen-Requests/Limits. |
| services.llm-agent.image | string | `"autonomous-plant-ops/llm-agent"` | Image-Repository. |
| services.llm-agent.replicas | int | `1` | Replica-Anzahl. |
| services.llm-agent.port | int | `8002` | Container-/Service-Port. |
| services.llm-agent.healthPath | string | `"/health"` | HTTP-Pfad für Probes. |
| services.llm-agent.env | object | `{"OLLAMA_MODEL":"llama3.2:3b"}` | Zusätzliche Umgebungsvariablen. `OLLAMA_HOST` wird automatisch aus `.ollama` gesetzt. |
| services.llm-agent.resources | object | `{}` | Ressourcen-Requests/Limits. |
| services.orchestrator.image | string | `"autonomous-plant-ops/orchestrator"` | Image-Repository. |
| services.orchestrator.replicas | int | `1` | Replica-Anzahl. Muss `1` bleiben (sonst doppelte Szenario-Trigger). |
| services.orchestrator.service | bool | `false` | `false` = kein Kubernetes-Service/Port (reiner Loop-Container). |
| services.orchestrator.env | object | `{"AGENT_URL":"http://llm-agent:8002","CYCLE_INTERVAL":"12","DASHBOARD_URL":"http://dashboard-api:8003","SCENARIO_CHANCE":"0.08","SENSOR_URL":"http://sensor-simulator:8001"}` | Umgebungsvariablen des Monitoring-Loops. |
| services.orchestrator.resources | object | `{}` | Ressourcen-Requests/Limits. |
| services.dashboard-api.image | string | `"autonomous-plant-ops/dashboard-api"` | Image-Repository. |
| services.dashboard-api.replicas | int | `1` | Replica-Anzahl. |
| services.dashboard-api.port | int | `8003` | Container-/Service-Port. |
| services.dashboard-api.healthPath | string | `"/health"` | HTTP-Pfad für Probes. |
| services.dashboard-api.resources | object | `{}` | Ressourcen-Requests/Limits. |
| services.dashboard-frontend.image | string | `"autonomous-plant-ops/dashboard-frontend"` | Image-Repository (nginx; proxyt `/api/` zur dashboard-api). |
| services.dashboard-frontend.replicas | int | `1` | Replica-Anzahl. |
| services.dashboard-frontend.port | int | `80` | Container-/Service-Port. |
| services.dashboard-frontend.resources | object | `{}` | Ressourcen-Requests/Limits. |
| ollama.mode | string | `"external"` | Betriebsmodus: `external` (externer Endpoint) oder `in-cluster` (Ollama im Cluster). |
| ollama.external.host | string | `"http://host.docker.internal:11434"` | Voll qualifizierte URL des externen Ollama-Servers (nur bei `mode: external`). |
| ollama.inCluster.image | string | `"ollama/ollama:latest"` | Ollama-Image (nur bei `mode: in-cluster`). |
| ollama.inCluster.pullPolicy | string | `"IfNotPresent"` | Image pull policy. |
| ollama.inCluster.port | int | `11434` | Service-Port. |
| ollama.inCluster.model | string | `"llama3.2:3b"` | Modell (muss nach Deploy einmalig gepullt werden, siehe NOTES). |
| ollama.inCluster.resources | object | `{}` | Ressourcen-Requests/Limits. |
| ollama.inCluster.persistence.enabled | bool | `true` | Persistente Modell-Ablage via PVC. |
| ollama.inCluster.persistence.size | string | `"20Gi"` | PVC-Größe. |
| ollama.inCluster.persistence.storageClass | string | `""` | StorageClass (leer = Default). |
| ollama.inCluster.gpu.enabled | bool | `false` | GPU für Ollama aktivieren. |
| ollama.inCluster.gpu.resourceName | string | `"nvidia.com/gpu"` | GPU-Ressourcenname. |
| ollama.inCluster.gpu.count | int | `1` | Anzahl GPUs. |
| ollama.inCluster.gpu.nodeSelector | object | `{}` | NodeSelector für GPU-Nodes. |
| ollama.inCluster.gpu.tolerations | list | `[]` | Tolerations für GPU-Nodes. |
| ingress.enabled | bool | `true` | Ingress aktivieren. |
| ingress.className | string | `"nginx"` | IngressClass. |
| ingress.host | string | `"plant-ops.local"` | Hostname. |
| ingress.annotations | object | `{"nginx.ingress.kubernetes.io/proxy-buffering":"off","nginx.ingress.kubernetes.io/proxy-read-timeout":"3600","nginx.ingress.kubernetes.io/proxy-send-timeout":"3600"}` | Annotations (Defaults halten den SSE-Stream `/events/stream` offen). |
| ingress.tls.enabled | bool | `false` | TLS aktivieren. |
| ingress.tls.secretName | string | `""` | Name des TLS-Secrets. |
| podAnnotations | object | `{}` | Pod-Annotations (alle Deployments). |
| nodeSelector | object | `{}` | NodeSelector (alle Deployments). |
| tolerations | list | `[]` | Tolerations (alle Deployments). |
| affinity | object | `{}` | Affinity (alle Deployments). |

----

_Diese Datei wird von [helm-docs](https://github.com/norwoodj/helm-docs) generiert. Quelle: `values.yaml` + `README.md.gotmpl` — nicht manuell editieren._
