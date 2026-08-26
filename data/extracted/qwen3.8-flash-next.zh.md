# Qwen3.8-Flash-Next

> English: [qwen3.8-flash-next.md](./qwen3.8-flash-next.md)

*Schema 版本: 7*

_章节标题、字段名与样板文字译为中文；字段取值保留源材料原文（多为英文），以避免翻译引入偏差。术语解释见 [docs/glossary/](../../docs/glossary/)。_

## 概览

| | |
|---|---|
| 模型家族 | Qwen |
| 发布时间 | 2026-08 |
| 开放程度 | 开放权重 |
| 总参数量 | 125B (plus 51B n-gram embedding tables held off-accelerator, plus 4B MTP module) |
| 激活参数量 | 6B |

**变体策略（variant policy）：** **Despite the 3.8 version number, this is not a Qwen3.8 sibling — it is a Qwen4 architecture preview.** The HF class is `Qwen4ExpForConditionalGeneration` (model_type `qwen4_exp`, i.e. Qwen4-experimental) and the README states it plainly: 'This experimental preview of the architecture that will underpin Qwen4.' The tech report's own title calls it the 'Qwen3.8-Next Architecture'. It shares essentially nothing load-bearing with Qwen3.8-27B / 3.8-2.4T-A95B beyond the vocabulary, the vision encoder and the chat template — the attention modifier, residual topology, embedding strategy and optimizer are all new. Released under a custom `qwen-community-1.0` licence (neither the 27B's Apache-2.0 nor the 2.4T's `qwen3.8-max` terms — three different licences inside one version number). The open-vs-hosted split established with Qwen3.8 continues: README says the hosted **Qwen3.8-Flash** on Qwen Cloud is 'the official version based on Qwen3.8-Flash-Next with more production features, e.g., 1M context length by default, official built-in tools'. Runtime modes are unchanged from Qwen3.8-27B — the chat template is byte-identical apart from a trailing newline (`enable_thinking` on/off, `reasoning_effort` xhigh/medium/low, `preserve_thinking` default ON).

## 数据源

- <https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/config.json>
- <https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/chat_template.jinja>
- <https://huggingface.co/Qwen/Qwen3.8-Flash-Next/raw/main/README.md>
- <https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf>
- <https://qwen.ai/blog?id=qwen3.8-flash-next>

## 架构

### 骨干网络

| | |
|---|---|
| 层数 | 48 |
| 隐藏维度 | 2560 |
| 上下文窗口 | 262144 |

**上下文说明：** Native 262,144 (config.text_config.max_position_embeddings=262144), extensible to 1,000,000 via opt-in static YaRN at serving time. Long-context retrieval is evaluated to 1M in the tech report (RULER 4K-1000K, 8-needle MRCR 128K-1M) and QSA *improves* on full attention at the long end: RULER 512K-1M 90.08 -> 93.00, MRCR 512K 30.66 -> 40.53, MRCR 1M 20.71 -> 26.44.

**上下文扩展：**

| | |
|---|---|
| 方法 | yarn |
| 训练最大长度 | 262144 |
| 扩展最大长度 | 1000000 |
| 倍率 | 4.0 |
| RoPE 原始最大长度 | 262144 |

_说明：_ Same recipe and same mRoPE parameters as the rest of the Qwen 3.x line (mrope_section=[11,11,10], mrope_interleaved=true, partial_rotary_factor=0.25, rope_theta=10,000,000, original_max_position_embeddings=262144). Unlike Qwen3.8-2.4T-A95B, this card DOES ship the full 'Processing Ultra-Long Texts' YaRN block with per-framework override snippets (vLLM / SGLang / TokenSpeed). Note the continued-pretraining sequence length was 256K, so the 262K native window is trained, not extrapolated.

### 注意力（hybrid）

