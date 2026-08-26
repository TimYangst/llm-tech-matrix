# GLM-5.3-Flash

> English: [glm-5.3-flash.md](./glm-5.3-flash.md)

*Schema 版本: 7*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | GLM-5 |
| 发布时间 | 2026-08 |
| 开放程度 | 开放权重 |
| 总参数量 | 320B |
| 激活参数量 | 18B |

**变体策略（variant policy）：** **A new architecture line, not a 5.2 refresh.** HF class is `Glm5NextForConditionalGeneration` (model_type `glm5_next`) versus `GlmMoeDsaForCausalLM` for GLM-5 / 5.1 / 5.2 — the 'Next' naming mirrors Qwen's `qwen4_exp` move of shipping a next-generation architecture under a current version number. README: 'GLM-5.3-Flash starts from a newly trained base model, with its architecture and training recipe redesigned around capability and efficiency.' It is also **the first natively multimodal model in the GLM-5 series**. Distribution differs from every prior GLM record: the primary `GLM-5.3-Flash` repo ships **FP8-quantized weights** (`quantization_config`: e4m3, dynamic activation scaling) with a separate `GLM-5.3-Flash-BF16` repo for the unquantized checkpoint — the reverse of the GLM-5 / 5.1 / 5.2 pattern where bf16 was primary and FP8 the sibling. MIT licence, as with 5.2. Runtime modes: `reasoning_effort` ∈ {low, high, max} (max default) — the low level is new — and **`enable_thinking` is gone**: the template always opens a `<think>` block, so there is no non-thinking mode. `clear_thinking` now defaults to false, i.e. **full reasoning history is preserved by default**.

## 数据源

- <https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/config.json>
- <https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/chat_template.jinja>
- <https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/tokenizer_config.json>
- <https://huggingface.co/zai-org/GLM-5.3-Flash/raw/main/README.md>
- <https://arxiv.org/pdf/2602.15763>
- <https://z.ai/blog/glm-5.3-flash>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 45 |
| 隐藏维度 | 4096 |
| 上下文窗口 | 1048576 |

**上下文说明：** 1,048,576 native, carried over from GLM-5.2's 1M window. No YaRN or other scaling block is documented — the window is native. Long-context serving cost is the stated design driver: 'we introduce a hybrid architecture combining sparse and linear attention, sharply reducing long-context serving costs while preserving precise long-context capabilities'.

### 注意力（hybrid）

| | |
|---|---|
| 变体 | hybrid |
| 头数 | 64 |
| KV 头数 | [Unknown/Not Disclosed] |
| 头维度 | [Unknown/Not Disclosed] |

**RoPE：** type=`none`, base=`[Unknown/Not Disclosed]`

**MLA 特有字段：**

| | |
|---|---|
| kv_lora_rank | 512 |
| q_lora_rank | 1536 |
| qk_nope_head_dim | 256 |
| qk_rope_head_dim | 0 |
| v_head_dim | 256 |

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `kda_linear_attention` | `linear_attention` | 64 | 64 | 128 | Not applicable — linear attention carries position implicitly in its recurrent state. | **Z.AI adopts Kimi Delta Attention.** `config.text_config.linear_attn_config` = {num_heads: 64, head_dim: 128, short_conv_kernel_size: 4, gate_lower_bound: -5.0}, and the layer list is literally named `kda_layers`. This is the first time in this repo that a KDA-family linear attention appears outside Moonshot's own models (Kimi Linear → Kimi K3). `gate_lower_bound=-5.0` bounds the decay gate from below, capping how fast the recurrent state can be forgotten. 34 of 45 layers. |
| `dsa_mla` | `sparse_softmax_attention` | 64 | [Unknown/Not Disclosed] | 256 | **NoPE** — `mla_use_nope: true` with `qk_rope_head_dim: 0` and `qk_nope_head_dim: 256`. GLM's MLA path drops rotary position encoding entirely, relying on the interleaved KDA layers to carry position. This is the same choice Kimi K3 made and the opposite of Qwen3.8-Flash-Next, which tested NoPE and rejected it for post-training generation behaviour. | MLA with DSA sparsification (config layer type `deepseek_sparse_attention`). Down-projections `kv_lora_rank=512` / `q_lora_rank=1536` (narrower q path than GLM-5.2's 2048), `v_head_dim=256`. 11 of 45 layers. |

