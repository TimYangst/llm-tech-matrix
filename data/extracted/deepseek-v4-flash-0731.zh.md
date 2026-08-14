# DeepSeek-V4-Flash-0731

> English: [deepseek-v4-flash-0731.md](./deepseek-v4-flash-0731.md)

*Schema 版本: 7*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | DeepSeek |
| 发布时间 | 2026-07 |
| 开放程度 | 开放权重 |
| 总参数量 | 284B |
| 激活参数量 | 13B |

**变体策略（variant policy）：** The official (non-preview) DeepSeek-V4-Flash checkpoint, superseding the April 2026 preview — README: 'DeepSeek-V4-Flash-0731 is the official release of DeepSeek-V4-Flash, superseding the preview version, with substantially enhanced agentic capabilities.' Two policy changes vs the preview. (1) SPECULATIVE DECODING IS NOW PART OF THE CHECKPOINT: 'It has the same model structure as DeepSeek-V4-Flash-DSpark, i.e. it comes with a speculative decoding module attached' — the draft weights ship in the same repo (SGLang docs explicitly say not to set --speculative-draft-model-path), collapsing what was a separate -DSpark sibling into the default release. (2) REASONING EFFORT IS NOW A NAMED API PARAMETER with three levels — `reasoning_effort` ∈ {low, high, max} — replacing the preview's prose-level Non-think / Think High / Think Max description; orthogonally, `thinking_mode` ∈ {thinking, chat} switches reasoning on and off. Still no separate Math / Coder / VL siblings. DeepSeek-V4-Pro remained in preview at the time of this release ('the V4-Pro official release will follow soon').

## 数据源

- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/tokenizer_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/generation_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/encoding/README.md>
- <https://arxiv.org/pdf/2606.19348>
- <https://arxiv.org/pdf/2607.05147>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 43 |
| 隐藏维度 | 4096 |
| 上下文窗口 | 1048576 |

**上下文说明：** 1M-token user-facing context (config.max_position_embeddings=1048576; tokenizer_config.model_max_length=1048576) — unchanged from the preview. The 0731 README's local-deployment guidance recommends a maximum OUTPUT length of 384K tokens for the `high` and `max` reasoning-effort levels (the preview README phrased the same number as a recommended context window for Think Max).

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 1048576 |
| 扩展最大长度 | 1048576 |
| 倍率 | 16.0 |
| RoPE 原始最大长度 | 65536 |