| | |
|---|---|
| 变体 | hybrid |
| 头数 | 24 |
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
| `gated_deltanet` | `linear_attention` | 16 | 16 | 128 | Not applicable - Gated DeltaNet is a linear-attention variant and does not use RoPE; positional information is implicit in its recurrent state update. | Same head geometry as Qwen3.5/3.6/3.8-27B (linear_num_value_heads=48 with linear_value_head_dim=128 -> 6144-dim V state; linear_num_key_heads=16 with linear_key_head_dim=128 -> 2048-dim K state; linear_conv_kernel_dim=4; mamba_ssm_dtype=float32), but with **two formulation changes documented in the tech report §2.1.1**: (1) the output gate is a bounded **sigmoid** rather than the original GDN's SiLU (config: output_gate_type=sigmoid, vs swish in every earlier Qwen 3.x model) — 'we observe consistent improvements across our experiments'; (2) **zero-centered RMSNorm** (inherited from Qwen3-Next) constrains RMSNorm weight growth, and is applied consistently to every RMSNorm in the model. q/k are L2-normalized after a short depthwise causal convolution and SiLU; decay alpha_t = exp(-exp(A)*softplus(W_alpha x + b)) and write strength beta_t = sigmoid(W_beta x). Used in 3 of every 4 layers (36 of 48). Report §2.1.1 ablation at 25B-A3B: the GDN hybrid beats a full-attention Transformer on 8 of 9 benchmarks and an SWA-128 hybrid on 7 of 9 (avg 53.81 vs 49.87 vs 51.15). Kernel: **FlashQLA**, a TileLang fused linear-attention library, 2-3x forward and ~2x backward over the FLA Triton kernel (open-sourced at github.com/QwenLM/FlashQLA). |
| `qwen_sparse_attention` | `sparse_softmax_attention` | 24 | 2 | 256 | Partial mRoPE — 64 of 256 head dims rotated (partial_rotary_factor=0.25), the remaining 192 NoPE. The indexer path applies partial RoPE to 64 of its 128 dims, deliberately matching the core attention's rotary dimension. Report §2.1.1 explicitly REJECTS full NoPE: RoPE and NoPE are indistinguishable during pre-training, but 'the NoPE variant exhibits a substantially higher rate of endless generation after post-training' — a late-stage failure a pre-training-only comparison would have missed. | This layer replaces the plain `gated_attention` of Qwen3.5/3.6/3.8. GQA drops to **24Q:2KV (12:1)** from the 27B's 24Q:4KV (6:1), halving KV width to 2*256=512. Every full-attention layer in both the backbone and the MTP module is a QSA layer; see `attention.sparse_attention` for the sparsification mechanism. Used in 1 of every 4 layers (12 of 48). |

**层模式：** (D,D,D,Q)x12 with D=gated_deltanet, Q=qwen_sparse_attention. config.text_config.layer_types is ['linear_attention' x3, 'full_attention'] repeated 12 times (48 layers: 36 linear + 12 QSA); full_attention_interval=4. README naming: '12 x (3 x (Gated DeltaNet -> MoE) -> 1 x (Qwen Sparse Attention -> MoE))'. The 3:1 cadence is unchanged from every other Qwen 3.x hybrid model; what changed is what sits in the 1.

**注意力补充说明：** Two independent things changed in the attention stack relative to Qwen3.8-27B: the full-attention slot became QSA (sparse), and KV heads halved from 4 to 2. Qwen is the **third vendor in this repo to ship a DSA-lineage sparse attention** after DeepSeek (V3.2-Exp, V4) and Z.AI (GLM-5), and the first to attack the indexer's own asymptotic cost.

**稀疏注意力：**

| | |
|---|---|
| 类型 | `qsa` |
| 保留条目数（top-k） | 2048 |
| Indexer 头数 | 4 |
| Indexer 头维度 | 128 |
| KV 压缩比 | 4 (indexer keys are average-pooled over non-overlapping micro-blocks of r=4 tokens BEFORE positional encoding, so each block gets one content summary and one block-level position — avoiding the averaging of representations at different rotary phases) |

**选择规则：** Top-k over **micro-blocks**, not tokens. A compressed lightweight MQA indexer scores block-level importance I_ib = sum over indexer heads of ReLU(<q_i^h, k_bar_b>), under a block-causal mask (a query may only score blocks it has fully observed). Each query takes the top K_B = ceil(K/r) blocks, which are expanded back to token indices, truncated to the budget K, and unioned with the tokens of the final incomplete block (always included).

**训练配方：** Retrofitted during continued pre-training at 256K sequence length, in two stages. **Stage 1 — dense distillation**: the backbone's full-sequence attention distribution is summed over teacher heads, L1-normalized, then MAX-pooled to block granularity (max rather than mean, to preserve salient token-level signal that averaging would dilute) and distilled into the indexer by KL. Indexer only, 1,000 steps, lr 1e-3, 8 sequences x 256K per step, ~2B tokens. **Stage 2 — sparse training**: the whole backbone trains under the indexer's selection, with the KL loss now computed only over the selected top-K_B blocks and the teacher renormalized within them. 8,000 steps, lr 2.5e-5, 96 sequences x 256K per step, ~200B tokens. The resulting LM-loss curve tracks the full-attention baseline to within ~1e-4.

