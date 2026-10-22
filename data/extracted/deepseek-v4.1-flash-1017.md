# DeepSeek-V4.1-Flash-1017

> 中文版：[deepseek-v4.1-flash-1017.zh.md](./deepseek-v4.1-flash-1017.zh.md)

*Schema version: 8*

## Overview

| | |
|---|---|
| Family | DeepSeek |
| Released | 2026-10 |
| Openness | Open weights |
| Total parameters | 552B backbone + 196B Engram (linked V4.1 family report; the 1017 config is identical to the September checkpoint) |
| Active parameters | 8B prefill / 16B decode (linked V4.1 family architecture report; unchanged 1017 config) |

**Variant policy:** October 17 minor update to DeepSeek-V4.1-Flash, with one image+text checkpoint, chat/thinking modes and continuous numeric reasoning effort. Current config is structurally identical to the September pinned config. The new release specifically discloses self-feedback RL and improved reasoning, coding, agentic and visual results with shorter output and task time; it does not publish a separate 1017 technical report or training budget. The model card links the earlier V4.1 report for architecture background.

## Sources

- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/tokenizer_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/encoding/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/encoding/encoding.py>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/model.py>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/vision.py>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/engram.py>
- <https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash-1017/revision/1bae0e1088993b9b82de08f59de5be5a34e42170>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/DeepSeek_V41_Tech_Report.pdf>
- <https://api-docs.deepseek.com/news/news261017/>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/dba1be0a40aa45a94ad051997016db3960a90277/config.json>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 40 |
| Hidden dim | 5120 |
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
| Heads | 64 |
| KV heads | 1 |
| Head dim | 512 |

**RoPE:** type=`yarn`, base=`10000`

RoPE scaling:

```json
{
  "rope_type": "yarn",
  "factor": 16,
  "beta_fast": 32,
  "beta_slow": 1,
  "original_max_position_embeddings": 65536,
  "compress_rope_theta": 160000
}
```

**Hybrid attention variants:**

| Name | Family | Q heads | KV heads | Head dim | RoPE | Notes |
|---|---|---|---|---|---|---|
| `sliding_window_attention` | `sliding_window` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | 128-token layer-local window in every layer; layers 0-1 are SWA only. |
| `csa2_full` | `other` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | Computes shared global KV and indexer keys; layers 2,8,14,20. |
| `csa2_reindex` | `other` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | Reuses global KV/indexer keys but computes fresh top-512; layers 24,28,32,36. |
| `csa2_reuse` | `other` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | Reuses preceding global KV and top-k; remaining 30 global-attention layers. |

**Layer pattern:** 40 backbone layers: 0-1 SWA only; 2-19 encoder CSA2 with ratio 2 and [Full, Reuse×5] repeated three times; 20-39 decoder ratio 1 with Full at 20, Reindex at 24/28/32/36 and Reuse otherwise. All layers retain local SWA. Current config matches the linked family report topology.

**Attention notes:** Current config: query low-rank projection 1280; grouped output projection 8 groups × rank 1024; partial RoPE width 64 of 512.

**Sparse attention:**

| | |
|---|---|
| Kind | `csa2` |
| Selected entries (top-k) | 512 |
| Indexer heads | 32 |
| Indexer head dim | 128 |
| KV compression ratio | 2 (encoder) / 1 (decoder) |

**Selection rule:** Full/Reindex layers score indexer keys projected from shared main KV; Reuse layers inherit top-512 indices. Layer 20 builds a candidate pool of top 2048 blocks × 8 positions (at most 16384 positions); decoder Reindex layers select within that pool (config + reference Indexer).

_Notes:_ Shapes and sharing topology from current config and reference code; the family report is earlier architecture background.

**Cross-layer sharing:**

| Kind | Shared state | Source layers | Consumer layers |
|---|---|---|---|
| `ced` | `kv_from_encoder_output` | [19] | [20] |
| `csa2` | `kv`, `indexer_keys` | [2, 8, 14, 20] | All other global-attention layers read the most recent Full layer state. |
| `csa2` | `topk_indices` | [2, 8, 14, 20, 24, 28, 32, 36] | The other 30 global-attention layers reuse the most recent index-source top-k. |

- **`ced`** (kv_from_encoder_output)
    - _Notes:_ Linked family report: decoder global KV is projected from final encoder output; under CSA2, Full layer 20 materializes it for decoder reuse. The minimal current reference runs the full stack and does not implement the optimized encoder-only prefill schedule.
- **`csa2`** (kv, indexer_keys)
    - _Notes:_ Current config kv_source_layer_ids and reference SharedAttentionRuntime.
