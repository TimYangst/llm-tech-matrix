# AWS Inferentia2 public snapshot

- Status: extracted; independent review pending.
- Snapshot: 2026-10-22. Scope: one physical accelerator (inferentia2 chip).
- Sources: [manifest](../../data/sources/hardware/aws-inferentia2/manifest.json). SHA256 receipts recorded; raw files cached and gitignored.
- Canonical record: [JSON](../../data/extracted/hardware/aws-inferentia2.json).
- Policy: official public sources only; no internal measurements or experiments.

## Evidence checks

- Per-device values are taken directly from source specifications, without dividing pod/instance totals.
- Source capacity units are retained in notes when published as GiB.
- Unknown qualifiers remain explicit; no inferred sparse/dense conversion.

## Open questions

- Per-chip TDP, manufacturing process and exact matrix/vector chip throughput require additional public evidence.