**层模式：** (K,K,K,S)×11 + K with K=kda_linear_attention, S=dsa_mla. `config.text_config.layer_types` is 34 `linear_attention` + 11 `deepseek_sparse_attention`, with the sparse layers at indices 3, 7, 11, … 43 and a trailing KDA layer at 44. The same **3:1 linear-to-full cadence** Qwen uses in its hybrid line and Kimi K3 uses for KDA:Gated-MLA — three vendors independently converged on 3:1.

**注意力补充说明：** Three separate efficiency mechanisms compose in this stack: 3:1 KDA linear attention (constant-state token mixing on 34 layers), NoPE MLA (no rotary, low-rank KV) on the remaining 11, and key-pooled DSA on top of those 11. `head_dim` is set to 0 in the config because neither path uses the plain per-head dim.

**稀疏注意力：**

| | |
|---|---|
| 类型 | `dsa` |
| 保留条目数（top-k） | 2048 |
| Indexer 头数 | 32 |
| Indexer 头维度 | 128 |
| KV 压缩比 | 4 (indexer keys pooled 4:1 before scoring — `index_kpool=4`, `index_kpool_compress=true`) |

**选择规则：** Top-k by lightning-indexer score, but over **pooled key blocks** rather than individual tokens: `index_kpool=4` with `index_kpool_compress=true` compresses the key sequence 4:1 before scoring, and `index_kpool_always_select_tail=true` forces the trailing (incomplete) block to always be selected.

**训练配方：** [Unknown/Not Disclosed] — the model is described as starting from a newly trained base, so DSA is presumably trained in rather than retrofitted, but no recipe is given for either the indexer or the key-pooling.

_说明：_ **This is the same idea Qwen shipped as QSA, appearing at another vendor within days.** GLM-5.2's answer to DSA's residual O(L²) indexer cost was cross-layer index sharing (IndexShare); GLM-5.3-Flash's answer is within-layer key compression — which is precisely the trade Qwen's Qwen3.8-Flash-Next report argued for, on the grounds that cross-layer sharing weakens in hybrid stacks where full-attention layers are separated by linear-attention layers. GLM-5.3-Flash *is* such a hybrid stack, and it switched sides accordingly: `index_share_for_mtp_iteration=true` remains (index reuse into MTP steps), but the per-layer `indexer_types` Full/Shared partition of GLM-5.2 is gone — every one of the 11 sparse layers computes its own selection. See [qsa](../../docs/glossary/qsa.md) and [indexshare](../../docs/glossary/indexshare.md).

### FFN（hybrid）

**Dense 中间维度：** `12288`

**MoE：**

| | |
|---|---|
| 可路由专家数 | 288 |
| 每 token 激活专家数 | 8 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Auxiliary-loss-free routing (`topk_method='noaux_tc'`) with sigmoid affinity scoring, `routed_scaling_factor=2.5`, `norm_topk_prob=true`, `n_group=1` / `topk_group=1`, `moe_router_dtype='float32'` — the GLM-5 line's routing carried over unchanged. Expert count rises 256 → **288** while per-expert width stays 2048 and top-k stays 8, so sparsity increases (8/288 ≈ 2.8% vs 8/256 = 3.1%). A `router_aux_loss_coef=0.001` key is also present alongside `noaux_tc`; under aux-loss-free routing this coefficient is not the primary balancing mechanism.

**层划分：** First 3 of 45 layers are dense FFN (intermediate_size=12288); the remaining 42 are MoE. `first_k_dense_replace=3`, and the config also enumerates `mlp_layer_types` (3 `dense` + 42 `sparse`). Note the dense layers coincide with KDA layers 0-2, so the bottom of the stack is linear-attention + dense-FFN throughout.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU with **clamping** — `swiglu_limit: 10.0`, present in both the text config and the vision config. This is the same guard DeepSeek-V4 introduced as SwiGLU Clamping and that Qwen3.8-Flash-Next explicitly reports *not* needing; GLM adopts it here. |
| 归一化 | RMSNorm, `rms_norm_eps=1e-05`. `attention_bias=false` on the text side; the vision encoder sets `attention_bias=true`. |

