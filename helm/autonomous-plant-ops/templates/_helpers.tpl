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
