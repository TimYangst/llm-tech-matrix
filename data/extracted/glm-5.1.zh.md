# GLM-5.1

> English: [glm-5.1.md](./glm-5.1.md)

*Schema 版本: 6*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | GLM-5 |
| 发布时间 | 2026-04 |
| 开放程度 | 开放权重 |
| 总参数量 | 744B |
| 激活参数量 | 40B |

**变体策略（variant policy）：** GLM-5.1 is a post-training-only refresh of GLM-5 — config.json byte-identical except `transformers_version` (5.0.2.dev0 → 5.4.0); tokenizer_config.json byte-identical. Same `GlmMoeDsaForCausalLM` architecture, same MLA + DSA + 256-expert MoE topology, same 744B / 40B active. Z.AI ships GLM-5.1 as two checkpoints (GLM-5.1 bf16 + GLM-5.1-FP8 quantized) sharing the same post-trained weights, mirroring the GLM-5 pair structure. Within a single checkpoint the chat-template kwargs `enable_thinking` and `clear_thinking` give the same three runtime behaviors as GLM-5 (interleaved / turn-level / preserved thinking).

## 数据源

- <https://huggingface.co/zai-org/GLM-5.1/raw/main/config.json>
- <https://huggingface.co/zai-org/GLM-5.1/raw/main/tokenizer_config.json>
- <https://huggingface.co/zai-org/GLM-5.1/raw/main/chat_template.jinja>
- <https://huggingface.co/zai-org/GLM-5.1/raw/main/README.md>
- <https://arxiv.org/pdf/2602.15763>
- <https://z.ai/blog/glm-5.1>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 78 |
| 隐藏维度 | 6144 |
| 上下文窗口 | 202752 |

**上下文说明：** Identical to GLM-5 — config.json max_position_embeddings=202752, num_hidden_layers=78, num_nextn_predict_layers=1. Mid-training context curriculum (32K → 128K → 200K) inherited from GLM-5 (paper §2.3); GLM-5.1 release notes do not document any further context-window change.

### 注意力（MLA）

| | |
|---|---|
| 变体 | MLA |
| 头数 | 64 |
| KV 头数 | [Unknown/Not Disclosed] |
| 头维度 | [Unknown/Not Disclosed] |

**RoPE：** type=`standard`, base=`1000000`

**MLA 特有字段：**

| | |
|---|---|
| kv_lora_rank | 512 |
| q_lora_rank | 2048 |
| qk_nope_head_dim | 192 |
| qk_rope_head_dim | 64 |
| v_head_dim | 256 |

### FFN（hybrid）

**Dense 中间维度：** `12288`

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Auxiliary-loss-free routing (config.topk_method='noaux_tc') with sigmoid affinity scoring (scoring_func='sigmoid'), routed_scaling_factor=2.5, norm_topk_prob=true, n_group=1 / topk_group=1. Identical to GLM-5 — the routing module weights are inherited from GLM-5 with post-training-only updates.

**层划分：** First 3 of 78 layers are dense FFN (intermediate_size=12288); remaining 75 layers are MoE (per-expert intermediate_size=2048, 1 shared expert at 2048). config.first_k_dense_replace=3, moe_layer_freq=1.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config.hidden_act='silu'). |
| 归一化 | RMSNorm (rms_norm_eps=1e-5). |

**Embedding 说明：** tie_word_embeddings=false. Vocabulary 154880. eos_token_id=[154820, 154827, 154829], pad_token_id=154820. attention_bias=false. Identical tokenizer and special-token layout to GLM-5; tokenizer_config.json byte-identical. Chat-template adds (vs GLM-5): a `tool_to_json` macro that filters out `defer_loading` and `strict` keys before serializing tool definitions, OpenAI-format `{function: {...}}` tool-envelope unwrapping, deferred-tool exclusion at emission time (`if tool.defer_loading is not defined or not tool.defer_loading`), more sophisticated `thinking_indices` history tracking (per-user-turn flag of whether the matched assistant response had `reasoning_content`), and a new `tool_reference` tool-message content type that inlines the matching tool definition into the `<tool_response>` (likely supporting deferred-loaded MCP tools surfaced cross-turn).

### 并行 / 基础设施

