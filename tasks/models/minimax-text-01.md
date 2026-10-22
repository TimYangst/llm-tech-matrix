# MiniMax-Text-01

Slug: `minimax-text-01`
Family: `minimax-01`
Status: `extracted`
Snapshot: `2026-10-22`

## Sources

Authoritative byte/hash list: `data/sources/minimax-text-01/manifest.json`. HF assets pin full commit SHAs; technical reports pin arXiv versions. Mutable announcement pages are identified by fetched SHA256.

- [config](https://huggingface.co/MiniMaxAI/MiniMax-Text-01/resolve/a7351bf2bee0e1253919d349f1ad304e6dac13e9/config.json) — Official MiniMax-Text-01 config.json, pinned HF revision a7351bf2bee0e1253919d349f1ad304e6dac13e9
- [readme](https://huggingface.co/MiniMaxAI/MiniMax-Text-01/resolve/a7351bf2bee0e1253919d349f1ad304e6dac13e9/README.md) — Official MiniMax-Text-01 README.md, pinned HF revision a7351bf2bee0e1253919d349f1ad304e6dac13e9
- [paper](https://arxiv.org/pdf/2501.08313v1) — Official technical report, pinned arXiv revision 2501.08313v1

## Evidence and scope

Architecture dimensions are read from this checkpoint config, not inherited from sibling models. Training claims cite named report sections and distinguish original-base/series-wide results from checkpoint-specific evidence. `open_weights` describes downloadable parameters without claiming full training reproducibility.

## Open questions

- [ ] Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

## Validation

Pydantic schema v8 validation passed; English/Chinese Markdown rendered deterministically. Independent review remains with coordinator.
