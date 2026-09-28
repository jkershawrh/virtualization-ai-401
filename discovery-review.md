# Discovery review

## Decision

Proceed as a distinct 401 catalog item after Virtualization + AI 301. The 301
item establishes identity, network, placement, observability, and a governed AI
advisory path. The 401 item earns its level by operating that same system through
maintenance, migration, dependency failure, and recovery without losing policy,
correlation, or human control.

## Established patterns selected

| Source | Exact revision | Reused pattern | Boundary |
|---|---|---|---|
| Virtualization + AI 401 | pending published immutable receipt | Triforce-derived presentation shell, governed adapter, evidence chain, handoff schema | No implementation copy until the revision and digests are final |
| Virtualization + AI 201 | `70a35189cce95b87240734ec7961a67685d4cb27` | workload-to-model separation and honest rehearsal state | Prerequisite only |
| OpenShift Virtualization Roadshow 2026 | `5d296c9c9fbe773af09c16935c78b89baebd1f81` | VM lifecycle, live migration, snapshots, restore, backup/recovery concepts | Selected operational concepts; no wholesale content copy |

## 401 capability boundary

Included:

- preflight and evidence snapshot before an operation;
- planned live migration with readiness and rollback gates;
- AI dependency outage and degraded-mode behavior;
- application continuity and correlation verification;
- snapshot/restore decision framing and recovery validation;
- explicit human approval and a durable operation receipt.

Excluded from the factory:

- unattended remediation;
- destructive node operations;
- production disaster-recovery claims;
- fleet-scale capacity or 501 certification claims;
- claims about Intel hardware without observed node and workload evidence;
- Migration Toolkit for Virtualization provisioning unless separately approved.

## Proposed architecture

The application VM remains the system of record. A namespace-scoped operations
adapter reads KubeVirt/OpenShift state and produces normalized evidence. A
deterministic policy evaluates readiness and chooses ALLOW_REVIEW, REFUSE, or
ABSTAIN. An optional LLM may explain evidence but cannot select or execute an
operation. The operator approves an operation, observes KubeVirt progress, and
validates application, network, storage, model-adapter, and evidence continuity.

## Open discovery items

- destination OpenShift and OpenShift Virtualization versions;
- storage classes supporting RWX migration and snapshot APIs;
- migration policy and node-drain permissions available to a participant;
- approved application health probe and rollback action;
- approved model endpoint and whether the AI path must remain available during
  VM movement;
- observable Intel node identity, placement, allocation, and utilization;
- Launchpad seat isolation, timeout, reset, and reclaim behavior.
