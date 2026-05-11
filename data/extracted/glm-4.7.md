# GLM-4.7

> 中文版：[glm-4.7.zh.md](./glm-4.7.zh.md)

*Schema version: 6*

## Overview

| | |
|---|---|
| Family | GLM-4.5 |
| Released | 2026-01 |
| Openness | Open weights |
| Total parameters | 358B |
| Active parameters | [Unknown/Not Disclosed] |

**Variant policy:** Z.AI's GLM-4.5 generation ships sibling-per-size and sibling-per-precision: full-flagship MoE (GLM-4.5: 355B per paper / 358B per HF model card; GLM-4.5-Air: 106B), each with FP8 quantized deployment siblings (e.g. GLM-4.7-FP8). Within the generation, post-training-only refreshes ship as separate generation tags (GLM-4.5 → GLM-4.6 → GLM-4.7), each carrying its own size siblings (GLM-4.7 + GLM-4.7-Flash for the smaller size; the GLM-4.5 ARC paper is cited as the canonical tech report for the entire generation through GLM-4.7). No separate Math/Coder/VL/Thinking siblings — runtime behavior is governed by chat-template kwargs `enable_thinking` and `clear_thinking` giving three modes (Interleaved Thinking default, Turn-level Thinking via per-turn enable_thinking, Preserved Thinking via clear_thinking=false; the latter two introduced in GLM-4.7 per the README).

## Sources

- <https://huggingface.co/zai-org/GLM-4.7/raw/main/config.json>
- <https://huggingface.co/zai-org/GLM-4.7/raw/main/tokenizer_config.json>
- <https://huggingface.co/zai-org/GLM-4.7/raw/main/chat_template.jinja>
- <https://huggingface.co/zai-org/GLM-4.7/raw/main/README.md>
- <https://arxiv.org/pdf/2508.06471>
- <https://z.ai/blog/glm-4.7>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 92 |
| Hidden dim | 5120 |
| Context window | 131072 |

**Context notes:** GLM-4.5 ARC paper §2.4 explicitly trains to a maximum sequence length of 128K (131072) during the long-context mid-training stage; GLM-4.5 ARC Figure 3 shows the staged extension 4K → 4K → 32K → 32K → 128K. GLM-4.7's config.json reports max_position_embeddings=202752 (~200K), a buffer larger than the 128K mid-training maximum — this may reflect a follow-up extended-context mid-training stage between GLM-4.5 and GLM-4.7 not documented in the GLM-4.5 ARC paper (see open_questions). num_hidden_layers=92 (3 dense + 89 MoE per paper Table 1) plus num_nextn_predict_layers=1 (single MTP layer for speculative decoding).

### Attention (GQA)

| | |
|---|---|
| Variant | GQA |
| Heads | 96 |
| KV heads | 8 |
| Head dim | 128 |

**RoPE:** type=`standard`, base=`1000000`

### FFN (hybrid)

**Dense intermediate size:** `12288`

**MoE:**

| | |
|---|---|
| Routed experts | 160 |
| Active experts per token | 8 |
| Shared experts | 1 |
| Per-expert intermediate size | 1536 |

**Routing:** Loss-free balance routing with sigmoid affinity scoring (paper §2.1: 'we employ loss-free balance routing and sigmoid gates for MoE layers'). Auxiliary sequence-level balance loss with weight 0.0001 used as a complementary signal to avoid extreme intra-sequence imbalance (paper §2.4). norm_topk_prob=true, routed_scaling_factor=2.5, n_group=1 / topk_group=1 (no node-limited grouped routing). 1 shared expert at moe_intermediate_size=1536. Sparsity 20 (160 routed / 8 active per token). Loss-free balance bias update rate scheduled: 0.001 for the first 15T tokens, 0.0 for the remaining.

**Layer partition:** First 3 of 92 layers are dense FFN (intermediate_size=12288); remaining 89 layers are MoE (per-expert intermediate_size=1536, 1 shared expert). config.first_k_dense_replace=3.