_说明：_ QSA follows DSA's indexer route (Liu et al. 2025a = DeepSeek-V3.2-Exp) but fixes DSA's residual cost: DSA's indexer is itself O(n^2), whereas compressing the key sequence by r before scoring makes indexing O(n^2/r), so **the indexing cost falls with sequence length**. At 1M context, kernel-level speedups are **7.6x prefill and 4.9x decode** vs dense attention. QSA is not merely loss-neutral: on 8 short-context benchmarks it matches or beats full attention on 7 (avg 75.9 -> 76.8), and it *widens* its lead as context grows. Report §2.1.2 also compares against **IndexShare** (cross-layer index sharing): QSA matches the full-attention RULER baseline at 0.25 relative indexer latency, while IndexShare is still below baseline at 0.5 — the report attributes this to low inter-layer similarity in hybrid stacks, which makes within-layer compression the better fit. A fused QSA kernel computes sparse attention output and the KL loss without materializing intermediates.

### FFN（moe）

**MoE：**

| | |
|---|---|
| 可路由专家数 | 512 |
| 每 token 激活专家数 | 10 |
| 共享专家数 | 1 |
| 单专家中间维度 | 640 |

**路由：** Top-10 over 512 routed experts plus 1 always-on shared expert (README: '10 Routed + 1 Shared'). Classic auxiliary load-balance loss, router_aux_loss_coef=0.001 — the same routing Qwen has used since Qwen3.5, unchanged even in a Qwen4-preview architecture. Uniform 640 width for routed and shared experts (moe_intermediate_size = shared_expert_intermediate_size = 640); total MoE width per token = 11 * 640 = 7040. The MoE **router is deliberately kept on AdamW** while the expert fc1/fc2 use Muon: the report finds Muon on the router exacerbates early-training fluctuation with no late-training gain, and hypothesizes that each router output dimension scores one expert independently, leaving 'no shared linear structure for orthogonalization to exploit'. Expert count is also the knob the n-gram-vocabulary ablations trade against under a fixed parameter budget (report Tab. 8).

**层划分：** Uniform MoE FFN across all 48 layers regardless of attention variant — every block, GDN or QSA, is followed by MoE.

### 组件

| | |
|---|---|
| 激活函数 | SwiGLU (config hidden_act=silu). The SwiGLU fc1 is split into its gate and up halves before Muon orthogonalization (see training.optimizer). |
| 归一化 | **Zero-centered RMSNorm throughout** (inherited from Qwen3-Next), applied consistently to every RMSNorm in the model to constrain weight growth. rms_norm_eps=1e-6, attention_bias=false. Critically, **the model has no conventional pre-normalization layer**: the Gated Residual read (see architecture.residual_connections) already normalizes and gates, so GR *replaces* each block's pre-norm rather than sitting in front of it, and widening the residual stream adds no normalization layer. |

**Embedding 说明：** tie_word_embeddings=false. Token Embedding 248,320 (padded) and LM Output 248,320 (padded); config.vocab_size=248320 — the same padded vocabulary as the whole Qwen 3.x line. Vision-reserved IDs unchanged: image 248056, video 248057, vision_start 248053, vision_end 248054; eos=bos=248044. **The distinctive part is a second embedding system**: a single n-gram embedding layer at layer 2 with a 20,000,000-entry table (config ngram_vocab_size_base=20000000, ngram_size=3, heads_per_ngram=8, ple_embed_dim=2560, ple_conv_kernel_size=4, ple_layer_ids=[2], split_ngram_parts=128, make_ngram_vocab_size_divisible_by=128) carrying 51B parameters that are held off-accelerator. See architecture.auxiliary_modules.

### 残差连接

| | |
|---|---|
| 类型 | `gated-residual` |
| 扩展因子（n_hc） | 4 |
| 求解迭代数 | [Unknown/Not Disclosed] |
| 动态参数化 | `True` |

