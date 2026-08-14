# GLM-5

> 中文版：[glm-5.zh.md](./glm-5.zh.md)

*Schema version: 7*

## Overview

| | |
|---|---|
| Family | GLM-5 |
| Released | 2026-02 |
| Openness | Open weights |
| Total parameters | 744B |
| Active parameters | 40B |

**Variant policy:** Z.AI ships GLM-5 as two checkpoints under one weight family — GLM-5 (bf16) and GLM-5-FP8 (post-training INT8/FP8 quantized for single-node deployment). The post-training-only refresh of GLM-5 is shipped as a separate generation tag (GLM-5.1, also with a GLM-5.1-FP8 sibling) rather than as a runtime mode on the same weights — distinct from the Qwen3.5/3.6 and K2.5/K2.6 'unified weights with chat-template kwargs' pattern. Within a single GLM-5 checkpoint, runtime behavior is controlled by chat-template kwargs `enable_thinking` (boolean toggle for the `<think>` reasoning block) and `clear_thinking` (boolean toggle for whether prior assistant turns retain their `<think>` blocks), giving three behaviors: interleaved thinking (default), turn-level thinking (per-turn enable_thinking control), and preserved thinking (clear_thinking=false carries past `<think>` blocks across multi-turn coding-agent sessions). No separate Math/Coder/VL/Thinking siblings exist for the GLM-5 generation.

## Sources

- <https://huggingface.co/zai-org/GLM-5/raw/main/config.json>
- <https://huggingface.co/zai-org/GLM-5/raw/main/tokenizer_config.json>
- <https://huggingface.co/zai-org/GLM-5/raw/main/chat_template.jinja>
- <https://huggingface.co/zai-org/GLM-5/raw/main/README.md>
- <https://arxiv.org/pdf/2602.15763>
- <https://z.ai/blog/glm-5>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 78 |
| Hidden dim | 6144 |
| Context window | 202752 |

**Context notes:** config.json max_position_embeddings=202752 (~200K). Paper §2.3 describes mid-training as a 3-stage progressive context extension: 32K (1T tokens), 128K (500B tokens), 200K (50B tokens) — the model is therefore trained out to the productized length without YaRN/NTK at deployment. Paper §2.1 separately reports 'reduces its layer count to 80' which conflicts with config.json's num_hidden_layers=78 (see open_questions). num_nextn_predict_layers=1 (single MTP module shared by 3 speculative steps via parameter sharing per paper §2.1).

### Attention (MLA)

| | |
|---|---|
| Variant | MLA |
| Heads | 64 |
| KV heads | [Unknown/Not Disclosed] |
| Head dim | [Unknown/Not Disclosed] |

**RoPE:** type=`standard`, base=`1000000`

**MLA-specific:**

| | |
|---|---|
| kv_lora_rank | 512 |
| q_lora_rank | 2048 |
| qk_nope_head_dim | 192 |
| qk_rope_head_dim | 64 |
| v_head_dim | 256 |

**Sparse attention:**

| | |
|---|---|
| Kind | `dsa` |
| Selected entries (top-k) | 2048 |
| Indexer heads | 32 |
| Indexer head dim | 128 |

**Selection rule:** Top-k by lightning-indexer score, per the DeepSeek-V3.2-Exp mechanism.

**Training recipe:** Continued Pre-Training (paper §2.1.1): indexer-only warm-up for 1000 steps x 14 sequences x 202752 tokens at max LR 5e-3 (~2.84B tokens), then sparse adaptation on 20B tokens — two orders of magnitude cheaper than DeepSeek-V3.2-Exp's 943.7B and still sufficient to recover dense-baseline quality.

_Notes:_ First non-DeepSeek adoption of DSA. config.indexer_rope_interleave=true. Paper §2.1.2 ablates DSA against SWA, search-based-pattern SWA, GDN and SimpleGDN and concludes DSA is the only one lossless by construction, since the indexer adapts to content instead of committing to a fixed sparsity pattern. RL-stability requirement (§3.2): the top-k operator must be deterministic — non-deterministic CUDA top-k caused sharp entropy collapse within a few steps, so GLM-5 uses torch.topk and freezes indexer parameters during RL by default.

### FFN (hybrid)

**Dense intermediate size:** `12288`

**MoE:**

| | |
|---|---|
| Routed experts | 256 |
| Active experts per token | 8 |
| Shared experts | 1 |
| Per-expert intermediate size | 2048 |

