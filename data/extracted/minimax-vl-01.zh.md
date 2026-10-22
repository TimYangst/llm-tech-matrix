# MiniMax-VL-01

> English: [minimax-vl-01.md](./minimax-vl-01.md)

*Schema 版本: 8*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | minimax-01 |
| 发布时间 | 2025-01 |
| 开放程度 | 开放权重 |
| 总参数量 | 456B language backbone + 303M vision encoder + projector (aggregate not stated) |
| 激活参数量 | 45.9B language backbone (vision/projector additional) |

**变体策略（variant policy）：** Separate Text-01 and VL-01 checkpoints; VL-01 adds a vision encoder and projector to Text-01.

## 数据源

- <https://huggingface.co/MiniMaxAI/MiniMax-VL-01/resolve/308b79934be140a43a0fb80f82b4e20d0ebe3cb8/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-VL-01/resolve/308b79934be140a43a0fb80f82b4e20d0ebe3cb8/README.md>
- <https://arxiv.org/pdf/2501.08313v1>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 80 |
| 隐藏维度 | 6144 |
| 上下文窗口 | [Unknown/Not Disclosed] |

**上下文说明：** Released VL config text_config.max_position_embeddings=8192, whereas inherited Text-01 long-context statements do not establish the supported VL product limit. No silent inheritance of 4M.

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
| 激活函数 | [Unknown/Not Disclosed] |
| 归一化 | RMSNorm, epsilon=1e-05; postnorm=true; DeepNorm scaling in the original Text-01 report. |

**Embedding 说明：** vocab_size=200064; tie_word_embeddings=false

### 并行 / 基础设施

Original MiniMax-01 report §3: expert/tensor/data parallelism, Expert Tensor Parallel (ETP), varlen ring attention for softmax, LASP+ for linear-attention sequence parallelism. Exact M1 deployment degrees not assumed.

## 训练

| | |
|---|---|
| 优化器 | Text-01 backbone pre-training: AdamW, beta1=0.9, beta2=0.95, weight_decay=0.1 (MiniMax-01 report §4.2). Multimodal-stage optimizer not stated. |
| 训练总 token 数 | Model card says 512B multimodal tokens; paper §6.3 states 80B+420B+44.8B across stages I–III (544.8B). Discrepancy unresolved; inherited Text-01 training is additional. |

**学习率调度：** Text-01 backbone: 500-step warmup to 2e-4; constant for 7.2T tokens; 1.3e-4 for next 3.2T; exponential decay over 1T to 3e-5; context extension adds 300B+32B+26B tokens (report §4.2).

**数据配比说明：** Text-01: academic literature, books, web content and code; byte-level BPE, multilingual upsampling and model-scored quality filtering. Exact domain percentages undisclosed (report §4.1).

### 训练目标（next-token prediction 之外）

**其他训练目标：**

- Vision encoder trained with CoCa-style contrastive image-text loss plus decoder cross-entropy (report §6.2.2).

### 对齐

**SFT：** Four-stage VL instruction/alignment pipeline (report §6.3).

**RL 方法：** DPO on model-scored multimodal preference pairs (report §6.3).

**RLAIF：** `True`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Modality alignment | `sft` | Update vision encoder and adapter using 80B caption tokens at 336×336. |
| 2 | Vision instruction tuning | `sft` | Unfreeze all parameters; 420B multimodal tokens mixed 20:1 with Text-01 post-training data. |
| 3 | User-experience tuning | `sft` | 44.8B multimodal tokens; one epoch. |
| 4 | Preference tuning | `dpo` | 40K image-text preference pairs scored by LLMs, including Text-01; mix pure-text pairs, early stopping before one epoch. |

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

## 多模态

| | |
|---|---|
| 模态 | text, image |
| 融合方式 | `projection_mlp` |

**融合方式说明：** 303M from-scratch ViT-L/14 → randomly initialized two-layer MLP → Text-01. Dynamic image grids 336×336 to 2016×2016 plus 336×336 thumbnail; patches encoded separately and concatenated, with no pooling compression (report §6.2).

### 视觉编码器

| | |
|---|---|
| 架构 | ViT-L/14 (from scratch) |
| 层数 | 24 |
| 隐藏维度 | 1024 |
| 中间维度 | 4096 |
| 头数 | 16 |
| patch 大小 | 14 |
| 输入通道数 | [Unknown/Not Disclosed] |
| 输出维度 → LM | 6144 |
| 空间合并大小 | [Unknown/Not Disclosed] |
| 时序 patch 大小 | [Unknown/Not Disclosed] |

_说明：_ CLIPVisionModel config architecture; CoCa-style training, not imported CLIP pretrained weights.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 200025 |
| video_token_id | [Unknown/Not Disclosed] |
| vision_start_token_id | [Unknown/Not Disclosed] |
| vision_end_token_id | [Unknown/Not Disclosed] |

## 待解问题（open_questions）

- VL-01 supported user-facing context remains unresolved: checkpoint text_config says 8192, the shared report describes Text-01 trained 1M/extrapolated 4M; vendor does not reconcile the VL-specific limit.
- VL-01 model card says 512B multimodal tokens; paper stage budgets 80B+420B+44.8B sum to 544.8B. Neither figure is silently chosen as an exact whole-model total.
- Vision training count differs by unit/scope: card says 694M image-caption pairs; paper §6.2.2 says 37B low-resolution training pairs followed by 1.2B high-resolution pairs. Likely repeated exposures versus unique pairs, but not equated without an explicit statement.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_由 `data/extracted/minimax-vl-01.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
