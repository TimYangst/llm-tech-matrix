# DeepSeek-V3.2-Exp

> 中文版：[deepseek-v3.2-exp.zh.md](./deepseek-v3.2-exp.zh.md)

*Schema version: 7*

## Overview

| | |
|---|---|
| Family | DeepSeek |
| Released | 2025-09 |
| Openness | Open weights |
| Total parameters | 671B |
| Active parameters | 37B |

**Variant policy:** An explicitly EXPERIMENTAL, single-checkpoint release — the vendor's own framing is 'an intermediate step toward our next-generation architecture' whose purpose is to 'explore and validate optimizations' (README). Ships as Base + Exp (post-trained) only; no Math / Coder / VL siblings. Thinking and non-thinking are runtime modes on the one checkpoint via the chat template's `thinking` kwarg — the V3.1 generation had already collapsed the V3-plus-R1 sibling split into modes, and V4 later turns the same axis into three reasoning-effort levels. The release was deliberately run as a CONTROLLED EXPERIMENT: post-training pipeline, algorithm and data are held identical to DeepSeek-V3.1-Terminus so that the only measured variable is DSA, and the vendor kept V3.1-Terminus callable on the API until 2025-10-15 for side-by-side comparison.

## Sources

- <https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp/raw/main/config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp/raw/main/README.md>
- <https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp/raw/main/tokenizer_config.json>
- <https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp/raw/main/generation_config.json>
- <https://raw.githubusercontent.com/deepseek-ai/DeepSeek-V3.2-Exp/main/DeepSeek_V3_2.pdf>
- <https://arxiv.org/pdf/2412.19437>
- <https://api-docs.deepseek.com/news/news250929>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 61 |
| Hidden dim | 7168 |
| Context window | 131072 |

**Context notes:** 128K. Continued training starts 'from a base checkpoint of DeepSeek-V3.1-Terminus, whose context length has been extended to 128K' (paper §2), and both continued-training stages use 128K-token sequences. config.max_position_embeddings=163840 and tokenizer_config.model_max_length=163840 are unchanged from DeepSeek-V3 (= YaRN factor 40 × original 4096); 131072 is recorded as the canonical user-facing spec, consistent with this repo's deepseek-v3 record.

**Context extension:**

| | |
|---|---|
| Method | yarn |
| Trained max | 131072 |
| Extended max | 131072 |
| Factor | 40.0 |
| Original max (RoPE) | 4096 |

_Notes:_ rope_scaling is byte-identical to DeepSeek-V3's (type=yarn, factor=40, original_max_position_embeddings=4096, beta_fast=32, beta_slow=1, mscale=1.0, mscale_all_dim=1.0, rope_theta=10000). The V3.1 lineage had already extended and trained out to 128K before DSA was attached, so V3.2-Exp inherits the window rather than extending it — its contribution is making that window CHEAPER, not longer (paper §3 'Inference Costs': core attention drops from O(L²) to O(Lk)).

### Attention (MLA + DSA)

| | |
|---|---|
| Variant | MLA + DSA |
| Heads | 128 |
| KV heads | [Unknown/Not Disclosed] |
| Head dim | [Unknown/Not Disclosed] |

**RoPE:** type=`yarn`, base=`10000`

RoPE scaling:

```json
{
  "factor": 40,
  "beta_fast": 32,
  "beta_slow": 1,
  "mscale": 1.0,
  "mscale_all_dim": 1.0,
  "original_max_position_embeddings": 4096
}
```

**MLA-specific:**

| | |
|---|---|
| kv_lora_rank | 512 |
| q_lora_rank | 1536 |
| qk_nope_head_dim | 128 |
| qk_rope_head_dim | 64 |
| v_head_dim | 128 |

**Hybrid attention variants:**