### Components

| | |
|---|---|
| Activation | SwiGLU (config.hidden_act='silu'). |
| Normalization | RMSNorm (rms_norm_eps=1e-5). Plus QK-Norm to stabilize attention-logit range — paper §2.1: 'We also incorporate QK-Norm to stabilize the range of attention logits.' (use_qk_norm=true). |

**Embedding notes:** tie_word_embeddings=false (separate output head). Vocabulary 151552. eos_token_id=[151329, 151336, 151338], pad_token_id=151329. attention_bias=true (note: distinct from GLM-5 which has attention_bias=false). partial_rotary_factor=0.5 — RoPE applied to half of the head_dim, the other half is rotation-free (a Hyena/non-rotary mix). Paper §2.1 highlights the 'wider-and-thinner head' design choice: 96 attention heads at hidden_dim 5120 = 2.5x more heads vs DeepSeek-V3's heads-per-hidden ratio; not loss-improving but consistently improves MMLU/BBH reasoning performance. The chat template opens with `[gMASK]<sop>` (legacy GLM ChatGLM-style sentence-piece-prefix), then uses `<|user|>` / `<|assistant|>` / `<|system|>` / `<|observation|>` role tokens and `<think>`...`</think>` for reasoning blocks. Tool-call wrappers `<tool_call>` / `</tool_call>` and per-arg `<arg_key>` / `<arg_value>` are emitted as plain text inside the assistant turn (XML-like, not single-token wrappers — paper §3.1 'Reducing Character Escaping in Function Call Templates' explicitly motivates this XML-like envelope to avoid per-arg JSON escaping for code-heavy arguments).

### Parallelism / infra

GLM-4.5 ARC paper does not detail inter-stage pipeline parallelism layout. Inference deployment supports vLLM (`--tensor-parallel-size 4` for FP8 single-node, larger TP for bf16) and SGLang (`--tp-size 8`); MTP-based speculative decoding with `--speculative-config.method mtp --speculative-config.num_speculative_tokens 1` (vLLM) or `--speculative-algorithm EAGLE --speculative-num-steps 3 --speculative-eagle-topk 1 --speculative-num-draft-tokens 4` (SGLang). FP8 deployment sibling (GLM-4.7-FP8) is the first-class single-node-deployment target.

## Training

| | |
|---|---|
| Optimizer | Muon optimizer (paper §2.4) — applied to all parameters except word embedding, bias, and RMSNorm weights. Hyperparameters: Newton-Schulz iteration steps N=5, momentum µ=0.95, update RMS scaled to 0.2. Paper notes Muon accelerates convergence and tolerates larger batch sizes vs the AdamW baseline. |
| Total training tokens | 23T total per GLM-4.5 ARC paper (15T main pre-training + 8T mid-training: 7T code-and-reasoning continual pre-training + 500B repo-level code + 500B synthetic reasoning + 100B long-context-and-agent — paper Figure 3). The GLM-5 README intro states GLM-4.5's pre-training corpus was 23T (now scaled to 28.5T for GLM-5), confirming 23T applies to the GLM-4.5/4.6/4.7 generation. Loss-free balance bias update rate transitions at the 15T-token boundary. MTP loss weight λ also schedule-transitions at 15T tokens (0.3 → 0.1). |

**LR schedule:** Cosine decay (paper §2.4) — chosen over warmup-stable-decay (WSD) after early experiments showed WSD-trained models underfit on SimpleQA / MMLU. Warmup from 0 to peak 2.5e-4, then decay to 2.5e-5 sustained until the end of mid-training. Batch size warmup 16M → 64M tokens over the first 500B tokens, constant thereafter. Weight decay 0.1, no dropout. RoPE base frequency adjusted from 10000 → 1000000 when extending sequence length to 32K (paper §2.4).

