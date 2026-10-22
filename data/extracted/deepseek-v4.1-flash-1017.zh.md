# DeepSeek-V4.1-Flash-1017

> English: [deepseek-v4.1-flash-1017.md](./deepseek-v4.1-flash-1017.md)

*Schema 版本: 8*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | DeepSeek |
| 发布时间 | 2026-10 |
| 开放程度 | 开放权重 |
| 总参数量 | 552B backbone + 196B Engram (linked V4.1 family report; the 1017 config is identical to the September checkpoint) |
| 激活参数量 | 8B prefill / 16B decode (linked V4.1 family architecture report; unchanged 1017 config) |

**变体策略（variant policy）：** October 17 minor update to DeepSeek-V4.1-Flash, with one image+text checkpoint, chat/thinking modes and continuous numeric reasoning effort. Current config is structurally identical to the September pinned config. The new release specifically discloses self-feedback RL and improved reasoning, coding, agentic and visual results with shorter output and task time; it does not publish a separate 1017 technical report or training budget. The model card links the earlier V4.1 report for architecture background.

## 数据源

- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/tokenizer_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/encoding/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/encoding/encoding.py>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/model.py>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/vision.py>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017/raw/1bae0e1088993b9b82de08f59de5be5a34e42170/inference/engram.py>
- <https://huggingface.co/api/models/deepseek-ai/DeepSeek-V4.1-Flash-1017/revision/1bae0e1088993b9b82de08f59de5be5a34e42170>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/DeepSeek_V41_Tech_Report.pdf>
- <https://api-docs.deepseek.com/news/news261017/>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/raw/dba1be0a40aa45a94ad051997016db3960a90277/config.json>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 40 |
| 隐藏维度 | 5120 |
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
| 头数 | 64 |
| KV 头数 | 1 |
| 头维度 | 512 |

**RoPE：** type=`yarn`, base=`10000`

RoPE scaling：

```json
{
  "rope_type": "yarn",
  "factor": 16,
  "beta_fast": 32,
  "beta_slow": 1,
  "original_max_position_embeddings": 65536,
  "compress_rope_theta": 160000
}
```

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `sliding_window_attention` | `sliding_window` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | 128-token layer-local window in every layer; layers 0-1 are SWA only. |
| `csa2_full` | `other` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | Computes shared global KV and indexer keys; layers 2,8,14,20. |
| `csa2_reindex` | `other` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | Reuses global KV/indexer keys but computes fresh top-512; layers 24,28,32,36. |
| `csa2_reuse` | `other` | 64 | 1 | 512 | 64 rotary dimensions; compressed branch theta=160000. | Reuses preceding global KV and top-k; remaining 30 global-attention layers. |

**层模式：** 40 backbone layers: 0-1 SWA only; 2-19 encoder CSA2 with ratio 2 and [Full, Reuse×5] repeated three times; 20-39 decoder ratio 1 with Full at 20, Reindex at 24/28/32/36 and Reuse otherwise. All layers retain local SWA. Current config matches the linked family report topology.

**注意力补充说明：** Current config: query low-rank projection 1280; grouped output projection 8 groups × rank 1024; partial RoPE width 64 of 512.

**稀疏注意力：**

| | |
|---|---|
| 类型 | `csa2` |
| 保留条目数（top-k） | 512 |
| Indexer 头数 | 32 |
| Indexer 头维度 | 128 |
| KV 压缩比 | 2 (encoder) / 1 (decoder) |

**选择规则：** Full/Reindex layers score indexer keys projected from shared main KV; Reuse layers inherit top-512 indices. Layer 20 builds a candidate pool of top 2048 blocks × 8 positions (at most 16384 positions); decoder Reindex layers select within that pool (config + reference Indexer).

_说明：_ Shapes and sharing topology from current config and reference code; the family report is earlier architecture background.

**跨层共享：**

| 类型 | 共享内容 | 来源层 | 复用层 |
|---|---|---|---|
| `ced` | `kv_from_encoder_output` | [19] | [20] |
| `csa2` | `kv`, `indexer_keys` | [2, 8, 14, 20] | All other global-attention layers read the most recent Full layer state. |
| `csa2` | `topk_indices` | [2, 8, 14, 20, 24, 28, 32, 36] | The other 30 global-attention layers reuse the most recent index-source top-k. |

