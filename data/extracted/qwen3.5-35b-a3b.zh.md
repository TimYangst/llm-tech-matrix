# Qwen3.5-35B-A3B

> English: [qwen3.5-35b-a3b.md](./qwen3.5-35b-a3b.md)

*Schema 版本: 6*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Qwen |
| 发布时间 | 2026-02 |
| 开放程度 | 开放权重 |
| 总参数量 | 35B |
| 激活参数量 | 3B |

**变体策略（variant policy）：** Unified weights per (size, dense/MoE) — Qwen3.5 ships ~7 open-weight sizes (per the Qwen3.6-27B README comparison table the 3.5 family includes 27B dense and 397B-A17B MoE among others). Each checkpoint handles thinking, non-thinking, vision and tool use through chat-template kwargs (`enable_thinking`) and serving-time parsers; there are NO separate Math / Coder / VL / Thinking siblings (a deliberate departure from Qwen2.5's Math/Coder/VL split). 'Coder' capability is exposed via the `--tool-call-parser qwen3_coder` serving flag (vLLM / SGLang) and post-training emphasis, not a separate weight checkpoint. Native VL is unified into the base weights via the `qwen3_5` ViT shared with the LM vocabulary (image / video / vision_start / vision_end token IDs). README pipeline_tag is `image-text-to-text` for both 27B and 35B-A3B.

## 数据源

- <https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.5-35B-A3B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.5>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 40 |
| 隐藏维度 | 2048 |
| 上下文窗口 | 262144 |

**上下文说明：** Native productized 262K (config.json max_position_embeddings=262144). Extensible to 1,010,000 via opt-in static YaRN configured at inference time (vLLM/SGLang); the static config.json ships rope_type=default (no scaling) for the 262K native window.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 1010000 |
| 倍率 | 4.0 |
| RoPE 原始最大长度 | 262144 |

_说明：_ Opt-in deployment-time scaling, identical recipe to Qwen3.5-27B. README 'Processing Ultra-Long Texts' specifies factor=4.0 with original_max_position_embeddings=262144 to lift effective context from 262K to ~1010K. Static implementation (factor constant regardless of input length) so should be enabled only when long context is actually needed; for typical use under 524K, factor=2.0 is recommended. mRoPE configuration (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000) is preserved across the extension.

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
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=32 with linear_value_head_dim=128 -> 4096-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. mamba_ssm_dtype=float32. Used in 3 out of every 4 layers (30 of 40). |
| `gated_attention` | `gqa` | 16 | 2 | 256 | mrope (multimodal RoPE) with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated, the remaining 192 are NoPE. mrope_section=[11,11,10] partitions the rotary dims across temporal/height/width axes; mrope_interleaved=true. | Softmax attention with output gating (config: attn_output_gate=true). GQA 16Q:2KV (group size 8) — twice as aggressive as Qwen3.5-27B's 24Q:4KV (group size 6). attention_bias=false. Used in 1 out of every 4 layers (10 of 40, 'full_attention' in config.layer_types). Effective Q dim 16*256=4096; KV dim 2*256=512. |

**层模式：** (D,D,D,F)x10 with D=gated_deltanet, F=gated_attention. config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 10 times (40 layers total). config.full_attention_interval=4 confirms the 1-in-4 cadence. README naming: '10 x (3 x (Gated DeltaNet -> MoE) -> 1 x (Gated Attention -> MoE))'.

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 512 |

**路由：** Top-8 routing over 256 routed experts plus 1 always-on shared expert per token (README: '8 Routed + 1 Shared'). Auxiliary load-balance loss with coefficient router_aux_loss_coef=0.001. Per-expert FFN intermediate dim is 512 for both routed (moe_intermediate_size) and shared (shared_expert_intermediate_size) experts — uniform width. Total MoE width per token = 9 * 512 = 4608 from 9 active experts (8 routed + 1 shared).

**层划分：** Uniform MoE FFN across all 40 layers regardless of attention variant (config.mlp_only_layers=[] - no dense FFN substitution at any depth).

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in each expert FFN). |
| 归一化 | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding 说明：** tie_word_embeddings=false (separate input embedding and output head). Token Embedding 248320 (padded) and LM Output 248320 (padded) per README; config.vocab_size=248320 confirms. Substantial vocab expansion vs Qwen3 (151,936) driven by 201-language coverage and native-VL reserved tokens. Vision-related reserved IDs in the LM vocabulary: image_token_id=248056, video_token_id=248057, vision_start_token_id=248053, vision_end_token_id=248054. eos_token_id=248044.

