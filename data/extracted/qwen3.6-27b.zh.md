# Qwen3.6-27B

> English: [qwen3.6-27b.md](./qwen3.6-27b.md)

*Schema 版本: 7*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Qwen |
| 发布时间 | 2026-04 |
| 开放程度 | 开放权重 |
| 总参数量 | 27B |
| 激活参数量 | 27B |

**变体策略（variant policy）：** Same unified-weights philosophy as Qwen3.5: one checkpoint per (size, dense/MoE), modes via chat-template kwargs. Qwen3.6 adds a third runtime mode `preserve_thinking` (multi-turn reasoning carryover) via a chat-template kwarg — composable with `enable_thinking`. As of release the open-weight surface is narrower than 3.5 — only 27B dense + 35B-A3B MoE shipped open-weight (README: 'first open-weight variant of Qwen3.6'). Same NO-separate-Math/Coder/VL-siblings policy; Coder capability is post-training emphasis ('Agentic Coding' highlight) plus the `qwen3_coder` serving parser, not a sibling checkpoint.

## 数据源

- <https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.6-27b>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 64 |
| 隐藏维度 | 5120 |
| 上下文窗口 | 262144 |

**上下文说明：** Native productized 262K (config.json max_position_embeddings=262144). Extensible to 1,010,000 via opt-in static YaRN configured at inference time (vLLM/SGLang); the static config.json ships rope_type=default (no scaling) for the 262K native window. Same recipe as Qwen3.5-27B.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 1010000 |
| 倍率 | 4.0 |
| RoPE 原始最大长度 | 262144 |

_说明：_ Identical to Qwen3.5-27B — opt-in deployment-time scaling, factor=4.0 with original_max_position_embeddings=262144, mRoPE configuration (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000) preserved across the extension. Static implementation; for typical use under 524K, factor=2.0 is recommended.

### 注意力（hybrid）

| | |
|---|---|
| 变体 | hybrid |
| 头数 | 24 |
| KV 头数 | 4 |
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
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=48 with linear_value_head_dim=128 -> 6144-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. output_gate_type=swish. mamba_ssm_dtype=float32. Used in 3 out of every 4 layers (48 of 64). Identical shape to Qwen3.5-27B — Qwen3.6-27B inherits the backbone wholesale. |
| `gated_attention` | `gqa` | 24 | 4 | 256 | mrope (multimodal RoPE) with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated, the remaining 192 are NoPE. mrope_section=[11,11,10] partitions the rotary dims across temporal/height/width axes; mrope_interleaved=true. | Softmax attention with output gating (config: attn_output_gate=true). GQA 24Q:4KV. attention_bias=false. Used in 1 out of every 4 layers ('full_attention' in config.layer_types). Effective Q dim 24*256=6144; KV dim 4*256=1024. Identical shape to Qwen3.5-27B. |

**层模式：** (D,D,D,F)x16 with D=gated_deltanet, F=gated_attention. config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 16 times. config.full_attention_interval=4 confirms the 1-in-4 cadence. README naming: '16 x (3 x (Gated DeltaNet -> FFN) -> 1 x (Gated Attention -> FFN))'.

### FFN（dense）

**Dense 中间维度：** `17408`

**层划分：** Uniform dense SwiGLU FFN across all 64 layers regardless of attention variant. (Qwen3.5-27B's config carried `mlp_only_layers=[]`; the Qwen3.6 config drops the key entirely — there is no dense/MoE split to describe for a dense model either way.)

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in the FFN). |
| 归一化 | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding 说明：** tie_word_embeddings=false (separate input embedding and output head). Token Embedding 248320 (padded) and LM Output 248320 (padded) per README; config.vocab_size=248320 confirms. Vision-related reserved IDs in the LM vocabulary: image_token_id=248056, video_token_id=248057, vision_start_token_id=248053, vision_end_token_id=248054. eos_token_id=248044. config.text_config also exposes bos_token_id=248044 (vs Qwen3.5-27B which omits it from text_config) — minor metadata-level diff with no architectural impact.

