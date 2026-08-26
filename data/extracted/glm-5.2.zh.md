# GLM-5.2

> English: [glm-5.2.md](./glm-5.2.md)

*Schema 版本: 7*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | GLM-5 |
| 发布时间 | 2026-06 |
| 开放程度 | 开放权重 |
| 总参数量 | 744B (vendor figure for the GLM-5 line, which GLM-5.2's topology inherits unchanged; the shipped bf16 checkpoint's safetensors index totals 1,506,659,919,872 bytes ≈ 753B bf16 parameters, ~0.6B FEWER than GLM-5.1 — consistent with IndexShare removing the per-layer indexer weights from the 57 Shared layers) |
| 激活参数量 | 40B |

**变体策略（variant policy）：** Unlike GLM-5.1 (a post-training-only refresh whose config was byte-identical to GLM-5), **GLM-5.2 is an architecture change**: same `GlmMoeDsaForCausalLM` class and same 78L / 6144-hidden / 256-expert topology, but three substantive config deltas — IndexShare indexer sharing, a 5.2× larger position window (202,752 → 1,048,576), and rope_theta 1e6 → 8e6. Ships as bf16 + FP8 checkpoint pair, matching the GLM-5 / GLM-5.1 pattern. Runtime modes gain a **reasoning-effort axis**: `reasoning_effort` ∈ {high, max} (max default) alongside the existing `enable_thinking` and `clear_thinking` kwargs. Z.AI foregrounds the licence as a product decision — README highlight 'Pure Open: An MIT open-source license — no regional limits, technical access without borders', a pointed contrast with the custom licences Qwen attached to two of its three August checkpoints.

## 数据源

- <https://huggingface.co/zai-org/GLM-5.2/raw/main/config.json>
- <https://huggingface.co/zai-org/GLM-5.2/raw/main/chat_template.jinja>
- <https://huggingface.co/zai-org/GLM-5.2/raw/main/tokenizer_config.json>
- <https://huggingface.co/zai-org/GLM-5.2/raw/main/README.md>
- <https://arxiv.org/pdf/2602.15763>
- <https://arxiv.org/pdf/2603.12201>
- <https://z.ai/blog/glm-5.2>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 78 |
| 隐藏维度 | 6144 |
| 上下文窗口 | 1048576 |

**上下文说明：** **1,048,576 — a 5.2× jump from GLM-5 / GLM-5.1's 202,752**, and the headline claim of the release ('a solid 1M-token context that stably sustains long-horizon work'). `rope_theta` was raised 1,000,000 → 8,000,000 to support it. The vendor's framing is that the 1M window is *usable*, not merely declared: several reported benchmarks (FrontierSWE, PostTrainBench, SWE-Marathon) were run by third parties at 1M context with max effort. No YaRN or other scaling block is documented — the window is native.

### 注意力（MLA）

| | |
|---|---|
| 变体 | MLA |
| 头数 | 64 |
| KV 头数 | [Unknown/Not Disclosed] |
| 头维度 | [Unknown/Not Disclosed] |

**RoPE：** type=`standard`, base=`8000000`

**MLA 特有字段：**

| | |
|---|---|
| kv_lora_rank | 512 |
| q_lora_rank | 2048 |
| qk_nope_head_dim | 192 |
| qk_rope_head_dim | 64 |
| v_head_dim | 256 |

**注意力补充说明：** One config key changed meaning rather than value: top-level `head_dim` went 64 → 192. GLM-5.1 reported the RoPE head dim there while GLM-5.2 reports the NoPE head dim; `qk_head_dim` (256), `qk_nope_head_dim` (192) and `qk_rope_head_dim` (64) are all unchanged, so the attention geometry is identical and this is a config-representation change, not an architecture change.

**稀疏注意力：**

| | |
|---|---|
| 类型 | `dsa` |
| 保留条目数（top-k） | 2048 |
| Indexer 头数 | 32 |
| Indexer 头维度 | 128 |

