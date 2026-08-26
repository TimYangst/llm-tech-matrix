# Qwen3.8-2.4T-A95B

Slug: `qwen3.8-2.4t-a95b`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3.8-2.4t-a95b/manifest.json` (committed).

Registered sources:

- [x] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/tokenizer_config.json`
- [x] `readme` (`model_card`) — `https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/README.md`
- [x] `blog` (`blog_html`) — `https://qwen.ai/blog?id=qwen3.8`

Considered but excluded:

- No arXiv paper.
- No `preprocessor_config.json` — this checkpoint is text-only.
- `Qwen/Qwen3.8-2.4T-A95B-FP8` — post-hoc serving quantization of the same weights.
- The repo's `LICENSE` (custom `qwen3.8-max` terms) is **not** registered — worth adding
  if licence terms become part of what the matrix tracks. Flagged in `open_questions`.

## Open questions

See `data/extracted/qwen3.8-2.4t-a95b.json` `open_questions`. The two that matter most:

1. **All published benchmarks are labelled "Qwen3.8-Max"**, i.e. measured on the hosted
   superset (vision, non-thinking, 1M default context, built-in tools), not on these open
   weights. There is no open-weights-only evaluation.
2. **The README asserts a 1,010,000-token ceiling but ships no YaRN block**, unlike every
   other Qwen 3.x card. `context_extension.method` and `.factor` are recorded UNKNOWN.

## Resolved

- ✅ **Is the open Max checkpoint multimodal?** No. `Type: Causal Language Model`, no
  `vision_config`, `pipeline_tag: text-generation`. Vision lives only in the hosted
  Qwen3.8-Max. This is the first Qwen 3.x open checkpoint that is *not* native-VL.
- ✅ **Does it keep a non-thinking mode?** No. The chat template raises
  `'Disabling thinking is not supported.'` — first model in the repo to drop the toggle.
- ✅ **Routing style** — classic aux-loss (`router_aux_loss_coef=0.001`), same as
  Qwen3.5-35B-A3B. Qwen still has not adopted aux-loss-free bias routing at any scale.

## Inferred fields (closed models only)

N/A — open-weight, though under a custom (non-Apache) `qwen3.8-max` licence.

## Notes

**Architecture snapshot** (README + config):

- 2.4T total / 95B activated, 92 layers, hidden 8192
- Layout `23 × (3 × (Gated DeltaNet → MoE) → 1 × (Gated Attention → MoE))` — the same
  3:1 hybrid cadence as the 27B dense model, held constant across a ~90× parameter range
- Gated DeltaNet: 128 V heads / 16 QK heads, head_dim 128
- Gated Attention: 64 Q / 4 KV (16:1), head_dim 256, rotary dim 64
- MoE: 512 experts, 10 routed + 1 shared, expert intermediate 2048, aux-loss coef 0.001
- MTP: `mtp_num_hidden_layers=1`, "trained with multi-steps"
- Context 262,144 native → 1,010,000 claimed
- `Qwen3_5MoeForCausalLM` / `qwen3_5_moe_text` — Qwen3.5 modeling code, unchanged

**Scale-up shape vs Qwen3.5-35B-A3B**: hidden 2048 → 8192, layers 40 → 92, experts
256 → 512, top-8 → top-10, expert width 512 → 2048. Routing algorithm, gating, hybrid
cadence and MTP topology all unchanged — this is a pure widen-and-deepen scale-up of an
unchanged recipe.

**KV cache observation**: KV width is 4 × 256 = 1024 at *both* 27B and 2.4T. Qwen holds
per-layer KV cost flat as the model scales, absorbing the growth into Q heads (24 → 64)
and into the Gated DeltaNet V state (48 → 128 heads).

**Benchmarks** (model card, labelled Qwen3.8-Max; columns are Opus 4.8, Fable 5,
GPT 5.6 Sol (max), Qwen3.7-Max, Qwen3.8-Max):

| Benchmark                        | Qwen3.7-Max | Qwen3.8-Max |
| -------------------------------- | ----------- | ----------- |
| Terminal Bench 2.1               | 74.5        | 86.6        |
| SWE-bench Pro                    | 60.6        | 67.7        |
| DeepSWE 1.1                      | 21.6        | 56.6        |
| FrontierSWE                      | 40.7        | 73.5        |
| QwenSWEBench                     | 63.4        | 80.7        |
| CoWorkBench                      | 64.6        | 74.8        |
| JobBench                         | 31.3        | 53.4        |
| Agents' Last Exam (pass / score) | 11.8 / 31.1 | 27.0 / 52.4 |
| GPQA Diamond                     | 92.4        | 92.6        |
| HLE                              | 41.4        | 43.6        |
