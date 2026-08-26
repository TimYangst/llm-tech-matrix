# Qwen3.8-27B

> English: [qwen3.8-27b.md](./qwen3.8-27b.md)

*Schema 版本: 7*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Qwen |
| 发布时间 | 2026-08 |
| 开放程度 | 开放权重 |
| 总参数量 | 27B |
| 激活参数量 | 27B |

**变体策略（variant policy）：** Unchanged unified-weights philosophy: one checkpoint per (size, dense/MoE), capabilities exposed as chat-template kwargs rather than sibling checkpoints. Qwen3.8's open-weight surface is 27B dense (Apache-2.0, native VL) + Qwen3.8-2.4T-A95B (custom `qwen3.8-max` license, text-only). Two policy shifts vs Qwen3.5/3.6. (1) **Version numbers now skip in the open line**: Qwen3.7 shipped only as hosted API models (Qwen3.7-Max, Qwen3.7-Plus) with no open weights, so 3.6 -> 3.8 is the open-weight succession; the 3.8 README benchmarks against `Qwen3.7-Plus` as an external reference point. (2) **Open checkpoint and hosted model are no longer the same product**: the README states Qwen3.8-27B 'will be available as a hosted version with more production features, e.g., 1M context length by default, official built-in tools' — the open weights are the same model with a smaller productized envelope. Runtime modes grow from two axes to three: `enable_thinking` (on/off), `reasoning_effort` (xhigh/medium/low, NEW in 3.8), and `preserve_thinking` (now default ON, was default OFF in 3.6). Still NO separate Math / Coder / VL / Thinking siblings.

## 数据源

- <https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/tokenizer_config.json>
- <https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.8>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 64 |
| 隐藏维度 | 5120 |
| 上下文窗口 | 262144 |

**上下文说明：** Native productized 262K (config.text_config.max_position_embeddings=262144). Extensible to 1,000,000 via opt-in static YaRN configured at inference time (vLLM/SGLang/TokenSpeed); the shipped config.json uses rope_type=default (no scaling). Note the README's stated ceiling is 1,000,000 for the 27B (the Qwen3.5/3.6-27B READMEs said 1,010,000, and the 2.4T-A95B sibling still says 1,010,000) — a documentation-level difference, not a config-level one, since both derive from the same factor=4.0 over a 262,144 original window.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 1000000 |
| 倍率 | 4.0 |
| RoPE 原始最大长度 | 262144 |

_说明：_ Identical recipe to Qwen3.5-27B / Qwen3.6-27B — opt-in deployment-time scaling, factor=4.0 with original_max_position_embeddings=262144, mRoPE configuration (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000) preserved across the extension. Static implementation; README still recommends factor=2.0 for typical use under 524K.

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
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=48 with linear_value_head_dim=128 -> 6144-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. output_gate_type=swish. mamba_ssm_dtype=float32. Used in 3 out of every 4 layers (48 of 64). Byte-identical to Qwen3.6-27B and shape-identical to Qwen3.5-27B — the backbone is now frozen across three consecutive generations. |
| `gated_attention` | `gqa` | 24 | 4 | 256 | mrope (multimodal RoPE) with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated (README: 'Rotary Position Embedding Dimension: 64'), the remaining 192 are NoPE. mrope_section=[11,11,10] partitions the rotary dims across temporal/height/width axes; mrope_interleaved=true. | Softmax attention with output gating (config: attn_output_gate=true). GQA 24Q:4KV. attention_bias=false. Used in 1 out of every 4 layers ('full_attention' in config.layer_types). Effective Q dim 24*256=6144; KV dim 4*256=1024. Byte-identical to Qwen3.6-27B. |

**层模式：** (D,D,D,F)x16 with D=gated_deltanet, F=gated_attention. config.text_config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 16 times. config.full_attention_interval=4 confirms the 1-in-4 cadence. README naming: '16 x (3 x (Gated DeltaNet -> FFN) -> 1 x (Gated Attention -> FFN))'.

**注意力补充说明：** The full config.json of Qwen3.8-27B is byte-identical to Qwen3.6-27B except `transformers_version` (4.57.1 -> 5.8.0.dev0). Every attention parameter — head counts, head dims, gating, conv kernel, layer_types list, RoPE — is unchanged, so architecturally this is a frozen backbone and the release delta lives entirely in post-training and the chat template.

