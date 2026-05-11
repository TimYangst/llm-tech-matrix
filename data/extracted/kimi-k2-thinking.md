# Kimi K2-Thinking

> 中文版：[kimi-k2-thinking.zh.md](./kimi-k2-thinking.zh.md)

*Schema version: 6*

## Overview

| | |
|---|---|
| Family | Kimi K2 |
| Released | [Unknown/Not Disclosed] |
| Openness | Open weights |
| Total parameters | 1T |
| Active parameters | 32B |

**Variant policy:** Within the K2 (text-only) generation Moonshot ships sibling-per-mode checkpoints — K2-Base (foundation), K2-Instruct (instruction-tuned), K2-Instruct-0905 (mid-cycle refresh), K2-Thinking (reasoning + native INT4 QAT). Each sibling shares the same architecture and 1T weight skeleton but is post-trained for a distinct use-case. The next generation (K2.5/K2.6) collapses this sibling-per-mode layout into a single unified-weights checkpoint with chat-template-kwarg modes — K2-Thinking is the last K2 sibling under the old layout and the recipe (native INT4 QAT, interleaved thinking + multi-step tool call) carries forward into K2.5/K2.6.

## Sources

- <https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/config.json>
- <https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/tokenizer_config.json>
- <https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/chat_template.jinja>
- <https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/README.md>
- <https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/docs/tool_call_guidance.md>
- <https://moonshotai.github.io/Kimi-K2/thinking.html>

## Architecture

### Backbone

| | |
|---|---|
| Layers | 61 |
| Hidden dim | 7168 |
| Context window | 262144 |

**Context notes:** README reports 256K; config.max_position_embeddings=262144 (= 64 x YaRN original 4096). Same long-context recipe as the K2 family.

**Context extension:**

| | |
|---|---|
| Method | yarn |
| Trained max | [Unknown/Not Disclosed] |
| Extended max | 262144 |
| Factor | 64.0 |
| Original max (RoPE) | 4096 |

_Notes:_ config.rope_scaling: type='yarn', factor=64, original_max_position_embeddings=4096, beta_fast=1.0, beta_slow=1.0, mscale=1.0, mscale_all_dim=1.0. K2-Thinking's beta_fast=1.0 differs from K2.5/K2.6's beta_fast=32.0 (K2.5/K2.6 use the YaRN paper defaults; K2-Thinking sets it equal to beta_slow). Pre-training sequence length not restated in the K2-Thinking README; K2 base tech report has not been published.

### Attention (MLA)

| | |
|---|---|
| Variant | MLA |
| Heads | 64 |
| KV heads | [Unknown/Not Disclosed] |
| Head dim | [Unknown/Not Disclosed] |

**RoPE:** type=`yarn`, base=`50000`

RoPE scaling:

```json
{
  "factor": 64.0,
  "beta_fast": 1.0,
  "beta_slow": 1.0,
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

### FFN (hybrid)

**Dense intermediate size:** `18432`

**MoE:**

| | |
|---|---|
| Routed experts | 384 |
| Active experts per token | 8 |
| Shared experts | 1 |
| Per-expert intermediate size | 2048 |

**Routing:** Auxiliary-loss-free routing (config.topk_method='noaux_tc') with sigmoid affinity scoring (scoring_func='sigmoid') and routed_scaling_factor=2.827. norm_topk_prob=true. n_group=1 (no grouped routing). seq_aux=true with aux_loss_alpha=0.001. Sparsity 48 (384/8). Identical to K2.5/K2.6 — single shared K2 architecture.

**Layer partition:** First 1 of 61 layers is dense (intermediate_size=18432); remaining 60 layers are MoE (per-expert intermediate_size=2048). config.first_k_dense_replace=1, moe_layer_freq=1.

### Components

| | |
|---|---|
| Activation | SwiGLU (config.hidden_act='silu' — gated SiLU is the SwiGLU form used in the FFN). |
| Normalization | RMSNorm (rms_norm_eps=1e-5). |

**Embedding notes:** tie_word_embeddings=false. Vocabulary 163840 (README: '160K'); TikTokenTokenizer. K2-Thinking's tokenizer_config does not include the K2.5-era `<|media_*|>` / `<think>` token additions in `added_tokens_decoder` (text-only model) but does include the same chat-role and tool-call special tokens (<|im_user|>/<|im_assistant|>/<|im_system|>/<|im_middle|>/<|im_end|>, <|tool_calls_section_begin|>...<|tool_call_end|>/<|tool_calls_section_end|>). eos_token_id=163586.

### Parallelism / infra

[Unknown/Not Disclosed] — README does not document training-infrastructure parallelism. The K2 base tech report (referenced from K2.5 paper §4.1) has not been published; K2.5's Decoupled Encoder Process (DEP) is multimodal-specific and does not apply to this text-only sibling.

## Training

| | |
|---|---|
| Optimizer | MuonClip — inherited from the K2 base (per K2.5 paper §4.1, which K2-Thinking shares as its foundation). README does not restate the optimizer. |
| Total training tokens | 15T (text only) — K2.5 paper §4.1 documents the K2-base pre-training corpus as '15 trillion high-quality text tokens'. K2-Thinking is a post-training derivative of that base; no additional pre-training corpus is reported. |

**LR schedule:** [Unknown/Not Disclosed] — K2 base tech report not published; K2-Thinking README documents only the post-training INT4 QAT change, not pre-training or RL hyperparameters.

**Data mix notes:** K2-Thinking inherits the K2-base pre-training data mix; K2 tech report not yet published, so per-domain percentages are not disclosed.

### Alignment

**SFT:** [Unknown/Not Disclosed] in detail — README §1: 'Starting with Kimi K2, we built it as a thinking agent that reasons step-by-step while dynamically invoking tools.' SFT trains for interleaved chain-of-thought reasoning + function calls capable of 200–300 sequential tool invocations. K2.5 paper later cites K2-Thinking as one of the SFT-data generators for K2.5.

**RL method:** End-to-end RL trained to interleave reasoning with tool calls (README §1, Key Features). Specific RL algorithm not disclosed in the README; the K2.5 paper §4.4.2 describes a token-level clip RL with MuonClip optimizer + budget-control reward + Generative Reward Models, and §4.4.2 also reports applying its 'Toggle' token-efficient RL heuristic specifically to K2-Thinking — implying K2-Thinking's post-training shares that RL family.

**RLAIF:** `[Unknown/Not Disclosed]`

**Post-training stages:**

| # | Name | Method | Description |
|---|---|---|---|
| 1 | Native INT4 Quantization-Aware Training | `qat` | Post-training-stage QAT applied to MoE expert weights only. README §4: 'thinking models use excessive decoding lengths, and thus quantization often results in substantial performance drops. To overcome this challenge, we adopt Quantization-Aware Training (QAT) during the post-training phase, applying INT4 weight-only quantization to the MoE components. It allows K2 Thinking to support native INT4 inference with a roughly 2x generation speed improvement while achieving state-of-the-art performance. All benchmark results are reported under INT4 precision.' config.quantization_config: format='pack-quantized', group_size=32, num_bits=4, type=int, symmetric=true, strategy='group', observer='minmax'. ignore patterns: lm_head, self_attn, shared_experts, mlp gate/up/down (so only routed-expert linears are INT4). |

**Inference modes (runtime-switchable):**

| Name | Trigger | Description |
|---|---|---|
| `thinking` | Sole mode — K2-Thinking's chat_template.jinja always emits an open `<think>` tag for the assistant turn (no conditional `thinking is false` branch like K2.5/K2.6). The model reasons before answering on every turn. | Always-on reasoning mode with end-to-end RL training to interleave chain-of-thought with multi-step tool calls. README §6 recommends temperature=1.0; SciCode evaluations follow the official benchmark setting at temperature=0.0. Maintains coherent goal-directed behaviour across 200–300 consecutive tool invocations (vs prior models that degrade after 30–50 steps). |
| `heavy` | Inference-time client-side parallel-sampling strategy (NOT a chat-template kwarg). Footnote 6: 'K2 Thinking Heavy Mode employs an efficient parallel strategy: it first rolls out eight trajectories simultaneously, then reflectively aggregates all outputs to generate the final result.' No `kwargs` because this is orchestrated outside the model — comparable to GPT-5 Pro's parallel-rollout pattern. | 8-way parallel sampling + reflective aggregation. Used for the highest reported HLE / AIME25 / HMMT25 scores (HLE 51.0, AIME25 100.0, HMMT25 97.5). The aggregation step is a separate model call. |

- **`thinking`**
    - Recommended sampling: `temperature=1.0`

**Tool-call protocol:**

| | |
|---|---|
| Format | `function-call-token` |
| Start token | `<|tool_call_begin|>` |
| End token | `<|tool_call_end|>` |
| Arguments schema | Each call: `<|tool_call_begin|>{tool_call_id}<|tool_call_argument_begin|>{json_arguments}<|tool_call_end|>`. tool_call_id format `functions.{name}:{idx}` where idx is a global per-conversation counter starting at 0. Arguments are the JSON-encoded function parameters object. Multiple calls per turn wrapped by `<|tool_calls_section_begin|>` ... `<|tool_calls_section_end|>`. Tool results returned in `tool` messages prefixed by `## Return of {tool_call_id}` (per chat_template.jinja). docs/tool_call_guidance.md is the canonical reference for the K2 family — K2.5 / K2.6 explicitly reuse it. |

