# Qwen3.6-35B-A3B

> English: [qwen3.6-35b-a3b.md](./qwen3.6-35b-a3b.md)

*Schema 版本: 5*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Qwen |
| 发布时间 | 2026-04 |
| 开放程度 | 开放权重 |
| 总参数量 | 35B |
| 激活参数量 | 3B |

## 数据源

- <https://huggingface.co/Qwen/Qwen3.6-35B-A3B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.6-35B-A3B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.6-35b-a3b>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 40 |
| 隐藏维度 | 2048 |
| 上下文窗口 | 262144 |

**上下文说明：** Native productized 262K (config.json max_position_embeddings=262144). Extensible to 1,010,000 via opt-in static YaRN configured at inference time (vLLM/SGLang); the static config.json ships rope_type=default (no scaling) for the 262K native window. Same recipe as Qwen3.5-35B-A3B.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 1010000 |
| 倍率 | 4.0 |
| RoPE 原始最大长度 | 262144 |

_说明：_ Identical to Qwen3.5-35B-A3B — opt-in deployment-time scaling, factor=4.0 with original_max_position_embeddings=262144. mRoPE configuration (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000) preserved across the extension.

### 注意力（hybrid）

| | |
|---|---|
| 变体 | hybrid |
| 头数 | 16 |
| KV 头数 | 2 |
| 头维度 | 256 |

**RoPE：** type=`mrope`, base=`10000000`

RoPE scaling：

```json
{
  "mrope_interleaved": true,
  "mrope_section": [
    11,
    11,
    10
  ],
  "partial_rotary_factor": 0.25
}
```

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=32 with linear_value_head_dim=128 -> 4096-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. mamba_ssm_dtype=float32. Used in 3 out of every 4 layers (30 of 40). Identical shape to Qwen3.5-35B-A3B - Qwen3.6-35B-A3B inherits the backbone wholesale (config.architectures still reports 'Qwen3_5MoeForConditionalGeneration' and config.model_type is still 'qwen3_5_moe', confirming the same HF model class is reused). |
| `gated_attention` | `gqa` | 16 | 2 | 256 | mrope (multimodal RoPE) with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated, the remaining 192 are NoPE. mrope_section=[11,11,10] partitions the rotary dims across temporal/height/width axes; mrope_interleaved=true. | Softmax attention with output gating (config: attn_output_gate=true). GQA 16Q:2KV (group size 8). attention_bias=false. Used in 1 out of every 4 layers (10 of 40, 'full_attention' in config.layer_types). Identical shape to Qwen3.5-35B-A3B. |

**层模式：** (D,D,D,F)x10 with D=gated_deltanet, F=gated_attention. config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 10 times (40 layers total). config.full_attention_interval=4 confirms the 1-in-4 cadence.

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 512 |

**路由：** Top-8 routing over 256 routed experts plus 1 always-on shared expert per token (README: '8 Routed + 1 Shared'). Auxiliary load-balance loss with coefficient router_aux_loss_coef=0.001. Per-expert FFN intermediate dim is 512 for both routed (moe_intermediate_size) and shared (shared_expert_intermediate_size) experts.

