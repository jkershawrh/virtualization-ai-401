{{- define "virtualization-ai-401.labels" -}}
app.kubernetes.io/part-of: virtualization-ai-401
app.kubernetes.io/managed-by: {{ .Release.Service }}
lab.redhat.com/candidate: virtualization-ai-401
{{- end }}
{{- define "virtualization-ai-401.image" -}}
{{- if .digest -}}{{ .repository }}@{{ .digest }}{{- else -}}{{ .repository }}:{{ .tag }}{{- end -}}
{{- end }}