### FFN（dense）

**Dense 中间维度：** `17408`

**层划分：** Uniform dense SwiGLU FFN across all 64 layers regardless of attention variant. (Unlike Qwen3.5-27B, the 3.6/3.8 configs no longer emit the `mlp_only_layers` key at all; there is no dense/MoE split to describe for a dense model.)

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in the FFN). |
| 归一化 | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding 说明：** tie_word_embeddings=false (separate input embedding and output head). Token Embedding 248320 (padded) and LM Output 248320 (padded) per README; config.text_config.vocab_size=248320 confirms. Vision-related reserved IDs in the LM vocabulary: image_token_id=248056, video_token_id=248057, vision_start_token_id=248053, vision_end_token_id=248054. eos_token_id=bos_token_id=248044. Identical to Qwen3.6-27B, and the tokenizer_config.json is identical outside the chat_template.

### 并行 / 基础设施

[Unknown/Not Disclosed]

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** No pre-training data disclosure. The README frames Qwen3.8 as 'the most capable generation in the Qwen open-model family to date', 'Built on the architectural foundation of Qwen3.5' — and the config confirms that literally: the architecture is byte-identical to Qwen3.6-27B. Whether the weights are a fresh pre-train, a continued pre-train, or post-training-only over the Qwen3.6 base is NOT stated; 'Training Stage: Pre-training & Post-training' in the model card is the same boilerplate used for 3.5 and 3.6. Four highlights are claimed, all post-training-shaped: (1) **Core Capabilities** — coding, professional work, research, long-horizon agentic tasks; (2) **Agent Execution** — stronger autonomous planning and better handling of environment feedback; (3) **Downstream Compatibility** — broader support for popular harnesses and dev tools; (4) **Flexible Thinking Control** — `reasoning_effort` plus preserved thinking. The reported gains vs Qwen3.6-27B are large for a frozen architecture: QwenSWEBench 49.3 -> 79.0, DeepSWE 1.1 13.3 -> 42.2, Terminal Bench 2.1 (Terminus) 63.4 -> 73.0, SWE-bench Pro 53.5 -> 61.7, NL2Repo-Bench 36.2 -> 42.3, CoWorkBench 61.0 -> 70.7, JobBench 21.8 -> 33.4, Agents' Last Exam pass@1 10.6 -> 20.4 (score 27.3 -> 42.9).

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | [Unknown/Not Disclosed] |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ MTP head with mtp_num_hidden_layers=1 (config) and mtp_use_dedicated_embeddings=false (shares input embeddings with the main model). README states 'MTP: trained with multi-steps' - exact step depth D is not disclosed. Unchanged from Qwen3.6-27B.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking / reasoning_effort=xhigh` | Default mode (thinking is on unless `enable_thinking=false`; `reasoning_effort` defaults to `xhigh`). NEW IN 3.8: the effort level is realized as a natural-language instruction injected into the system message by the chat template — 'Reasoning effort is set to xhigh. Please think carefully through the task, validate key assumptions, consider plausible alternatives, and prioritize correctness, consistency, and clarity in the final answer.' If no system message exists the template synthesizes one; if tools are declared the instruction is prepended inside the tools system block. The template raises an exception for any value outside {xhigh, medium, low}. | Deepest reasoning setting, for 'complex tasks demanding thorough analysis' (README). Reasoning is wrapped in <think>...</think> before the final response. |
| `thinking / reasoning_effort=medium` | `reasoning_effort="medium"` (via chat_template_kwargs, or as a top-level request field on Qwen Cloud). Distinctively, `medium` injects NO instruction text at all — the template sets `reasoning_instructions` to the empty string for this level, so `medium` is the bare prompt with thinking enabled. xhigh and low are the two levels that add text. | 'Balancing accuracy and speed' (README). |
| `thinking / reasoning_effort=low` | `reasoning_effort="low"`. Injects 'Reasoning effort is set to low. Keep your thinking brief and focused, moving directly to the conclusion without unnecessary elaboration.' into the system message. | 'Efficient reasoning optimizing for speed and cost' (README). The README carries an explicit caveat that in multi-turn agentic tasks lower effort does not always reduce end-to-end latency — insufficient analysis can cause more failures and retries, increasing total time and token consumption. |
| `non-thinking` | Set chat_template_kwargs={"enable_thinking": False} via the OpenAI-compatible API extra_body (vLLM/SGLang/TokenSpeed), or pass enable_thinking=False directly on Qwen Cloud. When thinking is disabled the template skips reasoning-effort resolution entirely, so `reasoning_effort` has no effect in this mode. | Direct, low-latency response without an explicit reasoning trace. Same mode as Qwen3.5/3.6; note the 2.4T-A95B sibling REMOVES it (its template raises on enable_thinking=false), so within one generation the dense open checkpoint keeps a non-thinking mode that the flagship open checkpoint does not have. |
| `preserved thinking (default ON)` | Default-on in 3.8 — the template condition is `preserve_thinking is undefined or preserve_thinking is true`, i.e. the kwarg must be explicitly set to False to opt OUT. This is a DEFAULT FLIP: Qwen3.6's template required `preserve_thinking is defined and preserve_thinking is true` to opt IN. | Retains <think> blocks from ALL historical assistant messages rather than only the latest turn. README rationale: 'ensures full context continuity and is especially beneficial for agent scenarios where decision consistency and reduced redundant reasoning are critical. It also improves KV cache utilization, optimizing inference efficiency in both thinking and non-thinking modes.' Setting it to False restores the Qwen3.6 default (interleaved thinking, latest turn only). A second template change accompanies the flip: Qwen3.6's fallback that split `<think>`/`</think>` out of historical content strings has been removed, so history is expected to arrive with reasoning already structured. |

- **`thinking / reasoning_effort=xhigh`**
    - Kwargs：`enable_thinking=true`, `reasoning_effort=xhigh`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`