**约束：** None imposed on a mixing operator, because there is no mixing operator — GR **drops H_res entirely** (the n_r x n_r inter-branch mixing matrix that HC uses and mHC constrains to doubly stochastic). The ablation showed that once read and write are expressive enough, H_res 'brings no significant improvement', and dropping it removes both a full read of the residual state per block (memory traffic, the dominant inference cost of a widened stream) and a constraint-bearing source of instability. Gates are bounded sigmoids throughout, chosen over tanh for both loss and stability.

_说明：_ n_r = 4 branches, with a **separate GR module for the attention block and the MLP block of every layer**. Read: each branch is RMSNorm'd with its own gain, then an elementwise per-branch-per-channel gate G = sigmoid(W_u SiLU(W_d vec(R_hat)/n_r)) is predicted from ALL branches through a low-rank bottleneck of rank d/8 = 320 (config hc_lowrank=320, hc_count=4), and the block input is the mean of the gated branches. Write: a single data-dependent scalar per branch, s = 2*sigmoid(W_w vec(R_hat)/n_r), so R'_i = R_i + s_i*y. This asymmetry is the ablation's central finding — **read granularity matters, write granularity does not**: refining the read from per-branch scalar to per-branch-per-channel helps, the same refinement of the write 'gives almost nothing'. GR is the merger of two prior lines: the widened residual stream of AltUp / Hyper-Connections, and GatedNorm (Qiu et al. 2026), a lightweight elementwise self-gate after RMSNorm found to markedly improve stability — the read the ablation converged on turned out to be exactly GatedNorm applied to the widened stream. Static terms bring no improvement and standard random init suffices (no special HC-style identity init needed). Ablation at 25B-A3B / 560B tokens (report Tab. 5): pre-norm 1.617 loss / 50.91 avg -> mHC static 1.596 / 52.49 -> mHC dynamic 1.594 / 54.47 -> GR 1.590 / 54.66. Note the loss/benchmark disagreement the report highlights: static->dynamic is worth only 0.002 loss but 1.98 accuracy points, while baseline->static is 0.021 loss but 1.58 points. Also compared against **AttnRes** (Kimi K3's residual scheme, report Tab. 6): full AttnRes reaches 1.762 and GR (n_r=4) matches it at 1.762. The residual state supports FP8 storage at inference to contain the memory traffic of carrying 4 branches.

### 辅助模块

**N-gram embedding layer**

| | |
|---|---|
| 用途 | `capacity_scaling — adds parameters outside the backbone at negligible per-token FLOPs, by conditioning memory retrieval on local context (short n-grams ending at each token) rather than token identity alone` |
| 是否随权重发布 | `True` |

**结构：** A single layer at **layer 2** holding **51B parameters** in a 20,000,000-entry table (ngram_size=3, i.e. bigrams/trigrams; heads_per_ngram=8; embed dim 2560; a depthwise conv of kernel 4; split into 128 parts). Tables are **held off-accelerator in host memory and asynchronously prefetched** — deterministic addressing is what makes offloading possible. Layer 2 was chosen specifically so the prefetch overlaps the computation of layer 1.

**启用方式：** Always on — part of the forward pass, not an opt-in serving feature. The 51B is reported separately from the 125B backbone total because it does not occupy accelerator memory.

_说明：_ Placement ablation (report Tab. 7, fixed parameter budget): no depth regime dominates, layers 1-2 are strongest, splitting the budget across multiple layers gives no consistent benefit — one layer suffices, and placement is largely insensitive to the attention mechanism. Vocabulary-scaling ablation (Tab. 9, 20V -> 200V where V=250K): **loss decreases monotonically while downstream accuracy saturates or fluctuates** — one of the report's headline loss/benchmark disagreements. Chinese benchmarks (C-Eval, CMMLU) are the exception, improving consistently with vocabulary size. Under a *fixed* total parameter budget traded against MoE experts (Tab. 8), the loss optimum sits at 10x (25% of params) but downstream shows no clear gain over the MoE-only baseline, leading the report to conclude that 'N-gram embeddings and MoE experts play distinct roles in scaling capacity'. Token normalization, non-uniform allocation across n-gram orders and frequency-based slot partitioning were all tried and gave no consistent gain. The n-gram table runs on Adam with weight decay disabled; its key/value projections are on Muon.

**MTP module**

| | |
|---|---|
| 用途 | `multi_token_prediction / speculative_decoding` |
| 是否随权重发布 | `True` |