- **`csa2`** (topk_indices)
    - _Notes:_ Current config index_source_layer_ids; candidate_source_layer_id=20 is an additional shared search-domain restriction.

### FFN (moe)

**MoE:**

| | |
|---|---|
| Routed experts | 384 |
| Active experts per token | 6 |
| Shared experts | 1 |
| Per-expert intermediate size | 2304 |

**Routing:** Current config: top-6 routed experts + 1 shared expert; SqrtSoftplus affinity (scoring_func=sqrtsoftplus); topk_method=noaux_tc; norm_topk_prob=true; routed_scaling_factor=1.5. Reference Gate uses correction biases for selection and unbiased scores for output weights. Current Gate has separate text/image selection biases (bias and bias_vl).

**Layer partition:** All backbone blocks instantiate MoE FFNs in inference/model.py.

### Components

| | |
|---|---|
| Activation | SwiGLU (hidden_act=silu), swiglu_limit=10.0 in current config and reference Expert. |
| Normalization | RMSNorm, rms_norm_eps=1e-20; separate hc_eps=1e-06 for Hyper-Connections. |

**Embedding notes:** vocab_size=129280; tie_word_embeddings=false. Image positions are replaced by visual embeddings in the reference Transformer.

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

**Architecture:** 3 draft blocks (reference inference/config.json n_mtp_layers=3), window-only attention; block_size=5; Markov rank 256; target layers [37, 38, 39].

_Notes:_ The reference Transformer constructs DSparkBlock modules when dspark_block_size is nonzero; this does not establish an MTP training objective.

### Memory modules

**Engram conditional memory**

| | |
|---|---|
| Kind | `engram` |
| Parameters | 196B (linked V4.1 family report; current table dimensions imply 196.614B embedding elements before projections) |
| Injected at layers | [1, 14] |

**Addressing:** Current config and inference/engram.py: n-gram orders 2,3,4 with 8 hash heads per order over tokenizer-compressed IDs; text only, image tokens masked.

**Table configuration:** engram_num_embeddings=[384006168,384016682]; head_dim=256; compressed vocab=99092; base vocab per hash=16000000. Current Engram projects retrieved vectors to per-HC-copy keys plus shared values and gates the update.

**Storage:** Current inference ParallelEngramEmbedding uses FP8 embedding weights. Production offload policy for the 1017 release is not separately specified.

_Notes:_ Forward-pass memory, separate from the DSpark draft. This entry does not import September optimizer or learning-rate claims.

### Parallelism / infra

Only inference topology is documented here; current-checkpoint training parallelism is undisclosed. Reference inference supports tensor-parallel torchrun and checkpoint conversion.

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] |
| Total training tokens | [Unknown/Not Disclosed] |

**LR schedule:** [Unknown/Not Disclosed]

**Data mix notes:** The current release does not disclose training-token counts or mixture fractions. Earlier family reports are not evidence for the dated update training budget.

### Alignment

**SFT:** [Unknown/Not Disclosed]

**RL method:** Reinforcement learning with self-feedback (official 2026-10-17 release note). The update does not name an RL algorithm or specify reward, feedback-label generation, or training budget.

**RLAIF:** `[Unknown/Not Disclosed]`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Self-feedback reinforcement learning | `rl` | Official release note attributes stronger end-to-end project development (game creation and 3D modeling) to self-feedback RL. Ordering relative to other training stages and implementation details are undisclosed. |

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `thinking-low` | thinking_mode=thinking, reasoning_effort=low | Reasoning effort selected by the current prompt encoder. |
| `thinking-high` | thinking_mode=thinking, reasoning_effort=high | Reasoning effort selected by the current prompt encoder. |
| `thinking-max` | thinking_mode=thinking, reasoning_effort=max | Reasoning effort selected by the current prompt encoder. |
| `chat` | thinking_mode=chat | Places </think> after the assistant prefix to skip reasoning. |

- **`thinking-low`**
    - Kwargs: `thinking_mode=thinking`, `reasoning_effort=low`
    - Recommended sampling: `temperature=1.0`, `top_p=1.0`
- **`thinking-high`**
    - Kwargs: `thinking_mode=thinking`, `reasoning_effort=high`
    - Recommended sampling: `temperature=1.0`, `top_p=1.0`
- **`thinking-max`**
    - Kwargs: `thinking_mode=thinking`, `reasoning_effort=max`
    - Recommended sampling: `temperature=1.0`, `top_p=1.0`
- **`chat`**
    - Kwargs: `thinking_mode=chat`

