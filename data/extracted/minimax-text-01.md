# MiniMax-Text-01

> 中文版：[minimax-text-01.zh.md](./minimax-text-01.zh.md)

*Schema version: 8*

## Overview

| | |
|---|---|
| Family | minimax-01 |
| Released | 2025-01 |
| Openness | Open weights |
| Total parameters | 456B |
| Active parameters | 45.9B |

**Variant policy:** Separate Text-01 and VL-01 checkpoints; VL-01 adds a vision encoder and projector to Text-01.

## Sources

- <https://huggingface.co/MiniMaxAI/MiniMax-Text-01/resolve/a7351bf2bee0e1253919d349f1ad304e6dac13e9/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-Text-01/resolve/a7351bf2bee0e1253919d349f1ad304e6dac13e9/README.md>
- <https://arxiv.org/pdf/2501.08313v1>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 80 |
| Hidden dim | 6144 |
| Context window | 4000000 |

**Context notes:** Card advertises up to 4 million inference tokens; report §4.2 trains to 1M and demonstrates 4M vanilla NIAH extrapolation. Config positional bound is 10240000 and is not treated as validated context.

**Context extension:**

| | |
|---|---|
| Method | hybrid-lightning extrapolation |
| Trained max | 1000000 |
| Extended max | 4000000 |
| Factor | 4.0 |
| Original max (RoPE) | 1000000 |

_Notes:_ Length extrapolation reported on vanilla NIAH; no YaRN claim. Training stages 128K/512K/1M use RoPE base 5M/10M/10M.

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
| Activation | silu |
| Normalization | RMSNorm, epsilon=1e-05; postnorm=true; DeepNorm scaling in the original Text-01 report. |

**Embedding notes:** vocab_size=200064; tie_word_embeddings=false

### Parallelism / infra

Original MiniMax-01 report §3: expert/tensor/data parallelism, Expert Tensor Parallel (ETP), varlen ring attention for softmax, LASP+ for linear-attention sequence parallelism. Exact M1 deployment degrees not assumed.

## Training

| | |
|---|---|
| Optimizer | AdamW, beta1=0.9, beta2=0.95, weight_decay=0.1 (report §4.2). |
| Total training tokens | 11.4T initial pre-training (7.2T+3.2T+1T), plus 358B context-extension tokens (300B+32B+26B), derived from report §4.2 stage budgets. |

**LR schedule:** Text-01 backbone: 500-step warmup to 2e-4; constant for 7.2T tokens; 1.3e-4 for next 3.2T; exponential decay over 1T to 3e-5; context extension adds 300B+32B+26B tokens (report §4.2).

**Data mix notes:** Text-01: academic literature, books, web content and code; byte-level BPE, multilingual upsampling and model-scored quality filtering. Exact domain percentages undisclosed (report §4.1).

### Alignment

**SFT:** Rejection-sampled demonstrations from domain expert models; diversity filtering (report §5.3).

**RL method:** Offline DPO followed by modified online GRPO with importance-weight clipping (report §§5.4.1–5.4.2).

**RLAIF:** `True`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Supervised fine-tuning | `sft` | Domain expert rejection-sampled demonstrations. |
| 2 | Offline RL | `dpo` | Reward models select best/worst sampled responses for preference pairs. |
| 3 | Online RL | `rl` | Modified GRPO with importance-weight clipping and additional stabilization. |

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

## Open questions

- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_Generated from `data/extracted/minimax-text-01.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