**结构：** 1 layer, ~4B parameters, configured as a hybrid module of its own (config.text_config.mtp = {hybrid: true, layer_types: ['full_attention'], num_hidden_layers: 1, rope_theta: 1e7}); mtp_use_dedicated_embeddings=false, so it shares input embeddings with the main model. Its full-attention layer is **also replaced by QSA**.

**启用方式：** [Unknown/Not Disclosed] — the README does not print per-framework speculative-decoding flags; the report evaluates four-step speculative decoding.

_说明：_ Following GLM-5, the MTP module **reuses the QSA top-k indices across speculative-decoding steps** to cut draft-model cost. Report Tab. 4 confirms this is free: mean accepted length under four-step speculative decoding is 4.06 with full attention and 4.07 with QSA (MT-Bench 3.44/3.47, GSM8K 4.19/4.20, MATH 4.29/4.30, HumanEval 4.24/4.26, MBPP 4.12/4.13).

### 并行 / 基础设施

Megatron-LM based (TP + DP with ZeRO-1). Muon forced two infrastructure changes, both described in report §3.1. (1) **Canzona**, a scheduler that decouples logical optimizer assignment from physical parameter layout: Newton-Schulz cost is ~4K*max(A,B)*min(A,B)^2 FLOPs, i.e. cubic in the shorter dimension, so Megatron's equal-element DP partition leaves severe stragglers; an alpha-balanced static partitioner reassigns whole parameters (never cutting inside a tensor) to equalize estimated NS FLOPs across DP ranks, and an asynchronous Micro-Group pipeline reconstructs each Muon-owned matrix via fused All-to-All across TP ranks. ZeRO-1 bucket geometry is preserved so Megatron's Reduce-Scatter/backward overlap still works. (2) After fused-parameter splitting a single layer contributes ~100 sub-matrices, making the optimizer step launch-bound; the whole step is captured in a **CUDA graph**.

## 训练

| | |
|---|---|
| 优化器 | **Muon** (Newton-Schulz orthogonalization of Nesterov-accelerated momentum, mu=0.95) as the main optimizer, with a deliberate parameter-class split. Muon covers the 2D weights that genuinely act as linear maps: attention q/k/v and output projections, GDN input/output projections, routed and shared expert fc1/fc2, and the n-gram key/value projections. **AdamW keeps**: input embeddings, output head, the MoE router (Muon destabilizes it early and adds nothing late — router dimensions are independent per-expert scores with no shared linear structure to orthogonalize), GR's two low-rank projections (very elongated shapes), the GDN decay/beta projections (per-head scalars, i.e. vectors), and the output gates (attention output gate and GDN z projection, where AdamW was on par or slightly better). The n-gram embedding table runs Adam with weight decay disabled. NS uses the **Polar Express** per-step coefficient schedule (minimax-optimal for a given step budget) at **8 iterations** — more than strictly needed for accuracy, chosen because it reduces both the magnitude and frequency of gradient-norm spikes under stress. Update scaled by 0.2*sqrt(max(A,B)) so update RMS is shape-independent; Frobenius-normalization epsilon 1e-14. **Fused parameters are split before orthogonalization** — qkv and the GDN input projection at per-head granularity, SwiGLU fc1 into gate and up halves — because orthogonalizing a concatenation mixes singular directions across unrelated sub-blocks and computes the shape scale from the wrong dimensions. Per-head qkv splitting improved both loss and benchmarks. |
| 训练总 token 数 | [Unknown/Not Disclosed] |

**学习率调度：** [Unknown/Not Disclosed] — the decay schedule is not stated. What IS disclosed is the hyperparameter *selection*: the Qwen3.5-era scaling law for learning rate and batch size was **refitted**, because both architecture and optimizer changed. The new law predicts a larger batch size and a larger learning rate, both verified independently. On a 4T-token budget with a 20-layer 10.8B-A0.89B MoE, moving from the previous recipe's B=12.6M to the predicted optimum B=25.2M is worth 7.2e-3 loss (B=37.7M slightly degrades); loss rises steeply below the predicted optimum and is nearly flat above it. **Batch-size warmup was dropped**: ramping 6.3M -> 25.2M ends no better than starting at the target and costs 18.8% more optimizer steps.

