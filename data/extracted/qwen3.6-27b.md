# Qwen3.6-27B

*Schema version: 4*

## Overview

| | |
|---|---|
| Family | Qwen |
| Released | 2026-04 |
| Openness | Open weights |
| Total parameters | 27B |
| Active parameters | 27B |

## Sources

- <https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.6-27b>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 64 |
| Hidden dim | 5120 |
| Context window | 262144 |

**Context notes:** Native productized 262K (config.json max_position_embeddings=262144). Extensible to 1,010,000 via opt-in static YaRN configured at inference time (vLLM/SGLang); the static config.json ships rope_type=default (no scaling) for the 262K native window. Same recipe as Qwen3.5-27B.

**Context extension:**

| | |
|---|---|
| Method | yarn |
| Trained max | 262144 |
| Extended max | 1010000 |
| Factor | 4.0 |
| Original max (RoPE) | 262144 |

_Notes:_ Identical to Qwen3.5-27B — opt-in deployment-time scaling, factor=4.0 with original_max_position_embeddings=262144, mRoPE configuration (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000) preserved across the extension. Static implementation; for typical use under 524K, factor=2.0 is recommended.

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
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=48 with linear_value_head_dim=128 -> 6144-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. output_gate_type=swish. mamba_ssm_dtype=float32. Used in 3 out of every 4 layers (48 of 64). Identical shape to Qwen3.5-27B — Qwen3.6-27B inherits the backbone wholesale. |
| `gated_attention` | `gqa` | 24 | 4 | 256 | mrope (multimodal RoPE) with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated, the remaining 192 are NoPE. mrope_section=[11,11,10] partitions the rotary dims across temporal/height/width axes; mrope_interleaved=true. | Softmax attention with output gating (config: attn_output_gate=true). GQA 24Q:4KV. attention_bias=false. Used in 1 out of every 4 layers ('full_attention' in config.layer_types). Effective Q dim 24*256=6144; KV dim 4*256=1024. Identical shape to Qwen3.5-27B. |

**Layer pattern:** (D,D,D,F)x16 with D=gated_deltanet, F=gated_attention. config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 16 times. config.full_attention_interval=4 confirms the 1-in-4 cadence. README naming: '16 x (3 x (Gated DeltaNet -> FFN) -> 1 x (Gated Attention -> FFN))'.

### FFN (dense)

**Dense intermediate size:** `17408`

**Layer partition:** Uniform dense SwiGLU FFN across all 64 layers regardless of attention variant (config.mlp_only_layers=[]). Same FFN width 17408 as Qwen3.5-27B.

### Components

| | |
|---|---|
| Activation | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in the FFN). |
| Normalization | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding notes:** tie_word_embeddings=false (separate input embedding and output head). Token Embedding 248320 (padded) and LM Output 248320 (padded) per README; config.vocab_size=248320 confirms. Vision-related reserved IDs in the LM vocabulary: image_token_id=248056, video_token_id=248057, vision_start_token_id=248053, vision_end_token_id=248054. eos_token_id=248044. config.text_config also exposes bos_token_id=248044 (vs Qwen3.5-27B which omits it from text_config) — minor metadata-level diff with no architectural impact.

### Parallelism / infra

[Unknown/Not Disclosed]

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] |
| Total training tokens | [Unknown/Not Disclosed] |

**LR schedule:** [Unknown/Not Disclosed]

**Data mix notes:** Qwen3.6 is a post-training-focused refresh of Qwen3.5 — the README states 'Following the February release of the Qwen3.5 series, we're pleased to share the first open-weight variant of Qwen3.6. Built on direct feedback from the community, Qwen3.6 prioritizes stability and real-world utility, offering developers a more intuitive, responsive, and genuinely productive coding experience.' The Qwen3.5 family-level highlights (early-fusion multimodal training, 201-language coverage, asynchronous RL infra, near-100% multimodal training efficiency) are not restated for Qwen3.6 in the README, suggesting the pre-training recipe is shared with Qwen3.5 (or unchanged at the granularity disclosed). Qwen3.6 highlights two post-training upgrades: (1) **Agentic Coding** — frontend workflows and repository-level reasoning; (2) **Thinking Preservation** — retain reasoning context from historical messages across multi-turn dialogs. No quantitative breakdown is disclosed for either pre-training or post-training data.

### Training objectives (beyond next-token prediction)

**Multi-Token Prediction (MTP):**

| | |
|---|---|
| Depth (D) | [Unknown/Not Disclosed] |
| Loss weight schedule | [Unknown/Not Disclosed] |

_Shared modules:_ MTP head with mtp_num_hidden_layers=1 (config) and mtp_use_dedicated_embeddings=false (shares input embeddings with the main model). README states only 'MTP: trained with multi-steps' - exact step depth D is not disclosed. Same serving recipes as Qwen3.5-27B (vLLM qwen3_next_mtp num_speculative_tokens=2; sglang NEXTN speculative-num-steps=3 / num-draft-tokens=4). Identical MTP topology to Qwen3.5-27B.

### Alignment

**SFT:** [Unknown/Not Disclosed]

**RL method:** [Unknown/Not Disclosed]