### 并行 / 基础设施

[Unknown/Not Disclosed]

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** Vendor highlights only (identical to Qwen3.5-27B; the README Highlights section is family-level). 'Global Linguistic Coverage: Expanded support to 201 languages and dialects' (vs Qwen3's 119). 'Unified Vision-Language Foundation: Early fusion training on multimodal tokens achieves cross-generational parity with Qwen3 and outperforms Qwen3-VL models across reasoning, coding, agents, and visual understanding benchmarks.' 'Next-Generation Training Infrastructure: Near-100% multimodal training efficiency compared to text-only training.' No quantitative breakdown (token totals, code/math/text shares, image/video token counts) is disclosed.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | [Unknown/Not Disclosed] |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ MTP head with mtp_num_hidden_layers=1 (config) and mtp_use_dedicated_embeddings=false (shares input embeddings with the main model). README states 'MTP: trained with multi-steps' - the exact step depth D is not disclosed.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking` | Default mode. Qwen3.5 thinks by default and wraps reasoning in <think>...</think> before producing the final response. README explicitly states the Qwen3-style /think and /no_think soft switches are NOT supported in Qwen3.5. | Long Chain-of-Thought reasoning before the final answer. Recommended sampling per README Best Practices: temperature=1.0, top_p=0.95, top_k=20, min_p=0.0, presence_penalty=1.5, repetition_penalty=1.0 (general); temperature=0.6 for precise coding tasks (e.g. WebDev). |
| `non-thinking` | Set chat_template_kwargs={"enable_thinking": False} via the OpenAI-compatible API extra_body (vLLM/SGLang/Qwen-Agent), or pass enable_thinking=False directly on Alibaba Cloud Model Studio. Soft switches /think and /no_think are NOT supported (README: 'Qwen3.5 does not officially support the soft switch of Qwen3'). | Direct, low-latency response without an explicit reasoning trace. Recommended sampling per README Best Practices: temperature=0.7, top_p=0.8, top_k=20, presence_penalty=1.5 (general); temperature=1.0, top_p=1.0, top_k=40, presence_penalty=2.0 for reasoning tasks in non-thinking mode. |

- **`thinking`**
    - Kwargs：`enable_thinking=true`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`
- **`non-thinking`**
    - Kwargs：`enable_thinking=false`
    - 推荐采样参数：`temperature=0.7`, `top_p=0.8`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<tool_call>` |
| 结束 token | `</tool_call>` |
| 参数编码方式 | Per-arg <parameter=name>VALUE</parameter> blocks nested inside a <function=NAME></function> wrapper. Values are stringified — in Qwen3.5 the chat template applies `tojson` only to mappings/sequences and falls back to Python `str()` for scalars (so booleans render as 'True'/'False' rather than 'true'/'false' — fixed in Qwen3.6 to apply `tojson` to anything that is not already a string). |

**服务端解析器参数：**

- `vllm`: `--tool-call-parser qwen3_coder`
- `sglang`: `--tool-call-parser qwen3_coder`

_说明：_ Verbatim from the chat template (tokenizer_config.json): '<tool_call>\n<function=example_function_name>\n<parameter=example_parameter_1>\nvalue_1\n</parameter>\n<parameter=example_parameter_2>\n...\n</parameter>\n</function>\n</tool_call>'. README serving snippets pair `--tool-call-parser qwen3_coder` with `--reasoning-parser qwen3` for combined reasoning + tool-use deployments. The natural-language reasoning may appear BEFORE but NOT after the tool call (template comment). Tool-call output is wrapped via `<tool_response>...</tool_response>` blocks emitted as a `tool` role message.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `native_early` |

**融合方式说明：** Vendor description: 'Unified Vision-Language Foundation. Early fusion training on multimodal tokens.' Vision tokens are inlined into the same backbone as text via four reserved vocabulary IDs (vision_start, image, video, vision_end). The vision encoder's projected output dim (vision_config.out_hidden_size=2048) equals the LM hidden dim (note: 2048 here vs 5120 for Qwen3.5-27B — the same vision encoder is reprojected to whatever LM width the backbone uses). README pipeline_tag=image-text-to-text confirms the model is shipped as a single causal LM that natively consumes image and video alongside text; there is no separate text-only checkpoint.

### 视觉编码器

| | |
|---|---|
| 架构 | ViT (HF model_type=qwen3_5_moe vision config). config.deepstack_visual_indexes=[] - no DeepStack injection layers configured. Same encoder geometry as Qwen3.5-27B (depth/hidden/heads/patch all match) — only the projection out_hidden_size differs to match the LM hidden. |
| 层数 | 27 |
| 隐藏维度 | 1152 |
| 中间维度 | 4304 |
| 头数 | 16 |
| patch 大小 | 16 |
| 输入通道数 | 3 |
| 输出维度 → LM | 2048 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 2 |

_说明：_ hidden_act=gelu_pytorch_tanh; num_position_embeddings=2304 (encoder's own positional table). Long-video tip from README Best Practices: setting video_preprocessor_config longest_edge=469,762,048 (~224K video tokens) enables higher frame-rate sampling for hour-scale videos.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 248056 |
| video_token_id | 248057 |
| vision_start_token_id | 248053 |
| vision_end_token_id | 248054 |

## 待解问题（open_questions）

- Pre-training optimizer, learning-rate schedule, batch size, peak/min LR, weight decay and gradient clipping are not disclosed for Qwen3.5-35B-A3B. The README/blog only describe vendor highlights; no separate Qwen3.5 LM-backbone arXiv tech report is available at extraction time (Qwen3.5-Omni Technical Report exists but covers the audio/visual omni-extension, not the LM backbone we characterize here).
- Total pre-training tokens and the data mix (code/math/text/multilingual/image/video shares) are not disclosed numerically. README only states the multilingual coverage expansion (119 -> 201 languages) and the early-fusion multimodal training claim.
- Multi-Token Prediction step depth D is not stated quantitatively. README writes 'MTP: trained with multi-steps' and config exposes mtp_num_hidden_layers=1 (head depth) but no explicit D for training-time multi-step loss; only inference-time speculative-decoding numbers (vLLM 2 / sglang 3-4) are provided as serving recipes.
- Post-training pipeline structure is undisclosed for Qwen3.5: no explicit stage count, no SFT data scale, no RL algorithm name. The blog highlights 'Reinforcement learning scaled across million-agent environments with progressively complex task distributions' and 'asynchronous RL frameworks supporting massive-scale agent scaffolds and environment orchestration', but the specific algorithm (GRPO vs PPO vs DPO vs other) and reward shaping are not named.
- Mixed-precision training recipe (BF16-only vs FP8 GEMM with BF16 master weights, etc.) is not disclosed; config.text_config.dtype=bfloat16 is the released checkpoint dtype, not necessarily the training-time precision.
- Parallelism strategy and training infrastructure (TP/PP/EP/DP shapes, GPU type and count, framework) are not disclosed. MoE-specific details (expert parallelism, all-to-all dispatch implementation, routing imbalance handling beyond aux_loss_coef=0.001) are also not disclosed.
- Why exactly 1 shared expert? Qwen3 dropped shared experts (vs Qwen2.5), citing global-batch load balancing as sufficient. Qwen3.5 reintroduces exactly 1 shared expert (matches DeepSeek-V3's count, but DeepSeek-V3 has 1 shared expert with much wider per-expert intermediate). The design rationale (was global-batch LB insufficient under hybrid attention? did the asymmetric V/K linear-attention budget create capacity gaps the shared expert covers?) is not discussed in vendor sources.
- Auxiliary-loss-free routing was a feature of Qwen3-235B-A22B's MoE; Qwen3.5-35B-A3B reverts to a classic auxiliary load-balance loss (router_aux_loss_coef=0.001 in config). No vendor explanation for the reversion.
- Routing algorithm specifics — top-k softmax vs sigmoid gating, expert-choice routing variants, capacity factor at training time, drop-token policy — are not disclosed beyond 'top-8 routed + 1 shared'.
- config.text_config.partial_rotary_factor=0.25 implies only 64 of the 256 attention head dims carry RoPE (remaining 192 are NoPE/non-positional). The README and blog do not explain the motivation for this NoPE/RoPE split.
- Vision encoder is the same geometry as Qwen3.5-27B (ViT depth=27, hidden=1152, heads=16, patch=16, spatial_merge=2, temporal_patch=2); only out_hidden_size differs (2048 here vs 5120). Whether the encoder weights are literally shared between the dense 27B and MoE 35B-A3B (same checkpoint, just reprojected) or independently trained is not disclosed.
- Cached blog.html at qwen.ai/blog?id=qwen3.5 is a client-side-rendered SPA shell (only 'Qwen' is present in the static HTML). Substantive blog content was therefore unavailable at extraction time; if a static rendering or per-section anchor URL appears later, re-source for a richer training/post-training description.

---

_由 `data/extracted/qwen3.5-35b-a3b.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
