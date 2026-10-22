# MiniMax-M2.7

> English: [minimax-m2.7.md](./minimax-m2.7.md)

*Schema 版本: 8*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | minimax-m2 |
| 发布时间 | 2026-03 |
| 开放程度 | 开放权重 |
| 总参数量 | 229.9B |
| 激活参数量 | 9.8B |

**变体策略（variant policy）：** Version-specific checkpoint. Serving speed tiers do not establish distinct architecture or weight identities; this record covers the named official HF checkpoint.

## 数据源

- <https://huggingface.co/MiniMaxAI/MiniMax-M2.7/resolve/d494266a4affc0d2995ba1fa35c8481cbd84294b/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-M2.7/resolve/d494266a4affc0d2995ba1fa35c8481cbd84294b/README.md>
- <https://huggingface.co/MiniMaxAI/MiniMax-M2.7/resolve/d494266a4affc0d2995ba1fa35c8481cbd84294b/chat_template.jinja>
- <https://huggingface.co/MiniMaxAI/MiniMax-M2.7/resolve/d494266a4affc0d2995ba1fa35c8481cbd84294b/generation_config.json>
- <https://arxiv.org/pdf/2605.26494v1>
- <https://www.minimax.io/news/minimax-m27-en>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 62 |
| 隐藏维度 | 3072 |
| 上下文窗口 | 204800 |

**上下文说明：** Pinned M2.7 config allows 204800 positions; original M2 base report uses native 192K=196608. Do not normalize these distinct bounds.

### 注意力（GQA）

| | |
|---|---|
| 变体 | GQA |
| 头数 | 48 |
| KV 头数 | 8 |
| 头维度 | 128 |

**RoPE：** type=`standard`, base=`5000000`

**注意力补充说明：** Pinned config: rotary_dim=64 of head_dim=128; RoPE applies to half of each attention head.

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 0 |
| 单专家中间维度 | 1536 |

**路由：** Sigmoid routing with expert-specific bias; 8 of 256 routed experts active. Paper §2.2.1 says biases are optimized jointly with model parameters and reduce reliance on auxiliary losses; not assumed to be DeepSeek fixed-step auxiliary-loss-free updates.

### 组件

| | |
|---|---|
| 激活函数 | silu |
| 归一化 | RMSNorm, epsilon=1e-06 |

**Embedding 说明：** vocab_size=200064; tie_word_embeddings=false

### 辅助模块

**MTP speculative draft modules**

| | |
|---|---|
| 用途 | `speculative_decoding` |
| 是否随权重发布 | `[Unknown/Not Disclosed]` |

**结构：** Three MTP modules; one transformer layer per module (config); original M2 report describes copy-initialization, short draft-only warmup, then joint training.

_说明：_ Config use_mtp=true, num_mtp_modules=3. Config alone does not verify tensor presence; no full weight download performed.

### 并行 / 基础设施

[Unknown/Not Disclosed]

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | 29.2T for original M2 base (19.9T constant + 9.3T decay phase); version-specific additional training tokens undisclosed. |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** Shared M2 base pre-training: web, academic literature, books, code, structured QA; code/math/STEM upsampled. Series report describes agent-driven executable-workspace coding/cowork pipelines; per-checkpoint proportions undisclosed.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | 3 |
| 损失权重调度 | Original M2: one MTP module during initial pre-training, weight 0.3→0.1 in decay; expanded to three MTP modules during continued pre-training (series report §2.3). |

_共享模块：_ Config for this checkpoint: num_mtp_modules=3, mtp_transformer_layers=1; paper Figure 2 follows DeepSeek-V3 style. Exact per-version loss schedule beyond original M2 undisclosed.

### 对齐

**SFT：** Series report §5: rejection-sampled interleaved reasoning/action/observation trajectories in chat, reasoning, code and cowork; exact version-specific SFT mixture undisclosed.

**RL 方法：** CISPO (series-wide report §6): clipped importance-sampling weights with agent/process rewards. Forge decouples training/inference from white-box or black-box agent scaffolds.

**RLAIF：** `[Unknown/Not Disclosed]`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Interleaved-thinking SFT | `sft` | Domain-reward rejection sampling and multi-stage data cleaning. |
| 2 | Agent RL | `rl` | CISPO; Forge asynchronous infrastructure, windowed-FIFO scheduling and prefix-tree merging. This is a series-wide recipe, not a disclosed identical run per version. |

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `Interleaved reasoning` | Standard checkpoint use; preserve reasoning in assistant history. | M2 card explicitly requires retaining <think>...</think> across tool turns; no documented per-version effort axis. |

- **`Interleaved reasoning`**
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`, `top_k=40`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<minimax:tool_call>` |
| 结束 token | `</minimax:tool_call>` |
| 参数编码方式 | One or more <invoke name="FUNCTION"><parameter name="ARG">VALUE</parameter></invoke>; strings emitted directly and non-string argument values JSON-encoded via tojson(ensure_ascii=False). |

_说明：_ Tool messages serialized by pinned checkpoint template; parser flags not inferred from third-party recipes.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

### 量化（发布权重）

| | |
|---|---|
| 权重格式 | `FP8 (e4m3)` |
| 激活格式 | `dynamic FP8 (float8_e4m3fn config)` |
| 方法 | `[Unknown/Not Disclosed]` |
| 粒度 | weight_block_size=[128,128] |

**作用范围：** All eligible modules except gate, e_score_correction_bias and lm_head (config.quantization_config.modules_to_not_convert).

_说明：_ quant_method=fp8; config does not establish QAT versus PTQ. Training arithmetic remains UNKNOWN.

## 待解问题（open_questions）

- The M2-series report retrospectively describes a common base and evolving data/RL system; exact additional tokens, optimizer, learning-rate schedule and per-version run configuration remain undisclosed.
- MTP config metadata is not proof that every configured draft tensor is in the public checkpoint. Objective depth is supported by the paper; shipment remains UNKNOWN without tensor-index audit.
- Model card self-evolution is an agent loop that edits memory, skills and scaffold (100+ rounds, reported 30% improvement), not evidence of online weight updates or a distinct attention mechanism.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_由 `data/extracted/minimax-m2.7.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