**Routing:** Auxiliary-loss-free routing (config.topk_method='noaux_tc', following DeepSeek-V3) with sigmoid affinity scoring (scoring_func='sigmoid'), routed_scaling_factor=2.5, norm_topk_prob=true. n_group=1 / topk_group=1 (no node-limited grouped routing). Sparsity 32 (256 routed / 8 active per token).

**Layer partition:** First 3 of 78 layers are dense FFN (intermediate_size=12288); remaining 75 layers are MoE (per-expert intermediate_size=2048, 1 shared expert at 2048). config.first_k_dense_replace=3, moe_layer_freq=1.

### Components

| | |
|---|---|
| Activation | SwiGLU (config.hidden_act='silu' — gated SiLU is the SwiGLU form used in the FFN). |
| Normalization | RMSNorm (rms_norm_eps=1e-5). |

**Embedding notes:** tie_word_embeddings=false (separate output head). Vocabulary 154880. eos_token_id=[154820, 154827, 154829] (multiple EOS for chat-role-end tokens including <|user|> / <|assistant|> / <|observation|>); pad_token_id=154820. attention_bias=false. The chat template opens with `[gMASK]<sop>` (legacy GLM ChatGLM-style sentence-piece-prefix), then uses `<|user|>` / `<|assistant|>` / `<|system|>` / `<|observation|>` role tokens and `<think>`...`</think>` for reasoning blocks. Tool-call wrappers `<tool_call>` / `</tool_call>` and per-arg `<arg_key>` / `<arg_value>` are emitted as plain text inside the assistant turn (XML-like, not single-token wrappers).

### Parallelism / infra

Paper §2.4: pipeline parallelism with flexible MTP placement (MTP output co-located with main output on the final stage for parameter sharing; embedding+transformer placed on the preceding stage to balance per-stage memory). Pipeline ZeRO2 gradient sharding (1/dp fraction per stage with 2-stage rolling double-buffered accumulation). Zero-redundant communication for the Muon distributed optimizer (all-gather restricted to per-rank parameter shards, overlap with local compute). Pipeline activation offloading (layer-granularity host-memory offload during PP warmup). Sequence-chunked output projection for memory. Workload-aware sequence reordering + dynamic redistribution of attention compute + flexible context-parallel partitioning + hierarchical all-to-all for QKV. Inference deployment uses multi-node EP64+DP64 over 8 nodes for KV-cache headroom; FP8 rollouts and MTP for tail-latency reduction; PD (Prefill-Decode) disaggregation to prevent prefill-decode interference; DP-aware routing for KV-cache locality across multi-turn agent rollouts.

## Training

| | |
|---|---|
| Optimizer | Muon, with the 'Muon Split' adaptation introduced in this paper (paper §2.1) — instead of applying matrix orthogonalization to the up-projection matrices W_UQ, W_UK, W_UV as a single matrix, Muon Split partitions them into per-attention-head matrices and orthogonalizes each independently, allowing different heads to update at different scales. This adaptation is what closes the MLA-vs-GQA-8 performance gap under Muon (paper Table 1) and obviates QK-Clip (logits remain stable without clipping). Distributed Muon implementation uses per-rank parameter-shard all-gather (no full-parameter broadcast) overlapped with local compute. |
| Total training tokens | 28.5T tokens for the base model (paper §2 / README intro: scaled from GLM-4.5's 23T to 28.5T). Mid-training adds 32K (1T tokens), 128K (500B tokens), 200K (50B tokens) on top (paper §2.3). DSA continued pre-training adds ~2.84B (warmup) + 20B (sparse adaptation) tokens (paper §2.1.1). |

**LR schedule:** [Unknown/Not Disclosed] — DSA continued-pretraining warmup uses max_learning_rate=5e-3 over 1000 steps × 14 sequences × 202752 tokens (paper §2.1.1). Mid-training and main pre-training lr schedules are not disclosed numerically.

**Data mix notes:** Paper §2.2: Web (refined GLM-4.5 pipeline + new DCLM classifier on sentence embeddings + World Knowledge classifier optimized via Wikipedia entries / LLM labels for long-tail knowledge). Code (refreshed snapshots from major code platforms + larger code-containing web pages, +28% deduplicated unique tokens vs GLM-4.5; Software Heritage metadata-alignment fixes; dedicated classifiers for low-resource languages including Scala/Swift/Lua). Math & Science (high-quality web/books/papers with refined PDF parsing + chunk-and-aggregate scoring for long documents; LLM-scored educational filtering; explicitly excludes synthetic / AI-generated / template-based data). No code/math/text percentage breakdown disclosed. Mid-training adds ~160B unique tokens of issue-PR pairs for software engineering (~10M issue-PR pairs after relaxed repo-level filtering + strengthened per-issue filtering).

### Training objectives (beyond next-token prediction)

**Multi-Token Prediction (MTP):**

| | |
|---|---|
| Depth (D) | 3 |
| Loss weight schedule | [Unknown/Not Disclosed] |

_Shared modules:_ Paper §2.1 introduces 'parameter sharing across 3 MTP layers during training' — config.json exposes num_nextn_predict_layers=1 (a single MTP module), but the paper's training recipe shares that one module's parameters across 3 sequential speculative-step predictions. Memory footprint matches DeepSeek-V3's single-MTP design while the model predicts 3 additional tokens at inference (vs DSV3's 2). MTP output layer co-located with the main output head on the final pipeline stage to enable parameter sharing; embedding+transformer components placed on the preceding stage to balance memory. Reported accept length 2.76 vs DeepSeek-V3.2's 2.55 at 4 speculative steps (paper Table 2).

