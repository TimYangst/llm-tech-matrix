# Qwen3.8-2.4T-A95B

> English: [qwen3.8-2.4t-a95b.md](./qwen3.8-2.4t-a95b.md)

*Schema 版本: 7*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Qwen |
| 发布时间 | 2026-08 |
| 开放程度 | 开放权重 |
| 总参数量 | 2.4T |
| 激活参数量 | 95B |

**变体策略（variant policy）：** First Qwen-Max-class model ever released with open weights — README: 'For the first time, Qwen3.8 brings a Qwen-Max-class model to open release.' This breaks the previous Qwen policy where the Max tier was hosted-only (Qwen3.7-Max, Qwen2.5-Max) and only mid-size checkpoints were opened. Three policy facts distinguish it from the 27B sibling. (1) **License splits by tier**: 27B is Apache-2.0; this checkpoint ships under a custom `qwen3.8-max` license. (2) **The open checkpoint is a strict subset of the hosted product**: README states 'Qwen3.8-Max is the official version based on Qwen3.8-2.4T-A95B with more features, such as vision input & non-thinking support, 1M context length by default, official built-in tools' — so vision and the non-thinking mode exist in the served model but not in the open weights, which are text-only and thinking-only. (3) **Runtime modes shrink rather than grow**: `enable_thinking=false` raises an exception in the chat template; only `reasoning_effort` (xhigh/medium/low) and `preserve_thinking` remain. Still no separate Math / Coder / Thinking sibling checkpoints. Note also that all published benchmark numbers in this model card are labelled 'Qwen3.8-Max', i.e. measured on the hosted superset, not on these open weights.

## 数据源

- <https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/tokenizer_config.json>
- <https://huggingface.co/Qwen/Qwen3.8-2.4T-A95B/raw/main/README.md>
- <https://qwen.ai/blog?id=qwen3.8>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 92 |
| 隐藏维度 | 8192 |
| 上下文窗口 | 262144 |

**上下文说明：** Native 262,144 (config.max_position_embeddings=262144); README states extensibility 'up to 1,010,000 tokens' but — unlike every prior Qwen3.5/3.6/3.8 model card — provides NO YaRN configuration or scaling instructions for this checkpoint. The shipped config uses rope_type=default (no scaling). The hosted Qwen3.8-Max serves 1M context by default.

**上下文扩展：**

| | |
|---|---|
| 方法 | [Unknown/Not Disclosed] |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 1010000 |
| 倍率 | [Unknown/Not Disclosed] |
| RoPE 原始最大长度 | 262144 |

_说明：_ The 1,010,000 ceiling is asserted in the Model Overview but the README's Best Practices section omits the 'Processing Ultra-Long Texts' / YaRN block that Qwen3.5-27B, Qwen3.6-27B and Qwen3.8-27B all carry. Given the identical 262,144 native window and the family's consistent factor=4.0 YaRN recipe, the same mechanism is the obvious candidate — but it is not vendor-stated for this checkpoint, so method and factor are left UNKNOWN rather than carried over from the siblings.

### 注意力（hybrid）

| | |
|---|---|
| 变体 | hybrid |
| 头数 | 64 |
| KV 头数 | 4 |
| 头维度 | 256 |

**RoPE：** type=`standard`, base=`10000000`

RoPE scaling：

```json
{
  "partial_rotary_factor": 0.25
}
```

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Linear attention with asymmetric V vs QK head counts (config: linear_num_value_heads=128 with linear_value_head_dim=128 -> 16384-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state). The V-head count scales with model width (48 at 27B/5120-hidden -> 128 at 2.4T/8192-hidden) while the QK-head count stays pinned at 16 across the whole family, so the K state is 2048-dim in every Qwen3.5/3.6/3.8 model regardless of scale. 1D causal conv pre-DeltaNet with linear_conv_kernel_dim=4. output_gate_type=swish. mamba_ssm_dtype=float32. Used in 3 out of every 4 layers (69 of 92). |
| `gated_attention` | `gqa` | 64 | 4 | 256 | Standard RoPE with rope_theta=10,000,000 and partial_rotary_factor=0.25 - only 64 of 256 head dims are rotated (README: 'Rotary Position Embedding Dimension: 64'), the remaining 192 are NoPE. NO mrope_section / mrope_interleaved here, unlike the native-VL 27B sibling: this is a text-only checkpoint so the multimodal RoPE axis partition is absent. | Softmax attention with output gating (config: attn_output_gate=true). GQA 64Q:4KV — a 16:1 ratio, the most aggressive KV sharing in the Qwen 3.x line (27B is 6:1). attention_bias=false. Used in 1 out of every 4 layers ('full_attention' in config.layer_types). Effective Q dim 64*256=16384; KV dim 4*256=1024 — identical KV width to the 27B despite 1.6x the hidden size, so per-layer KV cache cost does not grow with model scale. |

