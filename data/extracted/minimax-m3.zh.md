# MiniMax-M3

> English: [minimax-m3.md](./minimax-m3.md)

*Schema 版本: 8*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | minimax-m3 |
| 发布时间 | 2026-06 |
| 开放程度 | 开放权重 |
| 总参数量 | ~428B |
| 激活参数量 | ~23B |

**变体策略（variant policy）：** One native text/image/video checkpoint with enabled/adaptive/disabled thinking modes; MXFP8 is separately packaged and outside this record.

## 数据源

- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/config.json>
- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/README.md>
- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/chat_template.jinja>
- <https://huggingface.co/MiniMaxAI/MiniMax-M3/resolve/f0e1c1e04d40177e4673a22097036854f536e9c0/generation_config.json>
- <https://arxiv.org/pdf/2606.13392v1>
- <https://www.minimax.io/blog/minimax-m3>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 60 |
| 隐藏维度 | 6144 |
| 上下文窗口 | 1048576 |

**上下文说明：** Native 1M context; config.max_position_embeddings=1048576.

### 注意力（GQA）

| | |
|---|---|
| 变体 | GQA |
| 头数 | 64 |
| KV 头数 | 4 |
| 头维度 | 128 |

**RoPE：** type=`standard`, base=`5000000`

**层模式：** First 3 layers use dense GQA; layers 3–59 (zero-indexed) use MSA on GQA (sparse_attention_freq).

**注意力补充说明：** Pinned config: rotary_dim=64 of head_dim=128; RoPE applies to half of each attention head. Per-head QK normalization (qk_norm_type=per_head); use_gemma_norm=true; attention_output_gate=false.

**稀疏注意力：**

| | |
|---|---|
| 类型 | `msa` |
| 保留条目数（top-k） | [Unknown/Not Disclosed] |
| Indexer 头数 | 4 |
| Indexer 头维度 | 128 |

**选择规则：** Lightweight Index Branch max-pools token scores into blocks, independently selects top-k blocks per GQA group; always includes the local block. Main Branch performs exact softmax attention over selected blocks (MSA report §3).

**训练配方：** MSA mechanism: KL alignment of index distribution with group-averaged Main Branch distribution, stop-gradient at index inputs; dense-indexer warmup then sparse training. Production M3 stage/token budget is not disclosed.

_说明：_ Pinned production config: sparse_topk_blocks=16, sparse_block_size=128, sparse_score_type=max, sparse_local_block=1, sparse_init_block=0. This is a BLOCK budget, not 16 individual KV tokens; at most 2048 token slots per group before causal masking. No KV compression ratio is asserted.

### FFN（hybrid）

**Dense 中间维度：** `12288`

**MoE：**

| | |
|---|---|
| 可路由专家数 | 128 |
| 每 token 激活专家数 | 4 |
| 共享专家数 | 1 |
| 单专家中间维度 | 3072 |

**路由：** Sigmoid top-4 routing over 128 local experts with routing bias and routed_scaling_factor=2.0; one shared expert, shared_intermediate_size=3072 (config).

**层划分：** First 3 layers dense (moe_layer_freq=0), remaining 57 layers MoE; dense_intermediate_size=12288, routed expert intermediate_size=3072, shared expert intermediate_size=3072.

### 组件

| | |
|---|---|
| 激活函数 | swigluoai (config), alpha=1.702, limit=7.0; precise clamp formula not inferred from identifier alone. |
| 归一化 | RMSNorm epsilon=1e-6; use_gemma_norm=true; per-head QK normalization (config). |

**Embedding 说明：** vocab_size=200064; tie_word_embeddings=false

### 辅助模块

**Configured MTP modules**

| | |
|---|---|
| 用途 | `multi_token_prediction` |
| 是否随权重发布 | `[Unknown/Not Disclosed]` |

**结构：** text_config.num_mtp_modules=7 and num_nextn_predict_layers=1; mapping between module count and prediction horizon is not documented in the registered sources.

### 并行 / 基础设施

[Unknown/Not Disclosed]

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

### 训练目标（next-token prediction 之外）

**其他训练目标：**

- Native mixed text/image/video training from the first step (model card); detailed production losses and weights undisclosed.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `enabled` | API thinking=enabled; local chat template thinking_mode=enabled. | Always reason, including after tool results; local generation prefix <mm:think>. |
| `adaptive` | API thinking=adaptive; local chat template thinking_mode=adaptive. | Model decides whether to reason; local template default when thinking_mode is absent. |
| `disabled` | API thinking=disabled; local chat template thinking_mode=disabled. | Suppress reasoning; local generation prefix </mm:think>. |

- **`enabled`**
    - Kwargs：`thinking=enabled`, `thinking_mode=enabled`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`
- **`adaptive`**
    - Kwargs：`thinking=adaptive`, `thinking_mode=adaptive`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`
- **`disabled`**
    - Kwargs：`thinking=disabled`, `thinking_mode=disabled`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `]<]minimax[>[<tool_call>` |
| 结束 token | `]<]minimax[>[</tool_call>` |
| 参数编码方式 | Namespace prefix ]<]minimax[>[ before XML elements; <invoke name="FUNCTION"> with argument-name elements. Recursive XML expansion for nested mappings and arrays; null-valued mappings omitted. |

_说明：_ New wire format differs from M2 <parameter name=...>; reasoning markers <mm:think>...</mm:think>. Pinned template renders reasoning for all assistant turns.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `native_early` |

**融合方式说明：** Model card states mixed-modality training from the first step. Vision features are projected into the 6144-wide text stream; native training does not imply absence of a vision encoder/projector.

### 视觉编码器

| | |
|---|---|
| 架构 | ViT (clip_vision_model config), 3D RoPE |
| 层数 | 32 |
| 隐藏维度 | 1280 |
| 中间维度 | 5120 |
| 头数 | 16 |
| patch 大小 | 14 |
| 输入通道数 | 3 |
| 输出维度 → LM | 6144 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 2 |

_说明：_ image_size=2016; vision_segment_max_frames=4; patch_merge compression; vision RoPE base 10000, mode 3d (config). Pretrained initialization source not disclosed.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 200025 |
| video_token_id | 200026 |
| vision_start_token_id | [Unknown/Not Disclosed] |
| vision_end_token_id | [Unknown/Not Disclosed] |

## 待解问题（open_questions）

- MSA paper experiments use a 109B MoE and 3T-token budget; these do not disclose production M3 (~428B, ~23B active) training tokens, optimizer, schedule or post-training pipeline.
- MSA typed top_k remains UNKNOWN because the config defines 16 blocks ×128 tokens, while schema field describes KV-entry count. Block count/size recorded explicitly in sparse_attention.notes.
- MTP config has num_mtp_modules=7 and num_nextn_predict_layers=1. Exact objective depth, horizon, loss weight and public weight shipment require further vendor/code evidence.
- MiniMax M3.1 Flash (October 19) is a later API release with weights promised later; it is not the M3 checkpoint or an open-weight update in this snapshot.
- Unknown fields are deliberate; no optimizer, token mixture, full training precision or version deltas are inherited from neighboring checkpoints without source attribution.

---

_由 `data/extracted/minimax-m3.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
