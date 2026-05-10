# Qwen3.5-27B

Slug: `qwen3.5-27b`
Family: `qwen`
Status: `sourcing`

## Sources

The authoritative source list is `data/sources/qwen3.5-27b/manifest.json` (committed).
This section is for human notes — links to register, candidates considered, rationale.

Planned sources:

- [ ] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3.5-27B/raw/main/config.json`
- [ ] `tokenizer_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.5-27B/raw/main/tokenizer_config.json`
- [ ] `preprocessor_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.5-27B/raw/main/preprocessor_config.json`
- [ ] `model_card` (`model_card`) — `https://huggingface.co/Qwen/Qwen3.5-27B/raw/main/README.md`
- [ ] `blog` (`blog_html`) — `https://qwen.ai/blog?id=qwen3.5`

Considered but excluded:

- Same as `qwen3.5-35b-a3b` — no standalone non-Omni Qwen3.5 arXiv paper. If/when
  one appears, register it as `paper`.

## Open questions

- [ ] Same hybrid-backbone schema gap as the MoE sibling (see
  `qwen3.5-35b-a3b.md`) — `architecture.attention` cannot represent the
  `(3 × DeltaNet → 1 × Gated Attention)` layer pattern.
- [ ] **Dense FFN intermediate** is 17408 per HF model card. With dense FFN (no
  MoE), how does this compare to Qwen3-32B's 25600? Width/depth tradeoff against
  the new attention budget?
- [ ] **Cross-version dense compare**: Qwen3-32B is 64 layers / hidden 5120, FFN
  25600, full GQA. Qwen3.5-27B is also 64 layers / hidden 5120 but with hybrid
  backbone and FFN 17408. The "saved" FFN budget presumably went into the
  Gated DeltaNet + Gated Attention machinery.

## Resolved

- (none yet)

## Inferred fields (closed models only)

N/A — Qwen3.5-27B is open-weight (Apache 2.0).

## Notes

**HF model card snapshot:**

- Total params 27B (no activation count — dense)
- 64 layers, hidden 5120, **hybrid backbone**: 16 outer blocks of `(3×(Gated DeltaNet→FFN) + 1×(Gated Attention→FFN))`
- Gated DeltaNet: 48 V-heads, 16 QK-heads, head_dim 128
- Gated Attention: GQA 24Q/4KV, head_dim 256, RoPE dim 64
- FFN dense: intermediate 17408
- Context: 262144 native, YaRN-extensible to 1010000
- Native VL: "Causal Language Model with Vision Encoder"
- Chat template: same as MoE sibling (thinking by default, `<think>...</think>`,
  `enable_thinking=False` to disable, `/think` and `/nothink` soft switches)
- License: Apache 2.0
- Release: Feb 2026

The Qwen3.5-27B is the closest analogue to our existing Qwen3-32B for
cross-generation architecture comparison (similar depth and hidden, no MoE).