**Data mix notes:** Paper §2.2: Web (English/Chinese, Nemotron-CC-style quality-bucketed up-sampling — top quality bucket contributes >3.2 epochs; SemDedup applied to remove templated webpages MinHash misses); Multilingual (own crawl + Fineweb-2, quality classifier on educational utility); Code (GitHub + code hosting platforms, language-specific quality models with 3-tier classification, Fill-in-Middle applied to all source code, code-related web docs filtered via HTML tags + FastText classifier and re-parsed by a fine-grained parser); Math & Science (LLM-scored educational ratio + small classifier, threshold-up-sampled). Two-stage pre-training: stage 1 mostly general web; stage 2 up-samples GitHub source code and code/math/science web pages. No code/math/text percentage breakdown disclosed.

### Training objectives (beyond next-token prediction)

**Multi-Token Prediction (MTP):**

| | |
|---|---|
| Depth (D) | 1 |
| Loss weight schedule | MTP loss weight λ = 0.3 for the first 15T tokens, then 0.1 for the remaining tokens (paper §2.4). |

_Shared modules:_ 1 MTP layer (paper Table 1; config num_nextn_predict_layers=1) added as an MoE layer, shares the main model's vocabulary. Paper §2.1: 'we add an MoE layer as the MTP (Multi-Token Prediction) layer to support speculative decoding during inference'. Inference: speculative decoding via `--speculative-config.method mtp --speculative-config.num_speculative_tokens 1` (vLLM) or EAGLE 3-step (SGLang).

**Fill-in-Middle (FIM):**

| | |
|---|---|
| Format | [Unknown/Not Disclosed] |
| Rate | All source code data — paper §2.2: 'the Fill-In-the-Middle training objective is applied to all source code data'. |

### Alignment

**SFT:** Two-stage post-training (paper §3): Stage 1 Expert Training builds three expert models (Reasoning, Agent, General Chat) starting with Cold-start SFT (small set of extended-CoT data) → expert RL. Stage 2 Unified Training distills the experts back into a single hybrid-reasoning generalist via Overall SFT (millions of samples spanning reasoning / general chat / agentic tasks / long-context up to 128K) → unified RL. Two preparatory data techniques: (a) Reducing character escaping in function-call templates via the XML-like envelope (`<tool_call>...<arg_key>K</arg_key><arg_value>V</arg_value>...</tool_call>`) — paper §3.1 'Reducing Character Escaping in Function Call Templates' explicitly motivated by code-as-tool-arg usage; (b) Rejection sampling with a 4-step filter (repetition/length/format → correctness verification → reward-model filter for subjective Q → tool-trajectory protocol+terminal-state checks). Prompt selection drops bottom-50% by response length on hard prompts and applies response-level scaling (4 responses per prompt) for an additional 1–2% gain. Hybrid-reasoning training: balanced fold of full-CoT and CoT-free samples so the model learns both deliberative reasoning and direct response.

**RL method:** Multi-stage Expert RL → Unified RL (paper §3 — algorithmic specifics deferred in the available paper excerpt). Beyond GLM-4.5 baseline, GLM-4.7 README characterizes the GLM-4.6 → GLM-4.7 delta as multilingual agentic coding and terminal-task post-training (SWE-bench +5.8%, SWE-bench Multilingual +12.9%, Terminal Bench 2.0 +16.5% vs GLM-4.6) and tool-using/web-browsing improvements (τ²-Bench, BrowseComp). The Preserved-Thinking and Turn-level-Thinking inference modes are introduced in GLM-4.7 (the GLM-4.5 paper introduced Interleaved Thinking).

