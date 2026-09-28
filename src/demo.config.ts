import type { DemoConfig } from './types'

const technicalTopology = {
  boundary: { label: 'Governed operations boundary', detail: 'namespaced candidate; no cluster mutation authority' },
  entry: { id: 'operator', kind: 'authority', label: 'Human operator', detail: 'requests and explicitly approves an operation' },
  primaryPath: [
    { id: 'observe', kind: 'evidence', label: 'Observed state', detail: 'current identity, compatibility, and health', edgeLabel: 'snapshot' },
    { id: 'policy', kind: 'policy', label: 'Deterministic policy', detail: 'ALLOW_REVIEW · REFUSE · ABSTAIN', edgeLabel: 'evaluate' },
    { id: 'adapter', kind: 'deployment', label: 'Operations adapter', detail: 'records evidence; never remediates', endpoint: 'POST /api/v1/operations', edgeLabel: 'record' },
  ],
  supportPath: [
    { id: 'approval', kind: 'authority', label: 'Approval gate', detail: 'human · digest · expiry', edgeLabel: 'authorize review' },
    { id: 'operation', kind: 'external', label: 'External operation', detail: 'migration or recovery remains outside adapter authority', edgeLabel: 'observed result' },
    { id: 'application', kind: 'service', label: 'Application + AI path', detail: 'validated separately from infrastructure', edgeLabel: 'health' },
    { id: 'ledger', kind: 'data', label: 'Durable evidence ledger', detail: 'seven ordered, digest-bearing records', edgeLabel: 'learn' },
  ],
  optionalPath: { id: 'model', kind: 'external', label: 'Optional explainer', detail: 'describes a result; cannot decide or act', edgeLabel: 'LIVE identity required' },
}

