{{- define "virtualization-ai-401.labels" -}}
app.kubernetes.io/part-of: virtualization-ai-401
app.kubernetes.io/managed-by: {{ .Release.Service }}
lab.redhat.com/candidate: virtualization-ai-401
{{- end }}
{{- define "virtualization-ai-401.image" -}}
{{- if .digest -}}{{ .repository }}@{{ .digest }}{{- else -}}{{ .repository }}:{{ .tag }}{{- end -}}
{{- end }}
{{- define "virtualization-ai-401.routeHost" -}}
{{- $suffix := sha256sum .Release.Namespace | trunc 10 -}}
virt401-{{ $suffix }}.{{ required "presentation.ingressDomain is required" .Values.presentation.ingressDomain }}
{{- end }}