**数据配比说明：** No absolute token count or data mix is disclosed — only ratios against the predecessor. Qwen3.8-Flash-Next-Base is trained on 'roughly a third as many tokens' as the 397B-A17B previous-generation flagship, activating about a third as many parameters per token, for 'about a ninth of the training FLOPs'. Continued pre-training runs at 256K sequence length and is where QSA is introduced (~202B tokens across the two QSA stages). Ablations throughout the report use 25B-A3B MoE proxies (400B tokens @ 4K then 80B @ 32K, or 560B tokens) and a 300 tokens-per-active-parameter budget for the n-gram studies. Base-model results (report Tab. 11, 14 benchmarks): Qwen3.8-Flash-Next-Base beats Qwen3.8-27B-Base on **all 14**, and beats the ~3x larger Qwen3.7-Plus-Base (397B/17B) on 8 of 14, trailing on the rest by at most 2.6 points. Post-trained highlights vs Qwen3.8-27B: DeepSWE 1.1 42.2 -> 58.7, JobBench 33.4 -> 55.7, SWE-bench Multilingual 73.8 -> 81.0, Toolathlon Verified 67.1 -> 73.5, CoWorkBench 70.7 -> 73.9, HLE 30.8 -> 35.9.

### 训练目标（next-token prediction 之外）

**Multi-Token Prediction (MTP)：**

| | |
|---|---|
| 深度（D） | [Unknown/Not Disclosed] — README says 'trained with multi-steps'; four-step speculative decoding is what the report evaluates, but the trained step depth D is not stated (the same gap as every prior Qwen 3.x record). |
| 损失权重调度 | [Unknown/Not Disclosed] |

_共享模块：_ mtp_num_hidden_layers=1, mtp_use_dedicated_embeddings=false (shares input embeddings). Unlike earlier Qwen 3.x configs, the MTP head now has its own structured config block (config.text_config.mtp with hybrid=true, its own layer_types and rope_theta) and is counted separately in the parameter budget at ~4B. See architecture.auxiliary_modules for the module view, including QSA index reuse across draft steps.

### 对齐

**SFT：** [Unknown/Not Disclosed]

**RL 方法：** [Unknown/Not Disclosed]

**RLAIF：** `[Unknown/Not Disclosed]`

**后训练阶段：**

| # | 名称 | 方法 | 描述 |
|---|---|---|---|
| 1 | Continued pre-training — QSA Stage 1 (dense distillation) | `continued_pretraining` | Indexer-only warm-up at 256K sequence length. The backbone's full attention distribution is summed over teacher heads, L1-normalized, max-pooled to micro-block granularity, and distilled into the compressed indexer by KL divergence. 1,000 steps, lr 1e-3, 8 x 256K sequences per step, ~2B tokens. Backbone frozen. |
| 2 | Continued pre-training — QSA Stage 2 (sparse training) | `continued_pretraining` | Backbone and indexer trained jointly under the indexer's block selection; the KL loss is now restricted to the selected top-K_B blocks with the teacher renormalized within them. 8,000 steps, lr 2.5e-5, 96 x 256K sequences per step, ~200B tokens. The LM-loss trajectory tracks the full-attention baseline to ~1e-4. |

**推理模式（runtime 可切换）：**

| 名称 | 触发方式 | 描述 |
|---|---|---|
| `thinking / reasoning_effort=xhigh` | Default mode. The chat_template.jinja is byte-identical to Qwen3.8-27B's (bar a trailing newline): thinking is on unless `enable_thinking=false`, and `reasoning_effort` defaults to `xhigh`, injected as system-message instruction text ('Reasoning effort is set to xhigh. Please think carefully through the task, validate key assumptions, consider plausible alternatives, and prioritize correctness, consistency, and clarity in the final answer.'). Values outside {xhigh, medium, low} raise. | Deepest reasoning setting, for 'complex tasks demanding thorough analysis'. |
| `thinking / reasoning_effort=medium` | `reasoning_effort="medium"`. Injects no instruction text at all — the template leaves reasoning_instructions empty for this level. | 'Balancing accuracy and speed' (README). |
| `thinking / reasoning_effort=low` | `reasoning_effort="low"`. Injects 'Reasoning effort is set to low. Keep your thinking brief and focused, moving directly to the conclusion without unnecessary elaboration.' | 'Efficient reasoning optimizing for speed and cost', with the standard Qwen3.8 caveat that lower effort can raise end-to-end latency in multi-turn agentic tasks via retries. |
| `non-thinking` | chat_template_kwargs={"enable_thinking": False} (or top-level enable_thinking=False on Qwen Cloud). Unlike Qwen3.8-2.4T-A95B, this model KEEPS the non-thinking mode. | Direct response without an explicit reasoning trace. |
| `preserved thinking (default ON)` | Default-on (`preserve_thinking is undefined or ... is true`); pass False to fall back to latest-turn-only interleaved thinking. | Retains <think> blocks from all historical assistant messages. Same rationale as Qwen3.8-27B: decision consistency in agent loops, avoided re-derivation, better KV-cache utilization. |

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
| 参数编码方式 | Per-arg <parameter=name>VALUE</parameter> blocks nested inside <function=NAME></function>, tools declared as `<tools>` JSON lines in the system message. Byte-identical to Qwen3.8-27B. |

