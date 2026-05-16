{{/* Gemeinsame Labels fuer alle Ressourcen. */}}
{{- define "apo.labels" -}}
app.kubernetes.io/part-of: autonomous-plant-ops
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end -}}

{{/* Selector-Labels fuer einen einzelnen Service (Name als Argument). */}}
{{- define "apo.selectorLabels" -}}
app.kubernetes.io/name: {{ . }}
{{- end -}}

{{/* Vollqualifizierter Image-Name: <registry><image>:<tag>. */}}
{{- define "apo.image" -}}
{{- $root := .root -}}
{{- $img := .svc.image -}}
{{- /* Tag-Aufloesung: pro-Service-Override > globaler image.tag > Chart.AppVersion */ -}}
{{- $tag := .svc.tag | default $root.Values.image.tag | default $root.Chart.AppVersion -}}
{{- printf "%s%s:%s" $root.Values.image.registry $img $tag -}}
{{- end -}}

{{/*
OLLAMA_HOST aufloesen:
  - mode=in-cluster -> http://ollama:<port>
  - sonst           -> ollama.external.host
*/}}
{{- define "apo.ollamaHost" -}}
{{- if eq .Values.ollama.mode "in-cluster" -}}
http://ollama:{{ .Values.ollama.inCluster.port }}
{{- else -}}
{{ .Values.ollama.external.host }}
{{- end -}}
{{- end -}}

{{/*
TLS aktiv, wenn explizit eingeschaltet ODER cert-manager aktiv.
*/}}
{{- define "apo.tlsEnabled" -}}
{{- if or .Values.ingress.tls.enabled .Values.ingress.certManager.enabled -}}true{{- end -}}
{{- end -}}

{{/* Name des TLS-Secrets: explizit gesetzt, sonst <Release>-tls. */}}
{{- define "apo.tlsSecret" -}}
{{- .Values.ingress.tls.secretName | default (printf "%s-tls" .Release.Name) -}}
{{- end -}}

{{/*
Ingress-Annotations: Controller-Preset (SSE-tauglich: kein Buffering,
lange Timeouts) + optionale cert-manager-Issuer-Annotation, danach mit
den nutzerdefinierten ingress.annotations gemerged (User gewinnt).
*/}}
{{- define "apo.ingressAnnotations" -}}
{{- $a := dict -}}
{{- if eq .Values.ingress.controller "nginx" -}}
{{-   $_ := set $a "nginx.ingress.kubernetes.io/proxy-buffering" "off" -}}
{{-   $_ := set $a "nginx.ingress.kubernetes.io/proxy-read-timeout" "3600" -}}
{{-   $_ := set $a "nginx.ingress.kubernetes.io/proxy-send-timeout" "3600" -}}
{{- else if eq .Values.ingress.controller "traefik" -}}
{{-   $_ := set $a "traefik.ingress.kubernetes.io/router.entrypoints" (ternary "websecure" "web" (eq (include "apo.tlsEnabled" .) "true")) -}}
{{-   $_ := set $a "traefik.ingress.kubernetes.io/buffering" "{\"maxResponseBodyBytes\":0}" -}}
{{- end -}}
{{- if .Values.ingress.certManager.enabled -}}
{{-   if eq .Values.ingress.certManager.issuerKind "Issuer" -}}
{{-     $_ := set $a "cert-manager.io/issuer" .Values.ingress.certManager.issuerName -}}
{{-   else -}}
{{-     $_ := set $a "cert-manager.io/cluster-issuer" .Values.ingress.certManager.issuerName -}}
{{-   end -}}
{{- end -}}
{{- $merged := merge (deepCopy .Values.ingress.annotations) $a -}}
{{- toYaml $merged -}}
{{- end -}}