GLM-5.1 release notes do not separately document training infrastructure; post-training-only refresh inherits GLM-5's slime-based asynchronous RL framework (paper §3.6). Inference deployment matches GLM-5 (vLLM v0.19.0+, SGLang v0.5.10+, KTransformers v0.5.3+, Transformers v0.5.3+, xLLM v0.8.0+) — README §Serve adds a 'see [transformers docs](https://github.com/huggingface/transformers/blob/main/docs/source/en/model_doc/glm_moe_dsa.md)' pointer not present on the GLM-5 README, indicating the `glm_moe_dsa` model class is now upstreamed in mainline Transformers.

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] — GLM-5.1 is a post-training-only refresh; no separate paper or model-card section discloses RL optimizer details for the additional post-training. Base-model optimizer inherited from GLM-5: Muon with the Muon Split adaptation. |
| 训练总 token 数 | Inherits GLM-5's 28.5T base + 1.55T mid-training corpus; no additional pre-training tokens disclosed for GLM-5.1. The post-training-only refresh adds RL training on (per README §Introduction) long-horizon agentic-task data — 'sustains optimization over hundreds of rounds and thousands of tool calls' — but post-training token counts are not numerically disclosed. |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** No new pre-training data disclosed (post-training-only refresh). Post-training emphasis on long-horizon agentic engineering data — repo generation (NL2Repo), real-world terminal tasks (Terminal-Bench 2.0), full SWE workflows. README intro: 'It breaks complex problems down, runs experiments, reads results, and identifies blockers with real precision. By revisiting its reasoning and revising its strategy through repeated iteration, GLM-5.1 sustains optimization over hundreds of rounds and thousands of tool calls.'

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | 3 |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ Same parameter-shared 1-module / 3-step-prediction MTP design as GLM-5 (config num_nextn_predict_layers=1; paper §2.1 describes the parameter sharing across 3 MTP layers during training). Inference-time MTP draft-model speculation supported via `--speculative-config.method mtp --speculative-config.num_speculative_tokens 3` (vLLM) or `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4` (SGLang).

### 对齐

**SFT：** Inherited from GLM-5 (three-category SFT: General Chat, Reasoning, Coding & Agent; INT4 QAT during SFT). The GLM-5.1 README characterizes the post-training delta as agentic-engineering reinforcement on long-horizon coding workflows; no separate SFT corpus disclosed for the refresh.

**RL 方法：** Inherits GLM-5's pipeline (Reasoning RL via GRPO+IcePop without KL term → Agentic RL via the asynchronous slime framework → General RL via hybrid reward → On-Policy Cross-Stage Distillation). The GLM-5.1 README emphasizes that the post-training refresh focuses on long-horizon agentic optimization: 'GLM-5.1, by contrast, is built to stay effective on agentic tasks over much longer horizons. … sustains optimization over hundreds of rounds and thousands of tool calls.' This suggests scaled environment counts and longer rollouts; numerical specifics (env count, rollout length, training token count) are not disclosed for the refresh.

**RLAIF：** `[Unknown/Not Disclosed]`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | GLM-5 base post-training pipeline (inherited) | `rl` | Same SFT → Reasoning RL → Agentic RL → General RL → On-Policy Cross-Stage Distillation pipeline as GLM-5 (paper §3); GLM-5.1 inherits the slime asynchronous RL infrastructure, Multi-Task Rollout Orchestrator, TITO gateway, Direct Double-sided Importance Sampling, deterministic torch.topk DSA Indexer, frozen indexer, and DP-aware routing. |
| 2 | Long-horizon Agentic Refinement | `rl` | Post-training-only delta from GLM-5: extended Agentic RL targeting longer-horizon coding and engineering workflows. README §Introduction characterizes the gain as the model 'breaks complex problems down, runs experiments, reads results, and identifies blockers with real precision' over 'hundreds of rounds and thousands of tool calls'. Empirical: SWE-Bench Pro 55.1 → 58.4 (state-of-the-art), NL2Repo 35.9 → 42.7, Terminal-Bench 2.0 (Terminus-2) 56.2 → 63.5, BrowseComp 62.0 → 68.0, CyberGym 48.3 → 68.7, Vending-Bench 2 $4,432 → $5,634. The chat-template additions (`defer_loading` filter, OpenAI-format tool unwrap, `tool_reference` inlining) suggest training scenarios where large MCP-style tool catalogs are loaded lazily across turns. |

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `interleaved-thinking` | Default — chat-template kwarg `enable_thinking=true` (or omitted). Behavior identical to GLM-5: model emits `<think>...</think>` before every response and tool call. | Same as GLM-5; no documented sampling-preset change for GLM-5.1. |
| `non-thinking` | Chat-template kwarg `enable_thinking=false`. | Same as GLM-5 — turn-level disabling of reasoning for lightweight requests. |
| `preserved-thinking` | Chat-template kwarg `clear_thinking=false`. The 5.1 chat template additionally tracks per-user-turn thinking presence via the `thinking_indices` namespace, allowing more accurate historical-thinking-block re-rendering across multi-turn agent sessions. | Same intent as GLM-5 (carry historical `<think>` blocks forward across multi-turn coding-agent sessions for long-horizon tasks). The README emphasizes long-horizon optimization is the central GLM-5.1 delta — preserved-thinking is the load-bearing inference mode for the 'hundreds of rounds, thousands of tool calls' regime described in the introduction. |

