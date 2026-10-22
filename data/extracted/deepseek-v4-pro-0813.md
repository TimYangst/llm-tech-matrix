# DeepSeek-V4-Pro-0813

> 中文版：[deepseek-v4-pro-0813.zh.md](./deepseek-v4-pro-0813.zh.md)

*Schema version: 8*

## Overview

| | |
|---|---|
| Family | DeepSeek |
| Released | 2026-08 |
| Openness | Open weights |
| Total parameters | 1.6T backbone (linked V4 family report; current card explicitly retains Preview architecture) |
| Active parameters | 49B backbone per token (linked V4 family report; excludes DSpark draft) |

**Variant policy:** August 13 official/GA Pro release supersedes the Preview, retaining its architecture and adding an attached DSpark draft. Same weights expose thinking/chat and low/high/max reasoning-effort modes. The current card reports stronger agentic performance; it does not disclose the new post-training recipe.

## Sources

- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/tokenizer_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/encoding/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/inference/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/inference/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/inference/model.py>
- <https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4-Pro-0813/revision/72e1d3230f6c080a530b0a1d46f8eb4602340597>
- <https://api-docs.deepseek.com/updates/>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/resolve/ad664d5e83023a67c735992e8fe612aeab3c52d2/DeepSeek_V4.pdf>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/encoding/encoding_dsv4.py>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 61 |
| Hidden dim | 7168 |
| Context window | 1048576 |

**Context notes:** config.json max_position_embeddings=1048576 (1M tokens). Training curriculum for this dated checkpoint is not disclosed.

**Context extension:**

| | |
|---|---|
| Method | yarn |
| Trained max | [Unknown/Not Disclosed] |
| Extended max | 1048576 |
| Factor | 16.0 |
| Original max (RoPE) | 65536 |

_Notes:_ Config-declared YaRN; this does not establish a current-checkpoint pre-training curriculum.

### Attention (hybrid)

| | |
|---|---|
| Variant | hybrid |
| Heads | 128 |
| KV heads | 1 |
| Head dim | 512 |

**RoPE:** type=`yarn`, base=`10000`

RoPE scaling:

```json
{
  "beta_fast": 32,
  "beta_slow": 1,
  "factor": 16,
  "original_max_position_embeddings": 65536,
  "type": "yarn",
  "compress_rope_theta": 160000
}
```

**Hybrid attention variants:**

| Name | Family | Q heads | KV heads | Head dim | RoPE | Notes |
|---|---|---|---|---|---|---|
| `sliding_window_attention` | `sliding_window` | 128 | 1 | 512 | Partial RoPE width 64. | 128-token local window alongside global compressed attention; ratio 0 layers are SWA only. |
| `compressed_sparse_attention` | `other` | 128 | 1 | 512 | Compressed branch theta=160000. | CSA ratio 4; indexer selects top-1024 compressed entries. |
| `heavily_compressed_attention` | `other` | 128 | 1 | 512 | Compressed branch theta=160000. | HCA ratio 128; attends all causally available heavily compressed entries (reference Attention). |

**Layer pattern:** Zero-indexed backbone compress_ratios=[128, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4]. 0=SWA only, 4=CSA+SWA, 128=HCA+SWA. Trailing three ratio-0 entries belong to the draft stack in reference inference/config.json.

**Attention notes:** Current config: query low-rank projection 1536; grouped output projection 16 groups × rank 1024; partial RoPE width 64 of 512.

**Sparse attention:**

| | |
|---|---|
| Kind | `csa+hca` |
| Selected entries (top-k) | 1024 |
| Indexer heads | 64 |
| Indexer head dim | 128 |
| KV compression ratio | 4 (CSA) / 128 (HCA) |

**Selection rule:** CSA: lightning-indexer top-1024 over ratio-4 compressed positions. HCA: all causally available ratio-128 entries (reference Attention).

_Notes:_ Shapes and sharing topology from current config and reference code; the family report is earlier architecture background.

### FFN (moe)

**MoE:**

| | |
|---|---|
| Routed experts | 384 |
| Active experts per token | 6 |
| Shared experts | 1 |
| Per-expert intermediate size | 3072 |

**Routing:** Current config: top-6 routed experts + 1 shared expert; SqrtSoftplus affinity (scoring_func=sqrtsoftplus); topk_method=noaux_tc; norm_topk_prob=true; routed_scaling_factor=2.5. Reference Gate uses correction biases for selection and unbiased scores for output weights.

**Layer partition:** All backbone blocks instantiate MoE FFNs in inference/model.py. First three layers use hash routing for text token IDs; remaining layers use score-based routing.

### Components

| | |
|---|---|
| Activation | SwiGLU (hidden_act=silu), swiglu_limit=10.0 in current config and reference Expert. |
| Normalization | RMSNorm, rms_norm_eps=1e-06; separate hc_eps=1e-06 for Hyper-Connections. |

**Embedding notes:** vocab_size=129280; tie_word_embeddings=false. Text-only checkpoint.

### Residual connections

| | |
|---|---|
| Kind | `mhc` |
| Expansion factor (n_hc) | 4 |
| Solver iterations | 20 |
| Dynamic parameterization | `True` |

**Constraint:** Doubly stochastic residual mixing via Sinkhorn normalization in the current reference implementation.

_Notes:_ Current config hc_mult=4, hc_sinkhorn_iters=20.

### Auxiliary modules

**DSpark draft module**

| | |
|---|---|
| Purpose | `speculative_decoding` |
| Shipped in checkpoint | `True` |