**层模式：** (D,D,D,F)x23 with D=gated_deltanet, F=gated_attention. config.layer_types is the list ['linear_attention','linear_attention','linear_attention','full_attention'] repeated 23 times (92 layers total: 69 linear + 23 full). config.full_attention_interval=4. README naming: '23 x (3 x (Gated DeltaNet -> MoE) -> 1 x (Gated Attention -> MoE))'. The 3:1 linear-to-full cadence is held constant from the 27B dense model all the way to 2.4T.

**注意力补充说明：** Architecture class is `Qwen3_5MoeForCausalLM` and model_type `qwen3_5_moe_text` — i.e. the Qwen3.5 MoE modeling code, unchanged, three generations on. No vision_config block at all (contrast Qwen3.8-27B, which is `Qwen3_5ForConditionalGeneration` with a ViT).

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 512 |
| 每 token 激活专家数 | 10 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Top-10 routing over 512 routed experts plus 1 always-on shared expert per token (README: '10 Routed + 1 Shared'). Classic auxiliary load-balance loss with coefficient router_aux_loss_coef=0.001 — same aux-loss-based routing as Qwen3.5-35B-A3B, so Qwen has still not adopted DeepSeek-style aux-loss-free bias routing at any scale. Per-expert FFN intermediate dim is 2048 for both routed (moe_intermediate_size) and shared (shared_expert_intermediate_size) experts — uniform width. Total MoE width per token = 11 * 2048 = 22528 from 11 active experts. Sparsity is 10/512 routed (~2.0%), notably sparser than Qwen3.5-35B-A3B's 8/256 (3.1%). A per-layer shared_expert_gate is present (visible in the FP8 sibling's module list), inherited from the Qwen3.5 MoE implementation.

**层划分：** Uniform MoE FFN across all 92 layers regardless of attention variant — every block, linear-attention or full-attention, is followed by the MoE FFN. No dense-FFN substitution at any depth (the config emits no `mlp_only_layers` key).

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config reports hidden_act=silu; SwiGLU is the gated form used in each expert FFN). |
| 归一化 | RMSNorm with pre-normalization (rms_norm_eps=1e-6). attention_bias=false. |

**Embedding 说明：** tie_word_embeddings=false (separate input embedding and output head). Token Embedding 248,320 (padded) and LM Output 248,320 (padded) per README; config.vocab_size=248320 confirms — the SAME padded vocabulary as the native-VL 27B, even though this checkpoint has no vision encoder, so the vision-reserved token IDs (248053-248057) remain allocated but unused. eos_token_id=bos_token_id=248044.

### 并行 / 基础设施

[Unknown/Not Disclosed]

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** No pre-training disclosure whatsoever — no token count, no data mix, no curriculum, no infrastructure. The README's only architectural lineage statement is 'Built on the architectural foundation of Qwen3.5', which the config corroborates (unchanged `Qwen3_5MoeForCausalLM` modeling code, unchanged hybrid 3:1 layout, unchanged aux-loss routing) — the scale-up to 2.4T/95B is achieved by widening (hidden 2048 -> 8192), deepening (40 -> 92 layers) and growing the expert pool (256 -> 512) rather than by changing the recipe. Four claimed highlights, identical wording to the 27B sibling: Core Capabilities, Agent Execution, Downstream Compatibility, Flexible Thinking Control. All published benchmark rows are labelled 'Qwen3.8-Max' (the hosted superset) and compare against Opus 4.8, Fable 5, GPT 5.6 Sol (max) and Qwen3.7-Max; headline in-family deltas vs Qwen3.7-Max: DeepSWE 1.1 21.6 -> 56.6, FrontierSWE 40.7 -> 73.5, Terminal Bench 2.1 74.5 -> 86.6, QwenSWEBench 63.4 -> 80.7, JobBench 31.3 -> 53.4, Agents' Last Exam pass 11.8 -> 27.0 (score 31.1 -> 52.4).

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | [Unknown/Not Disclosed] |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ MTP head with mtp_num_hidden_layers=1 (config) and mtp_use_dedicated_embeddings=false (shares input embeddings with the main model). README states 'MTP: trained with multi-steps' - exact step depth D is not disclosed. Same MTP topology as every other Qwen 3.5/3.6/3.8 checkpoint.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking / reasoning_effort=xhigh` | Default and, in the open weights, the ONLY thinking state — the chat template raises 'Disabling thinking is not supported.' if enable_thinking is false. `reasoning_effort` defaults to `xhigh` and is realized as a natural-language instruction injected into the system message: 'Reasoning effort is set to xhigh. Please think carefully through the task, validate key assumptions, consider plausible alternatives, and prioritize correctness, consistency, and clarity in the final answer.' Values outside {xhigh, medium, low} raise an exception. Unlike the 27B template, effort resolution is unconditional (there is no non-thinking branch to skip it). | Deepest reasoning setting, for 'complex tasks demanding thorough analysis'. Reasoning is wrapped in <think>...</think> before the final response. |
| `thinking / reasoning_effort=medium` | `reasoning_effort="medium"` via chat_template_kwargs (or as a top-level request field on Qwen Cloud). Injects NO instruction text — the template leaves reasoning_instructions empty for this level, so `medium` is the bare prompt. | 'Balancing accuracy and speed' (README). |
| `thinking / reasoning_effort=low` | `reasoning_effort="low"`. Injects 'Reasoning effort is set to low. Keep your thinking brief and focused, moving directly to the conclusion without unnecessary elaboration.' into the system message. | 'Efficient reasoning optimizing for speed and cost' (README), with the same vendor caveat as the 27B that lower effort can increase end-to-end latency in multi-turn agentic tasks through retries. |
| `preserved thinking (default ON)` | Default-on — template condition is `preserve_thinking is undefined or preserve_thinking is true`; pass False to opt out and fall back to latest-turn-only interleaved thinking. | Retains <think> blocks from all historical assistant messages. Same rationale as the 27B: decision consistency in multi-turn agent loops, avoided re-derivation, better KV-cache utilization. |

- **`thinking / reasoning_effort=xhigh`**
    - Kwargs：`reasoning_effort=xhigh`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`, `top_k=20`, `min_p=0.0`, `presence_penalty=0.0`, `repetition_penalty=1.0`