### Alignment

**SFT:** Paper §3.1: SFT corpus covers three categories — General Chat (QA, writing, role-playing, translation, multi-turn dialog, long-context interactions), Reasoning (math, programming, science), Coding & Agent (frontend / backend code, tool calling, coding agents, search agents, general agents). Maximum context length extended to 202,752 tokens during SFT. Three thinking characteristics introduced (Interleaved Thinking, Preserved Thinking, Turn-level Thinking — see inference_modes). For Coding/Agent SFT, large numbers of execution environments are constructed; expert-RL-and-rejection-sampling-improved trajectories; erroneous segments are kept in the trajectory but masked out in the loss to teach error-correction without reinforcing incorrect actions. Compared to GLM-4.5, the Agent and Coding SFT data scale is significantly expanded.

**RL method:** GRPO with IcePop (paper §3.2) — pop-style mask suppresses tokens whose train-vs-inference policy mismatch ratio falls outside [1/β, β], distinguishing training policy π_train (gradient updates) from inference policy π_infer (trajectory sampling); KL regularization removed vs original IcePop to accelerate RL improvement. Hyperparameters β=2, ε_low=0.2, ε_high=0.28, group_size=32, batch_size=32. For Agentic RL (paper §3.3 / §4): fully asynchronous and decoupled framework — Multi-Task Rollout Orchestrator with per-task microservices (>1k concurrent rollouts), Token-in-Token-out (TITO) gateway eliminates re-tokenization mismatches, Direct Double-sided Importance Sampling with token-level clipping ([1−ε_l, 1+ε_h]) using rollout log-probabilities directly (no historical π_old tracking), drops off-policy samples staler than threshold τ, drops env-failure samples with valid-sample padding. DP-aware routing pins all requests from one rollout to the same DP rank for KV-cache locality. DSA-specific RL stability: deterministic torch.topk operator in the DSA Indexer (non-deterministic CUDA top-k caused drastic training degradation); indexer parameters frozen by default during RL.

