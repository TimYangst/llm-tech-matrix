# Qwen3.5-35B-A3B

> 中文版：[qwen3.5-35b-a3b.zh.md](./qwen3.5-35b-a3b.zh.md)

*Schema version: 6*

## Overview

| | |
|---|---|
| Family | Qwen |
| Released | 2026-02 |
| Openness | Open weights |
| Total parameters | 35B |
| Active parameters | 3B |

**Variant policy:** Unified weights per (size, dense/MoE) — Qwen3.5 ships ~7 open-weight sizes (per the Qwen3.6-27B README comparison table the 3.5 family includes 27B dense and 397B-A17B MoE among others). Each checkpoint handles thinking, non-thinking, vision and tool use through chat-template kwargs (`enable_thinking`) and serving-time parsers; there are NO separate Math / Coder / VL / Thinking siblings (a deliberate departure from Qwen2.5's Math/Coder/VL split). 'Coder' capability is exposed via the `--tool-call-parser qwen3_coder` serving flag (vLLM / SGLang) and post-training emphasis, not a separate weight checkpoint. Native VL is unified into the base weights via the `qwen3_5` ViT shared with the LM vocabulary (image / video / vision_start / vision_end token IDs). README pipeline_tag is `image-text-to-text` for both 27B and 35B-A3B.

## Sources

- <https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.5>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 40 |
| Hidden dim | 2048 |
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

_Notes:_ Opt-in deployment-time scaling, identical recipe to Qwen3.5-27B. README 'Processing Ultra-Long Texts' specifies factor=4.0 with original_max_position_embeddings=262144 to lift effective context from 262K to ~1010K. Static implementation (factor constant regardless of input length) so should be enabled only when long context is actually needed; for typical use under 524K, factor=2.0 is recommended. mRoPE configuration (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000) is preserved across the extension.

### Attention (hybrid)

| | |
|---|---|
| Variant | hybrid |
| Heads | 16 |
| KV heads | 2 |
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
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=32 with linear_value_head_dim=128 -> 4096-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. mamba_ssm_dtype=float32. Used in 3 out of every 4 layers (30 of 40). |
| `gated_attention` | `gqa` | 16 | 2 | 256 | mrope (multimodal RoPE) with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated, the remaining 192 are NoPE. mrope_section=[11,11,10] partitions the rotary dims across temporal/height/width axes; mrope_interleaved=true. | Softmax attention with output gating (config: attn_output_gate=true). GQA 16Q:2KV (group size 8) — twice as aggressive as Qwen3.5-27B's 24Q:4KV (group size 6). attention_bias=false. Used in 1 out of every 4 layers (10 of 40, 'full_attention' in config.layer_types). Effective Q dim 16*256=4096; KV dim 2*256=512. |

**Layer pattern:** (D,D,D,F)x10 with D=gated_deltanet, F=gated_attention. config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 10 times (40 layers total). config.full_attention_interval=4 confirms the 1-in-4 cadence. README naming: '10 x (3 x (Gated DeltaNet -> MoE) -> 1 x (Gated Attention -> MoE))'.

### FFN (moe)

**MoE:**

| | |
|---|---|
| Routed experts | 256 |
| Active experts per token | 8 |
| Shared experts | 1 |
| Per-expert intermediate size | 512 |

**Routing:** Top-8 routing over 256 routed experts plus 1 always-on shared expert per token (README: '8 Routed + 1 Shared'). Auxiliary load-balance loss with coefficient router_aux_loss_coef=0.001. Per-expert FFN intermediate dim is 512 for both routed (moe_intermediate_size) and shared (shared_expert_intermediate_size) experts — uniform width. Total MoE width per token = 9 * 512 = 4608 from 9 active experts (8 routed + 1 shared).

**Layer partition:** Uniform MoE FFN across all 40 layers regardless of attention variant (config.mlp_only_layers=[] - no dense FFN substitution at any depth).

### Components

| | |
|---|---|
| Activation | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in each expert FFN). |
| Normalization | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding notes:** tie_word_embeddings=false (separate input embedding and output head). Token Embedding 248320 (padded) and LM Output 248320 (padded) per README; config.vocab_size=248320 confirms. Substantial vocab expansion vs Qwen3 (151,936) driven by 201-language coverage and native-VL reserved tokens. Vision-related reserved IDs in the LM vocabulary: image_token_id=248056, video_token_id=248057, vision_start_token_id=248053, vision_end_token_id=248054. eos_token_id=248044.

### Parallelism / infra

[Unknown/Not Disclosed]

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] |
| Total training tokens | [Unknown/Not Disclosed] |

**LR schedule:** [Unknown/Not Disclosed]

