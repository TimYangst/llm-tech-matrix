# Hybrid Thinking (chat-template-driven thinking-mode fusion)

**Slug:** `hybrid-thinking`
**Category:** alignment
**One-line:** A post-training recipe that fuses long-CoT reasoning ("thinking") and direct response ("non-thinking") behaviors into a single set of weights, switched at inference via chat-template directives rather than serving two separate models.
**First introduced in:** [Qwen3 Technical Report (Qwen Team, 2025)](https://arxiv.org/abs/2505.09388)

## Description

Frontier models commonly split capabilities across two checkpoints: a
reasoning-tuned variant (long CoT, slow, expensive) and an instruction-tuned
variant (terse, fast, cheap). Hybrid Thinking collapses both into one checkpoint:

- **Training** (Stage 3 of Qwen3's four-stage post-training, called *Thinking Mode
  Fusion*): continual SFT on the reasoning-RL checkpoint with a 50/50-ish mix of
  thinking samples (rejection-sampled from the reasoning RL model itself, to
  preserve quality) and non-thinking samples (curated multi-domain instruction
  data). The chat template introduces `/think` and `/no_think` directives in the
  user/system message and uses an empty `<think></think>` block convention for
  non-thinking responses.

- **Inference**: the user toggles modes by inserting `/think` or `/no_think` in
  the prompt (or by setting `enable_thinking=False` in the HuggingFace tokenizer).
  Multi-turn dialogs can interleave the directives — the model adheres to the
  most recent flag.

- **Thinking budget** emerges naturally: once the model is comfortable producing
  responses with truncated thinking blocks, you can halt the thinking mid-stream
  by inserting a fixed stop-thinking sentinel, and the model finishes from
  whatever reasoning it has so far. This capability is *not* separately trained
  in Qwen3 — it's a free byproduct of Thinking Mode Fusion.

The pattern is closely related (but not identical) to OpenAI's reasoning-effort
and Anthropic Claude's extended-thinking knobs, which also expose a runtime
budget for explicit reasoning over a single model.

## Reference materials

- Original paper (Qwen3 §4.3): <https://arxiv.org/abs/2505.09388>

## Used by

| Model           | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                        |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Qwen3-32B       | `/think` (default) vs `/no_think` directives in user/system message; `<think>...</think>` delimits the reasoning block. Distinct sampling defaults per mode (thinking: T=0.6, top-p=0.95, top-k=20; non-thinking: T=0.7, top-p=0.8, top-k=20, presence_penalty=1.5). Thinking-budget control via inserted sentinel `"Considering the limited time by the user, I have to give the solution based on the thinking directly now. </think>"`. |
| Qwen3-235B-A22B | Same recipe as Qwen3-32B (the four-stage pipeline including Thinking Mode Fusion is shared across the two flagships). The 235B-A22B serves as one of the two distillation teachers (alongside 32B) that pass thinking + non-thinking behavior to the smaller Qwen3 sizes via Strong-to-Weak Distillation.                                                                                                                                  |

## Related techniques

- [GRPO](./grpo.md) — the Reasoning RL stage that builds the thinking ability before fusion
