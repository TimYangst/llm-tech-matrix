# Qwen3.6-35B-A3B

Slug: `qwen3.6-35b-a3b`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3.6-35b-a3b/manifest.json` (committed).
This section is for human notes — links to register, candidates considered, rationale.

Planned sources:

- [ ] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3.6-35B-A3B/raw/main/config.json`
- [ ] `tokenizer_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.6-35B-A3B/raw/main/tokenizer_config.json`
- [ ] `preprocessor_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.6-35B-A3B/raw/main/preprocessor_config.json`
- [ ] `model_card` (`model_card`) — `https://huggingface.co/Qwen/Qwen3.6-35B-A3B/raw/main/README.md`
- [ ] `blog` (`blog_html`) — `https://qwen.ai/blog?id=qwen3.6-35b-a3b`

Considered but excluded:

- A Qwen3.6 arXiv tech report does not appear to exist as of May 2026 — the
  release was blog-only with HF model cards. Register the GitHub repo
  `https://github.com/QwenLM/Qwen3.6` if it gains technical content.

## Open questions

(See `data/extracted/qwen3.6-35b-a3b.json` `open_questions` for the
authoritative list — pre-training continuation vs fresh pretrain, MTP step
depth D, agentic-coding RL recipe, preserve_thinking retention rule, mixed
precision, parallelism, soft-switch behavior at template level, why no
revisit of MoE load-balancing.)

## Resolved

- ✅ **Hybrid-backbone schema gap** — covered by schema v4; validated again
  here via the same `Attention.variants[]` + `layer_pattern` shape used for
  the 3.5 sibling.
- ✅ **MTP head topology confirmed identical to 3.5** — `mtp_num_hidden_layers=1`
  in config, same as 3.5-35B-A3B and as the 3.6-27B sibling. Multi-step
  training depth D remains undisclosed and is flagged in the extracted JSON's
  `open_questions`.
- ✅ **Soft-switch behavior is template-level still present** — confirmed at
  extraction: `/think` still appears 5× in the chat template; "not officially
  supported" is a docs/policy posture, not a template removal. Captured under
  `training.alignment.inference_modes` and flagged in `open_questions` for
  the lingering "what does the template actually do on `/think`" question.
- ✅ **`preserve_thinking` is template-level** — the chat template references
  `preserve_thinking` 2× and the README documents the API kwarg; captured as
  the third inference mode. The retention rule (sliding-window vs full-history
  vs tagged) is not specified and remains in `open_questions`.

## Inferred fields (closed models only)

N/A — Qwen3.6-35B-A3B is open-weight (Apache 2.0).

## Notes

**HF model card snapshot:**

- Total params 35B, activated 3B per token (same shape as Qwen3.5-35B-A3B)
- 40 layers, hidden 2048, **same hybrid layout** as Qwen3.5-35B-A3B
- Token Embedding: 248320 (Padded) — listed explicitly here, not in 3.5 card
- MoE: 256 experts × 512, 8 routed + 1 shared (same as 3.5)
- Context: 262144 native, 1010000 extended (same as 3.5)
- Native VL: "Causal Language Model with Vision Encoder" (same as 3.5)
- **Chat template change**: removes `/think` and `/nothink` soft switches; thinking
  control is via `chat_template_kwargs.enable_thinking` only
- **New parameter**: `preserve_thinking` to retain reasoning context across turns
- Release: April 16, 2026

**Cross-version compare framing** (per session prompt user emphasis):

| Aspect                      | Qwen3.5-35B-A3B (Feb 2026)                   | Qwen3.6-35B-A3B (Apr 2026)                                          |
| --------------------------- | -------------------------------------------- | ------------------------------------------------------------------- |
| Backbone                    | Hybrid Gated DeltaNet + Gated Attention      | (presumed same)                                                     |
| MoE                         | 256 experts, 8R+1S                           | 256 experts, 8R+1S                                                  |
| Token embedding             | (not stated in card)                         | 248320 padded                                                       |
| MTP                         | `mtp_num_hidden_layers: 1` (already present) | Reported "trained with multi-steps" — likely deeper                 |
| `/think` soft switch        | Active in template (5×)                      | Still in template (5×); marked "not officially supported" in docs   |
| `enable_thinking` API kwarg | Supported                                    | Supported                                                           |
| `preserve_thinking`         | Not in template                              | **In template (2×)** — opt-in retains `<think>` blocks across turns |
| Highlight                   | "Native multimodal agents"                   | "Agentic coding + thinking preservation"                            |
