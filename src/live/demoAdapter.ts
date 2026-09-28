import { createJsonAdapter, registerAdapter } from './adapters'

const request = {
  schema_version: 'virtualization-ai.redhat-intel.com/modernization-request/v1', correlation_id: '30100000-0000-4000-8000-000000000001', task: 'review-vm-modernization', note: 'Review the governed path for this synthetic VM.', allowed_categories: ['identity', 'connectivity', 'placement', 'operations', 'unknown'],
  declared: { identity: { namespace: 'virtualization-ai-301', vm_name: 'modernization-client', service_account: 'vm-modernization-client' }, destination: { service: 'virtualization-ai-301-adapter', port: 8080 }, placement: { architecture: 'amd64', required_labels: { 'feature.node.kubernetes.io/cpu-model.vendor_id': 'Intel' } } },
  observed: { identity: { namespace: 'virtualization-ai-301', vm_name: 'modernization-client', service_account: 'vm-modernization-client', vmi_uid: 'rehearsal-vmi-uid' }, destination: { service: 'virtualization-ai-301-adapter', port: 8080, network_policy: 'ENFORCED', endpoints_ready: true }, placement: { node_name: 'rehearsal-node', architecture: 'amd64', required_labels: {}, labels: { 'feature.node.kubernetes.io/cpu-model.vendor_id': 'Intel' } }, observability: { correlation_id: '30100000-0000-4000-8000-000000000001', collected_at: '2026-09-28T12:00:00Z', events_available: true } },
}

const fixtures = {
  allowed: { outcome: 'ALLOW_REVIEW', reason: 'CONTROLS_COMPLETE', authority: 'HUMAN_REVIEW_REQUIRED', source_state: 'REHEARSAL' },
  refused: { outcome: 'REFUSE', reason: 'IDENTITY_MISMATCH', authority: 'HUMAN_REVIEW_REQUIRED', source_state: 'REHEARSAL' },
  abstained: { outcome: 'ABSTAIN', reason: 'PLACEMENT_UNKNOWN', authority: 'HUMAN_REVIEW_REQUIRED', source_state: 'REHEARSAL' },
}

for (const [id, data] of Object.entries(fixtures)) {
  const body = structuredClone(request)
  if (id === 'refused') body.observed.identity.vm_name = 'different-vm'
  if (id === 'abstained') delete (body.observed.placement as { node_name?: string }).node_name
  registerAdapter(createJsonAdapter({ id: `governed-${id}`, url: '/api/v1/modernize', method: 'POST', body, timeoutMs: 2_500, rehearsal: { data, collectedAt: '2026-09-28T12:00:00.000Z' } }))
}