_说明：_ Unchanged wire format. As with the other Qwen3.8 cards, no `--tool-call-parser` / `--reasoning-parser` flags are printed (framework cookbooks are linked instead), so parser_flags is left empty rather than inferred.

### 进阶

**自蒸馏：** Not self-distillation of the LM, but note the QSA indexer is trained by distilling the model's OWN attention distribution (teacher = the same backbone's dense attention) — the same trick DeepSeek-V3.2-Exp used to make DSA retrofittable.

**混合精度：** [Unknown/Not Disclosed] for the training recipe. config dtype is bfloat16 and mamba_ssm_dtype=float32 for the GDN recurrent state. At inference the widened residual state supports FP8 storage, explicitly to contain the memory traffic of carrying 4 branches during decode.

**稳定性 trick：** Stability is treated as a first-class design axis, not an afterthought — the report's stress-test protocol holds the learning rate at multiples of its optimal value with a constant schedule, so instabilities that would only appear at production scale surface within a moderate budget (following Wortsman et al. 2023). The stated criterion: **the new recipe must be at least as stable as the generation it replaces under equal stress**. At 4x the optimal learning rate the Qwen3.5 structure spikes frequently while the new recipe stays stable throughout; isolating the GR gate on a single-variable pair identifies it as a key contributor to the margin. The payoff is reported directly: **full-scale training of Qwen3.8-Flash-Next completed without a single loss spike or anomalous gradient-norm fluctuation, and without qk-clip (Kimi) or SwiGLU-clip (DeepSeek-V4)** — i.e. this generation removes the explicit clipping crutches its cross-vendor peers rely on. The 8-step Newton-Schulz choice is also a stability choice rather than an accuracy one. The report frames the causal chain explicitly: GR supplies a rescaling that improves stability, and that stability margin is what permits the higher learning rate and batch size the refitted scaling law recommends.

## 多模态

| | |
|---|---|
| 模态 | text, image, video |
| 融合方式 | `native_early` |

**融合方式说明：** Same native-early fusion as the rest of the Qwen 3.x line — vision tokens inlined into the shared backbone via four reserved vocabulary IDs, vision_config.out_hidden_size=2560 matching LM hidden_size. HF pipeline_tag=image-text-to-text. The vision encoder is untouched by the Qwen4-preview changes: the architecture rewrite is entirely on the language side.

### 视觉编码器

| | |
|---|---|
| 架构 | ViT (vision_config model_type now reports `qwen4_exp`, tracking the new backbone class, but the geometry is unchanged from Qwen3.5/3.6/3.8). deepstack_visual_indexes=[] — no DeepStack injection layers. |
| 层数 | 27 |
| 隐藏维度 | 1152 |
| 中间维度 | 4304 |
| 头数 | 16 |
| patch 大小 | 16 |
| 输入通道数 | 3 |
| 输出维度 → LM | 2560 |
| 空间合并大小 | 2 |
| 时序 patch 大小 | 2 |

_说明：_ hidden_act=gelu_pytorch_tanh; num_position_embeddings=2304. preprocessor_config.json is byte-identical (sha256 27225450ac9c...) to Qwen3.5-27B, Qwen3.6-27B and Qwen3.8-27B — the image preprocessing pipeline has not changed across four generations. Only out_hidden_size differs (2560 here vs 5120 at 27B), tracking LM width. The repo also ships a separate video_preprocessor_config.json, not registered as a source in this extraction.

### Vision token anchor（LM vocab ID）