**选择规则：** Top-k by lightning-indexer score (DeepSeek-V3.2-Exp mechanism), but **only 21 of 78 layers compute their own selection**. Layers are partitioned into `Full` layers that run their own indexer and `Shared` layers that reuse the nearest preceding Full layer's top-k indices — the technique the model card calls **IndexShare** and its paper calls **IndexCache** (arXiv 2603.12201). config.indexer_types is the per-layer assignment: 21 `full` / 57 `shared`. Layers 0-2 (the dense-FFN layers) are Full; from layer 3 the pattern is period-4 with a Full layer every fourth (`index_topk_freq=4`, `index_skip_topk_offset=3`).

**训练配方：** The IndexShare paper offers two routes and GLM-5.2 ships the **training-aware** one: a multi-layer distillation loss trains each retained indexer against the *averaged* attention distributions of all the layers it serves, which the paper shows lets even a simple uniform interleaved pattern match full-indexer accuracy. (The training-free alternative — a greedy search that picks which layers keep indexers by directly minimizing LM loss on a calibration set, no weight updates — is what the paper recommends when retraining is not an option.) The underlying DSA indexer itself is inherited from GLM-5's Continued Pre-Training recipe.

_说明：_ **The motivation is that DSA's indexer is the residual O(L²) cost.** DSA reduces core attention from O(L²) to O(Lk), but the lightning indexer still runs independently at every layer at O(L²) — even though consecutive layers' top-k selections are highly similar. IndexShare exploits exactly that redundancy. Reported effect: **2.9× fewer per-token FLOPs at 1M context** (model card); the paper measures 75% of indexer computation removed with negligible quality loss on a 30B DSA model (1.82× prefill / 1.48× decode speedup), and ~1.2× end-to-end on production-scale GLM-5 at 50% removal. `index_share_for_mtp_iteration=true` extends the reuse into the MTP module's speculative-decoding iterations. **Cross-vendor note:** this is the same technique Qwen's Qwen3.8-Flash-Next report benchmarks against by name (cited there as 'training-aware IndexShare (Bai et al., 2026)') before choosing within-layer micro-block compression instead — Qwen's argument being that cross-layer index sharing is weakened in hybrid stacks where full-attention layers are separated by linear-attention layers. GLM-5.2 is a pure-MLA stack, where the cross-layer similarity IndexShare depends on is strongest. See [qsa](../../docs/glossary/qsa.md) for the other side of that argument.

### FFN（hybrid）

**Dense 中间维度：** `12288`

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Auxiliary-loss-free routing (`topk_method='noaux_tc'`) with sigmoid affinity scoring, `routed_scaling_factor=2.5`, `norm_topk_prob=true`, `n_group=1` / `topk_group=1` — unchanged from GLM-5 / GLM-5.1. One new key: `moe_router_dtype='float32'`, pinning the router to fp32 regardless of the bf16 model dtype. Z.AI does not comment on it, but it is the same class of numerical-stability guard as GLM-5's deterministic `torch.topk` in the DSA indexer.

**层划分：** First 3 of 78 layers are dense FFN (intermediate_size=12288); the remaining 75 are MoE (per-expert 2048, 1 shared expert at 2048). `first_k_dense_replace=3`, `moe_layer_freq=1`. New in 5.2, the config now emits this explicitly as an `mlp_layer_types` list (3 `dense` + 75 `sparse`) in addition to `first_k_dense_replace` — the same information, now enumerated. Note the dense layers and the IndexShare `Full` layers coincide at the bottom of the stack: layers 0-2 are both dense-FFN and own-indexer.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config `hidden_act=silu`). |
| 归一化 | RMSNorm, `rms_norm_eps=1e-05`, `attention_bias=false` — unchanged from GLM-5 / GLM-5.1. |

**Embedding 说明：** `tie_word_embeddings=false`, `vocab_size=154880`, `pad_token_id=154820`, three EOS ids (154820 / 154827 / 154829) — all unchanged from GLM-5 / GLM-5.1. `rope_interleave=true` and `indexer_rope_interleave=true` likewise carry over.

### 辅助模块

**MTP layer (improved for speculative decoding)**

| | |
|---|---|
| 用途 | `multi_token_prediction / speculative_decoding` |
| 是否随权重发布 | `True` |

**结构：** `num_nextn_predict_layers=1` — a single MTP layer, structurally as in GLM-5 / GLM-5.1. The 5.2 delta is in how it was trained and how it is served, not in its shape.

