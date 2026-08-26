# Reasoning-effort control

> 中文版：[reasoning-effort.zh.md](./reasoning-effort.zh.md)

**Slug:** `reasoning-effort`
**Category:** alignment
**One-line:** A per-request knob that trades reasoning depth against latency and token cost on a single thinking-capable checkpoint, without switching weights or turning thinking off entirely.
**First introduced in:** No canonical paper. The API-level name comes from OpenAI's o-series `reasoning_effort` request parameter; open-weight vendors have converged on the same surface independently, each implementing it differently underneath.

## Description

[Hybrid thinking](./hybrid-thinking.md) gives a model a binary axis — think or don't.
Reasoning-effort control adds a *continuous-ish* axis on top: given that the model is
thinking, how hard should it think? The motivation is economic. Long chains of thought
dominate cost and latency in agentic loops, and most steps of a long-horizon task do not
need the model's deepest reasoning.

What makes this worth tracking across vendors is that the **API surface has converged
while the mechanism has not**. Every implementation in this repo exposes essentially the
same three-or-four-level enum, but underneath:

- **DeepSeek-V4** prepends a *prompt prefix* — a block of instruction text placed before
  the system message ("Reasoning Effort: Absolute maximum with no shortcuts permitted…").
- **Kimi K3** renders the level as a *typed option message* inside its XTML chat template
  (`thinking-effort`), inserted after tool declarations and before the conversation.
- **Qwen3.8** injects a *natural-language instruction into the system message* — and
  notably its middle level (`medium`) injects nothing at all, making it the bare prompt.

None of the three is a control token, a routing decision, or a separate set of weights.
In every case the level is text the model reads, which raises the same open question for
all of them: was the policy actually RL-trained against these strings, or is the enum
prompt engineering with a vendor-blessed wording? No vendor has published an answer.

A second cross-vendor observation: as effort levels arrive, the *non-thinking* mode tends
to leave. Qwen3.8-2.4T-A95B's open weights refuse `enable_thinking=false` outright, and
DeepSeek-V4's non-think mode is selected by the *absence* of an effort prefix rather than
being a peer mode. Effort levels appear to be the successor surface to the thinking toggle,
not a companion to it.

## Reference materials

- Original paper: — (no canonical publication)
- Reference implementation: chat templates in the model repos — `tokenizer_config.json`
  for Qwen3.8 / Kimi K3; `encoding/README.md` for DeepSeek-V4-Flash-0731.
- Relevant blog/post: —

## Used by

| Model                  | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Pro        | Three modes: `non-think` / `think-high` / `think-max`. `think-max` is realized as a special instruction prepended to the system prompt ("Reasoning Effort: Absolute maximum with no shortcuts permitted…"); `non-think` is selected by the *absence* of that prefix, so the effort prefix is the only carrier.                                                                                                             |
| DeepSeek-V4-Flash      | Same three-mode structure as V4-Pro, same prompt-prefix mechanism.                                                                                                                                                                                                                                                                                                                                                         |
| DeepSeek-V4-Flash-0731 | The official release **renamed the levels**: the preview's top "Think Max" prefix is now `high`, and `max` is a new, stronger prefix above it. `encoding/README.md` pins the exact prefix text for each level — the most precisely documented implementation in this repo.                                                                                                                                                 |
| Kimi K3                | Top-level `reasoning_effort` request field (`max` default / `high` / `low`). The chat template renders it as a global option message of type `thinking-effort`, placed after the tool declaration and before the conversation — a *typed* slot rather than free prose. K3 has no thinking toggle at all; effort is the only depth control.                                                                                 |
| Qwen3.8-27B            | `reasoning_effort` chat-template kwarg with `xhigh` (default) / `medium` / `low`; unsupported values raise. Realized as an instruction injected into the system message (synthesizing one if absent, or prepending inside the tools system block). **`medium` injects no text**, so the "middle" level is the un-instructed baseline and only the two extremes are steered. Skipped entirely when `enable_thinking=false`. |
| Qwen3.8-2.4T-A95B      | Same three levels and same injection mechanism as the 27B, but resolution is *unconditional* — there is no non-thinking branch to skip it, because the template refuses `enable_thinking=false`.                                                                                                                                                                                                                           |
| Qwen3.8-Flash-Next     | Identical to Qwen3.8-27B — the `chat_template.jinja` is byte-for-byte the same file (bar a trailing newline), so the same three levels with the same injected strings and the same 'medium injects nothing' quirk. Worth noting because *everything else* about this model is a new architecture: the runtime-control surface was held fixed across an architecture generation boundary.                                   |
| GLM-5.2                | **First GLM model with an effort axis.** Two levels only: `reasoning_effort` ∈ {high, max}, default `max`, emitted as a \`\<                                                                                                                                                                                                                                                                                               |
| GLM-5.3-Flash          | Adds a **`low`** level: {low, high, max}, still defaulting to `max`, still a system prompt prefix. Resolution is now unconditional because `enable_thinking` was removed — there is no non-thinking branch to skip. Same silent fallback to `max` on unknown values.                                                                                                                                                       |

## Related techniques

- [Hybrid Thinking](./hybrid-thinking.md) — the binary think/no-think axis this sits on top of, and the home of the related `preserve_thinking` / interleaved-thinking behavior.
