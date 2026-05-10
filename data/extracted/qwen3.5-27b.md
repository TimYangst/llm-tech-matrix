# Qwen3.5-27B

> 中文版：[qwen3.5-27b.zh.md](./qwen3.5-27b.zh.md)

*Schema version: 6*

## Overview

| | |
|---|---|
| Family | Qwen |
| Released | 2026-02 |
| Openness | Open weights |
| Total parameters | 27B |
| Active parameters | 27B |

**Variant policy:** Unified weights per (size, dense/MoE) — Qwen3.5 ships ~7 open-weight sizes (per the Qwen3.6-27B README comparison table the 3.5 family includes 27B dense and 397B-A17B MoE among others). Each checkpoint handles thinking, non-thinking, vision and tool use through chat-template kwargs (`enable_thinking`) and serving-time parsers; there are NO separate Math / Coder / VL / Thinking siblings (a deliberate departure from Qwen2.5's Math/Coder/VL split). 'Coder' capability is exposed via the `--tool-call-parser qwen3_coder` serving flag (vLLM / SGLang) and post-training emphasis, not a separate weight checkpoint. Native VL is unified into the base weights via the `qwen3_5` ViT shared with the LM vocabulary (image / video / vision_start / vision_end token IDs). README pipeline_tag is `image-text-to-text` for both 27B and 35B-A3B.

## Sources

- <https://huggingface.co/Qwen/Qwen3.5-27B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.5-27B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.5>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 64 |
| Hidden dim | 5120 |
| Context window | 262144 |

**Context notes:** Native productized 262K (config.json max_position_embeddings=262144). Extensible to 1,010,000 via opt-in static YaRN configured at inference time (vLLM/SGLang); the static config.json ships rope_type=default (no scaling) for the 262K native window.

**Context extension:**

| | |
|---|---|
| Method | yarn |
| Trained max | 262144 |
| Extended max | 1010000 |
| Factor | 4.0 |
| Original max (RoPE) | 262144 |

_Notes:_ Opt-in deployment-time scaling. README 'Processing Ultra-Long Texts' specifies factor=4.0 with original_max_position_embeddings=262144 to lift effective context from 262K to ~1010K. README warns the implementation is static (factor constant regardless of input length) so it should be enabled only when long context is actually needed; for typical use under 524K, factor=2.0 is recommended. mRoPE configuration (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000) is preserved across the extension.

### Attention (hybrid)

| | |
|---|---|
| Variant | hybrid |
| Heads | 24 |
| KV heads | 4 |
| Head dim | 256 |

**RoPE:** type=`mrope`, base=`10000000`

RoPE scaling:

```json
{
  "mrope_interleaved": true,
  "mrope_section": [
    11,
    11,
    10
  ],
  "partial_rotary_factor": 0.25
}
```

**Hybrid attention variants:**

| Name | Family | Q heads | KV heads | Head dim | RoPE | Notes |
|---|---|---|---|---|---|---|
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=48 with linear_value_head_dim=128 -> 6144-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. mamba_ssm_dtype=float32. The Gated DeltaNet's output-gate activation function is not disclosed by this config (only the Qwen3.6-27B config in the same family explicitly sets output_gate_type=swish). Used in 3 out of every 4 layers. |
| `gated_attention` | `gqa` | 24 | 4 | 256 | mrope (multimodal RoPE) with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated, the remaining 192 are NoPE. mrope_section=[11,11,10] partitions the rotary dims across temporal/height/width axes; mrope_interleaved=true. | Softmax attention with output gating (config: attn_output_gate=true). GQA 24Q:4KV ratio. attention_bias=false. Used in 1 out of every 4 layers ('full_attention' in config.layer_types). Effective Q dim 24*256=6144; KV dim 4*256=1024. |

**Layer pattern:** (D,D,D,F)x16 with D=gated_deltanet, F=gated_attention. config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 16 times. config.full_attention_interval=4 confirms the 1-in-4 cadence. README naming: '16 x (3 x (Gated DeltaNet -> FFN) -> 1 x (Gated Attention -> FFN))'.

### FFN (dense)

**Dense intermediate size:** `17408`

**Layer partition:** Uniform dense SwiGLU FFN across all 64 layers regardless of attention variant (config.mlp_only_layers=[] - no MoE substitution).

### Components

| | |
|---|---|
| Activation | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in the FFN). |
| Normalization | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding notes:** tie_word_embeddings=false (separate input embedding and output head). README: Token Embedding 248320 padded; LM Output 248320 padded; config.vocab_size=248320 confirms. Substantial vocab expansion vs Qwen3 (151,936) driven by 201-language coverage and native-VL reserved tokens. Vision-related reserved IDs in the LM vocabulary: image_token_id=248056, video_token_id=248057, vision_start_token_id=248053, vision_end_token_id=248054. eos_token_id=248044.