**RLAIF:** `[Unknown/Not Disclosed]`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Stage 1 Expert Training: Reasoning Expert | `sft+rl` | Cold-start CoT SFT + reasoning-domain RL to produce a Reasoning expert specializing in math, science, programming. |
| 2 | Stage 1 Expert Training: Agent Expert | `sft+rl` | Cold-start SFT + tool-using RL with the XML-like function-call envelope; trajectories filtered for protocol adherence and terminal-state correctness. |
| 3 | Stage 1 Expert Training: General Chat Expert | `sft+rl` | Cold-start SFT + RL on general chat (writing / translation / chitchat); reward-model filtering for subjective questions. |
| 4 | Stage 2 Unified Training: Overall SFT | `sft` | Distill from the three expert models into one hybrid-reasoning generalist. Millions of samples covering reasoning / general chat / agentic / long-context (max 128K). Balanced mix of full-CoT and CoT-free samples to support both thinking and non-thinking modes. Hard-prompt response-level scaling (4 responses per prompt) for math/science gains. |
| 5 | Stage 2 Unified Training: Unified RL | `rl` | Final-stage RL on the unified model. GLM-4.6 → GLM-4.7 refresh emphasis (per README): multilingual agentic coding, terminal-task RL, tool-using and web-browsing tasks. |

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `interleaved-thinking` | Default mode — chat-template kwarg `enable_thinking=true` (or omitted; vLLM/SGLang both have thinking enabled by default per README). Originally introduced in GLM-4.5; further enhanced in GLM-4.7. The chat template emits an open `<think>` tag before the assistant turn so the model produces a reasoning block before every response and tool call. | Model thinks before every response and tool call, improving instruction following and the quality of generation. README sampling preset: temperature=1.0, top_p=0.95, max_new_tokens=131072. |
| `non-thinking` | Chat-template kwarg `enable_thinking=false` (vLLM/SGLang `chat_template_kwargs={'enable_thinking': False}`). The chat template emits an empty `</think>` immediately after `<|assistant|>`. | Per-turn disabling of reasoning for lightweight requests to reduce latency/cost (Turn-level Thinking, introduced in GLM-4.7). |
| `preserved-thinking` | Chat-template kwarg `clear_thinking=false` (sglang-only per README: `chat_template_kwargs={'enable_thinking': true, 'clear_thinking': false}`). Default behavior strips `<think>` blocks from past assistant turns; with `clear_thinking=false`, all historical `<think>` blocks are retained across multi-turn conversations. | Introduced in GLM-4.7 (README §Interleaved Thinking & Preserved Thinking). In coding-agent scenarios, the model retains all thinking blocks across multi-turn conversations, reusing existing reasoning instead of re-deriving from scratch. Reduces information loss and inconsistencies; well-suited for long-horizon, complex tasks. README explicitly recommends Preserved Thinking for τ²-Bench and Terminal Bench 2.0 multi-turn agentic evaluations. |

- **`interleaved-thinking`**
    - Kwargs: `enable_thinking=true`
    - Recommended sampling: `temperature=1.0`, `top_p=0.95`, `max_new_tokens=131072`
- **`non-thinking`**
    - Kwargs: `enable_thinking=false`
- **`preserved-thinking`**
    - Kwargs: `clear_thinking=false`, `enable_thinking=true`

**Tool-call protocol:**

| | |
|---|---|
| Format | `xml-like` |
| Start token | `<tool_call>` |
| End token | `</tool_call>` |
| Arguments schema | Per-arg `<arg_key>{key}</arg_key><arg_value>{value}</arg_value>` blocks inside one `<tool_call>{function-name}...</tool_call>` envelope. Non-string scalar values are JSON-encoded (`v | tojson(ensure_ascii=False) if v is not string else v` per chat_template.jinja); string values are emitted as raw strings — GLM-4.5 ARC paper §3.1 motivates this with 'a substantial proportion of characters within the code require escaping' under JSON args, which the XML-like envelope avoids. Tool definitions are serialized as a JSON array inside `<tools>...</tools>` in the system message. Tool results are returned in subsequent `tool` messages wrapped as `<|observation|><tool_response>...</tool_response>`. |

**Serving parser flags:**

- `vllm`: `--tool-call-parser glm47 --reasoning-parser glm45 --enable-auto-tool-choice`
- `sglang`: `--tool-call-parser glm47 --reasoning-parser glm45`

