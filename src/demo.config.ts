import type { DemoConfig } from './types'

const technicalTopology = {
  boundary: { label: 'OpenShift namespace', detail: 'namespaced development candidate' },
  entry: { id: 'vm', kind: 'virtual-machine', label: 'VM client', detail: 'declared identity + correlation ID' },
  primaryPath: [
    { id: 'service', kind: 'service', label: 'Governed adapter Service', detail: 'declared destination only', endpoint: ':8080', edgeLabel: 'HTTP JSON' },
    { id: 'policy', kind: 'policy', label: 'NetworkPolicy', detail: 'default deny + labeled exception', edgeLabel: 'admit / refuse' },
    { id: 'adapter', kind: 'deployment', label: 'Decision adapter', detail: 'ordered deterministic checks', endpoint: 'POST /api/v1/modernize', edgeLabel: 'evaluate' },
  ],
  supportPath: [
    { id: 'identity', kind: 'evidence', label: 'Identity observations', detail: 'namespace · VM · VMI UID · service account', edgeLabel: 'compare' },
    { id: 'placement', kind: 'evidence', label: 'Placement observations', detail: 'node · architecture · required labels', edgeLabel: 'compare' },
    { id: 'record', kind: 'data', label: 'Correlated record', detail: 'checks · reasons · state · timestamp', edgeLabel: 'export' },
    { id: 'human', kind: 'authority', label: 'Human reviewer', detail: 'only action authority', edgeLabel: 'accept / reject' },
  ],
  optionalPath: { id: 'model', kind: 'external', label: 'Approved model', detail: 'bounded advisory only after controls pass', edgeLabel: 'optional HTTPS' },
}

