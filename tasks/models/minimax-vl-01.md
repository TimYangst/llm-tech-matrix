# MiniMax-VL-01

Slug: `minimax-vl-01`
Family: `minimax-01`
Status: `extracted`
Snapshot: `2026-10-22`

## Sources

Authoritative byte/hash list: `data/sources/minimax-vl-01/manifest.json`. HF assets pin full commit SHAs; technical reports pin arXiv versions. Mutable announcement pages are identified by fetched SHA256.

- [config](https://huggingface.co/MiniMaxAI/MiniMax-VL-01/resolve/308b79934be140a43a0fb80f82b4e20d0ebe3cb8/config.json) — Official MiniMax-VL-01 config.json, pinned HF revision 308b79934be140a43a0fb80f82b4e20d0ebe3cb8
- [readme](https://huggingface.co/MiniMaxAI/MiniMax-VL-01/resolve/308b79934be140a43a0fb80f82b4e20d0ebe3cb8/README.md) — Official MiniMax-VL-01 README.md, pinned HF revision 308b79934be140a43a0fb80f82b4e20d0ebe3cb8
- [paper](https://arxiv.org/pdf/2501.08313v1) — Official technical report, pinned arXiv revision 2501.08313v1

## Evidence and scope

Architecture dimensions are read from this checkpoint config, not inherited from sibling models. Training claims cite named report sections and distinguish original-base/series-wide results from checkpoint-specific evidence. `open_weights` describes downloadable parameters without claiming full training reproducibility.

## Open questions

- [ ] VL-01 supported user-facing context remains unresolved: checkpoint text_config says 8192, the shared report describes Text-01 trained 1M/extrapolated 4M; vendor does not reconcile the VL-specific limit.
- [ ] VL-01 model card says 512B multimodal tokens; paper stage budgets 80B+420B+44.8B sum to 544.8B. Neither figure is silently chosen as an exact whole-model total.
- [ ] Vision training count differs by unit/scope: card says 694M image-caption pairs; paper §6.2.2 says 37B low-resolution training pairs followed by 1.2B high-resolution pairs. Likely repeated exposures versus unique pairs, but not equated without an explicit statement.
- [ ] Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

## Validation

Pydantic schema v8 validation passed; English/Chinese Markdown rendered deterministically. Independent review remains with coordinator.
