# DeepSeek-V3

Slug: `deepseek-v3`
Family: `deepseek`
Status: `extracted`

This was the **M1 pilot extraction**. Completed 2026-05-02 against schema_version=1.
The extracted JSON is at `data/extracted/deepseek-v3.json` and validates cleanly.

## Sources

The authoritative list is `data/sources/deepseek-v3/manifest.json`:

- `config` (`hf_config`) — `https://huggingface.co/deepseek-ai/DeepSeek-V3/raw/main/config.json` ✓
- `paper` (`arxiv_pdf`) — DeepSeek-V3 Technical Report (arXiv:2412.19437) ✓

Background reading consulted but not registered as sources:

- DeepSeek-V2 paper — for MLA design lineage.
- DeepSeekMoE paper — for routing algorithm context.

## Open questions (deferred to schema iteration)

These are **not** unknowns about DeepSeek-V3 itself — they're places where schema_version=1
doesn't have a slot for something the paper clearly states. They're tracked here and
mirrored in the extracted JSON's `open_questions` array. Resolution will come through a
schema_version=2 design pass, not by editing this extraction.

- [ ] **Hybrid dense+MoE FFN.** First 3 of 61 layers are dense (intermediate_size=18432);
  remaining 58 are MoE (per-expert 2048). Schema has one `intermediate_size` slot.
  Currently encoded as 2048 with the exception spelled out in `parallelism_notes`.
- [ ] **MLA-specific fields.** Schema's `num_kv_heads` is awkward for MLA — the
  architecture compresses K/V into a latent of dim 512 rather than keeping N_kv heads.
  Consider an MLA subobject capturing `kv_lora_rank=512`, `q_lora_rank=1536`,
  `qk_nope_head_dim=128`, `qk_rope_head_dim=64`, `v_head_dim=128`.
- [ ] **Multi-Token Prediction (MTP).** First-class architectural feature (D=1 extra
  prediction depth, lambda schedule 0.3 → 0.1, shared embedding/output head with main
  model). No schema slot today. Consider `architecture.training_objectives` or
  `training.objectives`.
- [ ] **Fill-in-Middle (FIM).** Pre-training augmentation (PSM, rate 0.1). No schema
  slot; currently mentioned only in `components.embedding_notes`.
- [ ] **Context window canonicalization.** Paper says 128K (NIAH-validated). Config
  says `max_position_embeddings=163840` (YaRN factor 40 × 4096). Recorded 131072.
  Pick one convention for cross-model comparison.
- [ ] **RLAIF definition.** DeepSeek-V3's model-based RM is an AI model trained on
  preference data with chain-of-thought reasoning. Paper doesn't use the term "RLAIF",
  so we recorded `rlaif=false`. Tighten the definition in `docs/schema.md`.
- [ ] **`data_mix` empty.** Paper says math/code ratios "enhanced" and multilingual
  "expanded" but gives no concrete percentages. Currently `{}` per the no-hallucination
  rule. Decide whether to add a free-text `data_mix_notes` field for cases like this.

## Resolved

- ✓ Sources fetched (config 1.6 KB, paper 1.8 MB) and verified via sha256.
- ✓ Extraction passes Pydantic validation against schema_version=1.

## Notes

The pilot did its job: cleanly extractable model produced 0 `[Unknown/Not Disclosed]`
fields but exposed 5+ real schema gaps. The next high-leverage move is a schema v2 pass
addressing the gaps before doing the next 5–7 extractions, otherwise we'll keep working
around the same edges. (See `docs/roadmap.md` cross-cutting initiatives.)