**层划分：** Uniform MoE FFN across all 40 layers regardless of attention variant (config.mlp_only_layers=[]).

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in each expert FFN). |
| 归一化 | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding 说明：** tie_word_embeddings=false (separate input embedding and output head). Token Embedding 248320 (padded) and LM Output 248320 (padded) per README; config.vocab_size=248320 confirms. Vision-related reserved IDs in the LM vocabulary: image_token_id=248056, video_token_id=248057, vision_start_token_id=248053, vision_end_token_id=248054. eos_token_id=248044. config.text_config explicitly exposes bos_token_id=248044 and pad_token_id=null (Qwen3.5-35B-A3B's config did not expose bos_token_id at the text_config layer; this is metadata-level only with no architectural impact).

### 并行 / 基础设施

[Unknown/Not Disclosed]

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** Qwen3.6 is a post-training-focused refresh of Qwen3.5 — the README opens with 'Following the February release of the Qwen3.5 series, we're pleased to share the first open-weight variant of Qwen3.6. Built on direct feedback from the community, Qwen3.6 prioritizes stability and real-world utility, offering developers a more intuitive, responsive, and genuinely productive coding experience.' The Qwen3.5 family-level pre-training highlights (early-fusion multimodal training, 201-language coverage, asynchronous RL infra) are not restated in the Qwen3.6 README. Two Qwen3.6 highlights: (1) **Agentic Coding** - frontend workflows and repository-level reasoning with greater fluency; (2) **Thinking Preservation** - retain reasoning context from historical messages across multi-turn dialogs. No quantitative breakdown is disclosed for either pre-training or post-training data.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | [Unknown/Not Disclosed] |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ MTP head with mtp_num_hidden_layers=1 (config) and mtp_use_dedicated_embeddings=false (shares input embeddings with the main model). README states 'MTP: trained with multi-steps' - exact step depth D is not disclosed.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking` | Default mode. Qwen3.6 thinks by default and wraps reasoning in <think>...</think> before producing the final response. README repeats the Qwen3.5 statement that the Qwen3-style /think and /no_think soft switches are NOT officially supported. | Long Chain-of-Thought reasoning before the final answer. Recommended sampling per README Best Practices (same as Qwen3.5): temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0 (general); temperature=0.6 for precise coding tasks (e.g. WebDev). |
| `non-thinking` | Set chat_template_kwargs={"enable_thinking": False} via the OpenAI-compatible API extra_body (vLLM/SGLang/Qwen-Agent), or pass enable_thinking=False directly on Alibaba Cloud Model Studio. Soft switches /think and /no_think are documented as NOT officially supported. | Direct, low-latency response without an explicit reasoning trace. Same recommended sampling as Qwen3.5-35B-A3B. |
| `preserve-thinking` | Set chat_template_kwargs={"preserve_thinking": True} via the API (Alibaba Cloud Model Studio shortens to top-level preserve_thinking=True). Composable with enable_thinking — the user can run thinking + preserve_thinking, or non-thinking + preserve_thinking. | **New in Qwen3.6.** README: 'By default, only the thinking blocks generated in handling the latest user message is retained, resulting in a pattern commonly as interleaved thinking. Qwen3.6 has been additionally trained to preserve and leverage thinking traces from historical messages.' Vendor argues it benefits multi-turn agent scenarios by improving decision consistency, can reduce total tokens by avoiding re-derivation, and improves KV-cache utilization. Default is False (interleaved-thinking pattern, matching Qwen3.5 behavior). The Qwen3.6 chat template references `preserve_thinking` 2x and still references `/think` 5x (same as Qwen3.5 templates) — soft-switch deprecation remains a docs/policy posture rather than a template-level removal. |

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `native_early` |

**融合方式说明：** Same native-early fusion as Qwen3.5-35B-A3B. Vision tokens are inlined into the same backbone as text via four reserved vocabulary IDs (vision_start, image, video, vision_end). vision_config.out_hidden_size=2048 matches LM hidden_size. README pipeline_tag=image-text-to-text. The vision encoder geometry and projector dim are identical to Qwen3.5-35B-A3B; vision_config.model_type still reports 'qwen3_5_moe' across both releases.

### 视觉编码器

| | |
|---|---|
| 架构 | ViT (HF model_type=qwen3_5_moe vision config). config.deepstack_visual_indexes=[] - no DeepStack injection layers. Identical encoder geometry to Qwen3.5-35B-A3B. |
| 层数 | 27 |
| 隐藏维度 | 1152 |
| 中间维度 | 4304 |
| 头数 | 16 |
| patch 大小 | 16 |
| 输入通道数 | 3 |
| 输出维度 → LM | 2048 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 2 |

_说明：_ hidden_act=gelu_pytorch_tanh; num_position_embeddings=2304. The Qwen3.6-35B-A3B config drops the top-level language_model_only flag that the Qwen3.6-27B config exposed; semantically equivalent (multimodal by default for both).

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 248056 |
| video_token_id | 248057 |
| vision_start_token_id | 248053 |
| vision_end_token_id | 248054 |

## 待解问题（open_questions）

- Pre-training optimizer, learning-rate schedule, batch size, LR, weight decay, gradient clipping are not disclosed for Qwen3.6-35B-A3B. Whether 3.6 reuses the 3.5 base checkpoint (continued post-training only), continues pre-training from it, or repeats pre-training from scratch on similar data is not stated.
- Total pre-training tokens and data mix are not disclosed numerically.
- Multi-Token Prediction step depth D is not stated quantitatively. Same gap as 3.5 - mtp_num_hidden_layers=1 (head depth) is exposed but training-time multi-step D is undisclosed.
- Post-training pipeline structure is undisclosed for Qwen3.6: no explicit stage count, no SFT data scale, no RL algorithm name. The two highlighted capabilities — Agentic Coding (frontend + repo-level reasoning) and Thinking Preservation (preserve_thinking API kwarg) — have no documented training recipe (execution-feedback RL? unit-test-grounded rewards? continued SFT? data scale?).
- Mixed-precision training recipe is not disclosed (config.text_config.dtype=bfloat16 reflects the released checkpoint dtype only).
- Parallelism strategy and training infrastructure are not disclosed. MoE-specific details (expert parallelism, all-to-all dispatch implementation, capacity factor, drop-token policy) remain undisclosed.
- Soft switches `/think` and `/no_think` are described as 'not officially supported' in the README, but the chat template (Jinja2) still references `/think` 5 times — same count as Qwen3.5 templates. Behavior on the soft tokens (silent ignore? graceful degrade? still routes to thinking/non-thinking?) is not characterized.
- preserve_thinking mechanism details: is the entire history of <think> blocks retained, only the most-recent N, or some tagged-by-user subset? The README/template do not explicitly bound the retention; the chat template references preserve_thinking 2x but the exact retention rule is not described in plain English.
- Why no revisit of MoE load-balancing in the 3.6 refresh? Qwen3.6 inherits the classic aux-loss recipe (router_aux_loss_coef=0.001) introduced by 3.5, despite Qwen3 having shipped global-batch LB and DeepSeek-V3 aux-loss-free routing. No vendor explanation.
- Cross-version compare: Qwen3.6-35B-A3B is architecturally identical to Qwen3.5-35B-A3B (same layers, hidden, attention shape, MoE topology, vocab, vision encoder, MTP topology, context window, RoPE config, even the same architectures='Qwen3_5MoeForConditionalGeneration' HF class name). The release is a post-training-only refresh as far as disclosed signals indicate. Confirm against any future tech report.
- Cached blog.html at qwen.ai/blog?id=qwen3.6-35b-a3b is a client-side-rendered SPA shell (only 'Qwen' is present in the static HTML), so substantive blog content was unavailable at extraction time.

---

_由 `data/extracted/qwen3.6-35b-a3b.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
