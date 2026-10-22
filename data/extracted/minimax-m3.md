# MiniMax-M3

> 中文版：[minimax-m3.zh.md](./minimax-m3.zh.md)

*Schema version: 8*

## Overview

| | |
|---|---|
| Family | minimax-m3 |
| Released | 2026-06 |
| Openness | Open weights |
| Total parameters | ~428B |
| Active parameters | ~23B |

**Variant policy:** One native text/image/video checkpoint with enabled/adaptive/disabled thinking modes; MXFP8 is separately packaged and outside this record.

## Sources

- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/README.md>
- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/chat_template.jinja>
- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/generation_config.json>
- <https://arxiv.org/pdf/2606.13392v1>
- <https://www.minimax.io/blog/minimax-m3>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 60 |
| Hidden dim | 6144 |
| Context window | 1048576 |

**Context notes:** Native 1M context; config.max_position_embeddings=1048576.

### Attention (GQA)

| | |
|---|---|
| Variant | GQA |
| Heads | 64 |
| KV heads | 4 |
| Head dim | 128 |

**RoPE:** type=`standard`, base=`5000000`

**Layer pattern:** First 3 layers use dense GQA; layers 3–59 (zero-indexed) use MSA on GQA (sparse_attention_freq).

**Attention notes:** Pinned config: rotary_dim=64 of head_dim=128; RoPE applies to half of each attention head. Per-head QK normalization (qk_norm_type=per_head); use_gemma_norm=true; attention_output_gate=false.

**Sparse attention:**

| | |
|---|---|
| Kind | `msa` |
| Selected entries (top-k) | [Unknown/Not Disclosed] |
| Indexer heads | 4 |
| Indexer head dim | 128 |

**Selection rule:** Lightweight Index Branch max-pools token scores into blocks, independently selects top-k blocks per GQA group; always includes the local block. Main Branch performs exact softmax attention over selected blocks (MSA report §3).

**Training recipe:** MSA mechanism: KL alignment of index distribution with group-averaged Main Branch distribution, stop-gradient at index inputs; dense-indexer warmup then sparse training. Production M3 stage/token budget is not disclosed.

_Notes:_ Pinned production config: sparse_topk_blocks=16, sparse_block_size=128, sparse_score_type=max, sparse_local_block=1, sparse_init_block=0. This is a BLOCK budget, not 16 individual KV tokens; at most 2048 token slots per group before causal masking. No KV compression ratio is asserted.

### FFN (hybrid)

**Dense intermediate size:** `12288`

**MoE:**

| | |
|---|---|
| Routed experts | 128 |
| Active experts per token | 4 |
| Shared experts | 1 |
| Per-expert intermediate size | 3072 |

**Routing:** Sigmoid top-4 routing over 128 local experts with routing bias and routed_scaling_factor=2.0; one shared expert, shared_intermediate_size=3072 (config).

**Layer partition:** First 3 layers dense (moe_layer_freq=0), remaining 57 layers MoE; dense_intermediate_size=12288, routed expert intermediate_size=3072, shared expert intermediate_size=3072.

### Components

| | |
|---|---|
| Activation | swigluoai (config), alpha=1.702, limit=7.0; precise clamp formula not inferred from identifier alone. |
| Normalization | RMSNorm epsilon=1e-6; use_gemma_norm=true; per-head QK normalization (config). |

**Embedding notes:** vocab_size=200064; tie_word_embeddings=false

### Auxiliary modules

**Configured MTP modules**

| | |
|---|---|
| Purpose | `multi_token_prediction` |
| Shipped in checkpoint | `[Unknown/Not Disclosed]` |

**Architecture:** text_config.num_mtp_modules=7 and num_nextn_predict_layers=1; mapping between module count and prediction horizon is not documented in the registered sources.

### Parallelism / infra

[Unknown/Not Disclosed]

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] |
| Total training tokens | [Unknown/Not Disclosed] |

**LR schedule:** [Unknown/Not Disclosed]

### Training objectives (beyond next-token prediction)

**Other objectives:**

- Native mixed text/image/video training from the first step (model card); detailed production losses and weights undisclosed.

### Alignment

**SFT:** [Unknown/Not Disclosed]

**RL method:** [Unknown/Not Disclosed]

**RLAIF:** `[Unknown/Not Disclosed]`

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `enabled` | API thinking=enabled; local chat template thinking_mode=enabled. | Always reason, including after tool results; local generation prefix <mm:think>. |
| `adaptive` | API thinking=adaptive; local chat template thinking_mode=adaptive. | Model decides whether to reason; local template default when thinking_mode is absent. |
| `disabled` | API thinking=disabled; local chat template thinking_mode=disabled. | Suppress reasoning; local generation prefix </mm:think>. |

- **`enabled`**
    - Kwargs: `thinking=enabled`, `thinking_mode=enabled`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95`
- **`adaptive`**
    - Kwargs: `thinking=adaptive`, `thinking_mode=adaptive`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95`
- **`disabled`**
    - Kwargs: `thinking=disabled`, `thinking_mode=disabled`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95`

**Tool-call protocol:**

| | |
|---|---|
| Format | `xml-like` |
| Start token | `]<]minimax[>[<tool_call>` |
| End token | `]<]minimax[>[</tool_call>` |
| Arguments schema | Namespace prefix ]<]minimax[>[ before XML elements; <invoke name="FUNCTION"> with argument-name elements. Recursive XML expansion for nested mappings and arrays; null-valued mappings omitted. |

_Notes:_ New wire format differs from M2 <parameter name=...>; reasoning markers <mm:think>...</mm:think>. Pinned template renders reasoning for all assistant turns.

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

## Multimodal

| | |
|---|---|
| Modalities | text, image, video |
| Fusion | `native_early` |

**Fusion notes:** Model card states mixed-modality training from the first step. Vision features are projected into the 6144-wide text stream; native training does not imply absence of a vision encoder/projector.

### Vision encoder

| | |
|---|---|
| Architecture | ViT (clip_vision_model config), 3D RoPE |
| Depth (layers) | 32 |
| Hidden size | 1280 |
| Intermediate size | 5120 |
| Num heads | 16 |
| Patch size | 14 |
| Input channels | 3 |
| Output dim → LM | 6144 |
| Spatial merge size | 2 |
| Temporal patch size | 2 |

_Notes:_ image_size=2016; vision_segment_max_frames=4; patch_merge compression; vision RoPE base 10000, mode 3d (config). Pretrained initialization source not disclosed.

### Vision token anchors (LM vocab IDs)

| | |
|---|---|
| image_token_id | 200025 |
| video_token_id | 200026 |
| vision_start_token_id | [Unknown/Not Disclosed] |
| vision_end_token_id | [Unknown/Not Disclosed] |

## Open questions

- MSA paper experiments use a 109B MoE and 3T-token budget; these do not disclose production M3 (~428B, ~23B active) training tokens, optimizer, schedule or post-training pipeline.
- MSA typed top_k remains UNKNOWN because the config defines 16 blocks ×128 tokens, while schema field describes KV-entry count. Block count/size recorded explicitly in sparse_attention.notes.
- MTP config has num_mtp_modules=7 and num_nextn_predict_layers=1. Exact objective depth, horizon, loss weight and public weight shipment require further vendor/code evidence.
- MiniMax M3.1 Flash (October 19) is a later API release with weights promised later; it is not the M3 checkpoint or an open-weight update in this snapshot.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_Generated from `data/extracted/minimax-m3.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