**Reasoning effort:**

| | |
|---|---|
| API parameter | `reasoning_effort` |
| Delivery | `prompt_prefix` |
| Scale | `continuous` |
| Range | 1-100 |

| Level | Numeric value | Default | Rendering | Notes |
|---|---|---|---|---|
| `low` | 50 |  | <｜System｜>Reasoning Effort: 50 (range 1-100, the higher the value, the more thorough the reasoning)

 | — |
| `high` | 75 | ✓ | <｜System｜>Reasoning Effort: 75 (range 1-100, the higher the value, the more thorough the reasoning)

 | — |
| `max` | 100 |  | <｜System｜>Reasoning Effort: 100 (range 1-100, the higher the value, the more thorough the reasoning)

 | — |

**Applies when:** thinking_mode=thinking; prefix inserted at conversation index 0 before the system text.

**Unrecognized value:** Reference render_reasoning_effort asserts: only exact Python ints within 1-100 or low/high/max aliases are accepted; None selects high. Validation runs even when the prefix is not rendered.

_Notes:_ Current encoding.py and encoding/README.md. The September report describes effort-conditioned RL, but the 1017 update does not restate its training method.

**Tool-call protocol:**

| | |
|---|---|
| Format | `xml-like` |
| Start token | `<｜DSML｜ calls>` |
| End token | `</｜DSML｜ calls>` |
| Arguments schema | <｜DSML｜ invoke name="..."> with per-argument <｜DSML｜ parameter name="..." string="true\|false">; raw strings or JSON for non-strings. |

_Notes:_ Current encoding supports namespace::function; leading spaces in V4.1 DSML tags differ from V4. No published production parser flag in the current model card.

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

### Quantization (shipped weights)

| | |
|---|---|
| Weight format | `fp4+fp8 mixed` |
| Activation format | `fp8 dynamic (config.quantization_config.activation_scheme=dynamic)` |
| Method | `[Unknown/Not Disclosed]` |
| Granularity | FP8 weight blocks [32, 32]; scale_fmt=ue8m0. |

**Scope:** FP4 routed-expert weights; FP8 quantization configuration for other quantized weights. This is a deployment format, not proof of the current training precision.

_Notes:_ Current config uses quant_method=fp8 together with expert_dtype=fp4. The dated checkpoint does not disclose a new quantization training recipe.

**Stability tricks:** Current config/reference Expert clamps SwiGLU activations at 10. The update does not disclose loss-spike handling or a full training-stability recipe.

## Multimodal

| | |
|---|---|
| Modalities | text, image |
| Fusion | `native_early` |

**Fusion notes:** Linked V4.1 family report describes multimodal training from the start; current 1017 code retains the same architecture. Current inference/vision.py: 3×3 spatial merging followed by two linear aligner layers with GELU; projected image features replace image positions in the shared LM stream.

### Vision encoder

| | |
|---|---|
| Architecture | DeepSeek ViT with full bidirectional attention, 2D RoPE, linear RGB patch embedding, RMSNorm and SwiGLU (current inference/vision.py) |
| Depth (layers) | 32 |
| Hidden size | 1024 |
| Intermediate size | 2816 |
| Num heads | 16 |
| Patch size | 14 |
| Input channels | 3 |
| Output dim → LM | 5120 |
| Spatial merge size | 3 |
| Temporal patch size | [Unknown/Not Disclosed] |

_Notes:_ max image tokens=1024; min pixels=295936; max width/height ratio=None. No video/audio path disclosed.

### Vision token anchors (LM vocab IDs)

| | |
|---|---|
| image_token_id | 129264 |
| video_token_id | [Unknown/Not Disclosed] |
| vision_start_token_id | [Unknown/Not Disclosed] |
| vision_end_token_id | [Unknown/Not Disclosed] |

## Open questions

- 1017 optimizer, LR schedule, update-token budget, data mixture, SFT/distillation and exact RL algorithm are undisclosed; do not carry over September Muon/45T/GRPO/OPD claims.
- Self-feedback RL does not disclose whether AI generates preference labels; rlaif remains UNKNOWN.
- Parameter figures are architecture-level figures from the linked September report; no separate 1017 accounting is published. HF safetensors element totals include packed/quantized and auxiliary tensors and are not substituted for paper parameter counts.
- The minimal reference executes all 40 backbone blocks for prefill; encoder-only prefill, SWA bounded replay and production cache performance are described by the linked family report, not benchmarked for 1017.

---

_Generated from `data/extracted/deepseek-v4.1-flash-1017.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
