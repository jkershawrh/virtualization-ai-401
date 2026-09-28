{{- define "virtualization-ai-301.labels" -}}
app.kubernetes.io/part-of: virtualization-ai-301
app.kubernetes.io/managed-by: {{ .Release.Service }}
lab.redhat.com/candidate: virtualization-ai-301
{{- end }}
{{- define "virtualization-ai-301.image" -}}
{{- if .digest -}}{{ .repository }}@{{ .digest }}{{- else -}}{{ .repository }}:{{ .tag }}{{- end -}}
{{- end }}