### 并行 / 基础设施

[Unknown/Not Disclosed]

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** Qwen3.6 is a post-training-focused refresh of Qwen3.5 — the README states 'Following the February release of the Qwen3.5 series, we're pleased to share the first open-weight variant of Qwen3.6. Built on direct feedback from the community, Qwen3.6 prioritizes stability and real-world utility, offering developers a more intuitive, responsive, and genuinely productive coding experience.' The Qwen3.5 family-level highlights (early-fusion multimodal training, 201-language coverage, asynchronous RL infra, near-100% multimodal training efficiency) are not restated for Qwen3.6 in the README, suggesting the pre-training recipe is shared with Qwen3.5 (or unchanged at the granularity disclosed). Qwen3.6 highlights two post-training upgrades: (1) **Agentic Coding** — frontend workflows and repository-level reasoning; (2) **Thinking Preservation** — retain reasoning context from historical messages across multi-turn dialogs. No quantitative breakdown is disclosed for either pre-training or post-training data.

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
| `non-thinking` | Set chat_template_kwargs={"enable_thinking": False} via the OpenAI-compatible API extra_body (vLLM/SGLang/Qwen-Agent), or pass enable_thinking=False directly on Alibaba Cloud Model Studio. Soft switches /think and /no_think are documented as NOT officially supported. | Direct, low-latency response without an explicit reasoning trace. Same recommended sampling as Qwen3.5-27B. |
| `preserve-thinking` | Set chat_template_kwargs={"preserve_thinking": True} via the API (Alibaba Cloud Model Studio shortens to top-level preserve_thinking=True). Composable with enable_thinking — the user can run thinking + preserve_thinking, or non-thinking + preserve_thinking. | **New in Qwen3.6.** README: 'By default, only the thinking blocks generated in handling the latest user message is retained, resulting in a pattern commonly as interleaved thinking. Qwen3.6 has been additionally trained to preserve and leverage thinking traces from historical messages.' Vendor argues it benefits multi-turn agent scenarios by improving decision consistency, can reduce total tokens by avoiding re-derivation, and improves KV-cache utilization. Default is False (interleaved-thinking pattern, matching Qwen3.5 behavior). |

- **`thinking`**
    - Kwargs：`enable_thinking=true`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`
- **`non-thinking`**
    - Kwargs：`enable_thinking=false`
    - 推荐采样参数：`temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`
- **`preserve-thinking`**
    - Kwargs：`preserve_thinking=true`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<tool_call>` |
| 结束 token | `</tool_call>` |
| 参数编码方式 | Per-arg <parameter=name>VALUE</parameter> blocks nested inside a <function=NAME></function> wrapper. Qwen3.6 fixes a Qwen3.5 JSON-encoding bug — the chat template now applies `tojson` to anything that is not already a string (non-string scalars like booleans and numbers serialize as JSON 'true'/'false'/'5' rather than Python 'True'/'False'/'5'). Strings pass through unchanged. |

**服务端解析器参数：**

- `vllm`: `--tool-call-parser qwen3_coder`
- `sglang`: `--tool-call-parser qwen3_coder`

_说明：_ Same Qwen3-Coder XML-like wire format as Qwen3.5; only difference is the tool-arg scalar encoding fix above. README serving snippets pair `--tool-call-parser qwen3_coder` with `--reasoning-parser qwen3`. Compatible with `preserve_thinking` kwarg — README highlights agent scenarios as the primary motivation for the new preserve_thinking mode (full reasoning context across multi-turn tool-calling improves decision consistency and KV-cache utilization).

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `native_early` |

**融合方式说明：** Same native-early fusion as Qwen3.5-27B. Vision tokens are inlined into the same backbone as text via four reserved vocabulary IDs (vision_start, image, video, vision_end). vision_config.out_hidden_size=5120 matches LM hidden_size. README pipeline_tag=image-text-to-text. Qwen3.6 README does not restate the family-level early-fusion claim from Qwen3.5; the underlying mechanism appears unchanged.