_Notes:_ The reasoning-parser is named `glm45` (after the GLM-4.5 ARC paper, the format origin) and the tool-call-parser is named `glm47` (the parser was added to support GLM-4.7's interleaved-thinking + tool-call combination). Tool-result protocol matches the call protocol's `<|observation|><tool_response>...</tool_response>` envelope. The wire format is inherited unchanged by GLM-5 / GLM-5.1 — Z.AI did not bump the parser labels for the GLM-5 generation.

### Advanced

**Self-distillation:** Yes — Stage 2 Unified Training distills the three expert models (Reasoning, Agent, General Chat) trained in Stage 1 into a single hybrid-reasoning generalist via Overall SFT (paper §3). Sampling from the experts uses a 4-step rejection-sampling filter (format, correctness, reward-model, tool-trajectory) before the unified-model SFT.

**Mixed precision:** BF16 master parameters (config.dtype='bfloat16'). FP8 deployment sibling (GLM-4.7-FP8) is the first-class single-node-deployment target. Pre-training mixed-precision recipe is not separately disclosed in the GLM-4.5 ARC paper §2.4.

**Stability tricks:** QK-Norm — paper §2.1 explicitly cites attention-logit-range stability as the motivation for adding QK-Norm to GLM-4.5 (the only model in Table 1 with QK-Norm=Yes; DeepSeek-V3, Kimi K2, GLM-4.5-Air all run without it). Loss-free balance bias scheduling (0.001 → 0.0 at 15T tokens) prevents over-correction of expert load late in training. Auxiliary sequence-level balance loss (0.0001 weight) prevents intra-sequence routing imbalance even when global load is balanced.

## Open questions

- Total parameter count — GLM-4.5 ARC paper Table 1 reports GLM-4.5 as 355B 'including MTP layers but not word embeddings and the output layer'; the GLM-4.7 HF README and org-listing report 358B. The 3B difference is consistent with embedding+output-head parameters (vocab 151552 × hidden 5120 × 2 ≈ 1.55B per side ≈ 3.1B for the un-tied pair). Recorded as 358B for the model card / deployable checkpoint.
- Activated parameters for GLM-4.7 specifically — paper Table 1 lists GLM-4.5 at 32B activated; assuming GLM-4.7 is a post-training-only refresh on the GLM-4.5 architecture, the activated count carries over. The GLM-4.7 README does not restate this; recorded as UNKNOWN to reflect the strict-extraction rule.
- Context window discrepancy — GLM-4.5 ARC paper §2.4 / Figure 3 explicitly trains to a maximum of 131072 (128K). GLM-4.7's config.json has max_position_embeddings=202752 (~200K). This may indicate either a follow-up mid-training stage extending GLM-4.5/4.6/4.7's effective context to 200K (matching GLM-5's 200K) not documented in the GLM-4.5 ARC paper, or simply a buffer reservation with no actual training beyond 128K. Recorded as 131072 (paper-authoritative) with the discrepancy noted here.
- GLM-4.6 → GLM-4.7 RL details not disclosed — README characterizes the delta qualitatively (multilingual coding RL, terminal-task RL, tool-using RL) but provides no algorithm names, environment counts, reward-system specifics, or token budgets. The slime asynchronous RL infrastructure is referenced in the GLM-5 paper as 'initialized in GLM-4.5'; whether GLM-4.7 already used the full slime pipeline is not stated.
- GLM-4.5 ARC paper §3 post-training section excerpt available covers SFT data preparation in detail (Cold Start, Overall SFT, Rejection Sampling, Function Call Templates, Prompt Selection, Automatic Agentic SFT Data Construction) but does not include the RL algorithm specifics (PPO/GRPO variant, reward-model architectures, hyperparameters) that would be needed to fully populate `rl_method`.
- Pre-training data mix percentages not disclosed (qualitative descriptions only — Web/Multilingual/Code/Math&Science).
- Pre-training tensor/pipeline parallelism layout, mixed-precision recipe, and training infrastructure details are not in the available paper excerpt.

---

_Generated from `data/extracted/glm-4.7.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