| | |
|---|---|
| image_token_id | 248056 |
| video_token_id | 248057 |
| vision_start_token_id | 248053 |
| vision_end_token_id | 248054 |

## 待解问题（open_questions）

- **Version-number vs architecture mismatch.** The model ships as 'Qwen3.8-Flash-Next' but its HF class is `Qwen4ExpForConditionalGeneration` / model_type `qwen4_exp`, and the README calls it 'the architecture that will underpin Qwen4'. This record is filed under family `Qwen` with a 3.8 name for source fidelity, but it is NOT comparable to Qwen3.8-27B / 3.8-2.4T-A95B as a sibling. If Qwen4 ships, revisit whether the repo needs an explicit lineage/generation field — `metadata.family` cannot currently express 'named 3.8, architecturally 4'.
- Absolute pre-training token count and data mix are still undisclosed — only ratios against the 397B-A17B predecessor ('a third of the tokens', 'a ninth of the FLOPs'). The predecessor's own token count has never been published either, so the ratio does not resolve to a number.
- Post-training is entirely undisclosed: no SFT description, no RL algorithm, no reward design, no agentic-environment details. The tech report is an *architecture and optimization* report and says so — §4 evaluates the base model, and the post-trained numbers appear only on the model card without method. This is a much better disclosure floor than Qwen3.5/3.6/3.8 (which had no report at all) but the post-training half remains dark.
- The learning-rate decay schedule is not stated. The report gives the scaling-law-predicted optimum for LR and batch size and states batch warmup was dropped, but not the schedule shape (WSD? cosine?) or the peak/final values at production scale.
- MTP trained step depth D is still not disclosed — four-step speculative decoding is evaluated, but that is an inference-time configuration, not necessarily the trained depth.
- How the n-gram embedding fits the schema is unresolved. It is recorded under `architecture.auxiliary_modules` because it is a separately-parameterized, off-accelerator, deterministically-addressed table, but it sits inside the forward pass at layer 2, so it is not 'auxiliary' in the DSpark/draft-head sense the v7 field was added for. If a second vendor ships embedding-table capacity scaling, the schema likely needs a dedicated slot rather than a stretched one.
- Parameter accounting is three-way (125B backbone + 51B n-gram + 4B MTP) and the schema's `params_total` is a single string. The value here spells all three out, but cross-model aggregation over `params_total` will not parse it. Worth considering a structured parameter-budget field if off-accelerator or module-external parameters recur.
- `indexer_budget=2048` is a token budget that maps to 512 micro-blocks at r=4. `sparse_attention.top_k` is recorded as 2048 (tokens) to stay comparable with DSA-family records, but the selection actually operates on 512 block units — the two conventions differ, and a naive cross-model comparison of `top_k` will mis-rank QSA against DSA.
- GR's relationship to mHC (DeepSeek-V4) and AttnRes (Kimi K3) is documented by the vendor with head-to-head loss numbers, but all comparisons are at 25B-A3B / 28-layer proxy scale. Whether GR's advantage over mHC (which at that scale the report calls 'comparable', with GR winning on efficiency rather than quality) holds at production scale is not shown.
- `ple_*` config keys (ple_embed_dim, ple_conv_kernel_size, ple_layer_ids) suggest a Per-Layer-Embedding lineage in the implementation naming, but the report and card describe the mechanism only as 'N-gram Embedding'. Whether PLE naming implies anything beyond the described n-gram lookup is not stated.
- The custom `qwen-community-1.0` licence file was not registered as a source; its terms are not captured here. Note this is a third distinct licence within the Qwen3.8 name (27B Apache-2.0, 2.4T-A95B `qwen3.8-max`, Flash-Next `qwen-community-1.0`).
- The hosted Qwen3.8-Flash on Qwen Cloud is described as this model plus '1M context length by default, official built-in tools'. Which built-in tools, and whether the hosted variant differs in weights or only in serving configuration, is not stated — the same open-vs-hosted gap flagged on the other two Qwen3.8 records.
- Cached blog.html at qwen.ai/blog?id=qwen3.8-flash-next is a client-side-rendered SPA shell, so substantive blog content was unavailable at extraction time. Unlike previous Qwen extractions this costs little, since the tech report covers the architecture in depth.

---

_由 `data/extracted/qwen3.8-flash-next.json` 通过 `python -m llm_tech_matrix.extraction.render` 自动生成。请勿直接编辑此文件——修改 JSON 或渲染器。_