_说明：_ Byte-identical rope_scaling to the preview (type=yarn, factor=16, original_max_position_embeddings=65536, beta_fast=32, beta_slow=1, rope_theta=10,000; compressed-KV branches use compress_rope_theta=160,000). No re-pre-training occurred, so the 4K → 16K → 64K → 1M curriculum described in the V4 technical report still applies.

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
  "type": "yarn",
  "factor": 16,
  "original_max_position_embeddings": 65536,
  "beta_fast": 32,
  "beta_slow": 1,
  "compress_rope_theta": 160000,
  "partial_rotary_factor": "64/512 = 0.125 (paper Section 2.3.3 'Partial Rotary Positional Embedding'; unchanged from the preview)"
}
```

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `sliding_window_attention` | `sliding_window` | 64 | 1 | 512 | Partial RoPE on last 64 dims of Q/K (qk_rope_head_dim=64). | Unchanged from the preview. Pure SWA (no KV compression) at the first 2 layers (config.compress_ratios[0]=0, [1]=0), sliding window n_win=128 (config.sliding_window=128) — the V4-Flash-specific deviation from V4-Pro, which uses pure HCA at layers 0-1. The DSpark draft backbone also uses sliding-window attention of 128 (DSpark paper §5.1), which is consistent with the three trailing compress_ratios=0 entries added in this release. |
| `compressed_sparse_attention` | `other` | 64 | 1 | 512 | Partial RoPE on last 64 dims of Q/K and a -i-position RoPE applied to the last 64 dims of core-attention outputs to preserve relative-position semantics through KV aggregation. | Unchanged from the preview: CSA = compress (m=4, two interleaved softmax-weighted compressors over overlapping windows) + DeepSeek Sparse Attention. Lightning Indexer with n_I_h=64 indexer query heads of head_dim c_I=128 (config.index_n_heads=64, index_head_dim=128) ranks compressed blocks via ReLU(q·K_indexer); top-k=512 compressed entries (config.index_topk=512) feed sparse Multi-Query core attention. Query latent d_c=1024 (config.q_lora_rank=1024); outputs split into g=8 groups (config.o_groups=8) of d_g=1024 (config.o_lora_rank=1024). Supplementary n_win=128 sliding-window branch; per-head learnable attention sink. Used at even-indexed layers 2, 4, ..., 42. |
| `heavily_compressed_attention` | `other` | 64 | 1 | 512 | Same partial RoPE / -i output rotation scheme as CSA. | Unchanged from the preview: HCA compresses the KV cache by m'=128 (non-overlapping, one entry per 128 tokens) with no sparse selection and no lightning indexer (dense attention over all compressed entries). Same Multi-Query core-attention shape as CSA. Used at odd-indexed layers 3, 5, ..., 41. |

**层模式：** Identical to the preview across the 43 transformer layers: [SWA, SWA, CSA, HCA, CSA, HCA, ..., HCA, CSA]. Layers 0-1 pure Sliding Window Attention; from layer 2 onwards CSA(m=4) at even indices and HCA(m'=128) at odd indices, so the stack ends with CSA at layer 42. The ONLY config-level change in this release is the length of config.compress_ratios: 44 entries in the preview → 46 here, with two additional trailing zeros ([..., 4, 128, 4, 0] → [..., 4, 128, 4, 0, 0, 0]). Reading: the preview's single trailing 0 covered the MTP head, while the 0731 checkpoint's three trailing zeros cover the DSpark parallel draft backbone, which the DSpark paper §5.1 describes as 'three MoE layers with mHC and a sliding window attention of 128' — uncompressed, hence compress_ratio 0.

**稀疏注意力：**

| | |
|---|---|
| 类型 | `csa+hca` |
| 保留条目数（top-k） | 512 |
| Indexer 头数 | 64 |
| Indexer 头维度 | 128 |
| KV 压缩比 | 4 (CSA) / 128 (HCA) |

**选择规则：** CSA layers: top-k by lightning indexer over COMPRESSED entries. HCA layers: no selection — dense attention over heavily compressed entries.

**训练配方：** Unchanged from the preview — no re-pre-training occurred. First 1T tokens dense; sparse attention introduced at the 64K sequence-length stage.

_说明：_ Byte-identical indexer configuration to the preview (index_n_heads=64, index_head_dim=128, index_topk=512). Serving enables an FP4 indexer cache (vLLM `--attention-config '{"use_fp4_indexer_cache": true}'`).

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 6 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Unchanged from the preview. Auxiliary-loss-free routing (config.topk_method='noaux_tc') with SqrtSoftplus affinity scoring (config.scoring_func='sqrtsoftplus'), top-6 routed experts (config.num_experts_per_tok=6) plus 1 always-on shared expert, routed_scaling_factor=1.5, norm_topk_prob=true, no node-limited routing. Sequence-wise balance loss weight 0.0001; noaux_tc bias-update speed 0.001.

**层划分：** Unchanged from the preview: all 43 transformer layers use MoE FFN, with the first 3 (config.num_hash_layers=3) using deterministic Hash routing instead of SqrtSoftplus aux-loss-free routing. Routed-expert weights in FP4 (config.expert_dtype='fp4'); non-expert parameters FP8/BF16. The attached DSpark draft backbone is itself 3 MoE layers with mHC (DSpark paper §5.1), so the shipped checkpoint contains MoE FFNs beyond the 43 target layers.

### 组件

| | |
|---|---|
| 激活函数 | Unchanged from the preview: SwiGLU (config.hidden_act='silu') with SwiGLU clamping — linear component clamped to [-10, 10], gate capped at 10 (config.swiglu_limit=10.0). |
| 归一化 | Unchanged from the preview: RMSNorm (config.rms_norm_eps=1e-6), pre-norm, plus per-query-head and shared-KV-head RMSNorm before core attention, which is what lets V4 skip QK-Clip. The DSpark draft's context-feature injection also applies RMSNorm to the concatenated target-layer hidden states before projection (DSpark paper Eq. 2). |

**Embedding 说明：** tokenizer_config.json is byte-identical to the preview's: PreTrainedTokenizerFast, vocab 129,280, <｜begin▁of▁sentence｜> id=0, <｜end▁of▁sentence｜> id=1 (also pad), model_max_length=1048576, tie_word_embeddings=false. The 0731 encoding/README.md pins the full special-token table: <｜begin▁of▁sentence｜>, <｜end▁of▁sentence｜>, <｜User｜>, <｜Assistant｜>, <｜latest_reminder｜>, <think>/</think>, and the ｜DSML｜ markup token. Supported roles: system, user, assistant, tool, latest_reminder, developer (the developer role is internal to DeepSeek's search-agent pipeline and is rejected by the official API). Quick Instruction tokens unchanged: <｜action｜>, <｜title｜>, <｜query｜>, <｜authority｜>, <｜domain｜>, <｜extracted_url｜>, <｜read_url｜>. NEW in this release: config.dspark_noise_token_id=128799, a reserved vocabulary slot used by the DSpark draft module (the DSpark paper describes the draft input as an anchor-token embedding followed by γ mask-token embeddings; the config key is named 'noise', and the sources do not state the correspondence explicitly).

### 残差连接

| | |
|---|---|
| 类型 | `mhc` |
| 扩展因子（n_hc） | 4 |
| 求解迭代数 | 20 |
| 动态参数化 | `True` |

**约束：** Residual mapping B constrained to the manifold of doubly stochastic matrices (Birkhoff polytope) via 20 Sinkhorn-Knopp iterations. Input mapping A and output mapping C constrained non-negative and bounded via Sigmoid (A = σ(Ã), C = 2·σ(C̃)).

_说明：_ Unchanged from the preview: mHC with n_hc=4 (config.hc_mult=4), Sinkhorn-Knopp t_max=20 (config.hc_sinkhorn_iters=20), tolerance 1e-6, dynamically parameterized mappings. Notably the DSpark draft backbone ALSO uses mHC (DSpark paper §5.1), so the residual topology is shared between target and draft.

### 辅助模块

**DSpark speculative-decoding module**

| | |
|---|---|
| 用途 | `speculative_decoding` |
| 是否随权重发布 | `True` |

**结构：** Semi-autoregressive draft. Parallel backbone: 3 MoE layers with mHC and sliding-window attention of 128, conditioned on the target via DFlash-style KV injection — hidden states from target layers [40, 41, 42] (config.dspark_target_layer_ids) concatenated and projected as H_ctx = RMSNorm(W_c[H^(l1);...;H^(lm)]), then concatenated into every draft layer's keys and values. Shares the target's frozen embedding and LM head. Sequential module: a Markov head adding a first-order transition bias B(x_{k-1}, .) = W1[x_{k-1}]W2 at rank 256 (config.dspark_markov_rank), which restores intra-block dependency and mitigates the suffix acceptance decay of purely parallel drafters. Confidence head: c_k = sigmoid(w^T[h_k; W1[x_{k-1}]]) predicting per-position survival probability. Max block size gamma=5 (config.dspark_block_size).

**启用方式：** vLLM: --speculative-config '{"method":"dspark","num_speculative_tokens":7,"draft_sample_method":"greedy"}'. SGLang: --speculative-algorithm DSPARK with NO --speculative-draft-model-path, since target and draft weights come from the same checkpoint.

_说明：_ Supersedes MTP-1 as DeepSeek's production speculative-decoding baseline: 60-85% faster per-user generation at matched throughput for V4-Flash (arXiv:2607.05147). Verification is confidence-scheduled — a hardware-aware prefix scheduler verifies the full block under light load and only the confident prefix under heavy load, so batch capacity is not spent on tokens with high rejection risk. Published speedups were measured with drafts co-deployed against the PREVIEW targets, not this checkpoint.

### 并行 / 基础设施

Training infrastructure is unchanged from the preview (V4 technical report §3: DualPipe + Expert Parallelism + ZeRO; MegaMoE single-fused EP kernel; hybrid ZeRO bucketing for Muon; two-stage Contextual Parallelism for compressed attention; heterogeneous + on-disk KV cache; TileLang kernels; batch-invariant deterministic kernel library; validated on NVIDIA GPUs and HUAWEI Ascend NPUs). SERVING is where this release changes. DSpark speculative decoding is enabled by a single serving flag and the draft weights come from the same checkpoint: vLLM `--speculative-config '{"method":"dspark","num_speculative_tokens":7,"draft_sample_method":"greedy"}'`, SGLang `--speculative-algorithm DSPARK` with no `--speculative-draft-model-path`. The README's reference vLLM command targets a single 4×GB300 node with `--kv-cache-dtype fp8 --block-size 256 --data-parallel-size 4 --enable-expert-parallel --moe-backend deep_gemm_mega_moe --attention-config '{"use_fp4_indexer_cache": true}'`; the SGLang command uses `--moe-runner-backend flashinfer_mxfp4 --tp 4 --chunked-prefill-size 4096 --swa-full-tokens-ratio 0.1`. Note that the serving default of 7 speculative tokens exceeds the trained maximum block size γ=5 (config.dspark_block_size=5, DSpark paper §5.1).

## 训练

| | |
|---|---|
| 优化器 | Unchanged from the preview (no re-pre-training): Muon for the majority of parameters, AdamW for the embedding module, prediction head, RMSNorm weights, and the static biases + gating factors of mHC. AdamW β1=0.9, β2=0.95, ε=1e-20, weight_decay=0.1; Muon momentum=0.95, weight_decay=0.1, update-RMS rescale 0.18, hybrid Newton-Schulz (10 iterations: 8 with (3.4445, -4.7750, 2.0315) then 2 with (2, -1.5, 0.5)), Nesterov trick. |
| 训练总 token 数 | 32T |

**学习率调度：** Unchanged from the preview: sequence-length curriculum 4K → 16K → 64K → 1M; linear warmup over 2,000 steps to peak LR 2.7e-4, constant for most of training, cosine decay to 2.7e-5; batch size ramping to 75.5M tokens; first 1T tokens dense attention before the sparse-attention curriculum begins at the 64K stage; MTP loss weight 0.3 → 0.1 at LR decay. The 0731 release re-runs POST-training only, and no post-training hyper-parameters are disclosed for it.

**数据配比说明：** Unchanged from the preview — the same 32T V4-Flash corpus (V4 technical report §4.1), since 0731 is a post-training-only refresh. No new pre-training data is reported, and no quantitative percentage breakdown is disclosed for either release.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | 1 |
| 损失权重调度 | MTP loss weight λ=0.3 for most of training, decayed to 0.1 when the main LR decay begins (V4 technical report §4.2.2). Unchanged from the preview. |

_共享模块：_ config.num_nextn_predict_layers=1 is unchanged in the 0731 config, so the V3-style single MTP head is still declared. In production, however, MTP-1 is explicitly the BASELINE that DSpark replaces: the DSpark paper's headline result is measured 'compared to the established production baseline (MTP-1)', reporting 60%–85% faster per-user generation at matched throughput for V4-Flash.

**Fill-in-Middle (FIM)：**

| | |
|---|---|
| 格式 | PSM (Prefix-Suffix-Middle) inherited from DeepSeek-V3 (V4 technical report §4.1). Unchanged from the preview. |
| 比例 | [Unknown/Not Disclosed] |

**其他训练目标：**

- DSpark draft-model objective (arXiv:2607.05147) — the attached speculative-decoding module is trained on the target model's output distributions, not on ground-truth text. Its confidence head is supervised with the analytical per-step acceptance rate c*_k = 1 - ½‖p_draft − p_target‖ (total variation distance between draft and target next-token distributions) and subsequently calibrated. Trained in DeepSeek's internal HAI-LLM framework with hidden-state communication instead of full-vocabulary logit transfer (V ≈ 10^5) to bound memory and inter-worker traffic.

### 对齐

**SFT：** [Unknown/Not Disclosed] — the 0731 README describes the delta only as 'substantially enhanced agentic capabilities' and publishes no post-training details. The V4 technical report covers the preview pipeline; no 0731-specific report has been released.

**RL 方法：** GRPO (Group Relative Policy Optimization) — the preview recipe. The 0731 checkpoint is re-post-trained, but its specific RL recipe, reward design and data are undisclosed. The benchmark table is the only quantitative evidence of the delta, and the jumps are large: Terminal Bench 2.1 61.8 → 82.7, NL2Repo 39.4 → 54.2, Cybergym 38.7 → 76.7, DeepSWE 7.3 → 54.4, Toolathlon-Verified 49.7 → 70.3, Agents' Last Exam 15.8 → 25.2, AutomationBench Public 10.8 → 25.1, DSBench-FullStack 37.0 → 68.7, DSBench-Hard 25.8 → 59.6 — all agentic/coding, all on unchanged weights-architecture, and all now above DeepSeek-V4-Pro (Preview) despite 13B vs 49B activated parameters.

**RLAIF：** `False`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Specialist Cultivation — per-domain SFT | `sft` | Preview-generation pipeline (V4 technical report §5.1.1): per target domain (mathematics, coding, agent, instruction following, …) the V4-Flash base model is fine-tuned on domain-specific data to establish foundational capability, with hyper-parameters aligned to the DeepSeek-V3.2 post-training pipeline. Whether the 0731 re-post-training keeps this exact structure is not disclosed. |
| 2 | Specialist Cultivation — per-domain RL (GRPO) | `rl` | Preview-generation pipeline: each domain specialist optimized with GRPO; rule-based verifiers / unit tests for easy-to-verify tasks, rubric-guided RL judged by a Generative Reward Model (the actor itself, jointly optimized) for hard-to-verify tasks; distinct length penalties and context windows per reasoning-effort level. The 0731 agentic gains are consistent with a substantially expanded agent-domain stage, but the sources do not document it. |
| 3 | On-Policy Distillation (OPD) into a unified model | `distillation` | Preview-generation pipeline (V4 technical report §5.1.2): a single unified model minimizes Σ w_i · D_KL(π_θ ‖ π_E_i) over >10 expert teachers, reverse-KL on student-sampled trajectories with full-vocabulary logit distillation, replacing the mixed-RL stage used in DeepSeek-V3.2. |
| 4 | DSpark draft-module training | `distillation` | New in this release (arXiv:2607.05147). A semi-autoregressive speculative-decoding module is trained against the frozen target and shipped inside the checkpoint. PARALLEL BACKBONE: three MoE layers with mHC and sliding-window attention of 128, conditioned on the target model via DFlash-style KV injection — hidden states from a set of target layers are concatenated and projected, H_ctx = RMSNorm(W_c[H^(l1);…;H^(lm)]), then injected into every draft layer by concatenating along the key/value sequence dimension; config.dspark_target_layer_ids=[40, 41, 42] names those layers. The draft shares the target's (frozen) embedding and LM head, consumes an anchor token followed by γ mask-token embeddings, and emits logits for all block positions in one forward pass. SEQUENTIAL MODULE: a lightweight Markov head restores intra-block dependency, adding a first-order transition bias B(x_{k-1}, ·) = W1[x_{k-1}]W2 factorized at rank r = 256 (config.dspark_markov_rank=256) — this is what mitigates the suffix acceptance decay of purely parallel drafters. An RNN-head variant exists but gave only marginal gains, so Markov is the default. Maximum block size γ = 5 (config.dspark_block_size=5). CONFIDENCE-SCHEDULED VERIFICATION: a per-position confidence head c_k = σ(w^T[h_k; W1[x_{k-1}]]) predicts the conditional probability that draft token k survives verification, feeding a hardware-aware prefix scheduler that verifies the full block under light load and only the confident prefix under heavy load. |

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking / reasoning_effort=low` | `thinking_mode="thinking"` with `reasoning_effort="low"` (the default). encoding/README.md: the effort level is realized purely as a text prefix at the very start of the prompt, before the system message — and for `low` the prefix is NONE, so the encoding is the bare thinking-mode prompt. | Baseline reasoning mode. The assistant turn is framed `<｜Assistant｜><think>{reasoning}</think>{response}<｜end▁of▁sentence｜>`. Note the naming realignment vs the preview: the preview's three modes were Non-think / Think High / Think Max, where 'Think High' was the unprefixed thinking mode; in 0731 that unprefixed mode is called `low`. |
| `thinking / reasoning_effort=high` | `thinking_mode="thinking"` with `reasoning_effort="high"`. Prepends the prompt prefix 'Reasoning Effort: Absolute maximum with no shortcuts permitted. …' (full text in encoding/README.md). | Elevated deliberation. This is exactly the prefix the PREVIEW used for its top mode 'Think Max' (V4 technical report Table 3) — the 0731 release demotes it to `high` and adds a stronger level above it. README recommends a maximum output length of 384K tokens for `high` and `max`. |
| `thinking / reasoning_effort=max` | `thinking_mode="thinking"` with `reasoning_effort="max"`. Prepends the prompt prefix 'Reasoning Effort: Beyond maximum — exhaustive, relentless, and uncompromising. …' (full text in encoding/README.md). | NEW top effort level in this release, strictly above the preview's ceiling. All README §Notes benchmark numbers are reported at `max` with temperature 1.0 / top_p 0.95, using the minimal mode of DeepSeek Harness as the agent framework. README recommends a maximum output length of 384K tokens. |
| `chat (non-thinking)` | `thinking_mode="chat"`. The encoder places `</think>` immediately after `<｜Assistant｜>`, closing the thinking block before generation starts so the model produces content directly. `reasoning_effort` has no effect in this mode. | The preview's 'Non-think' mode, now an explicit encoder parameter rather than a described behaviour. No reasoning block is produced at all. |
| `interleaved thinking (drop_thinking)` | Controlled by the encoder's `drop_thinking` parameter (default true) and AUTOMATICALLY DISABLED when tools are declared on the system or developer message. | Now a documented, named parameter rather than an inferred behaviour. Without tools, `drop_thinking` strips reasoning content from assistant turns before the last user message, so only the final assistant turn keeps its `<think>` block. With tools, it is force-disabled and every turn retains its reasoning, 'because tool-calling conversations require full context for the model to track multi-step reasoning across tool calls'. Matches the preview's Figure 7a/7b behaviour, now with an explicit knob. |