**启用方式：** [Unknown/Not Disclosed] — the README does not print per-framework speculative-decoding flags, linking to SGLang / vLLM / KTransformers / Unsloth recipes instead.

_说明：_ README: 'We also improve GLM-5.2's MTP layer for speculative decoding, increasing the acceptance length by up to 20%.' The training change behind that number is not described. Separately, `index_share_for_mtp_iteration=true` lets the MTP iterations reuse the backbone's IndexShare selections rather than recomputing them — the same index-reuse trick Qwen3.8-Flash-Next later credits to GLM.

### 并行 / 基础设施

[Unknown/Not Disclosed] for GLM-5.2 specifically; the GLM-5 technical report (arXiv 2602.15763) covers the family's training infrastructure and GLM-5.2 does not restate or amend it.

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] for GLM-5.2 specifically. The GLM-5 family report documents Muon with Z.AI's 'Muon Split' per-head adaptation; GLM-5.2 does not state whether the recipe changed. |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** No pre-training disclosure specific to GLM-5.2 — the model card cites the GLM-5 family report (arXiv 2602.15763) rather than describing a new corpus, and does not say whether 5.2 is a continued pre-train of the GLM-5 base, a fresh pre-train, or post-training plus an architecture retrofit. Given IndexShare is presented as a retrofittable technique with a training-aware distillation route, a retrofit-plus-continued-training path is the most consistent reading, but it is not stated. Reported gains over GLM-5.1 are large and concentrated in long-horizon agentic work: DeepSWE 18 → 46.2, FrontierSWE (Dominance) 30.5 → 74.4, Terminal Bench 2.1 (Terminus-2) 63.5 → 81.0, ProgramBench 50.9 → 63.7, SWE-Marathon 1.0 → 13.0, HLE 31 → 40.5, SWE-bench Pro 58.4 → 62.1, NL2Repo 42.7 → 48.9, MCP-Atlas 71.8 → 76.8. Several of these were run by third-party evaluators (Proximal, PostTrainBench, Abundant AI) at 1M context.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | [Unknown/Not Disclosed] |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ `num_nextn_predict_layers=1`, parameter-shared MTP as in the GLM-5 line. See architecture.auxiliary_modules for the 5.2-specific acceptance-length improvement and the IndexShare reuse into MTP iterations.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed] for GLM-5.2 specifically; the GLM-5 family report documents slime async RL with GRPO+IcePop and no KL term.

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking / reasoning_effort=max` | Default. The chat template resolves `effective_reasoning_effort` to `max` unless `reasoning_effort == 'high'` is passed explicitly, then emits a `<|system|>Reasoning Effort: Max` prefix as the very first thing in the prompt. **NEW IN 5.2** — GLM-5 / GLM-5.1 had no effort axis. | Deepest reasoning. README highlight: 'Stronger coding capabilities with multiple thinking effort levels to balance performance and latency.' Third-party evaluations of the headline agentic benchmarks were run at max effort. |
| `thinking / reasoning_effort=high` | `reasoning_effort="high"` — the only accepted non-default value. The template is a strict two-way branch: anything that is not exactly `'high'` falls back to `max`, so an unrecognized level silently becomes the most expensive one rather than raising (contrast Qwen3.8, which raises on unknown levels). | Lower-cost reasoning level. Emitted as `<|system|>Reasoning Effort: High`. |
| `non-thinking` | `enable_thinking=false`. The template then emits a pre-closed `<think></think>` block after `<|assistant|>` so generation starts directly on content, and suppresses the Reasoning Effort prefix entirely (the effort line is guarded by `enable_thinking`). | Direct response with no reasoning trace. Inherited unchanged from GLM-5 / GLM-5.1. |
| `preserved thinking (clear_thinking=false)` | `clear_thinking=false`. Default behaviour retains `<think>` blocks only for messages after the last user turn; passing `clear_thinking=false` retains them across the whole history. | Full multi-turn reasoning carryover, as in GLM-5 / GLM-5.1. Note the polarity is inverted relative to Qwen's `preserve_thinking`: GLM names the kwarg for the *clearing* behaviour, so preservation is `clear_thinking=false` rather than `preserve_thinking=true`. |

- **`thinking / reasoning_effort=max`**
    - Kwargs：`reasoning_effort=max`
- **`thinking / reasoning_effort=high`**
    - Kwargs：`reasoning_effort=high`
- **`non-thinking`**
    - Kwargs：`enable_thinking=false`
- **`preserved thinking (clear_thinking=false)`**
    - Kwargs：`clear_thinking=false`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<tool_call>` |