- **`ced`** (kv_from_encoder_output)
    - _说明：_ Linked family report: decoder global KV is projected from final encoder output; under CSA2, Full layer 20 materializes it for decoder reuse. The minimal current reference runs the full stack and does not implement the optimized encoder-only prefill schedule.
- **`csa2`** (kv, indexer_keys)
    - _说明：_ Current config kv_source_layer_ids and reference SharedAttentionRuntime.
- **`csa2`** (topk_indices)
    - _说明：_ Current config index_source_layer_ids; candidate_source_layer_id=20 is an additional shared search-domain restriction.

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 384 |
| 每 token 激活专家数 | 6 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2304 |

**路由：** Current config: top-6 routed experts + 1 shared expert; SqrtSoftplus affinity (scoring_func=sqrtsoftplus); topk_method=noaux_tc; norm_topk_prob=true; routed_scaling_factor=1.5. Reference Gate uses correction biases for selection and unbiased scores for output weights. Current Gate has separate text/image selection biases (bias and bias_vl).

**层划分：** All backbone blocks instantiate MoE FFNs in inference/model.py.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (hidden_act=silu), swiglu_limit=10.0 in current config and reference Expert. |
| 归一化 | RMSNorm, rms_norm_eps=1e-20; separate hc_eps=1e-06 for Hyper-Connections. |

**Embedding 说明：** vocab_size=129280; tie_word_embeddings=false. Image positions are replaced by visual embeddings in the reference Transformer.

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

**结构：** 3 draft blocks (reference inference/config.json n_mtp_layers=3), window-only attention; block_size=5; Markov rank 256; target layers [37, 38, 39].

_说明：_ The reference Transformer constructs DSparkBlock modules when dspark_block_size is nonzero; this does not establish an MTP training objective.

### 记忆模块

**Engram conditional memory**

| | |
|---|---|
| 类型 | `engram` |
| 参数量 | 196B (linked V4.1 family report; current table dimensions imply 196.614B embedding elements before projections) |
| 注入层 | [1, 14] |

**寻址方式：** Current config and inference/engram.py: n-gram orders 2,3,4 with 8 hash heads per order over tokenizer-compressed IDs; text only, image tokens masked.

**表配置：** engram_num_embeddings=[384006168,384016682]; head_dim=256; compressed vocab=99092; base vocab per hash=16000000. Current Engram projects retrieved vectors to per-HC-copy keys plus shared values and gates the update.

**存储位置：** Current inference ParallelEngramEmbedding uses FP8 embedding weights. Production offload policy for the 1017 release is not separately specified.

_说明：_ Forward-pass memory, separate from the DSpark draft. This entry does not import September optimizer or learning-rate claims.

### 并行 / 基础设施

Only inference topology is documented here; current-checkpoint training parallelism is undisclosed. Reference inference supports tensor-parallel torchrun and checkpoint conversion.

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** The current release does not disclose training-token counts or mixture fractions. Earlier family reports are not evidence for the dated update training budget.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** Reinforcement learning with self-feedback (official 2026-10-17 release note). The update does not name an RL algorithm or specify reward, feedback-label generation, or training budget.

**RLAIF：** `[Unknown/Not Disclosed]`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Self-feedback reinforcement learning | `rl` | Official release note attributes stronger end-to-end project development (game creation and 3D modeling) to self-feedback RL. Ordering relative to other training stages and implementation details are undisclosed. |

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking-low` | thinking_mode=thinking, reasoning_effort=low | Reasoning effort selected by the current prompt encoder. |
| `thinking-high` | thinking_mode=thinking, reasoning_effort=high | Reasoning effort selected by the current prompt encoder. |
| `thinking-max` | thinking_mode=thinking, reasoning_effort=max | Reasoning effort selected by the current prompt encoder. |
| `chat` | thinking_mode=chat | Places </think> after the assistant prefix to skip reasoning. |

- **`thinking-low`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=low`
    - 推荐采样参数：`temperature=1.0`, `top_p=1.0`
- **`thinking-high`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=high`
    - 推荐采样参数：`temperature=1.0`, `top_p=1.0`
- **`thinking-max`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=max`
    - 推荐采样参数：`temperature=1.0`, `top_p=1.0`
- **`chat`**
    - Kwargs：`thinking_mode=chat`

**推理强度（reasoning effort）：**

