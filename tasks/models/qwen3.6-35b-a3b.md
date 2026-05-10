# Qwen3.6-35B-A3B

Slug: `qwen3.6-35b-a3b`
Family: `qwen`
Status: `sourcing`

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

- [ ] Same hybrid-backbone schema gap as Qwen3.5 (see `qwen3.5-35b-a3b.md`).
- [ ] **MTP step depth.** Qwen3.5 already has `mtp_num_hidden_layers: 1` in
  config — i.e., 1 MTP head, like DeepSeek-V3. The 27B Qwen3.6 model card says
  "MTP: trained with multi-steps". Need to confirm whether the 35B-A3B 3.6
  config exposes a higher `mtp_num_hidden_layers` or the multi-step is inside
  a single head.
- [ ] **Soft-switch "removal" — actually a docs-only change.** The HF card says
  Qwen3.6 "does not officially support the soft switch of Qwen3, i.e., `/think`
  and `/nothink`", but a quick grep shows `/think` still appears 5× in the
  Qwen3.6 chat template (identical count to Qwen3.5). So the deprecation is
  policy/docs, not template-level. Confirm at extraction time whether the
  template still routes `/think` end-of-message to enable thinking, or whether
  it now no-ops.
- [ ] **`preserve_thinking` mechanism** — what determines which prior turns'
  thinking get retained? Sliding-window? All? Tagged-by-user?
- [ ] **Agentic-coding RL recipe** — execution-feedback RL (Docker-sandboxed
  test-running) was mentioned in third-party coverage but not in the HF model
  card we read. Confirm via the official blog.

## Resolved

- (none yet)

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
