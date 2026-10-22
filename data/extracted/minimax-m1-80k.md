# MiniMax-M1-80k

> 中文版：[minimax-m1-80k.zh.md](./minimax-m1-80k.zh.md)

*Schema version: 8*

## Overview

| | |
|---|---|
| Family | minimax-m1 |
| Released | 2025-06 |
| Openness | Open weights |
| Total parameters | 456B |
| Active parameters | 45.9B |

**Variant policy:** This record covers the 80K-output-budget checkpoint only. M1-40k is a separate intermediate checkpoint in the same RL run; -hf repositories are packaging variants, not independently extracted here. Vendor evaluation/recommendation: temperature=1.0, top_p=0.95; 80K is a separate checkpoint, not a runtime inference mode.

## Sources

- <https://huggingface.co/MiniMaxAI/MiniMax-M1-80k/resolve/8d1494b1a260e22040d5b9b2eb332eb44500b34d/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-M1-80k/resolve/8d1494b1a260e22040d5b9b2eb332eb44500b34d/README.md>
- <https://arxiv.org/pdf/2506.13585v1>
- <https://arxiv.org/pdf/2501.08313v1>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 80 |
| Hidden dim | 6144 |
| Context window | 1000000 |

**Context notes:** M1 report/card state native 1M input and 80K output budget. The config upper bound max_position_embeddings=10240000 is not an advertised 10.24M validated context.

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

**Routing:** Top-2 of 32 experts; shared_intermediate_size=0. M1 continued training reduces the MoE auxiliary-loss coefficient, but its final value is undisclosed.

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
| Optimizer | AdamW for RL, beta1=0.9, beta2=0.95, epsilon=1e-15 (M1 report §3.2); full inherited pre-training optimizer is not reasserted here. |
| Total training tokens | 7.5T additional continual-pretraining tokens; lifetime total including Text-01 is not stated as one figure. |

**LR schedule:** Continual pre-training: 8e-5 constant for 2.5T tokens, then decay over 5T tokens to 8e-6 (report §2.1). RL learning-rate schedule undisclosed.

**Data mix:**

| | |
|---|---|
| STEM/code/books/reasoning | 70% of continual-pretraining corpus |

**Data mix notes:** Natural QA from webpages/forums/textbooks; explicitly avoids synthetic data in the continual-pretraining QA pipeline. SFT math+coding account for ~60%, a separate post-training distribution.

### Alignment

**SFT:** Cold-start long-CoT SFT on math, code, STEM, writing, QA and multi-turn chat; reflection behavior (report §2.2).

**RL method:** CISPO: Clipped IS-weight Policy Optimization; clips importance sampling weights rather than dropping token gradients; group-relative advantages and token-level loss (report §3.1).

**RLAIF:** `[Unknown/Not Disclosed]`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Continual pre-training | `continued_pretraining` | 7.5T additional tokens and gradual context extension from 32K to 1M. |
| 2 | Cold-start SFT | `sft` | High-quality long-CoT demonstrations with reflection; ~60% math/code. |
| 3 | 40K then 80K reasoning RL | `rl` | CISPO; 40K checkpoint is intermediate. Output length extended 40K→48K→56K→64K→72K→80K; full RL run uses 512 H800 GPUs for three weeks. |

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** RL output LM head raised to FP32 to align training and rollout probabilities; other compute/master-weight precision not fully specified (report §3.2).

**Stability tricks:** Smooth context extension prevents gradient explosion; repetition truncation when 3000 consecutive tokens each have probability >0.99; small AdamW epsilon chosen for very small gradients.

## Open questions

- M1-40k and HF-compatible repackagings are not separate canonical records in this collection. Exact per-variant weight/dtype differences require future audit.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_Generated from `data/extracted/minimax-m1-80k.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