**RLAIF:** `[Unknown/Not Disclosed]`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Multi-task SFT | `sft` | Three-category SFT (General Chat / Reasoning / Coding & Agent) with context length extended to 202752, introducing the three thinking characteristics (Interleaved/Preserved/Turn-level). INT4 QAT applied during SFT (paper §2.4.3) using a quantization kernel that ensures bitwise-identical training-vs-inference behavior. |
| 2 | Reasoning RL | `rl` | Mixed-domain RL across math, science, code, and tool-integrated reasoning (TIR). GRPO + IcePop without KL term. Difficulty filtering against GLM-4.7 (problems GLM-4.7 rarely solves but stronger teachers like GPT-5.2 xhigh / Gemini 3 Pro can solve). Code: competitive programming (Codeforces, TACO, SYNTHETIC-2-RL) + scientific coding decomposed by internal pipelines. TIR: math/science subset + STEM questions explicitly designed for tool answers. Domain/source-specific judge models or evaluation systems produce binary outcome rewards; mixture roughly balanced across the four domains. |
| 3 | Agentic RL | `rl` | Fully asynchronous + decoupled RL for coding and search agents on the slime framework. Group-wise policy optimization (only model-generated tokens in the loss; environment feedback ignored). Verifiable executable environments at scale: >10k SWE environments across 9 languages built via RepoLaunch with auto-extracted Fail-to-Pass / Pass-to-Pass tests; thousands of terminal-agent envs in Harbor format synthesized via a 3-phase agentic data pipeline (task draft → concrete task → iterative refinement) with >90% Docker-build accuracy; deep-search multi-hop QA pairs from a Web Knowledge Graph (WKG) over 2M+ web pages with 3-stage difficulty filtering and bidirectional verification. For BrowseComp at inference, GLM-5 introduces a Hierarchical Context Management strategy (Keep-recent-k=5 fold + Discard-all reset at T=32K). |
| 4 | General RL | `rl` | 3-dimensional optimization: Foundational Correctness (instruction following, logical consistency, factuality, hallucination, language disfluency — usability baseline), Emotional Intelligence (empathetic/insightful/natural responses), Task-specific Quality (writing, text processing, QA, role-playing, translation). Hybrid reward system mixing rule-based reward functions + Outcome Reward Models (ORMs, low-variance but reward-hackable) + Generative Reward Models (GRMs, robust but higher-variance). Distinctive: explicit human-authored response anchors (rather than only model-generated optimization) to avoid converging to model-like patterns. |
| 5 | On-Policy Cross-Stage Distillation | `distillation` | Final post-training stage to mitigate cumulative degradation from sequential single-objective optimization (paper §3.5). Final checkpoints from preceding stages (SFT, Reasoning RL, General RL) serve as teachers; training prompts sampled from each teacher's RL training set and mixed in proportion. Loss reuses the GRPO formulation with the advantage replaced by the teacher-vs-student log-ratio (with stop-gradient on the teacher term). Group size 1 (no need for variance estimation since advantage comes from teacher gap), batch size 1024. |

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `interleaved-thinking` | Default mode — chat-template kwarg `enable_thinking=true` (or omitted). The chat template emits an open `<think>` tag before the assistant turn so the model produces a reasoning block before every response and tool call (paper §3.1, README §1). | The model thinks before every response and tool call, improving instruction following and the quality of generation. README sampling preset for HLE (default reasoning): temperature=1.0, top_p=0.95, max_new_tokens=131072. |
| `non-thinking` | Chat-template kwarg `enable_thinking=false`. The chat template emits an empty `</think>` immediately after `<|assistant|>` so the model skips the reasoning block. | Per-turn disabling of reasoning for lightweight requests to reduce latency/cost (Turn-level Thinking, paper §3.1). |
| `preserved-thinking` | Chat-template kwarg `clear_thinking=false`. The default behavior strips `<think>` blocks from past assistant turns (only the most recent assistant turn carries its `<think>` block forward when re-rendered). With `clear_thinking=false`, all historical `<think>` blocks are retained across multi-turn conversations. | In coding-agent scenarios, the model retains all thinking blocks across multi-turn conversations, reusing existing reasoning instead of re-deriving it from scratch. Reduces information loss and inconsistencies; well-suited for long-horizon, complex tasks (paper §3.1, README §1). Inspired by Claude Opus 4.5's thinking-block preservation. |