- **`interleaved-thinking`**
    - Kwargs：`enable_thinking=true`
- **`non-thinking`**
    - Kwargs：`enable_thinking=false`
- **`preserved-thinking`**
    - Kwargs：`clear_thinking=false`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<tool_call>` |
| 结束 token | `</tool_call>` |
| 参数编码方式 | Per-arg `<arg_key>{key}</arg_key><arg_value>{value}</arg_value>` blocks inside one `<tool_call>{function-name}...</tool_call>` envelope (identical to GLM-5). Non-string scalar values JSON-encoded; string values raw. Tool definitions serialized as a JSON array inside `<tools>...</tools>` in the system message, but GLM-5.1 adds a `tool_to_json` macro that filters `defer_loading` and `strict` keys from each tool object before emission, and unwraps OpenAI-style `{function: {...}}` envelopes to a flat tool object. Tool-result protocol extended: in addition to `<|observation|><tool_response>{string}</tool_response>`, GLM-5.1 supports `tool_reference` content items in tool messages — when present, the chat template emits `<|observation|><tool_response><tools>\n{tool_definition_json}\n</tools></tool_response>`, inlining the matching tool definition cross-turn (likely an MCP-style deferred-tool-loading workflow). |

**服务端解析器参数：**

- `vllm`: `--tool-call-parser glm47 --reasoning-parser glm45 --enable-auto-tool-choice`
- `sglang`: `--tool-call-parser glm47 --reasoning-parser glm45`

_说明：_ Parser names (`glm47` tool-call, `glm45` reasoning) inherited from GLM-5/4.7 — Z.AI did not bump the parser labels for the 5.1 refresh. Speculative decoding (vLLM `--speculative-config.method mtp --speculative-config.num_speculative_tokens 3`; SGLang EAGLE 3-step) inherited from GLM-5. The `defer_loading` chat-template addition is the wire-format-level marker that GLM-5.1 has been trained on lazy / deferred MCP tool-loading scenarios that GLM-5 was not.

### 进阶

**自蒸馏：** Yes — inherits GLM-5's On-Policy Cross-Stage Distillation final-stage recipe (paper §3.5). The post-training-only refresh's additional long-horizon agentic RL likely runs through the same distillation finalization, but specifics are not separately disclosed for GLM-5.1.

**混合精度：** BF16 master parameters (config.dtype='bfloat16'); FP8 rollouts during RL; INT4 QAT during SFT — all inherited from GLM-5. The GLM-5.1-FP8 deployment sibling is post-training quantized for single-node deployment, mirroring the GLM-5/GLM-5-FP8 pair structure.

**稳定性 trick：** Inherits GLM-5's stability machinery (Muon Split, deterministic torch.topk DSA Indexer, frozen indexer in RL, off-policy sample dropping, env-failure-sample dropping, IcePop pop-mask). No GLM-5.1-specific stability tricks are disclosed beyond GLM-5's.

## 待解问题（open_questions）

- GLM-5.1 has no dedicated tech report — the README cites the GLM-5 paper (arxiv:2602.15763) as the canonical reference. Specifics of the post-training refresh (RL token budget, environment counts, rollout-length distribution, hyperparameter changes vs GLM-5) are not numerically disclosed.
- Pre-training data totals carry over from GLM-5; whether GLM-5.1 saw any additional pre-training tokens vs GLM-5 (continued pre-training, additional mid-training stages, etc.) is not stated. README phrasing ('next-generation flagship model for agentic engineering, with significantly stronger coding capabilities than its predecessor') is consistent with post-training-only.
- The chat-template additions (`defer_loading` / `strict` key filtering, OpenAI-format unwrapping, `tool_reference` content type) suggest GLM-5.1 was trained with a deferred / lazy tool-loading workflow — likely related to MCP servers exposing many tools where only a subset is materialized per turn. The training data recipe for this scenario is not documented.
- Sampling presets per inference mode are not separately disclosed for GLM-5.1 — README §Benchmark uses the GLM-5 evaluation settings (temperature/top_p inherited per task).

---

_由 `data/extracted/glm-5.1.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