- **`thinking / reasoning_effort=medium`**
    - Kwargs：`enable_thinking=true`, `reasoning_effort=medium`
- **`thinking / reasoning_effort=low`**
    - Kwargs：`enable_thinking=true`, `reasoning_effort=low`
- **`non-thinking`**
    - Kwargs：`enable_thinking=false`
    - 推荐采样参数：`temperature=0.7`, `top_p=0.80`, `top_k=20`, `min_p=0.0`, `presence_penalty=1.5`, `repetition_penalty=1.0`
- **`preserved thinking (default ON)`**
    - Kwargs：`preserve_thinking=true`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<tool_call>` |
| 结束 token | `</tool_call>` |
| 参数编码方式 | Per-arg <parameter=name>VALUE</parameter> blocks nested inside a <function=NAME></function> wrapper, unchanged from Qwen3.5/3.6. Tool schemas are declared in the system message as `<tools>` with one `tool | tojson` line per tool. One template-level hardening vs 3.6: the argument loop now skips arguments whose value is the empty string (`tool_call.arguments is defined and tool_call.arguments != ''`), where 3.6 only checked for definedness. |

_说明：_ The wire format is identical to Qwen3.6, but the DISCLOSURE changed: the Qwen3.8 README no longer prints `--tool-call-parser qwen3_coder` / `--reasoning-parser qwen3` serving snippets, replacing them with links to per-framework cookbooks (SGLang, vLLM, TokenSpeed). parser_flags is therefore left empty rather than carried over from 3.6 — see open_questions.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

**稳定性 trick：** [Unknown/Not Disclosed]

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `native_early` |

**融合方式说明：** Same native-early fusion as Qwen3.5-27B / Qwen3.6-27B. Vision tokens are inlined into the same backbone as text via four reserved vocabulary IDs (vision_start, image, video, vision_end). vision_config.out_hidden_size=5120 matches LM hidden_size. HF pipeline_tag=image-text-to-text. README highlight: 'Native support for image and video understanding, from STEM diagrams and documents to hour-scale videos.'

### 视觉编码器

| | |
|---|---|
| 架构 | ViT (HF vision_config model_type=qwen3_5 — still reporting the Qwen3.5 vision model type three generations on, confirming a shared vision encoder). config.vision_config.deepstack_visual_indexes=[] - no DeepStack injection layers configured. |
| 层数 | 27 |
| 隐藏维度 | 1152 |
| 中间维度 | 4304 |
| 头数 | 16 |
| patch 大小 | 16 |
| 输入通道数 | 3 |
| 输出维度 → LM | 5120 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 2 |

_说明：_ hidden_act=gelu_pytorch_tanh; num_position_embeddings=2304. Identical geometry to Qwen3.5-27B and Qwen3.6-27B, and preprocessor_config.json is byte-identical across all three (sha256 27225450ac9c...) — the image preprocessing pipeline has not changed since Qwen3.5.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 248056 |
| video_token_id | 248057 |
| vision_start_token_id | 248053 |
| vision_end_token_id | 248054 |

## 待解问题（open_questions）

- Is Qwen3.8-27B a fresh pre-train, a continued pre-train, or post-training-only over the Qwen3.6-27B base? config.json is byte-identical to Qwen3.6-27B except transformers_version, which proves architectural freeze but says nothing about the weights. The benchmark deltas are unusually large for a post-training-only refresh (QwenSWEBench 49.3 -> 79.0, DeepSWE 1.1 13.3 -> 42.2), which is weak evidence for new pre-training or a large mid-training stage — but the README does not say. Compare with GLM-5 -> GLM-5.1 and Kimi K2.5 -> K2.6, where the same config-identity signal accompanied explicitly post-training-only releases.
- Pre-training optimizer, LR schedule, token count, data mix, parallelism and mixed-precision recipe are all undisclosed — the same disclosure floor as Qwen3.5 and Qwen3.6. Qwen has now shipped three consecutive generations on this architecture with no technical report.
- The post-training recipe behind the agentic gains is entirely undisclosed: no RL algorithm, no reward design, no environment/harness description, no data scale. 'Agent Execution: stronger autonomous planning and better handling of environment feedback' is the only signal, and it is a capability claim, not a method.
- Multi-Token Prediction step depth D is still not stated (third generation running; README says 'trained with multi-steps', config exposes mtp_num_hidden_layers=1).
- `reasoning_effort` is implemented as SYSTEM-PROMPT TEXT INJECTION, not as a control token or a trained mode switch — and `medium` injects nothing at all. Whether the model was actually RL-trained against these three instruction strings, or whether the levels are pure prompt engineering over a single policy, is not disclosed. This is the third distinct vendor mechanism for the same knob in this repo (DeepSeek-V4: prompt-prefix text before the system message; Kimi K3: a typed 'thinking-effort' option message; Qwen3.8: system-message instruction injection) — worth watching as a candidate for a structured schema slot if a fourth occurrence appears.
- The README dropped the explicit `--tool-call-parser qwen3_coder` / `--reasoning-parser qwen3` serving flags that Qwen3.5/3.6 documented, in favor of framework cookbook links. The wire format in the chat template is unchanged, so the qwen3_coder parser is very likely still correct — but it is no longer vendor-stated, so tool_call_protocol.parser_flags is left empty rather than inferred.
- README states the extended context ceiling as 1,000,000 tokens for the 27B while the Qwen3.5/3.6-27B READMEs and the Qwen3.8-2.4T-A95B README all say 1,010,000. YaRN factor (4.0) and original window (262,144) are identical, so this reads as a rounding/documentation change rather than a capability change — but it is a vendor inconsistency worth flagging.
- The open checkpoint and the hosted 'Qwen3.8-27B' on Qwen Cloud are documented as different products (hosted adds 1M default context and official built-in tools). Which built-in tools, and whether the hosted variant uses different weights or only different serving configuration, is not stated. This open-vs-hosted split is new for Qwen and is not something the schema currently models.
- Qwen3.7 has no open weights at all (API-only Qwen3.7-Max / Qwen3.7-Plus), so the open-weight lineage jumps 3.6 -> 3.8 with an unobservable generation in between. Any 3.6 -> 3.8 delta attributed here may in fact have landed in 3.7.
- Cached blog.html at qwen.ai/blog?id=qwen3.8 is a client-side-rendered SPA shell (only 'Qwen' present in the static HTML), so substantive blog content was unavailable at extraction time — same limitation as the Qwen3.5 and Qwen3.6 extractions.

---

_由 `data/extracted/qwen3.8-27b.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