**Architecture:** 3 draft blocks (reference inference/config.json n_mtp_layers=3), window-only attention; block_size=5; Markov rank 512; target layers [58, 59, 60].

**How to enable:** vLLM --speculative-config with method=dspark; SGLang --speculative-algorithm DSPARK (same checkpoint; no separate draft path).

_Notes:_ The reference Transformer constructs DSparkBlock modules when dspark_block_size is nonzero; this does not establish an MTP training objective.

### Parallelism / infra

Only inference topology is documented here; current-checkpoint training parallelism is undisclosed. Reference inference supports tensor-parallel torchrun and checkpoint conversion.

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] |
| Total training tokens | [Unknown/Not Disclosed] |

**LR schedule:** [Unknown/Not Disclosed]

**Data mix notes:** No current-update token budget or mixture disclosed. The linked V4 report describes the earlier Preview and is not treated as the 0813 training recipe.

### Alignment

**SFT:** [Unknown/Not Disclosed]

**RL method:** [Unknown/Not Disclosed]

**RLAIF:** `[Unknown/Not Disclosed]`

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `thinking-low` | thinking_mode=thinking, reasoning_effort=low | Prompt prefix controls reasoning effort on the same weights. |
| `thinking-high` | thinking_mode=thinking, reasoning_effort=high | Prompt prefix controls reasoning effort on the same weights. |
| `thinking-max` | thinking_mode=thinking, reasoning_effort=max | Prompt prefix controls reasoning effort on the same weights. |
| `chat` | thinking_mode=chat | Places </think> after the assistant prefix to skip reasoning. |

- **`thinking-low`**
    - Kwargs: `thinking_mode=thinking`, `reasoning_effort=low`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95 (agentic) / 1.0 (otherwise)`
- **`thinking-high`**
    - Kwargs: `thinking_mode=thinking`, `reasoning_effort=high`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95 (agentic) / 1.0 (otherwise)`, `max_tokens=384K`
- **`thinking-max`**
    - Kwargs: `thinking_mode=thinking`, `reasoning_effort=max`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95 (agentic) / 1.0 (otherwise)`, `max_tokens=384K`
- **`chat`**
    - Kwargs: `thinking_mode=chat`

**Reasoning effort:**

| | |
|---|---|
| API parameter | `reasoning_effort` |
| Delivery | `prompt_prefix` |
| Scale | `discrete` |

| Level | Numeric value | Default | Rendering | Notes |
|---|---|---|---|---|
| `low` | — | ✓ | none | — |
| `high` | — |  | Reasoning Effort: Absolute maximum with no shortcuts permitted.
You MUST be very thorough in your thinking and comprehensively decompose the problem to resolve the root cause, rigorously stress-testing your logic against all potential paths, edge cases, and adversarial scenarios.
Explicitly write out your entire deliberation process, documenting every intermediate step, considered alternative, and rejected hypothesis to ensure absolutely no assumption is left unchecked.

 | — |
| `max` | — |  | Reasoning Effort: Beyond maximum — exhaustive, relentless, and uncompromising.
You MUST reason with the utmost depth and rigor, leaving absolutely nothing to chance: exhaustively decompose the problem into its most fundamental components, trace every causal chain to its root, and resolve the underlying cause rather than any surface symptom.
Do not stop reasoning until you have independently verified the solution from multiple angles and are certain that no assumption remains unchecked and no error remains undiscovered.

 | — |

**Applies when:** thinking_mode=thinking at conversation index 0; prefix before system text. No effect in chat mode.

**Unrecognized value:** Reference render_message uses the low default for falsy values, then asserts membership in low/high/max. Other unknown nonempty values raise AssertionError; validation occurs in chat mode too.

_Notes:_ Verified against this checkpoint's encoding/encoding_dsv4.py; low is the default.

**Tool-call protocol:**

| | |
|---|---|
| Format | `xml-like` |
| Start token | `<｜DSML｜tool_calls>` |
| End token | `</｜DSML｜tool_calls>` |
| Arguments schema | <｜DSML｜invoke name="..."> and per-argument <｜DSML｜parameter string="true\|false">; raw strings or JSON for non-strings. |

_Notes:_ Current encoding/README.md; retains V4 DSML spelling without V4.1 leading spaces.

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

### Quantization (shipped weights)

| | |
|---|---|
| Weight format | `fp4+fp8 mixed` |
| Activation format | `fp8 dynamic (config.quantization_config.activation_scheme=dynamic)` |
| Method | `[Unknown/Not Disclosed]` |
| Granularity | FP8 weight blocks [128, 128]; scale_fmt=ue8m0. |

**Scope:** FP4 routed-expert weights; FP8 quantization configuration for other quantized weights. This is a deployment format, not proof of the current training precision.

_Notes:_ Current config uses quant_method=fp8 together with expert_dtype=fp4. The dated checkpoint does not disclose a new quantization training recipe.

**Stability tricks:** Current config/reference Expert clamps SwiGLU activations at 10. The update does not disclose loss-spike handling or a full training-stability recipe.

## Open questions

- 0813 optimizer, LR schedule, training-token budget, data mixture and post-training algorithm are undisclosed. The linked V4 report is earlier Preview background, not update evidence.
- HF config num_nextn_predict_layers=1 conflicts with reference inference/config.json n_mtp_layers=3 and three trailing ratio-0 draft entries; current card confirms DSpark attachment but does not reconcile the count. Training MTP objective remains unasserted.
- The earlier DeepSeek-V4-Pro report URL now returns 404. This manifest pins the official shared V4 report in the Flash repository instead; architecture matches current config.

---

_Generated from `data/extracted/deepseek-v4-pro-0813.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
