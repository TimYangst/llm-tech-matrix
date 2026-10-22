# MiniMax-M1-80k

> English: [minimax-m1-80k.md](./minimax-m1-80k.md)

*Schema 版本: 8*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | minimax-m1 |
| 发布时间 | 2025-06 |
| 开放程度 | 开放权重 |
| 总参数量 | 456B |
| 激活参数量 | 45.9B |

**变体策略（variant policy）：** This record covers the 80K-output-budget checkpoint only. M1-40k is a separate intermediate checkpoint in the same RL run; -hf repositories are packaging variants, not independently extracted here. Vendor evaluation/recommendation: temperature=1.0, top_p=0.95; 80K is a separate checkpoint, not a runtime inference mode.

## 数据源

- <https://huggingface.co/MiniMaxAI/MiniMax-M1-80k/resolve/8d1494b1a260e22040d5b9b2eb332eb44500b34d/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-M1-80k/resolve/8d1494b1a260e22040d5b9b2eb332eb44500b34d/README.md>
- <https://arxiv.org/pdf/2506.13585v1>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 80 |
| 隐藏维度 | 6144 |
| 上下文窗口 | 1000000 |

**上下文说明：** M1 report/card state native 1M input and 80K output budget. The config upper bound max_position_embeddings=10240000 is not an advertised 10.24M validated context.

### 注意力（hybrid）

| | |
|---|---|
| 变体 | hybrid |
| 头数 | 64 |
| KV 头数 | 8 |
| 头维度 | 128 |

**RoPE：** type=`standard`, base=`10000000`

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `lightning_attention` | `linear_attention` | 64 | [Unknown/Not Disclosed] | 128 | RoPE is documented for the softmax branch; no rotary operation assumed for linear attention. | Lightning Attention: I/O-aware linear attention with recurrent state and blockwise execution (MiniMax-01 report §§2.1–2.2). |
| `gqa` | `gqa` | 64 | 8 | 128 | Partial RoPE, rotary_dim=64; final checkpoint base 10000000. | — |

**层模式：** (7 Lightning Attention layers, 1 GQA softmax layer) × 10, 80 total; config.attn_type_list has GQA at zero-based indices 7,15,...,79.

**注意力补充说明：** Pinned config: rotary_dim=64 of head_dim=128; RoPE applies to half of each attention head.

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 32 |
| 每 token 激活专家数 | 2 |
| 共享专家数 | 0 |
| 单专家中间维度 | 9216 |

**路由：** Top-2 of 32 experts; shared_intermediate_size=0. M1 continued training reduces the MoE auxiliary-loss coefficient, but its final value is undisclosed.

### 组件

| | |
|---|---|
| 激活函数 | silu |
| 归一化 | RMSNorm, epsilon=1e-05; postnorm=true; DeepNorm scaling in the original Text-01 report. |

**Embedding 说明：** vocab_size=200064; tie_word_embeddings=false

### 并行 / 基础设施

Original MiniMax-01 report §3: expert/tensor/data parallelism, Expert Tensor Parallel (ETP), varlen ring attention for softmax, LASP+ for linear-attention sequence parallelism. Exact M1 deployment degrees not assumed.

## 训练

| | |
|---|---|
| 优化器 | AdamW for RL, beta1=0.9, beta2=0.95, epsilon=1e-15 (M1 report §3.2); full inherited pre-training optimizer is not reasserted here. |
| 训练总 token 数 | 7.5T additional continual-pretraining tokens; lifetime total including Text-01 is not stated as one figure. |

**学习率调度：** Continual pre-training: 8e-5 constant for 2.5T tokens, then decay over 5T tokens to 8e-6 (report §2.1). RL learning-rate schedule undisclosed.

**数据配比：**

| | |
|---|---|
| STEM/code/books/reasoning | 70% of continual-pretraining corpus |

**数据配比说明：** Natural QA from webpages/forums/textbooks; explicitly avoids synthetic data in the continual-pretraining QA pipeline. SFT math+coding account for ~60%, a separate post-training distribution.

### 对齐

**SFT：** Cold-start long-CoT SFT on math, code, STEM, writing, QA and multi-turn chat; reflection behavior (report §2.2).

**RL 方法：** CISPO: Clipped IS-weight Policy Optimization; clips importance sampling weights rather than dropping token gradients; group-relative advantages and token-level loss (report §3.1).

**RLAIF：** `[Unknown/Not Disclosed]`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Continual pre-training | `continued_pretraining` | 7.5T additional tokens and gradual context extension from 32K to 1M. |
| 2 | Cold-start SFT | `sft` | High-quality long-CoT demonstrations with reflection; ~60% math/code. |
| 3 | 40K then 80K reasoning RL | `rl` | CISPO; 40K checkpoint is intermediate. Output length extended 40K→48K→56K→64K→72K→80K; full RL run uses 512 H800 GPUs for three weeks. |

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** RL output LM head raised to FP32 to align training and rollout probabilities; other compute/master-weight precision not fully specified (report §3.2).

**稳定性 trick：** Smooth context extension prevents gradient explosion; repetition truncation when 3000 consecutive tokens each have probability >0.99; small AdamW epsilon chosen for very small gradients.

## 待解问题（open_questions）

- M1-40k and HF-compatible repackagings are not separate canonical records in this collection. Exact per-variant weight/dtype differences require future audit.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_由 `data/extracted/minimax-m1-80k.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
