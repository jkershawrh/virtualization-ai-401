import { createJsonAdapter, registerAdapter } from './adapters'

const base = {
  schema_version: 'demo-story.redhat-intel.com/virtualization-ai-401/operation-request/v1',
  request_id: 'op-401-migration-healthy', operation: 'LIVE_MIGRATE',
  target: { namespace: 'virtualization-ai-401', virtual_machine: 'hybrid-workload' }, requested_by: 'platform-operator',
  evidence_snapshot: [{ schema_version: 'demo-story.redhat-intel.com/virtualization-ai-401/evidence/v1', evidence_id: 'snapshot-401-healthy', request_id: 'op-401-migration-healthy', state: 'OBSERVE', kind: 'KUBEVIRT', source: 'rehearsal-fixture', source_state: 'REHEARSAL', observed_at: '2026-09-28T18:00:00Z', freshness: 'FRESH', digest: `sha256:${'a'.repeat(64)}`, payload: { vm_identity: 'hybrid-workload' } }],
  preflight: { identity_match: true, network_compatible: true, storage_compatible: true, evidence_fresh: true, correlation_complete: true },
  approval: { approved_by: 'change-reviewer', expires_at: '2027-09-28T18:30:00Z', operation_digest: 'sha256:89d7a0bf610a6284b20a5da4cfce58b8c413459f46204f536036b28250cf61f0' },
  observed_result: { operation_complete: true, infrastructure_success: true, application_healthy: true, ai_dependency_healthy: true, correlation_continuity: true },
}

const cases = {
  healthy: { body: base, data: { decision: 'ALLOW_REVIEW', reason: 'VALIDATION_COMPLETE', source_state: 'REHEARSAL' } },
  dependency: { body: { ...base, request_id: 'op-401-ai-dependency-outage', observed_result: { ...base.observed_result, ai_dependency_healthy: false } }, data: { decision: 'ABSTAIN', reason: 'AI_DEPENDENCY_UNAVAILABLE', source_state: 'REHEARSAL' } },
  application: { body: { ...base, request_id: 'op-401-application-failure', operation: 'VALIDATE_RECOVERY', observed_result: { ...base.observed_result, application_healthy: false } }, data: { decision: 'REFUSE', reason: 'APPLICATION_FAILED_AFTER_INFRA_SUCCESS', source_state: 'REHEARSAL' } },
}

for (const [id, item] of Object.entries(cases)) {
  registerAdapter(createJsonAdapter({ id: `operation-${id}`, url: '/api/v1/operations', method: 'POST', body: item.body, timeoutMs: 2_500, rehearsal: { data: item.data, collectedAt: '2026-09-28T18:05:00.000Z' } }))
}
