# MiniMax-Text-01

> English: [minimax-text-01.md](./minimax-text-01.md)

*Schema 版本: 8*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | minimax-01 |
| 发布时间 | 2025-01 |
| 开放程度 | 开放权重 |
| 总参数量 | 456B |
| 激活参数量 | 45.9B |

**变体策略（variant policy）：** Separate Text-01 and VL-01 checkpoints; VL-01 adds a vision encoder and projector to Text-01.

## 数据源

- <https://huggingface.co/MiniMaxAI/MiniMax-Text-01/resolve/a7351bf2bee0e1253919d349f1ad304e6dac13e9/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-Text-01/resolve/a7351bf2bee0e1253919d349f1ad304e6dac13e9/README.md>
- <https://arxiv.org/pdf/2501.08313v1>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 80 |
| 隐藏维度 | 6144 |
| 上下文窗口 | 4000000 |

**上下文说明：** Card advertises up to 4 million inference tokens; report §4.2 trains to 1M and demonstrates 4M vanilla NIAH extrapolation. Config positional bound is 10240000 and is not treated as validated context.

**上下文扩展：**

| | |
|---|---|
| 方法 | hybrid-lightning extrapolation |
| 训练最大长度 | 1000000 |
| 扩展最大长度 | 4000000 |
| 倍率 | 4.0 |
| RoPE 原始最大长度 | 1000000 |

_说明：_ Length extrapolation reported on vanilla NIAH; no YaRN claim. Training stages 128K/512K/1M use RoPE base 5M/10M/10M.

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

**路由：** Top-2 routing; MoE auxiliary loss coefficient 0.01 in original Text-01 pre-training (paper §4.2).

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
| 优化器 | AdamW, beta1=0.9, beta2=0.95, weight_decay=0.1 (report §4.2). |
| 训练总 token 数 | 11.4T initial pre-training (7.2T+3.2T+1T), plus 358B context-extension tokens (300B+32B+26B), derived from report §4.2 stage budgets. |

**学习率调度：** Text-01 backbone: 500-step warmup to 2e-4; constant for 7.2T tokens; 1.3e-4 for next 3.2T; exponential decay over 1T to 3e-5; context extension adds 300B+32B+26B tokens (report §4.2).

**数据配比说明：** Text-01: academic literature, books, web content and code; byte-level BPE, multilingual upsampling and model-scored quality filtering. Exact domain percentages undisclosed (report §4.1).

### 对齐

**SFT：** Rejection-sampled demonstrations from domain expert models; diversity filtering (report §5.3).

**RL 方法：** Offline DPO followed by modified online GRPO with importance-weight clipping (report §§5.4.1–5.4.2).

**RLAIF：** `True`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Supervised fine-tuning | `sft` | Domain expert rejection-sampled demonstrations. |
| 2 | Offline RL | `dpo` | Reward models select best/worst sampled responses for preference pairs. |
| 3 | Online RL | `rl` | Modified GRPO with importance-weight clipping and additional stabilization. |

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

## 待解问题（open_questions）

- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_由 `data/extracted/minimax-text-01.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
