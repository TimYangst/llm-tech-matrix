# Google TPU7x (Ironwood) public snapshot

- Status: extracted; independent review pending.
- Snapshot: 2026-10-22. Scope: one physical accelerator (TPU7x whole chip; two chiplets).
- Sources: [manifest](../../data/sources/hardware/google-tpu7x-ironwood/manifest.json). SHA256 receipts recorded; raw files cached and gitignored.
- Canonical record: [JSON](../../data/extracted/hardware/google-tpu7x-ironwood.json).
- Policy: official public sources only; no internal measurements or experiments.

## Evidence checks

- Per-device values are taken directly from source specifications, without dividing pod/instance totals.
- Source capacity units are retained in notes when published as GiB.
- Unknown qualifiers remain explicit; no inferred sparse/dense conversion.

## Open questions

- Process technology, per-chip power, and exact matrix/vector decomposition remain undisclosed in this snapshot.
