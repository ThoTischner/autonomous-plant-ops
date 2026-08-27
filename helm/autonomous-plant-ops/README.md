# autonomous-plant-ops

AI-powered autonomous monitoring of industrial plants — Sensor Simulator, LLM Agent, Orchestrator, Dashboard API/Frontend and optionally Ollama.

![Version: 0.3.0](https://img.shields.io/badge/Version-0.3.0-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 1.1.0](https://img.shields.io/badge/AppVersion-1.1.0-informational?style=flat-square)

## Installation

```bash
helm repo add autonomous-plant-ops https://thotischner.github.io/autonomous-plant-ops
helm repo update
helm install plant-ops autonomous-plant-ops/autonomous-plant-ops
```

Choose the Ollama mode (default: external endpoint):

```bash
# Ollama inside the cluster (optionally with GPU)
helm install plant-ops autonomous-plant-ops/autonomous-plant-ops \
  --set ollama.mode=in-cluster \
  --set ollama.inCluster.gpu.enabled=true
```

With `ollama.mode=in-cluster`, pull the model once:

```bash
kubectl exec deploy/ollama -- ollama pull llama3.2:3b
```

## Operational notes

- Service names are fixed (inter-service URLs depend on them) — do not rename.
- `services.orchestrator.replicas` must stay `1`.
- Ingress keeps the SSE stream `/events/stream` open (annotations in `values`).
- Images are pinned to `Chart.AppVersion` and multi-arch (amd64/arm64).

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| image.registry | string | `"ghcr.io/thotischner/"` | Registry prefix including the trailing slash. Empty (`""`) for local builds. |
| image.tag | string | `""` | Image tag. Empty = pinned to `Chart.AppVersion` (recommended, reproducible). For dev e.g. `main`. |
| image.pullPolicy | string | `"IfNotPresent"` | Image pull policy. |
| imagePullSecrets | list | `[]` | Pull secrets for private registries. |
| services | object | see fields below | Application services. The keys are used verbatim as Kubernetes service names (do not rename — inter-service URLs depend on them). |
| services.sensor-simulator.image | string | `"autonomous-plant-ops/sensor-simulator"` | Image repository (combined with `image.registry` and tag). |
| services.sensor-simulator.replicas | int | `1` | Replica count. |
| services.sensor-simulator.port | int | `8001` | Container/service port. |
| services.sensor-simulator.healthPath | string | `"/health"` | HTTP path for the readiness/liveness probe. |
| services.sensor-simulator.env | object | `{"EQUIPMENT_FILE":"/data/equipment.json"}` | Environment variables. |
| services.sensor-simulator.persistence | object | `{"enabled":true,"mountPath":"/data","size":"1Gi","storageClass":""}` | Persistent equipment definition (PVC). `enabled: false` = ephemeral. |
| services.sensor-simulator.resources | object | `{}` | Resource requests/limits. |
| services.llm-agent.image | string | `"autonomous-plant-ops/llm-agent"` | Image repository. |
| services.llm-agent.replicas | int | `1` | Replica count. |
| services.llm-agent.port | int | `8002` | Container/service port. |
| services.llm-agent.healthPath | string | `"/health"` | HTTP path for the probes. |
| services.llm-agent.env | object | `{"OLLAMA_MODEL":"llama3.2:3b"}` | Additional environment variables. `OLLAMA_HOST` is set automatically from `.ollama`. |
| services.llm-agent.resources | object | `{}` | Resource requests/limits. |
| services.orchestrator.image | string | `"autonomous-plant-ops/orchestrator"` | Image repository. |
| services.orchestrator.replicas | int | `1` | Replica count. Must stay `1` (otherwise duplicate scenario triggers). |
| services.orchestrator.service | bool | `false` | `false` = no Kubernetes service/port (pure loop container). |
| services.orchestrator.env | object | `{"AGENT_URL":"http://llm-agent:8002","CYCLE_INTERVAL":"12","DASHBOARD_URL":"http://dashboard-api:8003","SCENARIO_CHANCE":"0.08","SENSOR_URL":"http://sensor-simulator:8001"}` | Environment variables of the monitoring loop. |
| services.orchestrator.resources | object | `{}` | Resource requests/limits. |
| services.dashboard-api.image | string | `"autonomous-plant-ops/dashboard-api"` | Image repository. |
| services.dashboard-api.replicas | int | `1` | Replica count. |
| services.dashboard-api.port | int | `8003` | Container/service port. |
| services.dashboard-api.healthPath | string | `"/health"` | HTTP path for the probes. |
| services.dashboard-api.resources | object | `{}` | Resource requests/limits. |
| services.dashboard-frontend.image | string | `"autonomous-plant-ops/dashboard-frontend"` | Image repository (Chainguard/Wolfi nginx, nonroot; proxies `/api/` to the dashboard-api). |
| services.dashboard-frontend.replicas | int | `1` | Replica count. |
| services.dashboard-frontend.port | int | `8080` | Container/service port (nonroot nginx -> unprivileged port 8080). |
| services.dashboard-frontend.readOnlyRootFilesystem | bool | `false` | nginx needs writable runtime paths -> no read-only root. |
| services.dashboard-frontend.resources | object | `{}` | Resource requests/limits. |
| ollama.mode | string | `"external"` | Operating mode: `external` (external endpoint) or `in-cluster` (Ollama inside the cluster). |
| ollama.external.host | string | `"http://host.docker.internal:11434"` | Fully qualified URL of the external Ollama server (only for `mode: external`). |
| ollama.inCluster.image | string | `"ollama/ollama:latest"` | Ollama image (only for `mode: in-cluster`). |
| ollama.inCluster.pullPolicy | string | `"IfNotPresent"` | Image pull policy. |
| ollama.inCluster.port | int | `11434` | Service port. |
| ollama.inCluster.model | string | `"llama3.2:3b"` | Model (must be pulled once after deploy, see NOTES). |
| ollama.inCluster.resources | object | `{}` | Resource requests/limits. |
| ollama.inCluster.persistence.enabled | bool | `true` | Persistent model storage via PVC. |
| ollama.inCluster.persistence.size | string | `"20Gi"` | PVC size. |
| ollama.inCluster.persistence.storageClass | string | `""` | StorageClass (empty = default). |
| ollama.inCluster.gpu.enabled | bool | `false` | Enable GPU for Ollama. |
| ollama.inCluster.gpu.resourceName | string | `"nvidia.com/gpu"` | GPU resource name. |
| ollama.inCluster.gpu.count | int | `1` | Number of GPUs. |
| ollama.inCluster.gpu.nodeSelector | object | `{}` | NodeSelector for GPU nodes. |
| ollama.inCluster.gpu.tolerations | list | `[]` | Tolerations for GPU nodes. |
| frontend | object | `{"service":{"annotations":{},"loadBalancerIP":"","nodePort":"","type":"ClusterIP"}}` | Exposure of the user-facing entry point (dashboard-frontend). Internal services always stay ClusterIP. Freely combinable with `ingress`. |
| frontend.service.type | string | `"ClusterIP"` | Service type: `ClusterIP` | `NodePort` | `LoadBalancer`. |
| frontend.service.nodePort | string | `""` | Fixed NodePort (only `type: NodePort`; empty = automatic 30000–32767). |
| frontend.service.loadBalancerIP | string | `""` | Desired LoadBalancer IP (only `type: LoadBalancer`, optional). |
| frontend.service.annotations | object | `{}` | Additional service annotations (e.g. cloud LB tuning). |
| ingress.enabled | bool | `true` | Enable ingress (independent of `frontend.service.type`). |
| ingress.className | string | `"nginx"` | IngressClass name: `nginx` | `traefik` | custom name | `""` (default class). |
| ingress.controller | string | `"nginx"` | Annotation preset matching the controller: `nginx` | `traefik` | `none`. Keeps the SSE stream `/events/stream` open (no buffering, long timeouts). |
| ingress.host | string | `"plant-ops.local"` | Hostname. |
| ingress.path | string | `"/"` | HTTP path. |
| ingress.pathType | string | `"Prefix"` | pathType: `Prefix` | `Exact` | `ImplementationSpecific`. |
| ingress.annotations | object | `{}` | Additional annotations (merged over the controller preset, can override it). |
| ingress.tls.enabled | bool | `false` | Enable TLS. |
| ingress.tls.secretName | string | `""` | Name of the TLS secret (empty = `<Release>-tls`). |
| ingress.certManager | object | `{"enabled":false,"issuerKind":"ClusterIssuer","issuerName":""}` | cert-manager integration: sets the issuer annotation and enables TLS automatically. |
| ingress.certManager.enabled | bool | `false` | Enable cert-manager issuance. |
| ingress.certManager.issuerName | string | `""` | Name of the Issuer/ClusterIssuer. |
| ingress.certManager.issuerKind | string | `"ClusterIssuer"` | Issuer kind: `ClusterIssuer` | `Issuer`. |
| podAnnotations | object | `{}` | Pod annotations (all deployments). |
| nodeSelector | object | `{}` | NodeSelector (all deployments). |
| tolerations | list | `[]` | Tolerations (all deployments). |
| affinity | object | `{}` | Affinity (all deployments). |
| defaultResources | object | `{"limits":{"cpu":"1","memory":"512Mi"},"requests":{"cpu":"50m","memory":"64Mi"}}` | Default resources (apply when a service sets no own `resources`). Sets requests AND limits -> clears the KSV resource checks. |
| securityContext | object | `{"enabled":true,"fsGroup":65532,"readOnlyRootFilesystem":true,"runAsGroup":65532,"runAsUser":65532}` | Hardened SecurityContext for all deployments (matches the nonroot Wolfi/Chainguard images: runAsNonRoot, caps drop ALL, no privilege escalation, seccomp RuntimeDefault). Write access only via a /tmp emptyDir and persistent volumes. |
| securityContext.enabled | bool | `true` | Enable SecurityContext. |
| securityContext.runAsUser | int | `65532` | UID (nonroot, matches the images). |
| securityContext.runAsGroup | int | `65532` | GID. |
| securityContext.fsGroup | int | `65532` | fsGroup for mounted volumes. |
| securityContext.readOnlyRootFilesystem | bool | `true` | Read-only root filesystem (global). Overridable per service via `services.<name>.readOnlyRootFilesystem`. |

----

_This file is generated by [helm-docs](https://github.com/norwoodj/helm-docs). Source: `values.yaml` + `README.md.gotmpl` — do not edit manually._