_Notes:_ Canonical K2-family tool-call wire format; K2.5 README §6 says 'K2.5 shares the same design of Interleaved Thinking and Multi-Step Tool Call as K2 Thinking' and K2.6 README §6 repeats the claim. No published vLLM/SGLang/KTransformers `--tool-call-parser` flag — the K2-Thinking docs note that recent vLLM/SGLang versions are required for correct tool-call ID parsing. K2-Thinking is RL-trained for stable tool use across 200–300 sequential calls, well beyond the 30–50-step degradation point of prior thinking models.

### Advanced

**Self-distillation:** K2-Thinking acts as a teacher for the next generation: K2.5 paper §4.4.1 lists K2-Thinking among the synthesisers of high-quality SFT candidate responses for K2.5, and §4.4.2 evaluates the 'Toggle' token-efficient RL heuristic on K2-Thinking specifically.

**Mixed precision:** BF16 master parameters at training time (config.torch_dtype='bfloat16'); MoE expert weights deployed at native INT4 via post-training QAT (compressed-tensors format, group_size=32, num_bits=4, symmetric, group strategy). README §4: '~2x generation speed improvement while achieving state-of-the-art performance. All benchmark results are reported under INT4 precision.' Excluded from INT4: self_attn, shared_experts, mlp gate/up/down, lm_head — only routed-expert linears are quantised. Checkpoints can be unpacked to FP8/BF16 via the official compressed-tensors repo if a higher-precision deployment is required.

**Stability tricks:** QK-Clip (within MuonClip) inherited from K2 base; specific to K2-Thinking, README §4 frames the INT4 QAT itself as a stability mitigation: 'thinking models use excessive decoding lengths, and thus quantization often results in substantial performance drops' — QAT during post-training is the workaround that keeps the long-decoding INT4 inference path stable enough to be lossless at benchmark scale.

## Open questions

- Release date is not on the README or HF page header. Recorded as UNKNOWN. K2.5 paper (Feb 2026) cites K2-Thinking as a baseline, so K2-Thinking shipped before that.
- K2 base tech report has not been published — the K2.5 paper §4.1 promises details there. K2-Thinking pre-training fields (lr schedule, mixed-precision recipe, parallelism strategy, full data mix) stay at UNKNOWN until that report ships.
- Whether the K2-Thinking RL stack matches the K2.5 paper's token-level clip RL formulation exactly, or differs in some detail, is not documented. The K2.5 paper says it applies its Toggle heuristic to K2-Thinking but does not describe K2-Thinking's own RL algorithm.
- INT4 QAT calibration recipe (which forward-pass length, which calibration data, how the quantization-aware loss was weighted) is not disclosed in README §4. config records the resulting compressed-tensors layout but not the training procedure.
- K2-Thinking's chat_template.jinja injects a default system prompt 'You are Kimi, an AI assistant created by Moonshot AI.' if the user provides no system message — K2.5's changelog explicitly removed that default ('the default system prompt might cause confusion to users and unexpected behaviours, so we remove it'). Captured here for vendor-trajectory comparisons.

---

_Generated from `data/extracted/kimi-k2-thinking.json` by `python -m llm_tech_matrix.extraction.render`. Edit the JSON, not this file._