### Parallelism / infra

[Unknown/Not Disclosed]

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] |
| Total training tokens | [Unknown/Not Disclosed] |

**LR schedule:** [Unknown/Not Disclosed]

**Data mix notes:** Vendor highlights only. README: 'Global Linguistic Coverage: Expanded support to 201 languages and dialects' (vs Qwen3's 119). 'Unified Vision-Language Foundation: Early fusion training on multimodal tokens achieves cross-generational parity with Qwen3 and outperforms Qwen3-VL models across reasoning, coding, agents, and visual understanding benchmarks.' 'Next-Generation Training Infrastructure: Near-100% multimodal training efficiency compared to text-only training.' No quantitative breakdown (token totals, code/math/text shares, image/video token counts) is disclosed.

### Training objectives (beyond next-token prediction)

**Multi-Token Prediction (MTP):**

| | |
|---|---|
| Depth (D) | [Unknown/Not Disclosed] |
| Loss weight schedule | [Unknown/Not Disclosed] |

_Shared modules:_ MTP head with mtp_num_hidden_layers=1 (config) and mtp_use_dedicated_embeddings=false (shares input embeddings with the main model). README states 'MTP: trained with multi-steps' - the exact step depth D is not disclosed.

### Alignment

**SFT:** [Unknown/Not Disclosed]

**RL method:** [Unknown/Not Disclosed]

**RLAIF:** `[Unknown/Not Disclosed]`

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `thinking` | Default mode. Qwen3.5 thinks by default and wraps reasoning in <think>...</think> before producing the final response. README explicitly states the Qwen3-style /think and /no_think soft switches are NOT supported in Qwen3.5. | Long Chain-of-Thought reasoning before the final answer. Recommended sampling per README Best Practices: temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0 (general); temperature=0.6 for precise coding tasks (e.g. WebDev). |
| `non-thinking` | Set chat_template_kwargs={"enable_thinking": False} via the OpenAI-compatible API extra_body (vLLM/SGLang/Qwen-Agent), or pass enable_thinking=False directly on Alibaba Cloud Model Studio. Soft switches /think and /no_think are NOT supported (README: 'Qwen3.5 does not officially support the soft switch of Qwen3'). | Direct, low-latency response without an explicit reasoning trace. Recommended sampling per README Best Practices: temperature=0.7, top_p=0.8, top_k=20, presence_penalty=1.5 (general); temperature=1.0, top_p=1.0, top_k=40, presence_penalty=2.0 for reasoning tasks in non-thinking mode. |

- **`thinking`**
    - Kwargs: `enable_thinking=true`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`
- **`non-thinking`**
    - Kwargs: `enable_thinking=false`
    - Recommended sampling: `temperature=0.7`, `top_p=0.8`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`

**Tool-call protocol:**

| | |
|---|---|
| Format | `xml-like` |
| Start token | `<tool_call>` |
| End token | `</tool_call>` |
| Arguments schema | Per-arg <parameter=name>VALUE</parameter> blocks nested inside a <function=NAME></function> wrapper. Values are stringified — in Qwen3.5 the chat template applies `tojson` only to mappings/sequences and falls back to Python `str()` for scalars (so booleans render as 'True'/'False' rather than 'true'/'false' — fixed in Qwen3.6 to apply `tojson` to anything that is not already a string). |

**Serving parser flags:**

- `vllm`: `--tool-call-parser qwen3_coder`
- `sglang`: `--tool-call-parser qwen3_coder`

_Notes:_ Verbatim from the chat template (tokenizer_config.json): '<tool_call>\n<function=example_function_name>\n<parameter=example_parameter_1>\nvalue_1\n</parameter>\n<parameter=example_parameter_2>\n...\n</parameter>\n</function>\n</tool_call>'. README serving snippets pair `--tool-call-parser qwen3_coder` with `--reasoning-parser qwen3` for combined reasoning + tool-use deployments. The natural-language reasoning may appear BEFORE but NOT after the tool call (template comment). Tool-call output is wrapped via `<tool_response>...</tool_response>` blocks emitted as a `tool` role message.

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

## Multimodal

| | |
|---|---|
| Modalities | text, image, video |
| Fusion | `native_early` |

**Fusion notes:** Vendor description: 'Unified Vision-Language Foundation. Early fusion training on multimodal tokens.' Vision tokens are inlined into the same backbone as text via four reserved vocabulary IDs (vision_start, image, video, vision_end). The vision encoder's projected output dim (vision_config.out_hidden_size=5120) equals the LM hidden dim, indicating a direct projection into the shared hidden stream after spatial_merge_size=2 patch merging. README pipeline_tag=image-text-to-text confirms the model is shipped as a single causal LM that natively consumes image and video alongside text; there is no separate text-only checkpoint.

### Vision encoder

| | |
|---|---|
| Architecture | ViT (HF model_type=qwen3_5 vision config). config.deepstack_visual_indexes=[] - no DeepStack injection layers configured. |
| Depth (layers) | 27 |
| Hidden size | 1152 |
| Intermediate size | 4304 |
| Num heads | 16 |
| Patch size | 16 |
| Input channels | 3 |
| Output dim → LM | 5120 |
| Spatial merge size | 2 |
| Temporal patch size | 2 |

_Notes:_ hidden_act=gelu_pytorch_tanh; num_position_embeddings=2304 (encoder's own positional table). Long-video tip from README Best Practices: setting video_preprocessor_config longest_edge=469,762,048 (~224K video tokens) enables higher frame-rate sampling for hour-scale videos.

### Vision token anchors (LM vocab IDs)

| | |
|---|---|
| image_token_id | 248056 |
| video_token_id | 248057 |
| vision_start_token_id | 248053 |
| vision_end_token_id | 248054 |

## Open questions

- Pre-training optimizer, learning-rate schedule, batch size, peak/min LR, weight decay and gradient clipping are not disclosed for Qwen3.5-27B. The README/blog only describe vendor highlights; no separate Qwen3.5 arXiv tech report has been published as of extraction.
- Total pre-training tokens and the data mix (code/math/text/multilingual/image/video shares) are not disclosed numerically. README only states the multilingual coverage expansion (119 -> 201 languages) and the early-fusion multimodal training claim.
- Multi-Token Prediction step depth D is not stated quantitatively. README writes 'MTP: trained with multi-steps' and config exposes mtp_num_hidden_layers=1 (head depth) but no explicit D for training-time multi-step loss; only inference-time speculative-decoding numbers (vLLM 2 / sglang 3-4) are provided as serving recipes.
- Post-training pipeline structure is undisclosed for Qwen3.5: no explicit stage count, no SFT data scale, no RL algorithm name. The blog highlights 'Reinforcement learning scaled across million-agent environments with progressively complex task distributions' and 'asynchronous RL frameworks supporting massive-scale agent scaffolds and environment orchestration', but the specific algorithm (GRPO vs PPO vs DPO vs other) and reward shaping are not named.
- Mixed-precision training recipe (BF16-only vs FP8 GEMM with BF16 master weights, etc.) is not disclosed; config.text_config.dtype=bfloat16 is the released checkpoint dtype, not necessarily the training-time precision.
- Parallelism strategy and training infrastructure (TP/PP/EP/DP shapes, GPU type and count, framework) are not disclosed.
- Vision encoder training data, training stages (joint vs staged with the LM backbone), and pre-training tokens routed through the vision pathway are not disclosed.
- config.text_config.partial_rotary_factor=0.25 implies only 64 of the 256 attention head dims carry RoPE (the remaining 192 are NoPE/non-positional). The README and blog do not explain the motivation for this NoPE/RoPE split nor whether it is uniform across the 16 Gated Attention layers - captured under rope.scaling for completeness.
- Cross-version dense compare against Qwen3-32B (same 64L / hidden=5120 but FFN 25600 vs 17408 here, plus full GQA 64Q:8KV vs hybrid 24Q:4KV in only 1/4 of layers): the FFN budget appears reallocated to the new hybrid backbone machinery, but vendor sources do not directly justify the reallocation.
- Cached blog.html at qwen.ai/blog?id=qwen3.5 is a client-side-rendered SPA shell (only 'Qwen' is present in the static HTML). Substantive blog content was therefore unavailable at extraction time; if a static rendering or a per-section anchor URL appears later, re-source for a richer training/post-training description.

---

_Generated from `data/extracted/qwen3.5-27b.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
