# Kimi K2.6

> English: [kimi-k2.6.md](./kimi-k2.6.md)

*Schema 版本: 6*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Kimi K2 |
| 发布时间 | [Unknown/Not Disclosed] |
| 开放程度 | 开放权重 |
| 总参数量 | 1.04T |
| 激活参数量 | 32B |

**变体策略（variant policy）：** Same generation-level policy as K2.5 (unified-weights checkpoint with chat-template-kwarg modes), and the only post-K2.5 weight family in the K2 line. K2.6 is a post-training-only refresh of K2.5 — README §5: 'Kimi-K2.6 has the same architecture as Kimi-K2.5, and the deployment method can be directly reused.' Adds a third `preserve_thinking` chat-template kwarg that retains the prior turn's `<think>` block in multi-turn conversations (vs K2.5's strict-suffix-only rendering); no new sibling checkpoints.

## 数据源

- <https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/config.json>
- <https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/tokenizer_config.json>
- <https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/preprocessor_config.json>
- <https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/chat_template.jinja>
- <https://huggingface.co/moonshotai/Kimi-K2.6/raw/main/README.md>
- <https://arxiv.org/pdf/2602.02276>
- <https://www.kimi.com/blog/kimi-k2-6.html>
- <https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/docs/tool_call_guidance.md>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 61 |
| 隐藏维度 | 7168 |
| 上下文窗口 | 262144 |

**上下文说明：** README reports 256K; benchmark footnote says experiments use a context length of 262144 tokens (= config.max_position_embeddings). YaRN extension recipe is the same as K2.5 (the architecture is identical per the README).

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 262144 |
| 倍率 | 64.0 |
| RoPE 原始最大长度 | 4096 |

_说明：_ K2.6 inherits K2.5's long-context pre-training curriculum (paper §4.3 / Table 3: mid-training pre-trains at 32K then 256K via YaRN, 500B then 200B tokens). K2.6 is a post-training-only refresh — same backbone weights, same trained-out-to-256K maximum, same baked-in YaRN config (factor=64, original_max=4096). K2.6 README does not restate the curriculum but explicitly says the architecture is identical to K2.5.

### 注意力（MLA）

| | |
|---|---|
| 变体 | MLA |
| 头数 | 64 |
| KV 头数 | [Unknown/Not Disclosed] |
| 头维度 | [Unknown/Not Disclosed] |

**RoPE：** type=`yarn`, base=`50000`

RoPE scaling：

```json
{
  "factor": 64.0,
  "beta_fast": 32.0,
  "beta_slow": 1.0,
  "mscale": 1.0,
  "mscale_all_dim": 1.0,
  "original_max_position_embeddings": 4096
}
```

**MLA 特有字段：**

| | |
|---|---|
| kv_lora_rank | 512 |
| q_lora_rank | 1536 |
| qk_nope_head_dim | 128 |
| qk_rope_head_dim | 64 |
| v_head_dim | 128 |

### FFN（hybrid）

**Dense 中间维度：** `18432`

**MoE：**

| | |
|---|---|
| 可路由专家数 | 384 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Auxiliary-loss-free routing (config.topk_method='noaux_tc') with sigmoid affinity scoring (scoring_func='sigmoid') and routed_scaling_factor=2.827. norm_topk_prob=true. n_group=1 (no grouped / node-limited routing). seq_aux=true with aux_loss_alpha=0.001. Sparsity 48 (384/8). Identical to K2.5.

**层划分：** First 1 of 61 layers is dense (intermediate_size=18432); remaining 60 layers are MoE (per-expert intermediate_size=2048). config.first_k_dense_replace=1, moe_layer_freq=1.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config.hidden_act='silu' — gated SiLU is the SwiGLU form used in the FFN). |
| 归一化 | RMSNorm (rms_norm_eps=1e-5). |

