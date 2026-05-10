# Qwen3.6-27B

Slug: `qwen3.6-27b`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3.6-27b/manifest.json` (committed).
This section is for human notes — links to register, candidates considered, rationale.

Planned sources:

- [ ] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/config.json`
- [ ] `tokenizer_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/tokenizer_config.json`
- [ ] `preprocessor_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/preprocessor_config.json`
- [ ] `model_card` (`model_card`) — `https://huggingface.co/Qwen/Qwen3.6-27B/raw/main/README.md`
- [ ] `blog` (`blog_html`) — `https://qwen.ai/blog?id=qwen3.6-27b`

Considered but excluded:

- Same as `qwen3.6-35b-a3b` — no Qwen3.6 arXiv paper exists.

## Open questions

(See `data/extracted/qwen3.6-27b.json` `open_questions` for the authoritative
list — pre-training continuation vs fresh pretrain, MTP step depth D, agentic
coding RL signal, preserve_thinking training recipe, mixed precision,
parallelism, and the lingering "/think soft switch in template but docs say
not supported" behavior question.)

## Resolved

- ✅ **Hybrid-backbone schema gap** — covered by schema v4 (validated via
  Qwen3.5-27B and -35B-A3B; identical layout reused here).
- ✅ **MTP semantic capture** — `training.objectives.multi_token_prediction.depth`
  fits the multi-step claim; exact D still UNKNOWN per vendor disclosure, but
  the schema field captures it (would be filled if the depth were stated).
- ✅ **Token embedding padded** — captured in `architecture.components.embedding_notes`
  with a cross-version note (Qwen3.5-27B is identical at 248320 padded; the
  unpadded count and padding rationale remain undisclosed and are flagged in
  the extracted JSON's `open_questions`).
- ✅ **Soft-switch policy vs template behavior** — captured under
  `training.alignment.inference_modes` triggers and flagged as an open question
  in the extracted JSON (template still references `/think` 5×; vendor doc
  says "not officially supported" — exact behavior on the soft tokens is not
  characterized, surface for downstream tooling).

## Inferred fields (closed models only)

N/A — Qwen3.6-27B is open-weight (Apache 2.0).

## Notes

**HF model card snapshot:**

- Total params 27B (dense — same shape as Qwen3.5-27B)
- 64 layers, hidden 5120, **hybrid layout** identical to Qwen3.5-27B
- Token Embedding: 248320 (Padded), LM Output: 248320 (Padded)
- FFN dense intermediate 17408 (same as 3.5)
- **MTP: trained with multi-steps** (explicit in model card)
- Context: 262144 native / 1010000 extended (same as 3.5)
- Native VL (same as 3.5)
- Chat template: same removal of `/think` `/nothink`, same `enable_thinking` and
  `preserve_thinking` kwargs as the MoE sibling
- Release: April 22, 2026

**Cross-version compare**: identical architecture-wise to Qwen3.5-27B. The
deltas live in:

1. Multi-step MTP (added in 3.6)
2. Chat template (soft switch removal + preserve_thinking)
3. Post-training recipe (agentic-coding focus, presumed execution-feedback RL)
4. Token embedding now padded (was the 3.5 card silent on this, or actually
   different? — flag for comparison)
