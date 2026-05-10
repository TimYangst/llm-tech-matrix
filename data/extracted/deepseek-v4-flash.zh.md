# DeepSeek-V4-Flash

> English: [deepseek-v4-flash.md](./deepseek-v4-flash.md)

*Schema 版本: 5*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | DeepSeek |
| 发布时间 | 2026-04 |
| 开放程度 | 开放权重 |
| 总参数量 | 284B |
| 激活参数量 | 13B |

## 数据源

- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/tokenizer_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/generation_config.json>
- <https://huggingface.co/blog/deepseekv4>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 43 |
| 隐藏维度 | 4096 |
| 上下文窗口 | 1048576 |

**上下文说明：** 1M-token user-facing context (config.max_position_embeddings=1048576; tokenizer_config.model_max_length=1048576). Same family-level million-token native support as V4-Pro. README recommends context window ≥384K when using 'Think Max' reasoning mode.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 1048576 |
| 扩展最大长度 | 1048576 |
| 倍率 | 16.0 |
| RoPE 原始最大长度 | 65536 |

_说明：_ Same YaRN scaling configuration as V4-Pro (rope_scaling.type=yarn, factor=16, original_max_position_embeddings=65536, beta_fast=32, beta_slow=1, rope_theta=10,000); CSA/HCA compressed-KV branches use compress_rope_theta=160,000. Trained out to 1M during pre-training via 4K → 16K → 64K → 1M sequence-length curriculum; YaRN aligns RoPE base length with compressed-KV positional anchors rather than extending a short pre-trained window.

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
  "partial_rotary_factor": "64/512 = 0.125 (paper Section 2.3.3 'Partial Rotary Positional Embedding': RoPE applied to last 64 dims of Q/K/V vectors and to the last 64 dims of core-attention outputs with position -i to preserve relative-position semantics through KV-compression aggregation)"
}
```

**混合注意力变体：**

| 名称 | 家族 | Q 头数 | KV 头数 | 头维度 | RoPE | 说明 |
|---|---|---|---|---|---|---|
| `sliding_window_attention` | `sliding_window` | 64 | 1 | 512 | Partial RoPE on last 64 dims of Q/K (qk_rope_head_dim=64). | Pure SWA (no KV compression) used at the first 2 layers only (config.compress_ratios[0]=0, [1]=0). Sliding window n_win=128 (config.sliding_window=128). This is the V4-Flash-specific deviation from V4-Pro, which uses pure HCA at layers 0-1 instead of pure SWA. Paper Section 4.2.1: 'For the first two layers, we use pure sliding window attention'. Same shared-KV MQA shape (n_h=64 queries onto 1 KV head) and grouped output projection as the compressed variants. |
| `compressed_sparse_attention` | `other` | 64 | 1 | 512 | Partial RoPE on last 64 dims of Q/K and a -i-position RoPE applied to last 64 dims of core-attention outputs to preserve relative-position semantics through KV aggregation. | CSA = compress + DeepSeek Sparse Attention. KV cache compressed by m=4 along the sequence dimension via two interleaved softmax-weighted compressors (overlapping windows). Lightning Indexer with n_I_h=64 indexer query heads of head_dim c_I=128 ranks compressed blocks via ReLU(q·K_indexer); top-k=512 compressed entries selected for sparse Multi-Query core attention (vs Pro's top-k=1024). Query down-projection latent d_c=1024 (vs Pro's 1536; config.q_lora_rank=1024). After core attention the n_h=64 outputs are split into g=8 groups (vs Pro's 16; config.o_groups=8); each group projected to d_g=1024 (config.o_lora_rank=1024) then concatenated and projected to hidden_dim=4096. Supplementary sliding-window branch with n_win=128 uncompressed KV entries for local fine-grained dependencies. Attention sink (per-head learnable logit) added to softmax denominator. Used at layers 2, 4, 6, ..., 42 (even-indexed layers from 2 onwards) per config.compress_ratios. |
| `heavily_compressed_attention` | `other` | 64 | 1 | 512 | Same partial RoPE / -i output rotation scheme as CSA. | HCA = heavier compression, no sparse selection. KV cache compressed by m'=128 (non-overlapping) into one entry per 128 tokens. Same Multi-Query core attention shape as CSA: n_h=64 query heads from latent d_c=1024, head_dim c=512, sliding-window branch n_win=128, grouped output projection g=8 groups of d_g=1024. No lightning indexer (HCA does dense attention over all compressed entries). Used at layers 3, 5, 7, ..., 41 (odd-indexed layers in the interleaved zone) per config.compress_ratios. |

**层模式：** [SWA, SWA, CSA, HCA, CSA, HCA, ..., HCA, CSA] across 43 layers. config.compress_ratios = [0, 0, 4, 128, 4, 128, ..., 4, 0] (44 entries; final 0 marks the MTP head; the trailing transformer entry at index 42 is 4 = CSA). Layers 0,1 are pure Sliding Window Attention (paper Section 4.2.1: 'For the first two layers, we use pure sliding window attention') - this is the architectural delta from V4-Pro where layers 0,1 use pure HCA. From layer 2 onwards CSA(m=4) and HCA(m'=128) interleave 1:1 with CSA at even-indexed layers 2,4,...,42 and HCA at odd-indexed layers 3,5,...,41 (so the stack ends with CSA at layer 42, not HCA).

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 256 |
| 每 token 激活专家数 | 6 |
| 共享专家数 | 1 |
| 单专家中间维度 | 2048 |

**路由：** Auxiliary-loss-free routing (config.topk_method='noaux_tc') with SqrtSoftplus(·) affinity score (config.scoring_func='sqrtsoftplus'; same V4 family change from V3's Sigmoid). Top-6 routed experts per token (config.num_experts_per_tok=6) plus 1 always-on shared expert (config.n_shared_experts=1). Sequence-wise balance loss preserved with weight 0.0001. Bias-update speed for noaux_tc balancing bias = 0.001. Routed-expert score scaling factor = 1.5 (config.routed_scaling_factor; vs V4-Pro's 2.5). norm_topk_prob=true. Same V4-family removal of routing-target-node constraint (no node-limited routing) as Pro.

**层划分：** All 43 transformer layers use MoE FFN. The first 3 MoE layers (config.num_hash_layers=3) replace SqrtSoftplus aux-loss-free routing with deterministic Hash routing (Roller et al., 2021): target experts of each token determined by a fixed hash of the input token ID. Remaining 40 MoE layers use SqrtSoftplus aux-loss-free routing. Routed-expert weights stored in FP4 (config.expert_dtype='fp4') after post-training FP4 QAT; non-expert parameters use FP8/BF16.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config.hidden_act='silu'; SwiGLU is the gated form). Trained with SwiGLU clamping for stability: linear component clamped to [-10, 10], gate component capped at 10 (config.swiglu_limit=10.0; paper Section 4.2.3). Identical to V4-Pro. |
| 归一化 | RMSNorm (config.rms_norm_eps=1e-6) with pre-norm. Additional RMSNorm on each query head and on the single shared KV head before core attention (paper Section 2.3.3) to prevent attention-logit explosion. With per-head Q/KV RMSNorm in place V4 does not need QK-Clip. Identical to V4-Pro. |

**Embedding 说明：** tie_word_embeddings=false (separate output head). Vocabulary 129,280 (~128K base + special tokens). Inherits the DeepSeek-V3 byte-level BPE tokenizer; tokenizer_config matches V4-Pro byte-for-byte (PreTrainedTokenizerFast, <｜begin▁of▁sentence｜> id=0, <｜end▁of▁sentence｜> id=1=pad, model_max_length=1048576). Family-level V4 special tokens: |DSML| tool-call schema (XML-format invocations replacing JSON to mitigate string-escape failures - paper Table 4); <think>/</think> reasoning markers; Quick Instruction tokens <|action|>, <|title|>, <|query|>, <|authority|>, <|domain|>, <|extracted_url|>, <|read_url|> (paper Table 5). HF release ships no Jinja chat template; encoding via Python module encoding_dsv4.

### 残差连接

| | |
|---|---|
| 类型 | `mhc` |
| 扩展因子（n_hc） | 4 |
| 求解迭代数 | 20 |
| 动态参数化 | `True` |

**约束：** Residual mapping B constrained to the manifold of doubly stochastic matrices (Birkhoff polytope) via 20 Sinkhorn-Knopp iterations. Input mapping A and output mapping C constrained non-negative and bounded via Sigmoid (A = σ(Ã), C = 2·σ(C̃)).

_说明：_ Manifold-Constrained Hyper-Connections (mHC; Xie et al., 2026) - identical configuration to V4-Pro. n_hc=4 (config.hc_mult=4). Sinkhorn-Knopp t_max=20 (config.hc_sinkhorn_iters=20), tolerance hc_eps=1e-6. Doubly-stochastic constraint on B guarantees ∥B∥_2 ≤ 1 (non-expansive); the set is closed under multiplication (deep-stack stability). Mappings dynamically parameterized: static learnable bias plus dynamic input-dependent component generated from RMSNorm(vec(X_l))·W_l.

### 并行 / 基础设施

Same V4-family infrastructure as V4-Pro (paper Section 3): inherited DualPipe + Expert Parallelism + ZeRO foundation; fine-grained EP with MegaMoE single-fused kernel (1.50-1.73x speedup; up to 1.96x on RL-rollout latency); hybrid ZeRO bucketing for Muon (knapsack for dense, flatten-across-experts for MoE; BF16 stochastic-rounding gradient sync); two-stage Contextual Parallelism for compressed attention; heterogeneous KV cache layout (classical block + State Cache for SWA+uncompressed tail); on-disk KV cache for shared-prefix reuse; TileLang DSL with Z3 SMT-assisted formal integer analysis + Host Codegen; bitwise-reproducible batch-invariant deterministic kernels (DeepGEMM in place of cuBLAS; dual-kernel batch-invariant attention). Validated on NVIDIA GPUs and HUAWEI Ascend NPUs. Paper Figure 5 specifically uses the V4-Flash architecture to estimate the theoretical 1.92x EP-overlap speedup of the wave-scheduled scheme.

## 训练

| | |
|---|---|
| 优化器 | Muon (Jordan et al., 2024 / Liu et al., 2025) for the majority of parameters; AdamW for the embedding module, prediction head, all RMSNorm weights, and the static biases + gating factors of mHC modules. Identical hyper-parameters to V4-Pro: AdamW β1=0.9, β2=0.95, ε=1e-20, weight_decay=0.1. Muon momentum=0.95, weight_decay=0.1, RMS-of-update rescale to 0.18. Hybrid Newton-Schulz orthogonalization: 10 iterations, 8 steps with (a,b,c)=(3.4445, -4.7750, 2.0315) for rapid convergence + 2 steps with (2, -1.5, 0.5) to stabilize singular values at 1. Nesterov trick applied. Per-head/per-KV RMSNorm (see components) makes QK-Clip unnecessary. |
| 训练总 token 数 | 32T |

**学习率调度：** Sequence-length curriculum 4K → 16K → 64K → 1M (same as V4-Pro). Linear warmup over the first 2,000 steps to peak LR 2.7e-4 (vs Pro's peak 2.0e-4); constant 2.7e-4 for most of training; cosine decay to 2.7e-5 near the end (vs Pro's cosine decay endpoint 2.0e-5). Batch-size schedule starts small and ramps to a maximum of 75.5M tokens (vs Pro's 94.4M), held constant for most of training. Sparse-attention curriculum: first 1T tokens use dense attention; sparse attention introduced at the 64K sequence-length stage with a short Lightning-Indexer warmup pass before turning on full sparse routing. MTP loss weight 0.3 for most of training, dropped to 0.1 when LR decay starts. Auxiliary-loss-free bias update speed = 0.001, sequence balance loss weight = 0.0001. (Source: paper Section 4.2.2 'DeepSeek-V4-Flash'.)

**数据配比说明：** Same V4-family corpus as V4-Pro (33T for Pro, 32T for Flash; paper Section 1 / Section 4.1). Built on the DeepSeek-V3 corpus and pipeline. Web data filtered to remove batched auto-generated and templated content (model-collapse mitigation). Math and programming corpora remain core; mid-training phase explicitly incorporates agentic data to lift code-agent capability. Multilingual corpus enlarged for long-tail cross-cultural knowledge. Particular emphasis on long-document curation: scientific papers, technical reports, materials with 'unique academic values'. Inherits V3 tokenizer (128K vocab + new special tokens for context construction) and V3 token-splitting + Fill-in-Middle (FIM) strategies. Different from V3, V4 uses sample-level attention masking during pre-training (V3 packed without cross-sample masking). No quantitative percentage breakdown disclosed.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | 1 |
| 损失权重调度 | MTP loss weight λ=0.3 for most of training, decayed to 0.1 when the main LR decay begins (paper Section 4.2.2). Same schedule as V4-Pro. |

_共享模块：_ MTP configuration is identical to DeepSeek-V3 (paper Section 2.1: 'we adopt the same strategy for DeepSeek-V4 series without modification'). config.num_nextn_predict_layers=1 confirms single additional prediction head. Embedding and output-head sharing with the main model and DualPipe co-location follow V3.

**Fill-in-Middle (FIM)：**

| | |
|---|---|
| 格式 | PSM (Prefix-Suffix-Middle) inherited from DeepSeek-V3 (paper Section 4.1). Same as V4-Pro. |
| 比例 | [Unknown/Not Disclosed] |

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** GRPO (Group Relative Policy Optimization)

**RLAIF：** `False`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Specialist Cultivation - per-domain SFT | `sft` | Same V4-family pipeline as V4-Pro: per target domain (mathematics, coding, agent, instruction following, etc.) the V4-Flash base model is fine-tuned on high-quality domain-specific data to establish foundational capability. One specialist per domain. Hyper-parameters closely aligned with the DeepSeek-V3.2 post-training pipeline. |
| 2 | Specialist Cultivation - per-domain RL (GRPO) | `rl` | Each domain specialist optimized with GRPO under domain-specific prompts and reward signals. For easy-to-verify tasks: rule-based verifiers / unit tests. For hard-to-verify tasks: rubric-guided RL data evaluated by a Generative Reward Model (GRM) - actor network functions as the GRM and judging proficiency is jointly optimized with generative capability. Per reasoning-effort level (Non-think / Think High / Think Max) distinct length penalties and context windows are used during RL training. Same recipe as V4-Pro. |
| 3 | On-Policy Distillation (OPD) into a unified model | `distillation` | Single unified V4-Flash trained to minimize Σ w_i · D_KL(π_θ ∥ π_E_i) over >10 expert teachers (paper Section 5.1.2). Reverse KL on student-sampled trajectories (on-policy). Full-vocabulary logit distillation (rather than the variance-prone token-level KL estimate) - enabled at scale via centralized teacher-weight storage with on-demand ZeRO-like sharding, last-layer-hidden-state caching with on-the-fly logit reconstruction, and teacher-index-ordered sample dispatch. Replaces the mixed-RL stage that was used in DeepSeek-V3.2. |

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `non-think` | Default response mode. Output begins directly with '</think> summary' (no thinking tokens emitted). Per paper Section 5.3.1, evaluation context window 8K. | Fast, intuitive responses. Targets routine daily tasks, low-risk decisions. Trained as a separate specialist mode under shorter context window and tighter length penalty during RL. |
| `think-high` | Output framed as '<think> thinking tokens </think> summary'. Per paper Section 5.3.1 evaluation context window 128K. | Conscious logical analysis - slower but more accurate. Trained under longer context window than Non-think and a length-penalty schedule that allows more reasoning tokens. |
| `think-max` | Two ingredients: (1) special instruction prepended to the system prompt ('Reasoning Effort: Absolute maximum with no shortcuts permitted...' - paper Table 3); (2) <think>...</think> output framing. Per paper Section 5.3.1 evaluation context window 384K (README also recommends ≥384K when using Think Max). | Reasoning pushed to its fullest extent. DeepSeek-V4-Flash-Max in benchmarks always denotes V4-Flash under this mode. README: 'DeepSeek-V4-Flash-Max achieves comparable reasoning performance to the Pro version when given a larger thinking budget, though its smaller parameter scale naturally places it slightly behind on pure knowledge tasks and the most complex agentic workflows.' |
| `interleaved-thinking (cross-turn reasoning preservation)` | Behavior of all three reasoning modes when a tool-calling context is detected (paper Figure 7a). Conventional conversational scenarios still discard prior reasoning at each new user turn (paper Figure 7b). | In tool-calling scenarios all reasoning content is preserved across the entire conversation, including across user message boundaries. Enabled by the 1M context window. Same family-level behavior as V4-Pro. |

### 进阶

**自蒸馏：** Yes - multi-teacher On-Policy Distillation (OPD) consolidates >10 domain-specialist V4-Flash variants (each a per-domain SFT+GRPO derivative of the same V4-Flash base) into a single unified V4-Flash via reverse KL on student-sampled trajectories with full-vocabulary logit distillation. Intra-family / self-family distillation rather than cross-model distillation. Same family-level recipe as V4-Pro.

**混合精度：** Pre-training: FP8 (inherits V3 framework). Post-training adds FP4 Quantization-Aware Training (MXFP4) for: (1) MoE expert weights - FP32 master weights quantized to FP4 then dequantized losslessly to FP8 for compute (FP8 E4M3's exponent range absorbs the 1x32 FP4 sub-block scales within a 128x128 FP8 quant block); backward via STE; (2) Query-Key path in CSA's lightning indexer - QK activations cached/loaded/multiplied entirely in FP4. Index scores additionally quantized FP32→BF16 (2x speedup at 99.7% KV recall). Inference and RL rollout use native FP4 weights. KV cache uses BF16 for RoPE dimensions and FP8 for the remaining dimensions. Shipped checkpoint labeled 'FP4 + FP8 Mixed' (README Model Downloads). config.quantization_config: fmt=e4m3, scale_fmt=ue8m0, weight_block_size=[128,128], activation_scheme=dynamic. Identical recipe to V4-Pro.

**稳定性 trick：** Same two V4-family stability tricks as V4-Pro (paper Section 4.2.3 - which describes them for both V4-Flash and V4-Pro). (1) Anticipatory Routing: routing indices computed and applied using historical params θ_{t-Δt} while feature computation uses current params θ_t; pre-computed at step t-Δt and cached for use at step t (overhead bounded to ~20% wall-clock). Activated dynamically only on detected loss spike, then reverted. (2) SwiGLU Clamping: linear component of SwiGLU ∈ [-10, 10], gate component capped at 10 (config.swiglu_limit=10.0). Used throughout the training of both V4-Flash and V4-Pro.

## 待解问题（open_questions）

- FIM rate not restated in V4 paper; recorded as inherited PSM format from V3 with rate=Unknown (V3 used 0.1). Same gap as V4-Pro.
- Pre-training data percentage breakdown (code / math / text / multilingual / long-doc shares of the 32T) is not disclosed - only qualitative descriptions.
- SFT data scale undisclosed for V4-Flash. Paper says pipeline mirrors V3.2 but doesn't restate sample counts.
- Number of OPD teacher models given as '>10' but not exact; per-teacher importance weights w_i qualitative only.
- Hardware platform for V4-Flash actual production pre-training not specified. Paper Figure 5 evaluates the EP scheme's theoretical 1.92x speedup using the V4-Flash architecture, but the production training platform (NVIDIA vs Huawei Ascend NPU) is not stated.
- Pre-training start date and total wall-clock undisclosed.
- Per-mode evaluation context windows (Non-think 8K / Think High 128K / Think Max 384K) - whether trained limits or only eval-time configuration is ambiguous (same gap as V4-Pro).
- DeepSeek-V3.2 (immediate baseline V4 compares against) is not in this repo's extracted set.
- Why first-2-layer attention differs between V4-Flash (pure SWA) and V4-Pro (pure HCA) is not motivated in the paper - both architectures specify it tersely in Section 4.2.1 without ablation.
- Released variants V4-Flash-Base (FP8 Mixed) vs V4-Flash (FP4 + FP8 Mixed) per README Model Downloads - this extraction targets the post-FP4-QAT V4-Flash deployment release; V4-Flash-Base shares architecture but lacks FP4-quantized expert weights.
- config.compress_ratios array length 44 (vs num_hidden_layers=43) - trailing 0 inferred to be the MTP head, not a 44th transformer layer.
- README is byte-identical between V4-Pro and V4-Flash (the same family-level model card serves both); only config.json carries V4-Flash-specific values.

---

_由 `data/extracted/deepseek-v4-flash.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