**Data mix notes:** Vendor highlights only (identical to Qwen3.5-27B; the README Highlights section is family-level). 'Global Linguistic Coverage: Expanded support to 201 languages and dialects' (vs Qwen3's 119). 'Unified Vision-Language Foundation: Early fusion training on multimodal tokens achieves cross-generational parity with Qwen3 and outperforms Qwen3-VL models across reasoning, coding, agents, and visual understanding benchmarks.' 'Next-Generation Training Infrastructure: Near-100% multimodal training efficiency compared to text-only training.' No quantitative breakdown (token totals, code/math/text shares, image/video token counts) is disclosed.

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

**Fusion notes:** Vendor description: 'Unified Vision-Language Foundation. Early fusion training on multimodal tokens.' Vision tokens are inlined into the same backbone as text via four reserved vocabulary IDs (vision_start, image, video, vision_end). The vision encoder's projected output dim (vision_config.out_hidden_size=2048) equals the LM hidden dim (note: 2048 here vs 5120 for Qwen3.5-27B — the same vision encoder is reprojected to whatever LM width the backbone uses). README pipeline_tag=image-text-to-text confirms the model is shipped as a single causal LM that natively consumes image and video alongside text; there is no separate text-only checkpoint.

### Vision encoder

| | |
|---|---|
| Architecture | ViT (HF model_type=qwen3_5_moe vision config). config.deepstack_visual_indexes=[] - no DeepStack injection layers configured. Same encoder geometry as Qwen3.5-27B (depth/hidden/heads/patch all match) — only the projection out_hidden_size differs to match the LM hidden. |
| Depth (layers) | 27 |
| Hidden size | 1152 |
| Intermediate size | 4304 |
| Num heads | 16 |
| Patch size | 16 |
| Input channels | 3 |
| Output dim → LM | 2048 |
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

- Pre-training optimizer, learning-rate schedule, batch size, peak/min LR, weight decay and gradient clipping are not disclosed for Qwen3.5-35B-A3B. The README/blog only describe vendor highlights; no separate Qwen3.5 LM-backbone arXiv tech report is available at extraction time (Qwen3.5-Omni Technical Report exists but covers the audio/visual omni-extension, not the LM backbone we characterize here).
- Total pre-training tokens and the data mix (code/math/text/multilingual/image/video shares) are not disclosed numerically. README only states the multilingual coverage expansion (119 -> 201 languages) and the early-fusion multimodal training claim.
- Multi-Token Prediction step depth D is not stated quantitatively. README writes 'MTP: trained with multi-steps' and config exposes mtp_num_hidden_layers=1 (head depth) but no explicit D for training-time multi-step loss; only inference-time speculative-decoding numbers (vLLM 2 / sglang 3-4) are provided as serving recipes.
- Post-training pipeline structure is undisclosed for Qwen3.5: no explicit stage count, no SFT data scale, no RL algorithm name. The blog highlights 'Reinforcement learning scaled across million-agent environments with progressively complex task distributions' and 'asynchronous RL frameworks supporting massive-scale agent scaffolds and environment orchestration', but the specific algorithm (GRPO vs PPO vs DPO vs other) and reward shaping are not named.
- Mixed-precision training recipe (BF16-only vs FP8 GEMM with BF16 master weights, etc.) is not disclosed; config.text_config.dtype=bfloat16 is the released checkpoint dtype, not necessarily the training-time precision.
- Parallelism strategy and training infrastructure (TP/PP/EP/DP shapes, GPU type and count, framework) are not disclosed. MoE-specific details (expert parallelism, all-to-all dispatch implementation, routing imbalance handling beyond aux_loss_coef=0.001) are also not disclosed.
- Why exactly 1 shared expert? Qwen3 dropped shared experts (vs Qwen2.5), citing global-batch load balancing as sufficient. Qwen3.5 reintroduces exactly 1 shared expert (matches DeepSeek-V3's count, but DeepSeek-V3 has 1 shared expert with much wider per-expert intermediate). The design rationale (was global-batch LB insufficient under hybrid attention? did the asymmetric V/K linear-attention budget create capacity gaps the shared expert covers?) is not discussed in vendor sources.
- Auxiliary-loss-free routing was a feature of Qwen3-235B-A22B's MoE; Qwen3.5-35B-A3B reverts to a classic auxiliary load-balance loss (router_aux_loss_coef=0.001 in config). No vendor explanation for the reversion.
- Routing algorithm specifics — top-k softmax vs sigmoid gating, expert-choice routing variants, capacity factor at training time, drop-token policy — are not disclosed beyond 'top-8 routed + 1 shared'.
- config.text_config.partial_rotary_factor=0.25 implies only 64 of the 256 attention head dims carry RoPE (remaining 192 are NoPE/non-positional). The README and blog do not explain the motivation for this NoPE/RoPE split.
- Vision encoder is the same geometry as Qwen3.5-27B (ViT depth=27, hidden=1152, heads=16, patch=16, spatial_merge=2, temporal_patch=2); only out_hidden_size differs (2048 here vs 5120). Whether the encoder weights are literally shared between the dense 27B and MoE 35B-A3B (same checkpoint, just reprojected) or independently trained is not disclosed.
- Cached blog.html at qwen.ai/blog?id=qwen3.5 is a client-side-rendered SPA shell (only 'Qwen' is present in the static HTML). Substantive blog content was therefore unavailable at extraction time; if a static rendering or per-section anchor URL appears later, re-source for a richer training/post-training description.

---

_Generated from `data/extracted/qwen3.5-35b-a3b.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