### 视觉编码器

| | |
|---|---|
| 架构 | ViT (HF model_type=qwen3_5 vision config — Qwen3.6-27B's vision_config still reports model_type='qwen3_5', confirming the vision encoder is shared with Qwen3.5). config.deepstack_visual_indexes=[] - no DeepStack injection layers configured. |
| 层数 | 27 |
| 隐藏维度 | 1152 |
| 中间维度 | 4304 |
| 头数 | 16 |
| patch 大小 | 16 |
| 输入通道数 | 3 |
| 输出维度 → LM | 5120 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 2 |

_说明：_ hidden_act=gelu_pytorch_tanh; num_position_embeddings=2304. Identical geometry to Qwen3.5-27B vision encoder. config exposes top-level language_model_only=false flag (new in 3.6 config schema; no architectural impact).

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 248056 |
| video_token_id | 248057 |
| vision_start_token_id | 248053 |
| vision_end_token_id | 248054 |

## 待解问题（open_questions）

- Pre-training optimizer, learning-rate schedule, batch size, LR, weight decay, gradient clipping are not disclosed for Qwen3.6-27B. README implies the pre-training recipe is shared with (or close to) Qwen3.5 since it omits the family-level pre-training highlights and frames the release as a community-feedback refresh — but this is not stated explicitly.
- Total pre-training tokens and data mix are not disclosed numerically. Whether Qwen3.6 is a continued-pretraining refresh of Qwen3.5 weights, a fresh pretrain on similar data, or post-training-only over the same Qwen3.5 base is not stated.
- Multi-Token Prediction step depth D is not stated quantitatively (same gap as Qwen3.5; README says 'trained with multi-steps' and config exposes mtp_num_hidden_layers=1 only).
- Post-training pipeline structure for Qwen3.6 is undisclosed. Two new capabilities are highlighted — Agentic Coding (frontend + repo-level reasoning) and Thinking Preservation (preserve_thinking API kwarg) — but the underlying training algorithm, RL signals (execution feedback? unit-test rewards?), and SFT data mix for these are not detailed in README/blog.
- Mixed-precision training recipe is not disclosed (config.text_config.dtype=bfloat16 reflects the released checkpoint dtype only).
- Parallelism strategy and training infrastructure are not disclosed.
- Soft switches `/think` and `/no_think` are described as 'not officially supported' in the README, but the chat template (Jinja2) still references `/think` 5 times (per pre-extraction sourcing notes). The exact behavior — whether the template silently ignores soft-switch tokens, gracefully degrades, or still routes them to thinking/non-thinking modes — is not characterized. Verify against the rendered template if behavior matters for downstream tooling.
- Token embedding 248320 'Padded' is identical between Qwen3.5-27B and Qwen3.6-27B; the unpadded vocabulary size and the padding rationale (TP alignment? room for added vision/control tokens?) are not stated. The padding label is a vendor-disclosure artifact, not a behavioral difference.
- preserve_thinking is described as 'additionally trained' but the additional training recipe (continued SFT? small RL pass? data scale?) is not specified. For agent scenarios it is the most differentiated post-training feature in this release.
- Cross-version compare: Qwen3.6-27B is architecturally identical to Qwen3.5-27B (same layers, hidden, attention shape, FFN, vocab, vision encoder, MTP topology, context window, RoPE config). The release is a post-training-only refresh as far as disclosed signals indicate. If a Qwen3.6 tech report appears later disambiguating pre-training continuation vs fresh pretrain, re-read and update.
- Cached blog.html at qwen.ai/blog?id=qwen3.6-27b is a client-side-rendered SPA shell (only 'Qwen' is present in the static HTML), so substantive blog content was unavailable at extraction time.

---

_由 `data/extracted/qwen3.6-27b.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