- **`interleaved-thinking`**
    - Kwargs: `enable_thinking=true`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95`, `max_new_tokens=131072`
- **`non-thinking`**
    - Kwargs: `enable_thinking=false`
- **`preserved-thinking`**
    - Kwargs: `clear_thinking=false`

**Tool-call protocol:**

| | |
|---|---|
| Format | `xml-like` |
| Start token | `<tool_call>` |
| End token | `</tool_call>` |
| Arguments schema | Per-arg `<arg_key>{key}</arg_key><arg_value>{value}</arg_value>` blocks inside one `<tool_call>{function-name}...</tool_call>` envelope. Non-string scalar values are JSON-encoded (`v | tojson(ensure_ascii=False) if v is not string else v` per chat_template.jinja); string values are emitted as raw strings. Tool definitions are serialized as a JSON array inside `<tools>...</tools>` in the system message. Tool results are returned in subsequent `tool` messages wrapped as `<|observation|><tool_response>...</tool_response>`. |

**Serving parser flags:**

- `vllm`: `--tool-call-parser glm47 --reasoning-parser glm45 --enable-auto-tool-choice`
- `sglang`: `--tool-call-parser glm47 --reasoning-parser glm45`

_Notes:_ Wire format and parser names are inherited from GLM-4.7 (the reasoning parser is named `glm45` after GLM-4.5 ARC paper, the tool-call parser is named `glm47`). Speculative decoding via MTP (vLLM: `--speculative-config.method mtp --speculative-config.num_speculative_tokens 3`; SGLang: `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4`). The chat template additionally exposes `enable_thinking` and `clear_thinking` kwargs for runtime mode control.

### Advanced

**Self-distillation:** Yes — On-Policy Cross-Stage Distillation is the final post-training stage (paper §3.5). The final checkpoints from each preceding stage (SFT, Reasoning RL, General RL) serve as teachers within a single model lineage; training prompts sampled from each teacher's RL training set and mixed in proportion. Distillation loss replaces GRPO's advantage with the teacher-vs-student log-ratio (stop-gradient on teacher).

**Mixed precision:** BF16 master parameters (config.dtype='bfloat16'). FP8 rollouts during RL (paper §3.6.2 'Tail-latency reduction with FP8 rollouts and MTP'). INT4 QAT applied during SFT (paper §2.4.3) — a quantization kernel ensures bitwise-identical behavior between training and inference and is used both at training time and offline weight quantization. The FP8 GLM-5-FP8 deployment sibling is post-training quantized for single-node deployment. Pre-training mixed-precision (numerical format used during the 28.5T base run) is not separately disclosed.

### Quantization (shipped weights)

| | |
|---|---|
| Weight format | `int4` |
| Activation format | `[Unknown/Not Disclosed]` |
| Method | `qat` |

**Pipeline stage:** QAT applied during SFT (paper §2.4.3), with a quantization kernel that guarantees bitwise-identical behaviour between training and inference and is used both at training time and for offline weight quantization.

_Notes:_ A separate GLM-5-FP8 deployment sibling is POST-training quantized for single-node deployment — a different recipe from this INT4 QAT path.

**Stability tricks:** Muon Split (paper §2.1) — splitting the up-projection matrices per-head and orthogonalizing each independently keeps attention-logit scale stable during GLM-5 pre-training without QK-Clip (which the K2 family requires when using MuonClip on large transformers). Token-level clipping in the asynchronous Agentic RL [1−ε_l, 1+ε_h] with full token masking outside the trust region (paper §3.3, §4.1.2) — explicitly described as a stability mechanism for long-horizon multi-step rollouts. Drop off-policy samples whose oldest rollout policy version lags the current by more than τ. Deterministic top-k operator (torch.topk) in the DSA Indexer during RL — non-deterministic CUDA top-k implementations caused drastic RL degradation with sharp entropy drops within a few steps. Indexer parameters frozen by default during RL to prevent unstable indexer learning.

## Open questions

- Layer count discrepancy — paper §2.1 reports 'reduces its layer count to 80 to minimize expert parallelism communication overhead', but config.json has num_hidden_layers=78 (plus num_nextn_predict_layers=1 for MTP). Recorded as 78 (config-authoritative) with the paper's '80' flagged here; possible explanations include the paper counting MTP differently, pipeline-stage-level counts, or a late-stage architectural change not reflected in the released config.
- Reported total parameters discrepancy — paper §1 / §2.1 / README intro report 744B total / 40B active. The HuggingFace org-listing (https://huggingface.co/zai-org) shows GLM-5 as '754B' parameters in its summary tile; the paper's 744B is treated as authoritative.
- MTP parameter-sharing depth — config.json has num_nextn_predict_layers=1 (one MTP module). Paper §2.1 introduces 'parameter sharing across 3 MTP layers during training' to predict 3 additional tokens with the memory of a single MTP module. Recorded `depth=3` per the paper; the single config-level module reflects the parameter-shared physical realization.
- Loss weight schedule for the MTP head not stated.
- Pre-training data mix percentages not disclosed (qualitative descriptions only — Web/Code/Math&Science).
- Pre-training and mid-training lr schedules not disclosed numerically (only the DSA continued-pretraining warmup max-lr 5e-3 is stated).
- Whether IcePop's β=2 / ε_low=0.2 / ε_high=0.28 hyperparameters apply only to Reasoning RL or also carry over to Agentic RL is not explicit — Section 3.2 specifies them; Section 3.3 / 4.1.2 describes the asynchronous variant without restating the same numbers.
- GLM-4.5 ARC paper [arxiv:2508.06471] is referenced for several inherited details (mid-training framework, GLM-4.5 data pipeline) but is a separate document — items like the GLM-4.5 base architecture, original Muon recipe, and slime infrastructure design are not re-derived in the GLM-5 paper.

---

_Generated from `data/extracted/glm-5.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
