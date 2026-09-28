# Virtualization + AI 401 — Operate Hybrid VM and AI Workloads

This repository is the factory workspace for the 401-level Red Hat + Intel
Virtualization and AI catalog item. It teaches an operator to preserve service,
evidence, and human authority while a virtual machine and its AI advisory path
move through maintenance and failure conditions.

The candidate implementation is built from the exact immutable Virtualization
+ AI 301 source revision `91e30a4af72bb4a15a4e5dfe2f29abb5692c698f`. It is
not orderable, certified, or promoted. The default runtime is `REHEARSAL`.

## Learner outcome

Given a production-shaped VM-backed application with an advisory AI service,
the learner can inspect readiness, choose a governed day-two operation, observe
the operation end to end, verify application and evidence continuity, and stop
or recover when policy or evidence is incomplete.

## Factory boundary

- Presentation and lab are separate deliverables.
- Factory evidence is REHEARSAL unless a destination cluster proves otherwise.
- Model, provider, Intel CPU placement, and utilization are never inferred.
- Migration, recovery, and any external action require explicit human approval.
- The adapter never performs an operation or remediation; it evaluates supplied
  evidence and durably records the seven-state journey.
- Launchpad owns source approval, trusted rendering, live-seat qualification,
  capacity testing, reclaim verification, certification, and promotion.

## Local verification

`npm run check` validates the contracts, deterministic adapter, chart,
presentation, separate Showroom, offline behavior, and immutable-release gates.
The complete rehearsal also verifies ledger reload after a process restart and
removes its temporary runtime directory before writing the factory receipts.