**Embedding 说明：** tie_word_embeddings=false. Vocabulary 163840 (README: '160K'); TikTokenTokenizer. Same special-token table as K2.5; eos_token_id=163586 (vs K2.5's 163585) — the K2.6 EOS aligns with `<|im_end|>` rather than `[EOS]`. Reserved tokens unchanged: <|im_user|>/<|im_assistant|>/<|im_system|>/<|im_middle|>/<|im_end|>, <|tool_calls_section_begin|>...<|tool_call_end|>/<|tool_calls_section_end|>, <|media_begin|>/<|media_content|>/<|media_pad|>/<|media_end|>, <think>/</think>.

### 并行 / 基础设施

Identical to K2.5 (no architectural change). README §5 confirms the K2.5 deployment method can be reused without modification.

## 训练

| | |
|---|---|
| 优化器 | MuonClip — inherited from K2 / K2.5. The K2.6 README does not restate the optimizer choice. |
| 训练总 token 数 | [Unknown/Not Disclosed] — post-training delta on top of K2.5 weights; no new pre-training token count is reported. |

**学习率调度：** [Unknown/Not Disclosed] — K2.6 README does not document training-time hyperparameters (post-training-only refresh).

**数据配比说明：** K2.6 README does not document a pre-training data mix because no new pre-training was performed — improvements come from post-training emphasis on long-horizon coding, coding-driven design, proactive autonomous execution, and swarm-based task orchestration (README §1).

### 对齐

**SFT：** [Unknown/Not Disclosed] — README does not detail the K2.6-specific SFT pipeline. Inherits the K2.5 zero-vision SFT recipe by default.

**RL 方法：** [Unknown/Not Disclosed] — README does not detail the K2.6-specific RL recipe. Inherits the K2.5 token-level clip RL with MuonClip optimizer by default. The K2.6 footnote (Coding §4) notes that Terminal-Bench 2.0 was evaluated 'in preserve thinking mode', suggesting the new `preserve_thinking` kwarg is RL-trained for multi-turn coding-agent scenarios.

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking` | Default mode; chat-template kwarg `thinking=true` (or omitted). Official API: `extra_body={'thinking': {'type': 'enabled'}}`. The chat template emits an open `<think>` tag before the assistant turn. | Reasoning mode — produces a `<think>`...`</think>` block exposed as `reasoning` (K2.6 API) / `reasoning_content` on the OpenAI-compatible API. README §6 sets recommended sampling at temperature 1.0, top_p 0.95. |
| `instant` | Chat-template kwarg `thinking=false`. vLLM/SGLang: `extra_body={'chat_template_kwargs': {'thinking': false}}`. Official API: `extra_body={'thinking': {'type': 'disabled'}}`. | Non-reasoning mode — answers directly. README §6 sets recommended sampling at temperature 0.6, top_p 0.95. |
| `preserve-thinking` | Chat-template kwargs `thinking=true` and `preserve_thinking=true` (must be combined with thinking=true; README §6 'Preserve Thinking' note: we recommend enabling preserve_thinking only in think mode). vLLM/SGLang: `extra_body={'chat_template_kwargs': {'thinking': true, 'preserve_thinking': true}}`. Official API: `extra_body={'thinking': {'type': 'enabled', 'keep': 'all'}}`. | Multi-turn carryover mode (NEW in K2.6 — not in K2.5). The chat template's `preserve_thinking` branch keeps prior assistant `<think>` blocks visible in subsequent turns, instead of stripping them after the previous final answer. Aimed at coding-agent scenarios where reasoning continuity across tool-call cycles helps. K2.6 chat_template.jinja sets `last_non_tool_call_assistant_msg=-1` when preserve_thinking is true so all messages render with reasoning intact. |

- **`thinking`**
    - Kwargs：`thinking=true`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`
- **`instant`**
    - Kwargs：`thinking=false`
    - 推荐采样参数：`temperature=0.6`, `top_p=0.95`
- **`preserve-thinking`**
    - Kwargs：`thinking=true`, `preserve_thinking=true`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `function-call-token` |
| 起始 token | `<|tool_call_begin|>` |
| 结束 token | `<|tool_call_end|>` |
| 参数编码方式 | Each call is `<|tool_call_begin|>{tool_call_id}<|tool_call_argument_begin|>{json_arguments}<|tool_call_end|>` where `tool_call_id` has the form `functions.{name}:{idx}` and `{json_arguments}` is the JSON-encoded arguments object (compact `tojson` separators). Multiple calls per turn are wrapped by `<|tool_calls_section_begin|>` ... `<|tool_calls_section_end|>`. Tool results return as `tool` messages prefixed by `## Return of {tool_call_id}`. Identical to K2.5. |

_说明：_ Wire format unchanged from K2.5 (and K2-Thinking). README §6 notes K2.6 'shares the same design of Interleaved Thinking and Multi-Step Tool Call as K2 Thinking'. No published vLLM/SGLang/KTransformers `--tool-call-parser` flag — relies on the inference engine's built-in K2-family tool-parsing logic; the official FAQ recommends recent vLLM/SGLang for correct tool-call ID handling.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed] — K2.6 README does not restate distillation choices. Likely inherits K2.5's pattern (data synthesis from K2 + K2-Thinking + in-house experts) but not stated.

**混合精度：** BF16 master parameters (config.dtype='bfloat16'); MoE expert weights deployed at INT4 via QAT (compressed-tensors, group_size=32, num_bits=4, type=int, format=pack-quantized) — same recipe as K2.5 / K2-Thinking. K2.6 README §4 explicitly: 'Kimi-K2.6 adopts the same native int4 quantization method as Kimi-K2-Thinking.' Routed-expert linears only — config.quantization_config.ignore excludes self_attn, shared_experts, mlp gate/up/down projections, lm_head, vision_tower, and mm_projector.

**稳定性 trick：** Inherits K2.5's QK-Clip in MuonClip and (presumably) the token-level log-ratio gradient masking from RL. Not restated in the K2.6 README.

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `projection_mlp` |

**融合方式说明：** Identical to K2.5 — same MoonViT-3D vision encoder + MLP projector + Kimi K2 MoE LLM. README §5: 'Kimi-K2.6 has the same architecture as Kimi-K2.5, and the deployment method can be directly reused.' Video uses the same shared MoonViT-3D pipeline with 4× temporal compression at the projector. preprocessor_config.json is byte-identical to K2.5's.

### 视觉编码器

| | |
|---|---|
| 架构 | MoonViT-3D — identical to K2.5 (initialised from SigLIP-SO-400M, ~400M params, NaViT packing, 3D temporal extension over 4 consecutive frames). |
| 层数 | 27 |
| 隐藏维度 | 1152 |
| 中间维度 | 4304 |
| 头数 | 16 |
| patch 大小 | 14 |
| 输入通道数 | [Unknown/Not Disclosed] |
| 输出维度 → LM | 7168 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 4 |

_说明：_ config.vision_config: identical to K2.5 (mm_projector_type='patchmerger', merge_kernel_size=[2,2], merge_type='sd2_tpool', text_hidden_size=7168, video_attn_type='spatial_temporal'). Preprocessor config (MoonViTMediaProcessorConfig) byte-identical to K2.5. config flag use_unified_vision_chunk=true.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 163605 |
| video_token_id | [Unknown/Not Disclosed] |
| vision_start_token_id | 163602 |
| vision_end_token_id | 163604 |

## 待解问题（open_questions）

- Release date is not stated explicitly in the K2.6 README or HF page header; recorded as UNKNOWN. The README cites Claude Opus 4.6 and GPT-5.4 as comparison baselines, suggesting an early/mid-2026 release — but a precise YYYY-MM is not disclosed.
- K2.6's full post-training delta vs K2.5 is described qualitatively (long-horizon coding, coding-driven design, 300-sub-agent / 4000-step swarm, proactive 24/7 background agents) but not quantitatively — no separate K2.6 paper has been published; arXiv:2602.02276 covers K2.5 only.
- Whether `preserve_thinking` is a pure inference-time decoding/template change or also requires K2.6-specific post-training to be effective is not directly stated; the Terminal-Bench-2.0 footnote ('preserve thinking mode') hints at training alignment, but the README does not document it explicitly.
- The chat-template-level diff between K2.5 and K2.6 is exactly: (a) addition of `preserve_thinking` kwarg with the suffix-only / full-history split; (b) `reasoning` field name preferred over `reasoning_content` in the API surface (template falls back to `reasoning_content` for back-compat). Tokenizer_config.json is byte-identical between the two.

---

_由 `data/extracted/kimi-k2.6.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
