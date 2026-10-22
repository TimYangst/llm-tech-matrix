# MiniMax-M3

Slug: `minimax-m3`
Family: `minimax-m3`
Status: `extracted`
Snapshot: `2026-10-22`

## Sources

Authoritative byte/hash list: `data/sources/minimax-m3/manifest.json`. HF assets pin full commit SHAs; technical reports pin arXiv versions. Mutable announcement pages are identified by fetched SHA256.

- [config](https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/config.json) — Official MiniMax-M3 config.json, pinned HF revision f0e1c1e04d40177e4673a22097036854f536e9c0
- [readme](https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/README.md) — Official MiniMax-M3 README.md, pinned HF revision f0e1c1e04d40177e4673a22097036854f536e9c0
- [chat_template](https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/chat_template.jinja) — Official MiniMax-M3 chat_template.jinja, pinned HF revision f0e1c1e04d40177e4673a22097036854f536e9c0
- [generation_config](https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/generation_config.json) — Official MiniMax-M3 generation_config.json, pinned HF revision f0e1c1e04d40177e4673a22097036854f536e9c0
- [paper](https://arxiv.org/pdf/2606.13392v1) — Official technical report, pinned arXiv revision 2606.13392v1
- [blog](https://www.minimax.io/blog/minimax-m3) — Official dated release announcement; mutable page archived by SHA256 on fetch

## Evidence and scope

Architecture dimensions are read from this checkpoint config, not inherited from sibling models. Training claims cite named report sections and distinguish original-base/series-wide results from checkpoint-specific evidence. `open_weights` describes downloadable parameters without claiming full training reproducibility.

## Open questions

- [ ] MSA paper experiments use a 109B MoE and 3T-token budget; these do not disclose production M3 (~428B, ~23B active) training tokens, optimizer, schedule or post-training pipeline.
- [ ] MSA typed top_k remains UNKNOWN because the config defines 16 blocks ×128 tokens, while schema field describes KV-entry count. Block count/size recorded explicitly in sparse_attention.notes.
- [ ] MTP config has num_mtp_modules=7 and num_nextn_predict_layers=1. Exact objective depth, horizon, loss weight and public weight shipment require further vendor/code evidence.
- [ ] MiniMax M3.1 Flash (October 19) is a later API release with weights promised later; it is not the M3 checkpoint or an open-weight update in this snapshot.
- [ ] Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

## Validation

Pydantic schema v8 validation passed; English/Chinese Markdown rendered deterministically. Independent review remains with coordinator.