| Name | Family | Q heads | KV heads | Head dim | RoPE | Notes |
|---|---|---|---|---|---|---|
| `mla_with_dsa` | `mla` | 128 | [Unknown/Not Disclosed] | [Unknown/Not Disclosed] | Partial RoPE as in V3's MLA (qk_nope_head_dim=128 + qk_rope_head_dim=64). IMPLEMENTATION TRAP documented in the README's 2025-11-17 update: the indexer module's RoPE input requires a NON-INTERLEAVED layout while the MLA module's RoPE expects an INTERLEAVED layout; earlier versions of the published inference demo got this wrong, potentially degrading model quality. | DeepSeek Sparse Attention (DSA) — the single architectural change vs DeepSeek-V3.1-Terminus (paper §1: 'the only architectural modification'). Two components. (1) LIGHTNING INDEXER: computes an index score I_{t,s} = Σ_j w^I_{t,j} · ReLU(q^I_{t,j} · k^I_s) between query token t and every preceding token s, over H_I = 64 indexer heads (config.index_n_heads=64) of dimension d_I = 128 (config.index_head_dim=128). ReLU is chosen for throughput, and because the indexer has few heads and can run in FP8 its cost is small — though it remains O(L²). (2) FINE-GRAINED TOKEN SELECTION: only the key-value entries with the top-k index scores are retrieved, and core attention is computed over that sparse subset; k = 2048 (config.index_topk=2048). Core attention complexity drops from O(L²) to O(Lk). DSA is instantiated UNDER MLA in the MQA mode (each MLA latent — the KV entry — is shared across all query heads of a token), because kernel efficiency requires each KV entry to be shared across multiple queries. Note that V3.1-Terminus used the MHA mode of MLA for training/prefilling and the MQA mode only for decoding (paper Appendix A); DSA forces MQA mode throughout. For short-sequence prefilling the vendor ships a masked-MHA mode that simulates DSA more efficiently. |

**Layer pattern:** Uniform, not hybrid — all 61 layers use the same MLA + DSA attention; there is no per-layer interleaving of attention variants. The single `variants[]` entry carries the MLA head geometry; the DSA modifier that sits on top of it lives in the structured `sparse_attention` slot added in schema v7.

**Sparse attention:**

| | |
|---|---|
| Kind | `dsa` |
| Selected entries (top-k) | 2048 |
| Indexer heads | 64 |
| Indexer head dim | 128 |

**Selection rule:** Top-k by lightning-indexer score I_{t,s} = sum_j w^I_{t,j} * ReLU(q^I_{t,j} . k^I_s); core attention runs only over the retained key-value entries.

**Training recipe:** Retrofitted onto the dense DeepSeek-V3.1-Terminus checkpoint in two stages. (1) Dense warm-up: LR 1e-3, 1000 steps x 16 sequences x 128K = 2.1B tokens, dense attention retained, everything frozen except the indexer, which is trained by KL against the model's own head-summed L1-normalized attention distribution. (2) Sparse adaptation: LR 7.3e-6, 15000 steps x 480 sequences x 128K = 943.7B tokens, top-k selection on, all parameters trainable, the same KL loss restricted to the selected token set. The indexer input is detached from the computational graph throughout, so the indexer is driven only by L_I and the main model only by the language-modeling loss.

