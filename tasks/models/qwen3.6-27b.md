# Qwen3.6-27B

Slug: `qwen3.6-27b`
Family: `qwen`
Status: `sourcing`

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

- [ ] Same hybrid-backbone schema gap as Qwen3.5 (see `qwen3.5-35b-a3b.md`).
- [ ] **MTP details**. HF model card explicitly says "MTP: trained with
  multi-steps". Schema's `training.objectives.multi_token_prediction` is a
  single boolean/object — confirm we capture the step depth/count.
- [ ] **Token embedding 248320 (Padded)** — explicitly listed for both Qwen3.6
  variants. What's the unpadded vocab size, and what's the padding intent
  (alignment for tensor-parallel? new vision tokens?). Compare against Qwen3
  vocab.
- [ ] **"Soft-switch removal" is docs-only.** Quick template grep confirms
  `/think` still appears 5× in the Qwen3.6-27B chat template (same count as
  Qwen3.5 templates). The "not officially supported" claim from the HF model
  card is a policy/docs change, not a template change. Verify behavior at
  extraction.

## Resolved

- (none yet)

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
