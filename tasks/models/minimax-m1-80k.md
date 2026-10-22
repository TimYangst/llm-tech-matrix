# MiniMax-M1-80k

Slug: `minimax-m1-80k`
Family: `minimax-m1`
Status: `extracted`
Snapshot: `2026-10-22`

## Sources

Authoritative byte/hash list: `data/sources/minimax-m1-80k/manifest.json`. HF assets pin full commit SHAs; technical reports pin arXiv versions. Mutable announcement pages are identified by fetched SHA256.

- [config](https://huggingface.co/MiniMaxAI/MiniMax-M1-80k/resolve/8d1494b1a260e22040d5b9b2eb332eb44500b34d/config.json) — Official MiniMax-M1-80k config.json, pinned HF revision 8d1494b1a260e22040d5b9b2eb332eb44500b34d

- [readme](https://huggingface.co/MiniMaxAI/MiniMax-M1-80k/resolve/8d1494b1a260e22040d5b9b2eb332eb44500b34d/README.md) — Official MiniMax-M1-80k README.md, pinned HF revision 8d1494b1a260e22040d5b9b2eb332eb44500b34d

- [paper](https://arxiv.org/pdf/2506.13585v1) — Official technical report, pinned arXiv revision 2506.13585v1

- [architecture-paper](https://arxiv.org/pdf/2501.08313v1) — MiniMax-01 report explicitly cited for predecessor backbone and parallelism; not current M1 post-training evidence.

## Evidence and scope

Architecture dimensions are read from this checkpoint config, not inherited from sibling models. Training claims cite named report sections and distinguish original-base/series-wide results from checkpoint-specific evidence. `open_weights` describes downloadable parameters without claiming full training reproducibility.

## Open questions

- [ ] M1-40k and HF-compatible repackagings are not separate canonical records in this collection. Exact per-variant weight/dtype differences require future audit.
- [ ] Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

## Validation

Pydantic schema v8 validation passed; English/Chinese Markdown rendered deterministically. Independent review remains with coordinator.