_Notes:_ The canonical DSA reference implementation. Instantiated under MLA in MQA mode because kernel efficiency requires each KV entry to be shared across query heads (V3.1-Terminus used MLA's MHA mode for training/prefill and MQA only for decode). Core attention drops from O(L^2) to O(Lk); the indexer itself remains O(L^2) but is cheap — few heads, ReLU for throughput, implementable in FP8. A masked-MHA mode simulates DSA for short-sequence prefilling.

### FFN (hybrid)

**Dense intermediate size:** `18432`

**MoE:**

| | |
|---|---|
| Routed experts | 256 |
| Active experts per token | 8 |
| Shared experts | 1 |
| Per-expert intermediate size | 2048 |

**Routing:** Unchanged from DeepSeek-V3 — the config's MoE block is byte-identical. Auxiliary-loss-free routing (config.topk_method='noaux_tc') with sigmoid affinity scoring (config.scoring_func='sigmoid'), top-8 routed experts (config.num_experts_per_tok=8) plus 1 always-on shared expert, routed_scaling_factor=2.5, norm_topk_prob=true. Node-limited routing retained: 8 expert groups (config.n_group=8) with each token routed to its top-4 groups (config.topk_group=4) — the V4 generation later drops this constraint. Bias-update and sequence-wise balance-loss settings are not restated in the V3.2 paper.

**Layer partition:** First 3 of 61 layers are dense (intermediate_size=18432); remaining 58 are MoE (per-expert intermediate_size=2048). config.first_k_dense_replace=3, moe_layer_freq=1. Identical to DeepSeek-V3.

### Components

| | |
|---|---|
| Activation | SwiGLU (config.hidden_act='silu'). Unchanged from DeepSeek-V3 — no SwiGLU clamping (that arrives with V4). |
| Normalization | RMSNorm (config.rms_norm_eps=1e-6), pre-norm. Unchanged from DeepSeek-V3. |

**Embedding notes:** tie_word_embeddings=false; vocab_size=129,280; V3's byte-level BPE tokenizer (LlamaTokenizerFast, model_max_length=163840, bos <｜begin▁of▁sentence｜>, eos <｜end▁of▁sentence｜>). Chat-template special tokens: <｜User｜>, <｜Assistant｜>, <think>/</think>, and the tool-call family <｜tool▁calls▁begin｜>, <｜tool▁call▁begin｜>, <｜tool▁sep｜>, <｜tool▁call▁end｜>, <｜tool▁calls▁end｜>, <｜tool▁output▁begin｜>, <｜tool▁output▁end｜>. The FULL config.json diff against DeepSeek-V3 is remarkably small — three indexer keys (index_n_heads, index_head_dim, index_topk), quantization_config.scale_fmt='ue8m0', the class/model_type rename to DeepseekV32ForCausalLM / deepseek_v32, a dropped auto_map, and a transformers_version bump. Every other key is byte-identical, which is what licenses reporting V3's 671B total / 37B active for this checkpoint.

### Parallelism / infra

No training-infrastructure section is published for V3.2-Exp; the V3-lineage DualPipe + Expert Parallelism + ZeRO stack is assumed but not restated. What IS published is the inference/kernel surface, which is where DSA needed new work: TileLang kernels for readability/research (tile-ai/tilelang examples/deepseek_v32), high-performance indexer-logit CUDA kernels including paged variants (DeepGEMM PR #200), and sparse attention kernels (FlashMLA PR #98). Serving is day-0 supported by SGLang (`--tp 8 --dp 8 --enable-dp-attention`, with docker tags for H200, MI350 and Ascend NPUs) and vLLM. Inference-cost measurements in paper §3 come from the production service on H800 clusters at $2/GPU-hour.

## Training

| | |
|---|---|
| Optimizer | [Unknown/Not Disclosed] — the V3.2-Exp paper reports learning rates for the two continued-training stages but names no optimizer. DeepSeek-V3, whose architecture and pipeline this checkpoint inherits, used AdamW (β1=0.9, β2=0.95, weight_decay=0.1); V3.2-Exp does not restate it, and the V4 generation's move to Muon had not happened yet. |
| Total training tokens | 945.8B (continued training only: 2.1B dense warm-up + 943.7B sparse adaptation) |

**LR schedule:** Two continued-training stages, each at a constant learning rate (paper §2.1). (1) DENSE WARM-UP: LR 1e-3, 1000 steps × 16 sequences × 128K tokens = 2.1B tokens, with dense attention retained and ALL model parameters frozen except the lightning indexer. (2) SPARSE TRAINING: LR 7.3e-6, 15000 steps × 480 sequences × 128K tokens = 943.7B tokens, with fine-grained token selection switched on (k=2048) and all parameters trainable. No decay schedule is described for either stage.

**Data mix notes:** Not a from-scratch pre-training run. Continued training starts from the DeepSeek-V3.1-Terminus base checkpoint, and the data distribution for BOTH stages is 'totally aligned with the 128K long context extension data used for DeepSeek-V3.1-Terminus' (paper §2.1) — deliberate, so that DSA is the only variable under test. No composition percentages are disclosed, and the underlying V3.1-Terminus pre-training corpus and token count are not restated (DeepSeek-V3 was 14.8T).

### Training objectives (beyond next-token prediction)

**Multi-Token Prediction (MTP):**

| | |
|---|---|
| Depth (D) | 1 |
| Loss weight schedule | [Unknown/Not Disclosed] — not restated for the continued-training stages. |

_Shared modules:_ config.num_nextn_predict_layers=1, unchanged from DeepSeek-V3, so the V3 MTP head design (shared embedding and output head, one additional predicted token) carries over. The V3.2 paper does not discuss MTP.

**Other objectives:**

- Lightning-indexer KL alignment loss (paper §2.1) — the indexer is trained to imitate the main attention's own distribution, not the language-modeling target. In the warm-up stage the main attention scores for query t are summed across all heads and L1-normalized along the sequence dimension to give a target distribution p_{t,:}, and the indexer minimizes L_I = Σ_t D_KL(p_{t,:} ‖ Softmax(I_{t,:})). In the sparse stage the same loss is restricted to the selected token set S_t. Crucially the indexer input is DETACHED from the computational graph: the indexer is optimized only by L_I, the main model only by the language-modeling loss. This clean separation is what makes DSA bolt-on-able to an existing dense checkpoint.

### Alignment

**SFT:** Specialist distillation (paper §2.2). For each task a specialized model is fine-tuned from the same DeepSeek-V3.2 base checkpoint and trained with large-scale RL; the specialists then generate the domain-specific data used to train the final checkpoint. Five specialized domains beyond writing and general QA: mathematics, competitive programming, general logical reasoning, agentic coding, agentic search. Separate models generate long-chain-of-thought (thinking mode) and direct-response (non-thinking mode) data. Models trained on the distilled data land only marginally below the domain specialists, and the gap is closed by the subsequent RL stage. Pipeline, algorithm and data are held IDENTICAL to DeepSeek-V3.1-Terminus by design.

**RL method:** GRPO (Group Relative Policy Optimization), run as a SINGLE MIXED STAGE (paper §2.2). Unlike previous DeepSeek models trained with multi-stage RL, reasoning, agent and human-alignment training are merged into one stage — which 'balances performance across diverse domains while circumventing the catastrophic forgetting issues commonly associated with multi-stage training paradigms'. Rewards: rule-based outcome reward + length penalty + language-consistency reward for reasoning and agent tasks; a generative reward model with per-prompt rubrics for general tasks. The reward design explicitly balances two trade-offs — length vs accuracy, and language consistency vs accuracy. (This mixed-RL stage is exactly what DeepSeek-V4 later REPLACES with multi-teacher On-Policy Distillation.)

**RLAIF:** `False`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Continued pre-training — dense warm-up | `continued_pretraining` | Indexer-only training against the main attention's own distribution: dense attention retained, all parameters frozen except the lightning indexer, KL loss to the head-summed L1-normalized attention distribution. LR 1e-3, 1000 steps, 2.1B tokens. |
| 2 | Continued pre-training — sparse adaptation | `continued_pretraining` | Fine-grained top-k token selection switched on (k=2048) and all parameters unfrozen so the model adapts to the sparse pattern. Indexer keeps its KL alignment loss, now restricted to the selected token set, with the indexer input detached from the graph; the main model trains on the language-modeling loss. LR 7.3e-6, 15000 steps, 943.7B tokens. |
| 3 | Specialist distillation | `rejection_sampling+sft` | Per-domain specialists (mathematics, competitive programming, general logical reasoning, agentic coding, agentic search, plus writing and general QA), each fine-tuned from the same V3.2 base and trained with large-scale RL, then used to generate domain-specific training data for the final checkpoint. Distinct generators for thinking-mode and non-thinking-mode data. |
| 4 | Mixed RL (single stage) | `rl` | GRPO over reasoning + agent + human-alignment objectives merged into one stage to avoid catastrophic forgetting. Rule-based outcome rewards with length penalty and language-consistency reward for verifiable domains; rubric-per-prompt generative reward model for general tasks. Post-training employs sparse attention in the same way as the sparse continued-pre-training stage. |

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `thinking` | Chat-template kwarg `thinking=true`. The template then emits `<｜Assistant｜><think>` to open a reasoning block. | Long-chain-of-thought mode. All README benchmark rows labelled 'Reasoning Mode w/o Tool Use' use it. Paper Table 1 notes that V3.2-Exp scores below V3.1-Terminus on GPQA-Diamond, HLE and HMMT 2025 specifically because it GENERATES FEWER REASONING TOKENS, and that the gap closes when using intermediate checkpoints that produce a comparable token count. |
| `non-thinking` | Chat-template kwarg `thinking=false` (the template's default when the variable is undefined). The template emits `<｜Assistant｜></think>`, closing the reasoning block before generation so the model answers directly. | Direct-response mode. Post-training data for it is generated by a separate specialist from the thinking-mode data (paper §2.2). Assistant turns that begin a tool call are always rendered in this closed-`</think>` form by the template. |
| `prefix completion` | A trailing assistant message carrying `prefix: true`. Combined with `thinking=true` the template opens `<think>`; otherwise it emits `</think>` and continues from the supplied prefix without appending a new generation prompt. | Chat-template-level continuation mode inherited from the V3 lineage: lets a caller seed the beginning of the assistant turn and have the model continue it. Not documented in the README or paper — read directly from tokenizer_config.json's chat template. |

- **`thinking`**
    - Kwargs: `thinking=true`
- **`non-thinking`**
    - Kwargs: `thinking=false`
- **`prefix completion`**
    - Kwargs: `prefix=true`

**Tool-call protocol:**

| | |
|---|---|
| Format | `function-call-token` |
| Start token | `<｜tool▁calls▁begin｜>` |
| End token | `<｜tool▁calls▁end｜>` |
| Arguments schema | Each call is `<｜tool▁call▁begin｜>{function_name}<｜tool▁sep｜>{arguments}<｜tool▁call▁end｜>`, where `{arguments}` is the JSON-encoded arguments object emitted verbatim from `tool_calls[].function.arguments`. Multiple calls in one turn repeat the inner triple inside a single `<｜tool▁calls▁begin｜> … <｜tool▁calls▁end｜>` wrapper, which is terminated by `<｜end▁of▁sentence｜>`. Tool results return as `tool`-role messages wrapped in `<｜tool▁output▁begin｜>{content}<｜tool▁output▁end｜>`. An assistant turn that starts with tool calls is always rendered with the reasoning block already closed (`<｜Assistant｜></think>`). |

_Notes:_ Extracted from tokenizer_config.json's Jinja chat template — V3.2-Exp still SHIPS a Jinja template, unlike the V4 generation, which drops it for a Python `encoding_dsv4` module and switches to the `｜DSML｜` XML-like wire format. So this record is the V3-lineage endpoint of the tool-call protocol: JSON arguments delimited by special tokens, with no type discriminator and no structural nesting. Neither the README nor the paper documents the wire format; there is no published `--tool-call-parser` flag.

### Advanced

**Self-distillation:** Yes, twice over and in two different senses. (1) ATTENTION SELF-DISTILLATION: the lightning indexer is trained to match the model's own dense attention distribution via KL — a frozen-teacher/trainable-student setup inside a single model, and the mechanism that makes DSA retrofittable onto a dense checkpoint. (2) SPECIALIST DISTILLATION: per-domain specialists fine-tuned from the same V3.2 base generate the training data for the final unified checkpoint (paper §2.2), the same intra-family pattern that V4 later formalizes as multi-teacher On-Policy Distillation.

**Mixed precision:** FP8 (config.quantization_config: quant_method=fp8, fmt=e4m3, weight_block_size=[128,128], activation_scheme=dynamic) — inherited from DeepSeek-V3's FP8 training framework, with ONE change: scale_fmt='ue8m0' is new relative to V3's config, i.e. the FP8 scaling factors are stored in the UE8M0 format. The paper additionally notes the lightning indexer 'can be implemented in FP8', which is part of why its O(L²) cost is tolerable. torch_dtype=bfloat16.

**Stability tricks:** The design's stability argument is empirical rather than mechanical: paper §3 / Figure 2 shows the RL training curves of V3.2-Exp and V3.1-Terminus on BrowseComp and SWE Verified rising in close alignment throughout training, which the authors read as evidence of DSA's training stability. The indexer's optimization is deliberately isolated — its input is detached from the computational graph and it is driven only by L_I — so indexer gradients cannot perturb the main model. (The RL-time hazard that GLM-5 later documents for DSA — non-deterministic CUDA top-k causing entropy collapse — is not discussed here.)

## Open questions

- RESOLVED IN v7 — the sparse-attention modifier now has a structured home. DSA is not a per-layer attention variant (all 61 layers are uniform) but a mechanism layered ON TOP of MLA, and schema v6 had no slot for it, so the indexer parameters rode in a `variants[]` entry the schema intended for hybrid stacks. v7 adds `Attention.sparse_attention` (SparseAttentionConfig) plus a free-text `Attention.notes`; this record was the fourth to need it, after DeepSeek-V4 Pro/Flash (CSA/HCA) and GLM-5/5.1 (DSA).
- RESOLVED IN v7 — `AlignmentStage.method` now documents `continued_pretraining` as accepted vocabulary, so the two DSA continued-training stages no longer have to masquerade as distillation / RL. They remain in `alignment.stages` because it is still the only ordered-pipeline structure in the schema; a separate `training.pretraining_stages` list is a possible future refinement if pre-training pipelines get more elaborate.
- Optimizer is not named anywhere in the V3.2-Exp sources. AdamW is highly likely (V3 lineage, and Muon does not enter DeepSeek's stack until V4) but is not stated, so the field is UNKNOWN rather than inherited.
- params_total / params_active are not stated in the V3.2-Exp README or paper. 671B/37B is carried from the DeepSeek-V3 technical report on the strength of a config.json diff whose only architectural additions are the three indexer keys — plus the README's own inference config filename, `config_671B_v3.2.json`. The indexer itself adds parameters (64 heads × 128 dim of query/key projections per layer) that are not accounted for in either figure.
- The base pre-training corpus size behind V3.1-Terminus is not restated. Only the 945.8B continued-training budget is disclosed, so `data_total_tokens` records that rather than a lifetime total — a different accounting basis from the repo's other DeepSeek records (V3: 14.8T; V4-Flash: 32T; V4-Pro: 33T). Cross-model token-count comparisons must not treat this number as equivalent.
- DeepSeek-V3.1 and V3.1-Terminus are still unextracted in this repo, so the immediate baseline for every V3.2-Exp benchmark row has no record of its own. The V3 → V3.1 → V3.1-Terminus → V3.2-Exp chain is currently represented by its endpoints only.
- DeepSeek-V3.2 (the non-Exp, full hosted release of 2025-12) is a distinct later model and is not covered by this extraction.
- The 2025-11-17 README update reveals that the published inference demo had an indexer-RoPE layout bug (indexer needs non-interleaved, MLA needs interleaved). It is not stated whether the released WEIGHTS were trained with the correct layout throughout — the note is scoped to the demo code — nor whether any published benchmark numbers were affected.
- Sparse-stage hyper-parameters beyond LR and token count (batch schedule, warmup, whether the LR is truly constant) are not disclosed.
- The masked-MHA mode used to simulate DSA for short-sequence prefilling (paper §3) is mentioned in one sentence with no threshold given for when it engages.
- No FIM configuration is restated. DeepSeek-V3 used PSM Fill-in-Middle at rate 0.1, and V4 inherits it, but the V3.2-Exp continued-training stages say nothing about it, so `fill_in_middle` is left null rather than assumed.

---

_Generated from `data/extracted/deepseek-v3.2-exp.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
