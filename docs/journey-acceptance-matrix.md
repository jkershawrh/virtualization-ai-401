# Journey acceptance matrix

| Stage | Learner action | Required proof | Unsafe result |
|---|---|---|---|
| Observe | Inspect VM, VMI, application, AI adapter, storage, network, and evidence state | Named resources, timestamps, provenance, and source labels | ABSTAIN when identity or freshness is unknown |
| Preflight | Select a bounded day-two operation | Readiness, migration policy, storage/network compatibility, health baseline | REFUSE on policy, identity, or network violation |
| Propose | Review deterministic policy result and optional explanation | Policy version, matched rules, evidence references, no LLM authority | No executable proposal from model text alone |
| Approve | Human accepts the exact operation envelope | Actor, operation, target, expiry, rollback, and approval receipt | No approval means no execution |
| Execute | Observe the OpenShift/KubeVirt operation | Correlated operation events and bounded timeout | Stop and preserve evidence on timeout or divergence |
| Validate | Recheck application and advisory AI path | Service health, network, storage, model path, placement, and correlation | Incomplete validation cannot be called recovered |
| Learn | Compare baseline and final receipts | Outcome, exceptions, timings, evidence-chain verification | No policy promotion inside the lab |

## Required scenarios

1. Planned migration succeeds and service validation passes.
2. Identity mismatch is refused before execution.
3. Network or storage incompatibility is refused before execution.
4. Missing placement or correlation evidence produces ABSTAIN.
5. AI dependency loss enters a labeled degraded path without blocking the VM
   operation when policy allows it.
6. Operation timeout preserves evidence and presents rollback/recovery choices.
7. Recovery validation catches an infrastructure-success/application-failure
   split outcome.
8. Cleanup removes all participant-scoped resources with zero residue.

