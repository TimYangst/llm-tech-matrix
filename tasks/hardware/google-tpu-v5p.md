# Google TPU v5p public snapshot

- Status: extracted; independent review pending.
- Snapshot: 2026-10-22. Scope: one physical accelerator (v5p chip).
- Sources: [manifest](../../data/sources/hardware/google-tpu-v5p/manifest.json). SHA256 receipts recorded; raw files cached and gitignored.
- Canonical record: [JSON](../../data/extracted/hardware/google-tpu-v5p.json).
- Policy: official public sources only; no internal measurements or experiments.

## Evidence checks

- Per-device values are taken directly from source specifications, without dividing pod/instance totals.
- Source capacity units are retained in notes when published as GiB.
- Unknown qualifiers remain explicit; no inferred sparse/dense conversion.

## Open questions

- Per-chip power, process technology, and exact matrix/vector decomposition are not disclosed in this source snapshot.
