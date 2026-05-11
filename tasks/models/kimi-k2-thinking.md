# Kimi K2-Thinking

Slug: `kimi-k2-thinking`
Family: `kimi-k2`
Status: `extracted`

## Sources

Authoritative list in `data/sources/kimi-k2-thinking/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/tokenizer_config.json`
- [x] `chat_template` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/chat_template.jinja`
- [x] `readme` (`model_card`) — `https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/README.md`
- [x] `tool_call_guidance` (`other`) — `https://huggingface.co/moonshotai/Kimi-K2-Thinking/raw/main/docs/tool_call_guidance.md` (canonical for K2 family)
- [x] `blog` (`blog_html`) — `https://moonshotai.github.io/Kimi-K2/thinking.html`

## Open questions

- [ ] **K2 base tech report not yet published** — same blocker as K2.5/K2.6 — without the K2 paper, K2-Thinking's pre-training fields (lr schedule, mixed-precision recipe, parallelism strategy, full data mix) stay at UNKNOWN.
- [ ] **K2-Thinking RL algorithm details** — README §1 states the model is "end-to-end trained to interleave chain-of-thought reasoning with function calls" but does not name the RL algorithm. K2.5 paper §4.4.2 says it applies its 'Toggle' token-efficient RL heuristic to K2-Thinking, suggesting the K2-Thinking RL stack is in the same family as K2.5's token-level clip RL — but this is inference, not direct documentation.
- [ ] **INT4 QAT calibration recipe** — README §4 documents the resulting compressed-tensors layout but not the QAT training procedure (calibration data, loss weighting, forward-pass length).
- [ ] **Release date** — README has no explicit release date. K2.5 paper (Feb 2026) cites K2-Thinking as a baseline, so it shipped before that. Recorded as UNKNOWN.

## Resolved

- **Variant policy** — within K2 generation, the variant_policy is sibling-per-mode (Base / Instruct / Instruct-0905 / Thinking), all sharing the same 1T MoE skeleton but differing in post-training. Confirmed via the moonshotai HF org repo listing — 4 separate K2 text-only checkpoints exist with distinct purposes.
- **Architecture** — text-only `DeepseekV3ForCausalLM` (no multimodal wrapper). 1T total / 32B active / 61 layers / MLA / 384 routed × 1 shared experts / top-8. Identical to K2.5/K2.6 modulo the multimodal additions.
- **YaRN delta vs K2.5/K2.6** — K2-Thinking has `beta_fast=1.0` (vs K2.5/K2.6's 32.0). Means YaRN's "fast"-region scaling is applied to all RoPE frequencies (since beta_fast == beta_slow == 1) rather than only the high-frequency end. Captured in the YaRN glossary entry.
- **EOS token = `<|im_end|>` (163586)** — K2-Thinking and K2.6 share `eos_token_id=163586` (the chat-role end token); K2.5 differs at `eos_token_id=163585` (the bare `[EOS]`).
- **Default system prompt** — K2-Thinking's chat_template injects "You are Kimi, an AI assistant created by Moonshot AI." if no system message is provided. K2.5 changelog explicitly removed this default for K2.5 ("might cause confusion to users and unexpected behaviours"). Recorded as a vendor-trajectory note in `open_questions`.
- **No `<think>`/`</think>` in tokenizer added_tokens** — K2-Thinking's tokenizer_config.json does not list `<think>`/`</think>` as added tokens (K2.5 added them at 163606/163607). The chat template still emits the literal `<think>` ... `</think>` strings; they tokenize as ordinary subword sequences rather than as single special tokens.

## Notes

- K2-Thinking is the canonical wire-format reference for the entire K2 family. K2.5 and K2.6 both explicitly reference it for tool calling, INT4 QAT, and "Interleaved Thinking and Multi-Step Tool Call" design.
- K2-Thinking introduced "Heavy Mode" — 8 parallel rollouts + reflective aggregation (footnote 6 of the README). Recorded as a separate inference_modes entry in the JSON, but with empty `kwargs` because it's a client-side orchestration pattern (like GPT-5 Pro), not a chat-template kwarg.
- Stable agency across 200–300 sequential tool invocations is the headline capability — README §1 contrasts with prior models that degrade after 30–50 steps. This is the foundation that K2.5's Agent Swarm (parallel, 100-step sub-agents) and K2.6's "300 sub-agents × 4000 steps" build on.
- K2-Thinking acts as a **teacher model** for K2.5 (paper §4.4.1: SFT data synthesised by K2 + K2-Thinking + in-house experts) and as the **evaluation target** for the Toggle RL heuristic (§4.4.2). Captured in the `advanced.self_distillation` field of the K2-Thinking JSON.
