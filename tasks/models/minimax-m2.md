# MiniMax-M2

Slug: `minimax-m2`
Family: `minimax-m2`
Status: `extracted`
Snapshot: `2026-10-22`

## Sources

Authoritative byte/hash list: `data/sources/minimax-m2/manifest.json`. HF assets pin full commit SHAs; technical reports pin arXiv versions. Mutable announcement pages are identified by fetched SHA256.

- [config](https://huggingface.co/MiniMaxAI/MiniMax-M2/resolve/757303d492a50514c312788b5247a4f696a4c6a3/config.json) — Official MiniMax-M2 config.json, pinned HF revision 757303d492a50514c312788b5247a4f696a4c6a3
- [readme](https://huggingface.co/MiniMaxAI/MiniMax-M2/resolve/757303d492a50514c312788b5247a4f696a4c6a3/README.md) — Official MiniMax-M2 README.md, pinned HF revision 757303d492a50514c312788b5247a4f696a4c6a3
- [chat_template](https://huggingface.co/MiniMaxAI/MiniMax-M2/resolve/757303d492a50514c312788b5247a4f696a4c6a3/chat_template.jinja) — Official MiniMax-M2 chat_template.jinja, pinned HF revision 757303d492a50514c312788b5247a4f696a4c6a3
- [generation_config](https://huggingface.co/MiniMaxAI/MiniMax-M2/resolve/757303d492a50514c312788b5247a4f696a4c6a3/generation_config.json) — Official MiniMax-M2 generation_config.json, pinned HF revision 757303d492a50514c312788b5247a4f696a4c6a3
- [paper](https://arxiv.org/pdf/2605.26494v1) — Official technical report, pinned arXiv revision 2605.26494v1
- [blog](https://www.minimax.io/news/minimax-m2) — Official dated release announcement; mutable page archived by SHA256 on fetch

## Evidence and scope

Architecture dimensions are read from this checkpoint config, not inherited from sibling models. Training claims cite named report sections and distinguish original-base/series-wide results from checkpoint-specific evidence. `open_weights` describes downloadable parameters without claiming full training reproducibility.

## Open questions

- [ ] The M2-series report retrospectively describes a common base and evolving data/RL system; exact additional tokens, optimizer, learning-rate schedule and per-version run configuration remain undisclosed.
- [ ] MTP config metadata is not proof that every configured draft tensor is in the public checkpoint. Objective depth is supported by the paper; shipment remains UNKNOWN without tensor-index audit.
- [ ] Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

## Validation

Pydantic schema v8 validation passed; English/Chinese Markdown rendered deterministically. Independent review remains with coordinator.
