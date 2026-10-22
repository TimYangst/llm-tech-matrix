# MiniMax-VL-01

> 中文版：[minimax-vl-01.zh.md](./minimax-vl-01.zh.md)

*Schema version: 8*

## Overview

| | |
|---|---|
| Family | minimax-01 |
| Released | 2025-01 |
| Openness | Open weights |
| Total parameters | 456B language backbone + 303M vision encoder + projector (aggregate not stated) |
| Active parameters | 45.9B language backbone (vision/projector additional) |

**Variant policy:** Separate Text-01 and VL-01 checkpoints; VL-01 adds a vision encoder and projector to Text-01.

## Sources

- <https://huggingface.co/MiniMaxAI/MiniMax-VL-01/resolve/308b79934be140a43a0fb80f82b4e20d0ebe3cb8/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-VL-01/resolve/308b79934be140a43a0fb80f82b4e20d0ebe3cb8/README.md>
- <https://arxiv.org/pdf/2501.08313v1>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 80 |
| Hidden dim | 6144 |
| Context window | [Unknown/Not Disclosed] |

**Context notes:** Released VL config text_config.max_position_embeddings=8192, whereas inherited Text-01 long-context statements do not establish the supported VL product limit. No silent inheritance of 4M.

### Attention (hybrid)

| | |
|---|---|
| Variant | hybrid |
| Heads | 64 |
| KV heads | 8 |
| Head dim | 128 |

**RoPE:** type=`standard`, base=`10000000`

**Hybrid attention variants:**

| Name | Family | Q heads | KV heads | Head dim | RoPE | Notes |
|---|---|---|---|---|---|---|
| `lightning_attention` | `linear_attention` | 64 | [Unknown/Not Disclosed] | 128 | RoPE is documented for the softmax branch; no rotary operation assumed for linear attention. | Lightning Attention: I/O-aware linear attention with recurrent state and blockwise execution (MiniMax-01 report §§2.1–2.2). |
| `gqa` | `gqa` | 64 | 8 | 128 | Partial RoPE, rotary_dim=64; final checkpoint base 10000000. | — |

**Layer pattern:** (7 Lightning Attention layers, 1 GQA softmax layer) × 10, 80 total; config.attn_type_list has GQA at zero-based indices 7,15,...,79.

**Attention notes:** Pinned config: rotary_dim=64 of head_dim=128; RoPE applies to half of each attention head.

### FFN (moe)

**MoE:**

| | |
|---|---|
| Routed experts | 32 |
| Active experts per token | 2 |
| Shared experts | 0 |
| Per-expert intermediate size | 9216 |

**Routing:** Top-2 routing; MoE auxiliary loss coefficient 0.01 in original Text-01 pre-training (paper §4.2).

### Components

| | |
|---|---|
| Activation | [Unknown/Not Disclosed] |
| Normalization | RMSNorm, epsilon=1e-05; postnorm=true; DeepNorm scaling in the original Text-01 report. |

**Embedding notes:** vocab_size=200064; tie_word_embeddings=false

### Parallelism / infra

Original MiniMax-01 report §3: expert/tensor/data parallelism, Expert Tensor Parallel (ETP), varlen ring attention for softmax, LASP+ for linear-attention sequence parallelism. Exact M1 deployment degrees not assumed.

## Training

| | |
|---|---|
| Optimizer | Text-01 backbone pre-training: AdamW, beta1=0.9, beta2=0.95, weight_decay=0.1 (MiniMax-01 report §4.2). Multimodal-stage optimizer not stated. |
| Total training tokens | Model card says 512B multimodal tokens; paper §6.3 states 80B+420B+44.8B across stages I–III (544.8B). Discrepancy unresolved; inherited Text-01 training is additional. |

**LR schedule:** Text-01 backbone: 500-step warmup to 2e-4; constant for 7.2T tokens; 1.3e-4 for next 3.2T; exponential decay over 1T to 3e-5; context extension adds 300B+32B+26B tokens (report §4.2).

**Data mix notes:** Text-01: academic literature, books, web content and code; byte-level BPE, multilingual upsampling and model-scored quality filtering. Exact domain percentages undisclosed (report §4.1).

### Training objectives (beyond next-token prediction)

**Other objectives:**

- Vision encoder trained with CoCa-style contrastive image-text loss plus decoder cross-entropy (report §6.2.2).

### Alignment

**SFT:** Four-stage VL instruction/alignment pipeline (report §6.3).

**RL method:** DPO on model-scored multimodal preference pairs (report §6.3).

**RLAIF:** `True`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Modality alignment | `sft` | Update vision encoder and adapter using 80B caption tokens at 336×336. |
| 2 | Vision instruction tuning | `sft` | Unfreeze all parameters; 420B multimodal tokens mixed 20:1 with Text-01 post-training data. |
| 3 | User-experience tuning | `sft` | 44.8B multimodal tokens; one epoch. |
| 4 | Preference tuning | `dpo` | 40K image-text preference pairs scored by LLMs, including Text-01; mix pure-text pairs, early stopping before one epoch. |

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

## Multimodal

| | |
|---|---|
| Modalities | text, image |
| Fusion | `projection_mlp` |

**Fusion notes:** 303M from-scratch ViT-L/14 → randomly initialized two-layer MLP → Text-01. Dynamic image grids 336×336 to 2016×2016 plus 336×336 thumbnail; patches encoded separately and concatenated, with no pooling compression (report §6.2).

### Vision encoder

| | |
|---|---|
| Architecture | ViT-L/14 (from scratch) |
| Depth (layers) | 24 |
| Hidden size | 1024 |
| Intermediate size | 4096 |
| Num heads | 16 |
| Patch size | 14 |
| Input channels | [Unknown/Not Disclosed] |
| Output dim → LM | 6144 |
| Spatial merge size | [Unknown/Not Disclosed] |
| Temporal patch size | [Unknown/Not Disclosed] |

_Notes:_ CLIPVisionModel config architecture; CoCa-style training, not imported CLIP pretrained weights.

### Vision token anchors (LM vocab IDs)

| | |
|---|---|
| image_token_id | 200025 |
| video_token_id | [Unknown/Not Disclosed] |
| vision_start_token_id | [Unknown/Not Disclosed] |
| vision_end_token_id | [Unknown/Not Disclosed] |

## Open questions

- VL-01 supported user-facing context remains unresolved: checkpoint text_config says 8192, the shared report describes Text-01 trained 1M/extrapolated 4M; vendor does not reconcile the VL-specific limit.
- VL-01 model card says 512B multimodal tokens; paper stage budgets 80B+420B+44.8B sum to 544.8B. Neither figure is silently chosen as an exact whole-model total.
- Vision training count differs by unit/scope: card says 694M image-caption pairs; paper §6.2.2 says 37B low-resolution training pairs followed by 1.2B high-resolution pairs. Likely repeated exposures versus unique pairs, but not equated without an explicit statement.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_Generated from `data/extracted/minimax-vl-01.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