**Embedding 说明：** `tie_word_embeddings=false`, `vocab_size=154880` — the GLM-5 line's vocabulary, unchanged, now carrying multimodal control ids: image 154854, video 154855, image_start/end 154830/154831, video_start/end 154832/154833. Three EOS ids (154820 / 154827 / 154829) and `pad_token_id=154820` as before.

### 残差连接

| | |
|---|---|
| 类型 | `mhc` |
| 扩展因子（n_hc） | 4 |
| 求解迭代数 | 20 |
| 动态参数化 | `[Unknown/Not Disclosed]` |

**约束：** Manifold constraint via Sinkhorn-Knopp projection onto doubly stochastic matrices, `hc_eps=1e-06`.

_说明：_ **Z.AI adopts DeepSeek-V4's Manifold-Constrained Hyper-Connections.** `mhc: true`, `hc_mult: 4` (4× widened residual stream), `hc_sinkhorn_iters: 20`, `hc_eps: 1e-06`. README: 'The model also adopts Manifold-Constrained Hyper-Connections (mHC) to further improve scaling efficiency.' The FP8 `modules_to_not_convert` list confirms the implementation ships per-layer `hc_attn_base` / `hc_attn_fn` / `hc_attn_scale` and `hc_ffn_*` tensors, all held out of quantization, plus a `hyper_connection` module — i.e. a separate mHC block for the attention and FFN sublayers of every layer, matching DeepSeek-V4's structure. Whether the read/write operators are data-dependent (as in mHC's dynamic form) is not stated. This is the **second vendor to ship mHC**, and it lands the same month Qwen shipped Gated Residual — a third design in the same widened-residual family that deliberately drops the Sinkhorn-constrained mixing operator GLM keeps here.

### 辅助模块

**MTP layer**

| | |
|---|---|
| 用途 | `multi_token_prediction / speculative_decoding` |
| 是否随权重发布 | `True` |

**结构：** `num_nextn_predict_layers=1`, parameter-shared MTP as in the GLM-5 line.

**启用方式：** [Unknown/Not Disclosed] — README links SGLang / vLLM / TokenSpeed / KTransformers recipes rather than printing flags.

_说明：_ `index_share_for_mtp_iteration=true` carries over from GLM-5.2: the DSA top-k selections are reused across MTP speculative-decoding iterations rather than recomputed per step.

### 并行 / 基础设施

[Unknown/Not Disclosed]. The model card defers to the GLM-5 family report (arXiv 2602.15763), which predates this architecture.

## 训练

| | |
|---|---|
| 优化器 | [Unknown/Not Disclosed] for GLM-5.3-Flash specifically. The GLM-5 family report documents Muon with Z.AI's 'Muon Split' per-head adaptation; whether that carries into the redesigned recipe is not stated. |
| 训练总 token 数 | 30T (multimodal pre-training corpus; README: 'our latest 30T-token multimodal pre-training corpus') |

**学习率调度：** [Unknown/Not Disclosed]

**数据配比说明：** The one concrete pre-training disclosure is the corpus size: a **30T-token multimodal corpus**, described as 'our latest'. No modality split, no domain mix, no curriculum. The model is explicitly a fresh base: 'GLM-5.3-Flash starts from a newly trained base model, with its architecture and training recipe redesigned around capability and efficiency.' The efficiency claim is the headline: 320B total / 18B active, outperforming GLM-5.2 'across benchmarks and real-world workloads at one-tenth the price, while approaching Claude Opus 4.8 on coding and agentic benchmarks'. No benchmark table is inlined in the model card (results are shipped as an image), so no numeric deltas are recorded here — see open_questions.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | [Unknown/Not Disclosed] |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ `num_nextn_predict_layers=1`, parameter-shared, as in the GLM-5 line.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking / reasoning_effort=max` | Default, and unconditional — the template resolves `effective_reasoning_effort` before any thinking check and emits `<|system|>Reasoning Effort: Max` as the prompt prefix. Unlike GLM-5.2, the effort line is no longer guarded by `enable_thinking`, because there is no `enable_thinking`. | Deepest reasoning level. |
| `thinking / reasoning_effort=high` | `reasoning_effort="high"`. The template accepts `'low'` and `'high'` and silently falls back to `max` for anything else. | Intermediate reasoning level. |
| `thinking / reasoning_effort=low` | `reasoning_effort="low"`. **New in 5.3-Flash** — GLM-5.2 accepted only {high, max}. | Cheapest reasoning level, extending the effort axis downward as the model targets Flash-tier cost. |
| `preserved thinking (default ON)` | Default. `clear_thinking` now defaults to `false` (`clear_thinking if clear_thinking is defined else false`), so `<think>` blocks from the entire history are retained unless the caller passes `clear_thinking=true`. GLM-5.2's default was the opposite — latest-turn-only. | Full multi-turn reasoning carryover by default. The same default flip Qwen made with `preserve_thinking` in the Qwen3.8 generation, arrived at independently and expressed through the inverse-polarity kwarg. |

- **`thinking / reasoning_effort=max`**
    - Kwargs：`reasoning_effort=max`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`
- **`thinking / reasoning_effort=high`**
    - Kwargs：`reasoning_effort=high`
- **`thinking / reasoning_effort=low`**
    - Kwargs：`reasoning_effort=low`
- **`preserved thinking (default ON)`**
    - Kwargs：`clear_thinking=false`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<tool_call>` |
| 结束 token | `</tool_call>` |
| 参数编码方式 | GLM-line XML-like format with per-arg key/value blocks and tool schemas declared as JSON in a `<tools>` system block. The template adds a `tool_references_to_response` macro that expands a `tool_reference` back into a full `<tool_response><tools>…</tools></tool_response>` payload — the MCP-style lazy tool-loading mechanism introduced in GLM-5.1, now with an explicit rehydration path. |

_说明：_ The README links SGLang / vLLM / TokenSpeed / KTransformers cookbooks rather than printing parser flags.

### 进阶

**自蒸馏：** [Unknown/Not Disclosed]

**混合精度：** [Unknown/Not Disclosed] for training. Notably the **primary released checkpoint is FP8** (e4m3, dynamic activation scaling) with bf16 shipped separately as `GLM-5.3-Flash-BF16`, inverting the GLM-5 / 5.1 / 5.2 convention.

### 量化（发布权重）

| | |
|---|---|
| 权重格式 | `FP8 (e4m3)` |
| 激活格式 | `dynamic per-tensor scaling (`activation_scheme: dynamic`)` |
| 方法 | `[Unknown/Not Disclosed] — the config records the released format but not whether it came from QAT or post-hoc conversion. Z.AI used INT4 QAT during SFT for GLM-5; no equivalent statement is made here.` |

**作用范围：** Backbone linear layers. Held out of quantization (`modules_to_not_convert`): the full mHC apparatus (`hyper_connection`, per-layer `hc_attn_base/fn/scale`, `hc_ffn_base/fn/scale`), all KDA state-path tensors (`A_log`, `dt_bias`, conv1d kernels, the a/b/f/g low-rank projections, `o_norm`), every layernorm, `lm_head`, `model.embed_tokens`, `mapping_proj`, and the `attn_mha` / `attn_mqa` paths.

**所处阶段：** Released-checkpoint format; the primary repo ships FP8 and `GLM-5.3-Flash-BF16` ships the unquantized weights.

_说明：_ The exclusion list is itself informative: it is a precise inventory of the components Z.AI considers numerically fragile — the widened-residual mHC operators and the linear-attention recurrent state path, exactly the two newest parts of the architecture.

**稳定性 trick：** Three guards visible in the config, all borrowed rather than invented: `swiglu_limit=10.0` (SwiGLU clamping, from DeepSeek-V4), `moe_router_dtype='float32'` (carried from GLM-5.2), and `gate_lower_bound=-5.0` on the KDA decay gate. The mHC Sinkhorn projection (`hc_sinkhorn_iters=20`) is also a stability-bearing constraint. No narrative stability discussion is published for this model.

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `native_early` |

**融合方式说明：** **The first natively multimodal model in the GLM-5 series** (README). Vision tokens are inlined into the shared backbone via dedicated control ids (`<|begin_of_image|>` / `<|image|>` / `<|end_of_image|>` and the video equivalents), and `vision_config.out_hidden_size=4096` matches the LM hidden size. A `projection_intermediate_size=10240` indicates an MLP projector between encoder and backbone rather than direct dimension matching. Note the HF `pipeline_tag` is still `text-generation` despite the multimodal class and processor config — a metadata lag, not a capability statement.

### 视觉编码器

| | |
|---|---|
| 架构 | ViT (`vision_config.model_type = glm5_next_vision`), 24 layers, `attention_bias=true`, SwiGLU with the same `swiglu_limit=10.0` clamp as the text side. Fixed `image_size=448` rather than the native-resolution approach Qwen and Moonshot use. |
| 层数 | 24 |
| 隐藏维度 | 1024 |
| 中间维度 | 4096 |
| 头数 | 16 |
| patch 大小 | 14 |
| 输入通道数 | 3 |
| 输出维度 → LM | 4096 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 2 |

_说明：_ `hidden_act=silu`, `rms_norm_eps=1e-05`, `projection_intermediate_size=10240`. A compact encoder relative to the models it sits alongside (Qwen3.8's is 27 layers / 1152 hidden; Kimi's MoonViT-V2 is trained from scratch at larger scale), consistent with the Flash-tier cost target.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 154854 |
| video_token_id | 154855 |
| vision_start_token_id | 154830 |
| vision_end_token_id | 154831 |

## 待解问题（open_questions）

- **No numeric benchmark table is published in the model card** — results ship only as a rendered image (`bench_53.png`), so no GLM-5.3-Flash vs GLM-5.2 deltas are recorded in this extraction. The card's prose claims are: outperforms GLM-5.2 across benchmarks and real-world workloads at one-tenth the price, and approaches Claude Opus 4.8 on coding and agentic benchmarks. If Z.AI publishes a text table (as it did for 5.2), re-extract.
- **The chat template handles audio but nothing else does.** `emit_audio()` renders audio control tokens, yet there is no audio encoder in the config, no audio token id, and no audio claim in the README. Whether this is forward-looking scaffolding or an undocumented capability is unresolved.
- Post-training is entirely undisclosed — no SFT, no RL algorithm, no reward design, no agentic-environment description, despite agentic capability being the headline claim.
- Optimizer and training recipe for the redesigned architecture are undisclosed. The model card defers to the February GLM-5 report, which predates this architecture and cannot cover it. Given how much changed (KDA, NoPE MLA, mHC, key-pooled DSA), the deferral leaves the entire optimization story unknown.
- Whether the FP8 primary checkpoint came from quantization-aware training or post-hoc conversion is not stated. Z.AI used INT4 QAT during SFT for GLM-5, so a QAT path would be in character, but `training.quantization.method` is recorded UNKNOWN rather than assumed.
- mHC's read/write operators may be static or data-dependent; the config exposes only `mhc`, `hc_mult`, `hc_sinkhorn_iters` and `hc_eps`, so `dynamic_parameterization` is UNKNOWN. DeepSeek-V4's own records would predict dynamic, but that is a cross-model prior, not evidence.
- The 30T-token corpus is described as multimodal but no text/image/video split is given, and it is not stated how it relates to the corpus behind GLM-5 / 5.2.
- HF `pipeline_tag` is `text-generation` while the model is natively multimodal with a processor config. Treated as vendor metadata lag; worth re-checking if downstream tooling routes on the tag.
- GLM-5.3-Flash is a **Flash-tier model with no full-size sibling released** — there is no GLM-5.3. Whether the `glm5_next` architecture will carry a flagship, and whether this Flash release is functioning as a public preview the way Qwen3.8-Flash-Next does for Qwen4, is not stated.
- Cached blog.html at z.ai/blog/glm-5.3-flash is a client-side-rendered SPA shell (0 characters of extractable text), so blog content was unavailable at extraction time.

---

_由 `data/extracted/glm-5.3-flash.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