- **`thinking / reasoning_effort=medium`**
    - Kwargs：`reasoning_effort=medium`
- **`thinking / reasoning_effort=low`**
    - Kwargs：`reasoning_effort=low`
- **`preserved thinking (default ON)`**
    - Kwargs：`preserve_thinking=true`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<tool_call>` |
| 结束 token | `</tool_call>` |
| 参数编码方式 | Per-arg <parameter=name>VALUE</parameter> blocks nested inside a <function=NAME></function> wrapper — byte-identical instruction block to Qwen3.8-27B and unchanged from Qwen3.5/3.6. Tool schemas are declared in a `<tools>` system block, one `tool | tojson` per line. |

_说明：_ Identical wire format to the 27B sibling. As with the 27B, the README no longer prints `--tool-call-parser qwen3_coder` / `--reasoning-parser qwen3` serving flags, linking to per-framework cookbooks instead, so parser_flags is left empty rather than inferred from earlier generations.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed]

**稳定性 trick：** [Unknown/Not Disclosed]

## 待解问题（open_questions）

- This checkpoint is text-only (`Type: Causal Language Model`, no vision_config, pipeline_tag=text-generation) while the hosted Qwen3.8-Max built on it has vision input. Whether the served model adds a vision encoder on top of these exact weights, or is a different checkpoint entirely, is not stated. Same question for non-thinking support, which the hosted version has and the open template explicitly refuses.
- ALL benchmark numbers in this model card are labelled 'Qwen3.8-Max', i.e. measured on the hosted superset (vision, non-thinking, 1M default context, built-in tools) rather than on the open weights as released. No open-weights-only evaluation is published, so the numbers should not be read as reproducible from this checkpoint.
- Pre-training tokens, data mix, optimizer, LR schedule, parallelism, mixed precision and training infrastructure are all undisclosed — the disclosure floor for a 2.4T-parameter model here is the same as for a 27B one. No technical report exists for Qwen3.5, 3.6 or 3.8.
- Post-training / RL recipe is entirely undisclosed. For a model whose headline claims are agentic (Agent Execution, long-horizon task completion), no RL algorithm, reward design, environment harness or data scale is given.
- The README asserts extensibility to 1,010,000 tokens but omits the YaRN configuration block that every other Qwen 3.x model card carries, so context_extension.method and .factor are recorded as UNKNOWN. If a later revision adds the block, re-extract.
- Multi-Token Prediction step depth D remains unstated (config: mtp_num_hidden_layers=1; README: 'trained with multi-steps').
- Expert-parallel / routing implementation details beyond router_aux_loss_coef=0.001 are undisclosed: no expert-placement strategy, no capacity factor, no drop policy, no router-logit normalization. At 512 experts and 10 active this matters more than at 35B-A3B scale.
- Whether the 2.4T model was trained from scratch or upcycled/expanded from a smaller Qwen3.x MoE is not stated. The unchanged modeling class and unchanged 3:1 hybrid cadence are consistent with either.
- `reasoning_effort` is prompt-injected system text and `medium` injects nothing, so the three levels are indistinguishable at the weight level. Whether the model was RL-trained against these strings is undisclosed — same open question as Qwen3.8-27B, and the third distinct vendor mechanism for this knob in the repo (DeepSeek-V4 prompt prefix, Kimi K3 typed option message, Qwen3.8 system-message injection).
- The custom `qwen3.8-max` license (LICENSE file in the repo) was not fetched as a source asset; its redistribution and commercial-use terms are not captured in this extraction. The 27B sibling is plain Apache-2.0.
- Cached blog.html at qwen.ai/blog?id=qwen3.8 is a client-side-rendered SPA shell, so substantive blog content was unavailable at extraction time.

---

_由 `data/extracted/qwen3.8-2.4t-a95b.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