export const demoConfig: DemoConfig = {
  id: 'virtualization-ai-401', title: 'Modernize VMs with Governed AI', subtitle: 'Identity, network, placement, and evidence across Red Hat OpenShift Virtualization and Intel', event: 'Level 301 decision story', audience: 'Application, virtualization, and platform engineers', cta: 'Decide whether the governed construction lab earns review.',
  brand: { primary: { name: 'Red Hat', logo: '/logos/redhat.svg', alt: 'Red Hat' }, partner: { name: 'Intel', logo: '/logos/intel.png', alt: 'Intel' }, attribution: 'Red Hat × Intel' },
  acts: [
    { id: 'decision', label: '00', title: 'The decision', scenes: [
      { id: 'intro', type: 'intro', beat: 'ordinary-world', title: 'A working contract is only the beginning', subtitle: 'Level 201 connected a VM to AI. Level 301 governs whether its evidence may be reviewed.', speakerPrompt: 'State the prerequisite precisely. Do not imply this factory ran the path on a VM.' },
      { id: 'reframe', type: 'reframe', beat: 'stakes', eyebrow: 'The operational gap', title: 'Reachable does not mean governed', before: 'The request returned', after: 'The caller, path, placement, and record agree', detail: 'A mismatch must REFUSE. Missing evidence must ABSTAIN. ALLOW_REVIEW still requires a human.', speakerPrompt: 'Name the three outcomes and emphasize that none changes a workload.' },
    ] },
    { id: 'architecture', label: '01', title: 'Control architecture', scenes: [
      { id: 'guided-architecture', type: 'guided-architecture', beat: 'system-reveal', eyebrow: 'Declare before observe', title: 'Reveal one control boundary at a time', body: 'Every question compares declared intent with an independent observation.', layers: [
        { id: 'identity', component: 'Identity', tone: 'primary', question: 'Which workload is asking?', answer: 'Namespace, VM name, VMI UID, and service account must be attributable.', detail: 'A mismatch is a hard REFUSE before any model call.', activeNodeIds: ['vm', 'identity'] },
        { id: 'network', component: 'Network', tone: 'primary', question: 'Which path was actually used?', answer: 'Service, port, policy state, and ready endpoints must match the declared destination.', detail: 'Reachability by itself is not path qualification.', activeNodeIds: ['service', 'policy'] },
        { id: 'placement', component: 'Placement', tone: 'partner', question: 'Where did the VMI run?', answer: 'Node, architecture, and required labels must be observed rather than inferred.', detail: 'The fixture demonstrates policy behavior; it is not Intel hardware proof.', activeNodeIds: ['placement'] },
        { id: 'evidence', component: 'Observability', tone: 'success', question: 'Can one record join every check?', answer: 'The same correlation ID, timestamp, ordered reason codes, and source state stay visible.', detail: 'Missing correlation yields ABSTAIN.', activeNodeIds: ['adapter', 'record'] },
        { id: 'authority', component: 'Human authority', tone: 'primary', question: 'Who can act?', answer: 'Only the named reviewer may accept evidence or authorize later work.', detail: 'HUMAN_REVIEW_REQUIRED: the adapter and model cannot deploy, migrate, promote, or certify.', activeNodeIds: ['human', 'model'] },
      ], technicalTopology, speakerPrompt: 'Pause after each question. Reveal declared intent, independent observation, and fail-closed result.' },
    ] },
    { id: 'proof', label: '02', title: 'Changed conditions', scenes: [
      { id: 'live', type: 'live-journey', beat: 'live-proof', eyebrow: 'REHEARSAL unless the endpoint proves LIVE', title: 'One contract, three governed outcomes', body: 'Run complete evidence, identity mismatch, and placement unknown through the same ordered policy.', cta: 'Run governed conditions', workspace: { label: 'Open the governed workspace', href: '/?act=2&scene=0' }, nodes: [
        { id: 'request', label: 'Declared request', detail: 'one correlation', tone: 'primary' },
        { id: 'controls', label: 'Deterministic controls', detail: 'identity → network → evidence → placement', tone: 'primary' },
        { id: 'advisory', label: 'Bounded advisory', detail: 'only after controls pass', tone: 'partner' },
        { id: 'record', label: 'Evidence record', detail: 'ordered reasons', tone: 'success' },
        { id: 'reviewer', label: 'Human reviewer', detail: 'authority retained', tone: 'primary' },
      ], technicalTopology, steps: [
        { id: 'allowed', title: 'Complete representative evidence', detail: 'Every deterministic check passes; fixture output permits review but claims no live AI.', adapterId: 'governed-allowed', activeNode: 4, activeNodeIds: ['vm', 'service', 'policy', 'adapter', 'identity', 'placement', 'record', 'human'], resultFields: [{ key: 'outcome', label: 'Outcome' }, { key: 'reason', label: 'Reason' }, { key: 'authority', label: 'Authority' }] },
        { id: 'refused', title: 'Identity mismatch', detail: 'Identity fails first; later controls and the model do not run.', adapterId: 'governed-refused', activeNode: 3, activeNodeIds: ['vm', 'identity', 'adapter', 'record', 'human'], resultFields: [{ key: 'outcome', label: 'Outcome' }, { key: 'reason', label: 'Reason' }, { key: 'authority', label: 'Authority' }] },
        { id: 'abstained', title: 'Placement observation missing', detail: 'Identity, network, and correlation pass; absent placement evidence yields ABSTAIN.', adapterId: 'governed-abstained', activeNode: 4, activeNodeIds: ['vm', 'service', 'policy', 'adapter', 'placement', 'record', 'human'], resultFields: [{ key: 'outcome', label: 'Outcome' }, { key: 'reason', label: 'Reason' }, { key: 'authority', label: 'Authority' }] },
      ], speakerPrompt: 'Say REHEARSAL before interpreting fixtures. LIVE needs complete current-session identities and observations.' },
      { id: 'decision-matrix', type: 'comparison', beat: 'trials', title: 'The outcome follows evidence quality', columns: [
        { label: 'Complete', value: 'ALLOW_REVIEW', detail: 'Evidence may be reviewed; no operational action is authorized.', tone: 'success' },
        { label: 'Mismatch', value: 'REFUSE', detail: 'Known unsafe identity, network, or placement disagreement.', tone: 'danger' },
        { label: 'Unknown', value: 'ABSTAIN', detail: 'Missing correlation, placement, or model evidence.', tone: 'partner' },
      ], speakerPrompt: 'Explain why mismatch and absence differ while both fail closed.' },
    ] },
    { id: 'mechanisms', label: '03', title: 'Why it holds', scenes: [
      { id: 'mechanisms', type: 'mechanisms', beat: 'trials', eyebrow: 'Mechanisms', title: 'Policy is observable and ordered', body: 'These controls make the result repeatable without granting automation authority.', mechanisms: [
        { id: 'precedence', label: 'Refusal precedence', claim: 'Identity and network decide before model use.', detail: 'Unsafe callers and paths never become prompts.', tone: 'primary' },
        { id: 'correlation', label: 'One evidence key', claim: 'Every check retains one correlation identifier.', detail: 'A missing join becomes an abstention, not a guessed record.', tone: 'success' },
        { id: 'placement', label: 'Observed placement', claim: 'Required labels must be present in evidence.', detail: 'REHEARSAL labels exercise logic; only target receipts support hardware claims.', tone: 'partner' },
      ], speakerPrompt: 'Keep mechanisms causal: show which input changes which outcome.' },
    ] },
    { id: 'handoff', label: '04', title: 'Evidence and handoff', scenes: [
      { id: 'payoff', type: 'evidence-payoff', beat: 'transformation', eyebrow: 'What this session established', title: 'A decision record with an honest limit', adapterIds: ['governed-allowed', 'governed-refused', 'governed-abstained'], fallbackLine: 'Run the governed conditions to populate this payoff', evidenceFields: [{ key: 'outcome', label: 'Latest outcome' }, { key: 'reason', label: 'Ordered reason' }, { key: 'authority', label: 'Authority' }], line1: 'The same contract allowed review, refused a mismatch, and abstained on absence.', line2: 'Launchpad still owns live execution, measurement, cleanup, certification, and promotion.', cta: 'Close the story and build the controls in the separate Showroom lab →', speakerPrompt: 'Recap only conditions run in this browser session. Stop before certification.' },
    ] },
  ],
  journeyHandoffs: [{ depth: 'lab', title: 'Governed construction lab', duration: '90–120 minutes', question: 'Can the learner declare, observe, compare, refuse, review, and reclaim?', technology: 'OpenShift Virtualization · NetworkPolicy · typed evidence · governed AI', instruction: 'Open the separate Showroom and produce a human-reviewed evidence bundle.' }],
}
