# Intel Gaudi 3 OAM public snapshot

- Status: extracted; independent review pending.
- Snapshot: 2026-10-22. Scope: one physical accelerator (HL-325L OAM).
- Sources: [manifest](../../data/sources/hardware/intel-gaudi3-oam/manifest.json). SHA256 receipts recorded; raw files cached and gitignored.
- Canonical record: [JSON](../../data/extracted/hardware/intel-gaudi3-oam.json).
- Policy: official public sources only; no internal measurements or experiments.

## Evidence checks

- Per-device values are taken directly from source specifications, without dividing pod/instance totals.
- Source capacity units are retained in notes when published as GiB.
- Unknown qualifiers remain explicit; no inferred sparse/dense conversion.

## Open questions

- Table 5 does not specify sparse/dense conditions, accumulation precision, clock or FMA counting.
