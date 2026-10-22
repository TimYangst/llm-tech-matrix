# MiniMax-M2.5

> 中文版：[minimax-m2.5.zh.md](./minimax-m2.5.zh.md)

*Schema version: 8*

## Overview

| | |
|---|---|
| Family | minimax-m2 |
| Released | 2026-02 |
| Openness | Open weights |
| Total parameters | 229.9B |
| Active parameters | 9.8B |

**Variant policy:** Version-specific checkpoint. Serving speed tiers do not establish distinct architecture or weight identities; this record covers the named official HF checkpoint.

## Sources

- <https://huggingface.co/MiniMaxAI/MiniMax-M2.5/resolve/f710177d938eff80b684d42c5aa84b382612f21f/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-M2.5/resolve/f710177d938eff80b684d42c5aa84b382612f21f/README.md>
- <https://huggingface.co/MiniMaxAI/MiniMax-M2.5/resolve/f710177d938eff80b684d42c5aa84b382612f21f/chat_template.jinja>
- <https://huggingface.co/MiniMaxAI/MiniMax-M2.5/resolve/f710177d938eff80b684d42c5aa84b382612f21f/generation_config.json>
- <https://arxiv.org/pdf/2605.26494v1>
- <https://www.minimax.io/news/minimax-m25>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 62 |
| Hidden dim | 3072 |
| Context window | 196608 |

**Context notes:** Native 192K=196608 in M2 series report and this config.

### Attention (GQA)

| | |
|---|---|
| Variant | GQA |
| Heads | 48 |
| KV heads | 8 |
| Head dim | 128 |

**RoPE:** type=`standard`, base=`5000000`

**Attention notes:** Pinned config: rotary_dim=64 of head_dim=128; RoPE applies to half of each attention head.

### FFN (moe)

**MoE:**

| | |
|---|---|
| Routed experts | 256 |
| Active experts per token | 8 |
| Shared experts | 0 |
| Per-expert intermediate size | 1536 |

**Routing:** Sigmoid routing with expert-specific bias; 8 of 256 routed experts active. Paper §2.2.1 says biases are optimized jointly with model parameters and reduce reliance on auxiliary losses; not assumed to be DeepSeek fixed-step auxiliary-loss-free updates.

### Components

| | |
|---|---|
| Activation | silu |
| Normalization | RMSNorm, epsilon=1e-06 |

**Embedding notes:** vocab_size=200064; tie_word_embeddings=false

### Auxiliary modules

**MTP speculative draft modules**

| | |
|---|---|
| Purpose | `speculative_decoding` |
| Shipped in checkpoint | `[Unknown/Not Disclosed]` |

**Architecture:** Three MTP modules; one transformer layer per module (config); original M2 report describes copy-initialization, short draft-only warmup, then joint training.

_Notes:_ Config use_mtp=true, num_mtp_modules=3. Config alone does not verify tensor presence; no full weight download performed.

### Parallelism / infra

[Unknown/Not Disclosed]

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] |
| Total training tokens | 29.2T for original M2 base (19.9T constant + 9.3T decay phase); version-specific additional training tokens undisclosed. |

**LR schedule:** [Unknown/Not Disclosed]

**Data mix notes:** Shared M2 base pre-training: web, academic literature, books, code, structured QA; code/math/STEM upsampled. Series report describes agent-driven executable-workspace coding/cowork pipelines; per-checkpoint proportions undisclosed.

### Training objectives (beyond next-token prediction)

**Multi-Token Prediction (MTP):**

| | |
|---|---|
| Depth (D) | 3 |
| Loss weight schedule | Original M2: one MTP module during initial pre-training, weight 0.3→0.1 in decay; expanded to three MTP modules during continued pre-training (series report §2.3). |

_Shared modules:_ Config for this checkpoint: num_mtp_modules=3, mtp_transformer_layers=1; paper Figure 2 follows DeepSeek-V3 style. Exact per-version loss schedule beyond original M2 undisclosed.

### Alignment

**SFT:** Series report §5: rejection-sampled interleaved reasoning/action/observation trajectories in chat, reasoning, code and cowork; exact version-specific SFT mixture undisclosed.

**RL method:** CISPO (series-wide report §6): clipped importance-sampling weights with agent/process rewards. Forge decouples training/inference from white-box or black-box agent scaffolds.

**RLAIF:** `[Unknown/Not Disclosed]`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Interleaved-thinking SFT | `sft` | Domain-reward rejection sampling and multi-stage data cleaning. |
| 2 | Agent RL | `rl` | CISPO; Forge asynchronous infrastructure, windowed-FIFO scheduling and prefix-tree merging. This is a series-wide recipe, not a disclosed identical run per version. |

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `Interleaved reasoning` | Standard checkpoint use; preserve reasoning in assistant history. | M2 card explicitly requires retaining <think>...</think> across tool turns; no documented per-version effort axis. |

- **`Interleaved reasoning`**
    - Recommended sampling: `temperature=1.0`, `top_p=0.95`, `top_k=40`

**Tool-call protocol:**

| | |
|---|---|
| Format | `xml-like` |
| Start token | `<minimax:tool_call>` |
| End token | `</minimax:tool_call>` |
| Arguments schema | One or more <invoke name="FUNCTION"><parameter name="ARG">VALUE</parameter></invoke>; strings emitted directly and non-string argument values JSON-encoded via tojson(ensure_ascii=False). |

_Notes:_ Tool messages serialized by pinned checkpoint template; parser flags not inferred from third-party recipes.

### Advanced

**Self-distillation:** [Unknown/Not Disclosed]

**Mixed precision:** [Unknown/Not Disclosed]

### Quantization (shipped weights)

| | |
|---|---|
| Weight format | `FP8 (e4m3)` |
| Activation format | `dynamic FP8 (float8_e4m3fn config)` |
| Method | `[Unknown/Not Disclosed]` |
| Granularity | weight_block_size=[128,128] |

**Scope:** All eligible modules except gate, e_score_correction_bias and lm_head (config.quantization_config.modules_to_not_convert).

_Notes:_ quant_method=fp8; config does not establish QAT versus PTQ. Training arithmetic remains UNKNOWN.

## Open questions

- The M2-series report retrospectively describes a common base and evolving data/RL system; exact additional tokens, optimizer, learning-rate schedule and per-version run configuration remain undisclosed.
- MTP config metadata is not proof that every configured draft tensor is in the public checkpoint. Objective depth is supported by the paper; shipment remains UNKNOWN without tensor-index audit.
- M2.5/M2.5-Lightning are advertised as equal-capability speed tiers; no evidence here establishes different HF weights. Forge/CISPO/process-reward descriptions are explicit in this card.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_Generated from `data/extracted/minimax-m2.5.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
