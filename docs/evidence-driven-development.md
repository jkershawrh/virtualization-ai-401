# Evidence-driven development checkpoint

CDD fixed the operation, evidence, authority, validation, and decision
contracts before implementation. TDD then captured failing gates for the
seven-state journey, digest-bound approval, dependency degradation, split
infrastructure/application outcomes, persistent evidence, packaging, and the
noncertifying handoff.

EDD accepts a candidate only when produced evidence supports the claim:

- contract examples validate against versioned JSON Schemas;
- the deterministic workload suite exercises `ALLOW_REVIEW`, `REFUSE`, and
  `ABSTAIN`, including reload of the fsynced JSONL ledger;
- visual and unit checks cover exactly seven presentation scenes;
- Helm renders a PVC-backed, non-root, tokenless operations adapter;
- the Showroom remains a separate 90–120 minute lab;
- the local rehearsal removes its temporary process and ledger directory; and
- the exact-source release workflow must publish Linux/AMD64 images, scan with
  zero HIGH/CRITICAL findings, generate SPDX SBOMs, keylessly sign, attach SLSA
  provenance, and pull each image by exact digest.

Factory receipts remain `REHEARSAL`. Launchpad alone can produce target `LIVE`,
capacity, cleanup, certification, and promotion evidence.
