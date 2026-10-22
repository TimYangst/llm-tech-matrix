# DeepSeek-V4-Pro-0813

> English: [deepseek-v4-pro-0813.md](./deepseek-v4-pro-0813.md)

*Schema 版本: 8*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | DeepSeek |
| 发布时间 | 2026-08 |
| 开放程度 | 开放权重 |
| 总参数量 | 1.6T backbone (linked V4 family report; current card explicitly retains Preview architecture) |
| 激活参数量 | 49B backbone per token (linked V4 family report; excludes DSpark draft) |

**变体策略（variant policy）：** August 13 official/GA Pro release supersedes the Preview, retaining its architecture and adding an attached DSpark draft. Same weights expose thinking/chat and low/high/max reasoning-effort modes. The current card reports stronger agentic performance; it does not disclose the new post-training recipe.

## 数据源

- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/tokenizer_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/encoding/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/inference/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/inference/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/inference/model.py>
- <https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4-Pro-0813/revision/72e1d3230f6c080a530b0a1d46f8eb4602340597>
- <https://api-docs.deepseek.com/updates/>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/resolve/ad664d5e83023a67c735992e8fe612aeab3c52d2/DeepSeek_V4.pdf>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813/raw/72e1d3230f6c080a530b0a1d46f8eb4602340597/encoding/encoding_dsv4.py>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 61 |
| 隐藏维度 | 7168 |
| 上下文窗口 | 1048576 |

**上下文说明：** config.json max_position_embeddings=1048576 (1M tokens). Training curriculum for this dated checkpoint is not disclosed.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | [Unknown/Not Disclosed] |
| 扩展最大长度 | 1048576 |
| 倍率 | 16.0 |
| RoPE 原始最大长度 | 65536 |

_说明：_ Config-declared YaRN; this does not establish a current-checkpoint pre-training curriculum.

### 注意力（hybrid）

| | |
|---|---|
| 变体 | hybrid |
| 头数 | 128 |
| KV 头数 | 1 |
| 头维度 | 512 |

**RoPE：** type=`yarn`, base=`10000`

RoPE scaling：

```json
{
  "beta_fast": 32,
  "beta_slow": 1,
  "factor": 16,
  "original_max_position_embeddings": 65536,
  "type": "yarn",
  "compress_rope_theta": 160000
}
```

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `sliding_window_attention` | `sliding_window` | 128 | 1 | 512 | Partial RoPE width 64. | 128-token local window alongside global compressed attention; ratio 0 layers are SWA only. |
| `compressed_sparse_attention` | `other` | 128 | 1 | 512 | Compressed branch theta=160000. | CSA ratio 4; indexer selects top-1024 compressed entries. |
| `heavily_compressed_attention` | `other` | 128 | 1 | 512 | Compressed branch theta=160000. | HCA ratio 128; attends all causally available heavily compressed entries (reference Attention). |

**层模式：** Zero-indexed backbone compress_ratios=[128, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4, 128, 4]. 0=SWA only, 4=CSA+SWA, 128=HCA+SWA. Trailing three ratio-0 entries belong to the draft stack in reference inference/config.json.

**注意力补充说明：** Current config: query low-rank projection 1536; grouped output projection 16 groups × rank 1024; partial RoPE width 64 of 512.

**稀疏注意力：**

| | |
|---|---|
| 类型 | `csa+hca` |
| 保留条目数（top-k） | 1024 |
| Indexer 头数 | 64 |
| Indexer 头维度 | 128 |
| KV 压缩比 | 4 (CSA) / 128 (HCA) |

**选择规则：** CSA: lightning-indexer top-1024 over ratio-4 compressed positions. HCA: all causally available ratio-128 entries (reference Attention).

_说明：_ Shapes and sharing topology from current config and reference code; the family report is earlier architecture background.

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 384 |
| 每 token 激活专家数 | 6 |
| 共享专家数 | 1 |
| 单专家中间维度 | 3072 |

**路由：** Current config: top-6 routed experts + 1 shared expert; SqrtSoftplus affinity (scoring_func=sqrtsoftplus); topk_method=noaux_tc; norm_topk_prob=true; routed_scaling_factor=2.5. Reference Gate uses correction biases for selection and unbiased scores for output weights.

**层划分：** All backbone blocks instantiate MoE FFNs in inference/model.py. First three layers use hash routing for text token IDs; remaining layers use score-based routing.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (hidden_act=silu), swiglu_limit=10.0 in current config and reference Expert. |
| 归一化 | RMSNorm, rms_norm_eps=1e-06; separate hc_eps=1e-06 for Hyper-Connections. |

**Embedding 说明：** vocab_size=129280; tie_word_embeddings=false. Text-only checkpoint.

### 残差连接

| | |
|---|---|
| 类型 | `mhc` |
| 扩展因子（n_hc） | 4 |
| 求解迭代数 | 20 |
| 动态参数化 | `True` |

**约束：** Doubly stochastic residual mixing via Sinkhorn normalization in the current reference implementation.

_说明：_ Current config hc_mult=4, hc_sinkhorn_iters=20.

### 辅助模块

**DSpark draft module**