export const demoConfig: DemoConfig = {
  id: 'virtualization-ai-401',
  title: 'Operate Hybrid VM and AI Workloads',
  subtitle: 'A governed day-two path for migration, recovery, dependency failure, and durable evidence',
  event: 'Virtualization + AI 401',
  audience: 'Virtualization administrators, platform operators, and AI platform owners',
  cta: 'Decide whether the operation and its service outcome are safe to review.',
  brand: { primary: { name: 'Red Hat', logo: '/logos/redhat.svg', alt: 'Red Hat' }, partner: { name: 'Intel', logo: '/logos/intel.png', alt: 'Intel' }, attribution: 'Red Hat × Intel' },
  acts: [
    { id: 'observe', label: '01', title: 'OBSERVE', scenes: [
      { id: 'observe', type: 'intro', beat: 'ordinary-world', eyebrow: 'OBSERVE', title: 'Infrastructure health is not service health', subtitle: 'A planned migration can complete while the application or its AI dependency still fails.', speakerPrompt: 'State REHEARSAL. Do not infer model, provider, Intel placement, or resource use.' },
    ] },
    { id: 'preflight', label: '02', title: 'PREFLIGHT', scenes: [
      { id: 'preflight', type: 'guided-architecture', beat: 'system-reveal', eyebrow: 'PREFLIGHT', title: 'Qualify the operation before proposing it', body: 'Each answer is observed evidence, never an assumption.', layers: [
        { id: 'identity', component: 'Identity', tone: 'primary', question: 'Is this the declared VM?', answer: 'Namespace and VM identity must match.', detail: 'A known mismatch produces REFUSE.', activeNodeIds: ['operator', 'observe', 'policy'] },
        { id: 'compatibility', component: 'Compatibility', tone: 'primary', question: 'Can network and storage move safely?', answer: 'Both compatibility checks must pass.', detail: 'A known incompatibility produces REFUSE.', activeNodeIds: ['observe', 'policy'] },
        { id: 'currency', component: 'Evidence', tone: 'success', question: 'Are facts fresh and correlated?', answer: 'Freshness and correlation must be explicit.', detail: 'Missing facts produce ABSTAIN.', activeNodeIds: ['observe', 'ledger'] },
        { id: 'authority', component: 'Authority', tone: 'partner', question: 'Who can approve execution?', answer: 'Only the named human with a matching, unexpired digest.', detail: 'The policy and optional model have no execution authority.', activeNodeIds: ['approval', 'model'] },
      ], technicalTopology, speakerPrompt: 'Reveal refusal before abstention, then the human approval boundary.' },
    ] },
    { id: 'propose', label: '03', title: 'PROPOSE', scenes: [
      { id: 'propose', type: 'reframe', beat: 'reframe', eyebrow: 'PROPOSE', title: 'A passing preflight is a proposal, not permission', before: 'The checks passed', after: 'ALLOW_REVIEW · HUMAN_APPROVAL_REQUIRED', detail: 'The operation digest freezes exactly what the reviewer is asked to approve.', speakerPrompt: 'Separate policy eligibility from human authorization.' },
    ] },
    { id: 'approve', label: '04', title: 'APPROVE', scenes: [
      { id: 'approve', type: 'trust-boundary', beat: 'stakes', eyebrow: 'APPROVE', title: 'Authority stays with the operator', zones: [
        { id: 'human', label: 'Human authority', boundary: 'may approve the exact operation digest', items: ['named reviewer', 'expiry', 'accept or reject'], tone: 'primary' },
        { id: 'adapter', label: 'Adapter authority', boundary: 'may evaluate and record only', items: ['deterministic policy', 'durable evidence', 'no remediation'], tone: 'success' },
        { id: 'model', label: 'Model authority', boundary: 'NONE', items: ['optional explanation', 'no decision override', 'no infrastructure action'], tone: 'partner' },
      ], speakerPrompt: 'A digest mismatch or expiry is REFUSE. No silent renewal exists.' },
    ] },
    { id: 'execute', label: '05', title: 'EXECUTE', scenes: [
      { id: 'execute', type: 'live-journey', beat: 'live-proof', eyebrow: 'EXECUTE · REHEARSAL', title: 'Run three conditions through one contract', body: 'The adapter records an external operation result; it does not perform the migration or recovery.', cta: 'Run governed operation conditions', nodes: [
        { id: 'request', label: 'Approved request', detail: 'digest + expiry', tone: 'primary' },
        { id: 'operation', label: 'Observed operation', detail: 'external execution', tone: 'primary' },
        { id: 'infrastructure', label: 'Infrastructure result', detail: 'complete or failed', tone: 'success' },
        { id: 'service', label: 'Application + AI path', detail: 'independent health', tone: 'partner' },
        { id: 'ledger', label: 'Evidence ledger', detail: 'seven states', tone: 'success' },
      ], technicalTopology, steps: [
        { id: 'healthy', title: 'Planned migration validates', detail: 'Infrastructure, application, AI dependency, and correlation all pass.', adapterId: 'operation-healthy', activeNode: 4, activeNodeIds: ['operator', 'approval', 'operation', 'application', 'ledger'], resultFields: [{ key: 'decision', label: 'Decision' }, { key: 'reason', label: 'Reason' }, { key: 'source_state', label: 'Source' }] },
        { id: 'dependency', title: 'AI dependency is unavailable', detail: 'Infrastructure and application pass; the AI path is degraded, so the result ABSTAINs.', adapterId: 'operation-dependency', activeNode: 4, activeNodeIds: ['operation', 'application', 'model', 'ledger'], resultFields: [{ key: 'decision', label: 'Decision' }, { key: 'reason', label: 'Reason' }, { key: 'source_state', label: 'Source' }] },
        { id: 'application', title: 'Infrastructure succeeds, application fails', detail: 'A completed platform operation cannot mask a failed service outcome.', adapterId: 'operation-application', activeNode: 4, activeNodeIds: ['operation', 'application', 'ledger'], resultFields: [{ key: 'decision', label: 'Decision' }, { key: 'reason', label: 'Reason' }, { key: 'source_state', label: 'Source' }] },
      ], speakerPrompt: 'Call out the split result: infrastructure PASS, application FAIL, overall REFUSE.' },
    ] },
    { id: 'validate', label: '06', title: 'VALIDATE', scenes: [
      { id: 'validate', type: 'comparison', beat: 'trials', eyebrow: 'VALIDATE', title: 'Validate the service, not just the operation', columns: [
        { label: 'Healthy migration', value: 'ALLOW_REVIEW', detail: 'Infrastructure PASS · application PASS · AI path PASS', tone: 'success' },
        { label: 'Dependency outage', value: 'ABSTAIN', detail: 'Infrastructure PASS · application PASS · AI path FAIL', tone: 'partner' },
        { label: 'Split failure', value: 'REFUSE', detail: 'Infrastructure PASS · application FAIL', tone: 'danger' },
      ], speakerPrompt: 'No model explanation is fabricated when the dependency is unavailable.' },
    ] },
    { id: 'learn', label: '07', title: 'LEARN', scenes: [
      { id: 'learn', type: 'evidence-payoff', beat: 'transformation', eyebrow: 'LEARN', title: 'The durable record preserves what happened—and what did not', adapterIds: ['operation-healthy', 'operation-dependency', 'operation-application'], fallbackLine: 'Run the three REHEARSAL conditions to populate the evidence payoff', evidenceFields: [{ key: 'decision', label: 'Decision' }, { key: 'reason', label: 'Reason' }, { key: 'source_state', label: 'Source' }], line1: 'OBSERVE → PREFLIGHT → PROPOSE → APPROVE → EXECUTE → VALIDATE → LEARN remains correlated.', line2: 'Launchpad still owns target execution, measurement, cleanup verification, certification, and promotion.', cta: 'Continue in the separate 90–120 minute Showroom lab →', speakerPrompt: 'Close on bounded proof and the noncertifying handoff.' },
    ] },
  ],
  journeyHandoffs: [{ depth: 'lab', title: 'Operate Hybrid VM and AI Workloads lab', duration: '90–120 minutes', question: 'Can the learner qualify, approve, validate, and reclaim a governed day-two operation?', technology: 'OpenShift Virtualization · deterministic policy · durable evidence · optional AI explanation', instruction: 'Use the separate Showroom lab; begin in REHEARSAL and stop before certification.' }],
}