| | |
|---|---|
| API 参数 | `reasoning_effort` |
| 注入方式 | `prompt_prefix` |
| 刻度 | `continuous` |
| 取值范围 | 1-100 |

| 档位 | 数值 | 默认 | 注入内容 | 说明 |
|---|---|---|---|---|
| `low` | 50 |  | <｜System｜>Reasoning Effort: 50 (range 1-100, the higher the value, the more thorough the reasoning)

 | — |
| `high` | 75 | ✓ | <｜System｜>Reasoning Effort: 75 (range 1-100, the higher the value, the more thorough the reasoning)

 | — |
| `max` | 100 |  | <｜System｜>Reasoning Effort: 100 (range 1-100, the higher the value, the more thorough the reasoning)

 | — |

**生效条件：** thinking_mode=thinking; prefix inserted at conversation index 0 before the system text.

**非法取值的处理：** Reference render_reasoning_effort asserts: only exact Python ints within 1-100 or low/high/max aliases are accepted; None selects high. Validation runs even when the prefix is not rendered.

_说明：_ Current encoding.py and encoding/README.md. The September report describes effort-conditioned RL, but the 1017 update does not restate its training method.

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<｜DSML｜ calls>` |
| 结束 token | `</｜DSML｜ calls>` |
| 参数编码方式 | <｜DSML｜ invoke name="..."> with per-argument <｜DSML｜ parameter name="..." string="true\|false">; raw strings or JSON for non-strings. |

_说明：_ Current encoding supports namespace::function; leading spaces in V4.1 DSML tags differ from V4. No published production parser flag in the current model card.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

### 量化（发布权重）

| | |
|---|---|
| 权重格式 | `fp4+fp8 mixed` |
| 激活格式 | `fp8 dynamic (config.quantization_config.activation_scheme=dynamic)` |
| 方法 | `[Unknown/Not Disclosed]` |
| 粒度 | FP8 weight blocks [32, 32]; scale_fmt=ue8m0. |

**作用范围：** FP4 routed-expert weights; FP8 quantization configuration for other quantized weights. This is a deployment format, not proof of the current training precision.

_说明：_ Current config uses quant_method=fp8 together with expert_dtype=fp4. The dated checkpoint does not disclose a new quantization training recipe.

**稳定性 trick：** Current config/reference Expert clamps SwiGLU activations at 10. The update does not disclose loss-spike handling or a full training-stability recipe.

## 多模态

| | |
|---|---|
| 模态 | text, image |
| 融合方式 | `native_early` |

**融合方式说明：** Linked V4.1 family report describes multimodal training from the start; current 1017 code retains the same architecture. Current inference/vision.py: 3×3 spatial merging followed by two linear aligner layers with GELU; projected image features replace image positions in the shared LM stream.

### 视觉编码器

| | |
|---|---|
| 架构 | DeepSeek ViT with full bidirectional attention, 2D RoPE, linear RGB patch embedding, RMSNorm and SwiGLU (current inference/vision.py) |
| 层数 | 32 |
| 隐藏维度 | 1024 |
| 中间维度 | 2816 |
| 头数 | 16 |
| patch 大小 | 14 |
| 输入通道数 | 3 |
| 输出维度 → LM | 5120 |
| 空间合并大小 | 3 |
| 时序 patch 大小 | [Unknown/Not Disclosed] |

_说明：_ max image tokens=1024; min pixels=295936; max width/height ratio=None. No video/audio path disclosed.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 129264 |
| video_token_id | [Unknown/Not Disclosed] |
| vision_start_token_id | [Unknown/Not Disclosed] |
| vision_end_token_id | [Unknown/Not Disclosed] |

## 待解问题（open_questions）

- 1017 optimizer, LR schedule, update-token budget, data mixture, SFT/distillation and exact RL algorithm are undisclosed; do not carry over September Muon/45T/GRPO/OPD claims.
- Self-feedback RL does not disclose whether AI generates preference labels; rlaif remains UNKNOWN.
- Parameter figures are architecture-level figures from the linked September report; no separate 1017 accounting is published. HF safetensors element totals include packed/quantized and auxiliary tensors and are not substituted for paper parameter counts.
- The minimal reference executes all 40 backbone blocks for prefill; encoder-only prefill, SWA bounded replay and production cache performance are described by the linked family report, not benchmarked for 1017.

---

_由 `data/extracted/deepseek-v4.1-flash-1017.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