| | |
|---|---|
| 用途 | `speculative_decoding` |
| 是否随权重发布 | `True` |

**结构：** 3 draft blocks (reference inference/config.json n_mtp_layers=3), window-only attention; block_size=5; Markov rank 512; target layers [58, 59, 60].

**启用方式：** vLLM --speculative-config with method=dspark; SGLang --speculative-algorithm DSPARK (same checkpoint; no separate draft path).

_说明：_ The reference Transformer constructs DSparkBlock modules when dspark_block_size is nonzero; this does not establish an MTP training objective.

### 并行 / 基础设施

Only inference topology is documented here; current-checkpoint training parallelism is undisclosed. Reference inference supports tensor-parallel torchrun and checkpoint conversion.

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** No current-update token budget or mixture disclosed. The linked V4 report describes the earlier Preview and is not treated as the 0813 training recipe.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking-low` | thinking_mode=thinking, reasoning_effort=low | Prompt prefix controls reasoning effort on the same weights. |
| `thinking-high` | thinking_mode=thinking, reasoning_effort=high | Prompt prefix controls reasoning effort on the same weights. |
| `thinking-max` | thinking_mode=thinking, reasoning_effort=max | Prompt prefix controls reasoning effort on the same weights. |
| `chat` | thinking_mode=chat | Places </think> after the assistant prefix to skip reasoning. |

- **`thinking-low`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=low`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95 (agentic) / 1.0 (otherwise)`
- **`thinking-high`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=high`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95 (agentic) / 1.0 (otherwise)`, `max_tokens=384K`
- **`thinking-max`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=max`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95 (agentic) / 1.0 (otherwise)`, `max_tokens=384K`
- **`chat`**
    - Kwargs：`thinking_mode=chat`

**推理强度（reasoning effort）：**

| | |
|---|---|
| API 参数 | `reasoning_effort` |
| 注入方式 | `prompt_prefix` |
| 刻度 | `discrete` |

| 档位 | 数值 | 默认 | 注入内容 | 说明 |
|---|---|---|---|---|
| `low` | — | ✓ | none | — |
| `high` | — |  | Reasoning Effort: Absolute maximum with no shortcuts permitted.
You MUST be very thorough in your thinking and comprehensively decompose the problem to resolve the root cause, rigorously stress-testing your logic against all potential paths, edge cases, and adversarial scenarios.
Explicitly write out your entire deliberation process, documenting every intermediate step, considered alternative, and rejected hypothesis to ensure absolutely no assumption is left unchecked.

 | — |
| `max` | — |  | Reasoning Effort: Beyond maximum — exhaustive, relentless, and uncompromising.
You MUST reason with the utmost depth and rigor, leaving absolutely nothing to chance: exhaustively decompose the problem into its most fundamental components, trace every causal chain to its root, and resolve the underlying cause rather than any surface symptom.
Do not stop reasoning until you have independently verified the solution from multiple angles and are certain that no assumption remains unchecked and no error remains undiscovered.

 | — |

**生效条件：** thinking_mode=thinking at conversation index 0; prefix before system text. No effect in chat mode.

**非法取值的处理：** Reference render_message uses the low default for falsy values, then asserts membership in low/high/max. Other unknown nonempty values raise AssertionError; validation occurs in chat mode too.

_说明：_ Verified against this checkpoint's encoding/encoding_dsv4.py; low is the default.

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<｜DSML｜tool_calls>` |
| 结束 token | `</｜DSML｜tool_calls>` |
| 参数编码方式 | <｜DSML｜invoke name="..."> and per-argument <｜DSML｜parameter string="true\|false">; raw strings or JSON for non-strings. |

_说明：_ Current encoding/README.md; retains V4 DSML spelling without V4.1 leading spaces.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

### 量化（发布权重）

| | |
|---|---|
| 权重格式 | `fp4+fp8 mixed` |
| 激活格式 | `fp8 dynamic (config.quantization_config.activation_scheme=dynamic)` |
| 方法 | `[Unknown/Not Disclosed]` |
| 粒度 | FP8 weight blocks [128, 128]; scale_fmt=ue8m0. |

**作用范围：** FP4 routed-expert weights; FP8 quantization configuration for other quantized weights. This is a deployment format, not proof of the current training precision.

_说明：_ Current config uses quant_method=fp8 together with expert_dtype=fp4. The dated checkpoint does not disclose a new quantization training recipe.

**稳定性 trick：** Current config/reference Expert clamps SwiGLU activations at 10. The update does not disclose loss-spike handling or a full training-stability recipe.

## 待解问题（open_questions）

- 0813 optimizer, LR schedule, training-token budget, data mixture and post-training algorithm are undisclosed. The linked V4 report is earlier Preview background, not update evidence.
- HF config num_nextn_predict_layers=1 conflicts with reference inference/config.json n_mtp_layers=3 and three trailing ratio-0 draft entries; current card confirms DSpark attachment but does not reconcile the count. Training MTP objective remains unasserted.
- The earlier DeepSeek-V4-Pro report URL now returns 404. This manifest pins the official shared V4 report in the Flash repository instead; architecture matches current config.

---

_由 `data/extracted/deepseek-v4-pro-0813.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
