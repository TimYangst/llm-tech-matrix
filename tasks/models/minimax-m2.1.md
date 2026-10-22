# MiniMax-M2.1

Slug: `minimax-m2.1`
Family: `minimax-m2`
Status: `extracted`
Snapshot: `2026-10-22`

## Sources

Authoritative byte/hash list: `data/sources/minimax-m2.1/manifest.json`. HF assets pin full commit SHAs; technical reports pin arXiv versions. Mutable announcement pages are identified by fetched SHA256.

- [config](https://huggingface.co/MiniMaxAI/MiniMax-M2.1/resolve/cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c/config.json) — Official MiniMax-M2.1 config.json, pinned HF revision cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c
- [readme](https://huggingface.co/MiniMaxAI/MiniMax-M2.1/resolve/cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c/README.md) — Official MiniMax-M2.1 README.md, pinned HF revision cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c
- [chat_template](https://huggingface.co/MiniMaxAI/MiniMax-M2.1/resolve/cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c/chat_template.jinja) — Official MiniMax-M2.1 chat_template.jinja, pinned HF revision cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c
- [generation_config](https://huggingface.co/MiniMaxAI/MiniMax-M2.1/resolve/cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c/generation_config.json) — Official MiniMax-M2.1 generation_config.json, pinned HF revision cd97f59135f37b2a6bf09356e485d5e4aeb7dc9c
- [paper](https://arxiv.org/pdf/2605.26494v1) — Official technical report, pinned arXiv revision 2605.26494v1
- [blog](https://www.minimax.io/news/minimax-m21) — Official dated release announcement; mutable page archived by SHA256 on fetch

## Evidence and scope

Architecture dimensions are read from this checkpoint config, not inherited from sibling models. Training claims cite named report sections and distinguish original-base/series-wide results from checkpoint-specific evidence. `open_weights` describes downloadable parameters without claiming full training reproducibility.

## Open questions

- [ ] The M2-series report retrospectively describes a common base and evolving data/RL system; exact additional tokens, optimizer, learning-rate schedule and per-version run configuration remain undisclosed.
- [ ] MTP config metadata is not proof that every configured draft tensor is in the public checkpoint. Objective depth is supported by the paper; shipment remains UNKNOWN without tensor-index audit.
- [ ] December 2025 release emphasizes multilingual development, native applications and concise responses; shared architecture values are read from this checkpoint config, not copied from M2.
- [ ] Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

## Validation

Pydantic schema v8 validation passed; English/Chinese Markdown rendered deterministically. Independent review remains with coordinator.