| 结束 token | `</tool_call>` |
| 参数编码方式 | Inherited from the GLM-4.7 / GLM-5 line — per-arg `<arg_key>` / `<arg_value>` blocks inside a `<tool_call>` wrapper, with tool schemas declared as JSON in a `<tools>` system block. GLM-5.1's `tool_reference` content type for MCP-style lazy tool loading carries over. |

_说明：_ The README links per-framework cookbooks (SGLang, vLLM, Transformers, KTransformers, Unsloth, plus Ascend NPU guidance) rather than printing parser flags, so parser_flags is left empty rather than carried over from the GLM-5 record.

### 进阶

**自蒸馏：** IndexShare's training-aware route is a distillation *within* the model: each retained indexer is trained against the averaged attention distributions of the layers it serves. This is a second-order version of the self-distillation DSA already used (indexer trained by KL against the model's own attention) — here the target is an average over several layers rather than one.

**混合精度：** [Unknown/Not Disclosed] for training. The released checkpoint is bf16 (`dtype: bfloat16`) with an FP8 sibling (`GLM-5.2-FP8`); `moe_router_dtype='float32'` pins the router to fp32 at inference.

**稳定性 trick：** `moe_router_dtype='float32'` is new in 5.2 and is the only numerical guard visible in the config diff. The GLM-5 family report's stability measures (deterministic `torch.topk` in the DSA indexer for RL stability, Muon Split obviating QK-Clip) are not restated for 5.2.

## 待解问题（open_questions）

- **Is GLM-5.2 a continued pre-train, a fresh pre-train, or an architecture retrofit onto GLM-5.1?** The model card does not say, and cites only the February GLM-5 family report. IndexShare is presented as retrofittable (its training-aware route is a distillation onto existing indexers), and the parameter count *drops* by ~0.6B versus GLM-5.1 — both consistent with a retrofit — but the 1M context window and the rope_theta change imply substantial continued training regardless.
- The model card gives no parameter count. `params_total` here carries the vendor's GLM-5-line figure plus the byte-exact safetensors total for the shipped checkpoint, because those disagree slightly in a way that is itself informative (the ~0.6B reduction tracks the removed Shared-layer indexers). If Z.AI publishes a 5.2-specific figure, replace it.
- The MTP acceptance-length improvement ('up to 20%') has no method attached — whether it came from more MTP training, a different draft objective, or purely from the IndexShare reuse in MTP iterations is unstated.
- IndexShare naming: the model card calls it **IndexShare**, the paper it links (arXiv 2603.12201) calls it **IndexCache** throughout. Qwen's Qwen3.8-Flash-Next report cites it as 'IndexShare (Bai et al., 2026)'. Recorded here under the model card's name with the paper title noted; watch for the naming to settle.
- Which IndexShare variant shipped is inferred from the config's fixed period-4 pattern plus the paper's claim that training-aware distillation lets simple interleaved patterns match full-indexer accuracy. Z.AI does not state it outright. The training-free greedy search would be expected to produce an *irregular* layer set, which is not what the config shows.
- Post-training recipe for 5.2 is undisclosed. The jumps on long-horizon agentic benchmarks (DeepSWE 18 → 46.2, SWE-Marathon 1.0 → 13.0) are far too large to attribute to an attention-efficiency change, so there is substantial unpublished post-training work behind this release.
- Optimizer, LR schedule, token count, data mix, parallelism and mixed-precision recipe are all deferred to the GLM-5 family report and not restated or amended for 5.2.
- `moe_router_dtype='float32'` appears without comment. Whether it fixes an observed instability, is a serving-side determinism measure, or is simply an upstream `transformers` default that surfaced in the newer version is not stated.
- Cached blog.html at z.ai/blog/glm-5.2 is a client-side-rendered SPA shell (0 characters of extractable text), so blog content was unavailable at extraction time.

---

_由 `data/extracted/glm-5.2.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