**RLAIF:** `[Unknown/Not Disclosed]`

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `thinking` | Default mode. Qwen3.6 thinks by default and wraps reasoning in <think>...</think> before producing the final response. README repeats the Qwen3.5 statement that the Qwen3-style /think and /no_think soft switches are NOT officially supported. | Long Chain-of-Thought reasoning before the final answer. Recommended sampling per README Best Practices (same as Qwen3.5): temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0 (general); temperature=0.6 for precise coding tasks (e.g. WebDev). |
| `non-thinking` | Set chat_template_kwargs={"enable_thinking": False} via the OpenAI-compatible API extra_body (vLLM/SGLang/Qwen-Agent), or pass enable_thinking=False directly on Alibaba Cloud Model Studio. Soft switches /think and /no_think are documented as NOT officially supported. | Direct, low-latency response without an explicit reasoning trace. Same recommended sampling as Qwen3.5-27B. |
| `preserve-thinking` | Set chat_template_kwargs={"preserve_thinking": True} via the API (Alibaba Cloud Model Studio shortens to top-level preserve_thinking=True). Composable with enable_thinking — the user can run thinking + preserve_thinking, or non-thinking + preserve_thinking. | **New in Qwen3.6.** README: 'By default, only the thinking blocks generated in handling the latest user message is retained, resulting in a pattern commonly as interleaved thinking. Qwen3.6 has been additionally trained to preserve and leverage thinking traces from historical messages.' Vendor argues it benefits multi-turn agent scenarios by improving decision consistency, can reduce total tokens by avoiding re-derivation, and improves KV-cache utilization. Default is False (interleaved-thinking pattern, matching Qwen3.5 behavior). |

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

## Multimodal

| | |
|---|---|
| Modalities | text, image, video |
| Fusion | `native_early` |

**Fusion notes:** Same native-early fusion as Qwen3.5-27B. Vision tokens are inlined into the same backbone as text via four reserved vocabulary IDs (vision_start, image, video, vision_end). vision_config.out_hidden_size=5120 matches LM hidden_size. README pipeline_tag=image-text-to-text. Qwen3.6 README does not restate the family-level early-fusion claim from Qwen3.5; the underlying mechanism appears unchanged.

### Vision encoder

| | |
|---|---|
| Architecture | ViT (HF model_type=qwen3_5 vision config — Qwen3.6-27B's vision_config still reports model_type='qwen3_5', confirming the vision encoder is shared with Qwen3.5). config.deepstack_visual_indexes=[] - no DeepStack injection layers configured. |
| Depth (layers) | 27 |
| Hidden size | 1152 |
| Intermediate size | 4304 |
| Num heads | 16 |
| Patch size | 16 |
| Input channels | 3 |
| Output dim → LM | 5120 |
| Spatial merge size | 2 |
| Temporal patch size | 2 |

_Notes:_ hidden_act=gelu_pytorch_tanh; num_position_embeddings=2304. Identical geometry to Qwen3.5-27B vision encoder. config exposes top-level language_model_only=false flag (new in 3.6 config schema; no architectural impact).

### Vision token anchors (LM vocab IDs)

| | |
|---|---|
| image_token_id | 248056 |
| video_token_id | 248057 |
| vision_start_token_id | 248053 |
| vision_end_token_id | 248054 |

## Open questions

- Pre-training optimizer, learning-rate schedule, batch size, LR, weight decay, gradient clipping are not disclosed for Qwen3.6-27B. README implies the pre-training recipe is shared with (or close to) Qwen3.5 since it omits the family-level pre-training highlights and frames the release as a community-feedback refresh — but this is not stated explicitly.
- Total pre-training tokens and data mix are not disclosed numerically. Whether Qwen3.6 is a continued-pretraining refresh of Qwen3.5 weights, a fresh pretrain on similar data, or post-training-only over the same Qwen3.5 base is not stated.
- Multi-Token Prediction step depth D is not stated quantitatively (same gap as Qwen3.5; README says 'trained with multi-steps' and config exposes mtp_num_hidden_layers=1 only).
- Post-training pipeline structure for Qwen3.6 is undisclosed. Two new capabilities are highlighted — Agentic Coding (frontend + repo-level reasoning) and Thinking Preservation (preserve_thinking API kwarg) — but the underlying training algorithm, RL signals (execution feedback? unit-test rewards?), and SFT data mix for these are not detailed in README/blog.
- Mixed-precision training recipe is not disclosed (config.text_config.dtype=bfloat16 reflects the released checkpoint dtype only).
- Parallelism strategy and training infrastructure are not disclosed.
- Soft switches `/think` and `/no_think` are described as 'not officially supported' in the README, but the chat template (Jinja2) still references `/think` 5 times (per pre-extraction sourcing notes). The exact behavior — whether the template silently ignores soft-switch tokens, gracefully degrades, or still routes them to thinking/non-thinking modes — is not characterized. Verify against the rendered template if behavior matters for downstream tooling.
- Token embedding 248320 'Padded' is identical between Qwen3.5-27B and Qwen3.6-27B; the unpadded vocabulary size and the padding rationale (TP alignment? room for added vision/control tokens?) are not stated. The padding label is a vendor-disclosure artifact, not a behavioral difference.
- preserve_thinking is described as 'additionally trained' but the additional training recipe (continued SFT? small RL pass? data scale?) is not specified. For agent scenarios it is the most differentiated post-training feature in this release.
- Cross-version compare: Qwen3.6-27B is architecturally identical to Qwen3.5-27B (same layers, hidden, attention shape, FFN, vocab, vision encoder, MTP topology, context window, RoPE config). The release is a post-training-only refresh as far as disclosed signals indicate. If a Qwen3.6 tech report appears later disambiguating pre-training continuation vs fresh pretrain, re-read and update.
- Cached blog.html at qwen.ai/blog?id=qwen3.6-27b is a client-side-rendered SPA shell (only 'Qwen' is present in the static HTML), so substantive blog content was unavailable at extraction time.

---

_Generated from `data/extracted/qwen3.6-27b.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
