# Qwen3.5-27B

Slug: `qwen3.5-27b`
Family: `qwen`
Status: `extracted`

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

(See `data/extracted/qwen3.5-27b.json` `open_questions` for the authoritative list
of unresolved items surfaced during extraction — pre-training optimizer/LR/data
mix, MTP step depth D, post-training pipeline structure, mixed-precision recipe,
parallelism, vision-pathway training. README/blog disclose vendor highlights only;
no separate Qwen3.5 tech report exists at extraction time.)

## Resolved

- ✅ **Hybrid-backbone schema gap** — resolved by schema v4 (`Attention.variants[]`
  and `layer_pattern`) ahead of extraction. The 16 × (3 GatedDeltaNet, 1
  GatedAttention) layout is captured cleanly via two `AttentionVariant` entries
  and a textual `layer_pattern`. Source: `src/llm_tech_matrix/schema.py` v4 and
  `docs/conventions.md` schema changelog.
- ✅ **Dense FFN width vs Qwen3-32B** — confirmed 17408 (per HF README and
  `config.intermediate_size`); Qwen3-32B is 25600. Captured under
  `architecture.ffn.layer_partition` with cross-version commentary on the
  reallocation toward hybrid-backbone machinery.
- ✅ **Cross-version dense compare structure** — extraction notes the same depth
  (64L) and hidden (5120) as Qwen3-32B but the attention budget now flows through
  16 GQA layers (24Q:4KV with output gate + partial RoPE) plus 48 Gated DeltaNet
  layers, replacing 64 dense GQA layers. Recorded in `architecture.ffn.layer_partition`.

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