- **`thinking / reasoning_effort=low`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=low`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95 for agentic scenarios; 1.0 otherwise`
- **`thinking / reasoning_effort=high`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=high`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95 for agentic scenarios; 1.0 otherwise`
- **`thinking / reasoning_effort=max`**
    - Kwargs：`thinking_mode=thinking`, `reasoning_effort=max`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95`
- **`chat (non-thinking)`**
    - Kwargs：`thinking_mode=chat`
    - 推荐采样参数：`temperature=1.0`, `top_p=0.95 for agentic scenarios; 1.0 otherwise`
- **`interleaved thinking (drop_thinking)`**
    - Kwargs：`drop_thinking=true`

**Tool-call 协议：**

| | |
|---|---|
| 格式 | `xml-like` |
| 起始 token | `<｜DSML｜tool_calls>` |
| 结束 token | `</｜DSML｜tool_calls>` |
| 参数编码方式 | Inside the wrapper, one `<｜DSML｜invoke name="$TOOL_NAME">` block per call, containing one `<｜DSML｜parameter name="$PARAMETER_NAME" string="true|false">$PARAMETER_VALUE</｜DSML｜parameter>` block per argument. The `string` attribute is the type discriminator: `string="true"` means the value is a raw, unescaped string; `string="false"` means the value is JSON-encoded (numbers, booleans, arrays, objects). This is the mechanism behind the paper's claim that XML replaces JSON to mitigate string-escape failures — free-form string arguments never get JSON-escaped. Multiple `invoke` blocks may appear in a single `tool_calls` wrapper for parallel calls. Tool results come back inside `<tool_result>{result_json}</tool_result>` within a user message, and when several results are present they are sorted by the order of the corresponding tool_calls in the preceding assistant message. |

_说明：_ Fully pinned by encoding/README.md in this release (the preview extraction had to record end_token as UNKNOWN and defer argument encoding to the paper). Tools are declared OpenAI-style on the system or developer message; the encoder then injects a '## Tools' schema block with the literal grammar plus the tool definitions JSON into the prompt. The prompt block also carries the ordering rule: with thinking enabled, complete reasoning must be emitted inside `<think>…</think>` BEFORE any tool calls or final response. Declaring tools additionally force-disables `drop_thinking` (see inference modes). Still no Jinja chat template — the reference implementation is `encoding/encoding_dsv4.py` (`encode_messages`, `parse_message_from_completion_text`), and the README warns that the parser handles only well-formed output and does no error recovery. No `--tool-call-parser` flag is published; vLLM's V4-Flash recipe advertises tool_calling + reasoning support.

### 进阶

**自蒸馏：** Two layers of intra-family distillation in this checkpoint. (1) Target model: multi-teacher On-Policy Distillation consolidating >10 domain-specialist V4-Flash variants into one unified model via reverse KL on student-sampled trajectories with full-vocabulary logit distillation (preview recipe; the 0731 re-post-training presumably repeats it, but this is not documented). (2) Draft model: the DSpark module is trained against the frozen V4-Flash target's output distributions, with its confidence head supervised by the analytical per-step acceptance rate derived from the draft-vs-target total variation distance.

**混合精度：** Unchanged from the preview. Pre-training in FP8 (V3-inherited framework). Post-training FP4 QAT (MXFP4) for (a) MoE expert weights — FP32 master weights quantized to FP4 then dequantized losslessly to FP8 for compute, backward via STE — and (b) the Query-Key path of CSA's lightning indexer, cached/loaded/multiplied entirely in FP4 with index scores further quantized FP32→BF16. KV cache: BF16 for RoPE dimensions, FP8 for the rest. config.expert_dtype='fp4'; config.quantization_config unchanged (quant_method=fp8, fmt=e4m3, scale_fmt=ue8m0, weight_block_size=[128,128], activation_scheme=dynamic). Serving flags corroborate the recipe: vLLM `--kv-cache-dtype fp8` with `use_fp4_indexer_cache: true`, SGLang `--moe-runner-backend flashinfer_mxfp4`. DSpark draft weights follow the same target-model precision regime (its backbone is MoE layers with mHC).

### 量化（发布权重）

| | |
|---|---|
| 权重格式 | `mxfp4` |
| 激活格式 | `fp8-e4m3 (config.quantization_config.activation_scheme='dynamic', scale_fmt='ue8m0')` |
| 方法 | `qat` |
| 粒度 | weight_block_size 128x128 FP8 blocks, each absorbing 1x32 FP4 sub-block scales |

**作用范围：** MoE expert weights (config.expert_dtype='fp4') plus the Query-Key path of CSA's lightning indexer, whose QK activations are cached, loaded and multiplied entirely in FP4 with index scores further quantized FP32→BF16. Non-expert parameters remain FP8/BF16. KV cache: BF16 for RoPE dimensions, FP8 for the rest.

**所处阶段：** Post-training FP4 QAT: FP32 master weights quantized to FP4 then dequantized losslessly to FP8 for compute, backward via straight-through estimator. Inference and RL rollout both use native FP4 weights.

_说明：_ Shipped checkpoint is labelled 'FP4 + FP8 Mixed'.

**稳定性 trick：** Unchanged from the preview (V4 technical report §4.2.3), since no re-pre-training occurred: (1) Anticipatory Routing — routing indices computed from historical parameters θ_{t-Δt} and cached for use at step t while feature computation uses θ_t, activated dynamically only on a detected loss spike and then reverted (≈20% wall-clock overhead while active); (2) SwiGLU Clamping — linear component ∈ [-10, 10], gate capped at 10 (config.swiglu_limit=10.0).

## 待解问题（open_questions）

- No 0731-specific technical report exists. The README attributes the delta entirely to re-post-training ('substantially enhanced agentic capabilities') and the config confirms an unchanged architecture, but the actual post-training recipe — data, RL environments, reward design, whether the OPD teacher set changed — is undisclosed. All post-training fields therefore carry the preview's documented pipeline with an explicit caveat.
- RESOLVED IN v7 — attached modules now have a structured home. DSpark is a trained, shipped, weight-bearing component (3 MoE layers with mHC + SWA-128, a rank-256 Markov head, a confidence head) that is neither part of the 43-layer backbone nor a training objective, and under v6 it smeared across alignment.stages, objectives.other, ffn.layer_partition and parallelism_notes. v7 adds `architecture.auxiliary_modules[]`; Kimi K3's EAGLE-3 draft was the second independent occurrence that justified it.
- config.compress_ratios length grew 44 → 46 while num_hidden_layers stayed 43. The three trailing zeros are read as the DSpark draft backbone's three uncompressed (SWA-128) MoE layers, which matches DSpark paper §5.1 exactly; but no source states the array's semantics for non-backbone modules, and the preview's single trailing 0 was itself already read as the MTP head. If both the MTP head and the DSpark backbone are present, 43 + 1 + 3 = 47 ≠ 46, so at least one of the two readings is incomplete.
- config.num_nextn_predict_layers=1 is unchanged, yet the DSpark paper positions MTP-1 as the production baseline that DSpark supersedes. Whether the MTP head is still shipped and usable alongside DSpark, or whether the config key is vestigial, is not stated.
- config.dspark_noise_token_id=128799 is not explained in either README or the DSpark paper. The paper describes the draft input as an anchor-token embedding followed by γ mask-token embeddings; the config key name ('noise') is plausibly that mask token, but the sources do not confirm it.
- The serving default `num_speculative_tokens: 7` in the README's vLLM command exceeds the trained maximum block size γ=5 (config.dspark_block_size=5, DSpark paper §5.1). Whether the deployed draft was retrained at a larger γ for the official checkpoint, or whether the serving stack silently clamps, is not documented.
- DSpark's published measurements (60–85% speedup at matched throughput vs MTP-1) were taken with draft models 'co-deployed with the PREVIEW versions of DeepSeek-V4-Flash and DeepSeek-V4-Pro' (§5.1). The 0731 checkpoint attaches a draft module to the re-post-trained target; no acceptance-rate or speedup numbers are published for that pairing.
- SOURCE DRIFT — the technical-report URL used by the existing `deepseek-v4-pro` / `deepseek-v4-flash` manifests, https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf, now returns 404. The same report is on arXiv as 2606.19348 (v1, 26 Apr 2026) and is what this extraction cites. The two preview manifests should be updated to the arXiv URL.
- Benchmark comparison caveat: the README's table compares 0731 against DeepSeek-V4-Pro (PREVIEW), not against an official Pro build, because V4-Pro was still in preview at the time. The claim 'outperforms DeepSeek-V4-Pro despite its far smaller activated parameter count' is therefore a comparison against an older post-training generation, not a like-for-like size comparison.
- Reasoning-effort semantics shifted between releases and the names are not stable across the family: the preview's top mode ('Think Max', prefix 'Absolute maximum with no shortcuts permitted') is the 0731 `high` level, while `max` is a new, stronger prefix. Cross-version benchmark comparisons at 'max' are therefore not comparing the same prompt condition.
- The `developer` role is documented in encoding/README.md as existing for DeepSeek's internal search-agent pipeline and rejected by the official API. What capability it unlocks in the open weights is undisclosed.

---

_由 `data/extracted/deepseek-v4-flash-0731.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
