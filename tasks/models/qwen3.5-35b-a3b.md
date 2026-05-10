# Qwen3.5-35B-A3B

Slug: `qwen3.5-35b-a3b`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3.5-35b-a3b/manifest.json` (committed).
This section is for human notes — links to register, candidates considered, rationale.

Planned sources:

- [ ] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/config.json`
- [ ] `tokenizer_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/tokenizer_config.json` (contains the Jinja2 chat template)
- [ ] `preprocessor_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/preprocessor_config.json` (vision encoder image preprocessing)
- [ ] `model_card` (`model_card`) — `https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/README.md`
- [ ] `blog` (`blog_html`) — `https://qwen.ai/blog?id=qwen3.5` (Qwen Team's primary write-up; SPA so the saved HTML may be the JS shell only)

Considered but excluded:

- A standalone non-Omni Qwen3.5 arXiv tech report does not appear to exist as of
  May 2026; only `Qwen3.5-Omni Technical Report` (arXiv:2604.15804) is on arXiv,
  and that paper covers the audio/visual omni-extension rather than the LM
  backbone we're characterizing here. Could be revisited if the Omni paper
  redundantly documents the LM backbone too.

## Open questions

(See `data/extracted/qwen3.5-35b-a3b.json` `open_questions` for the authoritative
list of unresolved items surfaced during extraction — pre-training optimizer/LR/data
mix, MTP step depth D, post-training pipeline, mixed precision, parallelism, MoE
routing specifics beyond top-8 + 1 shared, why the shared expert was reintroduced
and why the LB strategy reverted from global-batch / aux-loss-free to classic
aux-loss with coef 0.001.)

## Resolved

- ✅ **Hybrid-backbone schema gap** — resolved by schema v4 (`Attention.variants[]`
  and `layer_pattern`) ahead of extraction. The 10 × (3 GatedDeltaNet, 1
  GatedAttention) layout is captured cleanly via two `AttentionVariant` entries
  and a textual `layer_pattern`.
- ✅ **Vision encoder details** — captured via the structured `Multimodal.vision_encoder`
  schema-v4 field (HF `vision_config` keys mirrored: depth=27, hidden=1152,
  intermediate=4304, num_heads=16, patch=16, spatial_merge=2, temporal_patch=2,
  out_hidden_size=2048). Encoder geometry matches Qwen3.5-27B exactly except for
  the projected output dim, which tracks LM hidden (2048 here, 5120 for the
  dense 27B); whether weights are literally shared between the variants remains
  open.
- ✅ **Shared expert reintroduction confirmed** — `shared_expert_intermediate_size=512`
  in config and "8 Routed + 1 Shared" on the HF model card. Design rationale
  remains undisclosed; carried forward in the extraction's `open_questions`.

## Inferred fields (closed models only)

N/A — Qwen3.5-35B-A3B is open-weight (Apache 2.0 per the HF model card).

## Notes

**HF model card snapshot** (for orientation; canonical source is `manifest.json`):

- Total params 35B, activated 3B per token
- 40 layers, hidden 2048, **hybrid backbone** in 10 outer blocks of `(3×(Gated DeltaNet→MoE) + 1×(Gated Attention→MoE))`
- Gated DeltaNet: 32 V-heads, 16 QK-heads, head_dim 128
- Gated Attention: GQA 16Q/2KV, head_dim 256, RoPE dim 64
- MoE: 256 experts × 512 expert intermediate dim, 8 routed + 1 shared per token
- Context: 262144 native; YaRN-extensible to 1010000
- Native VL: "Causal Language Model with Vision Encoder"
- Chat template: thinking-by-default, `<think>...</think>` block, `enable_thinking=False` in `chat_template_kwargs` to disable; `/think` references appear 5x in the Jinja template
- License: Apache 2.0
- Release: Feb 2026

**Findings already surfaced from `data/sources/qwen3.5-35b-a3b/config.json`:**

- `model_type: "qwen3_5_moe"`, `architectures: ["Qwen3_5MoeForConditionalGeneration"]` — net-new HF model class.
- `text_config.layer_types[]` explicitly enumerates the 40-entry per-layer pattern (`linear_attention` vs `full_attention`); `full_attention_interval: 4` codifies the 1-in-4 rhythm.
- `text_config.mtp_num_hidden_layers: 1` — **MTP is already present in Qwen3.5** (1 MTP layer); Qwen3.6's "trained with multi-steps" note will be the *step-depth* extension, not introduction.
- `text_config.shared_expert_intermediate_size: 512` confirms the 1 shared expert (matches HF model card "8 routed + 1 shared").
- `text_config.rope_parameters.mrope_interleaved: true` + `rope_theta: 10000000` — multimodal RoPE with base 1e7 (Qwen3 used 1e6).
- `vision_config` is a separate top-level subobject with `depth: 27` etc. — vision encoder details are inline in the same config.json.

**User-specified focus areas** (per session prompt):

1. **Changes vs Qwen3** — capture the hybrid Gated DeltaNet+MoE shift, native VL,
   shared-expert reintroduction, expanded context (32K→262K native), and the
   vision encoder.
2. **Chat template** — diff against Qwen3's template (especially the soft-switch
   token semantics, thinking block format, multi-turn history-pruning rule).
