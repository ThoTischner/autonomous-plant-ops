#!/usr/bin/env bash
# Smoke-Test gegen ein per Helm deploytes autonomous-plant-ops im aktuellen
# kubectl-Kontext/Namespace. Prueft Rollouts und /health-Endpoints.
set -euo pipefail

NS="${1:-default}"
echo "==> Smoke-Test im Namespace '$NS'"

DEPLOYMENTS="sensor-simulator llm-agent orchestrator dashboard-api dashboard-frontend"
for d in $DEPLOYMENTS; do
  echo "--> warte auf rollout: $d"
  kubectl -n "$NS" rollout status "deploy/$d" --timeout=180s
done

# Health-Checks ueber einen ephemeren curl-Pod gegen die Cluster-DNS-Namen.
declare -A HEALTH=(
  [sensor-simulator]="http://sensor-simulator:8001/health"
  [llm-agent]="http://llm-agent:8002/health"
  [dashboard-api]="http://dashboard-api:8003/health"
  [dashboard-frontend]="http://dashboard-frontend:80/"
)

fail=0
for svc in "${!HEALTH[@]}"; do
  url="${HEALTH[$svc]}"
  echo "--> health: $svc ($url)"
  if kubectl -n "$NS" run "smoke-$svc-$RANDOM" --rm -i --restart=Never \
      --image=curlimages/curl:8.10.1 --quiet -- \
      curl -fsS --max-time 10 --retry 5 --retry-delay 3 --retry-connrefused "$url" >/dev/null; then
    echo "    OK"
  else
    echo "    FEHLGESCHLAGEN"
    fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "==> Smoke-Test FEHLGESCHLAGEN"
  kubectl -n "$NS" get pods
  exit 1
fi
echo "==> Smoke-Test erfolgreich"
