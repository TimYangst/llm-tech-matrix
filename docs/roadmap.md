# Roadmap

This document tracks the **strategic** roadmap (milestones, scope, sequencing). For tactical per-model status, see `../tasks/ROADMAP.md`.

## Where we are

This document covers strategic milestones (M1 / M2 scope and exit criteria). For the
**live tactical state** — current phase, recent completions, recommended next model
— see [`../tasks/ROADMAP.md`](../tasks/ROADMAP.md)'s **Current focus** block. That's
the single source of truth; this section deliberately does not restate it.

## M1 — Text + multimodal LLMs

**Goal**: 10–15 high-quality extractions across the major families, enough to support meaningful horizontal and vertical comparison. *(Volume goal exceeded — 20 extractions as of 2026-08. What remains is coverage shape, not count.)*

Sequenced rollout:

1. ✅ **Pilot (1 model)** — DeepSeek-V3. Validated schema, extraction procedure, file layout; surfaced 7 schema gaps as intended.
2. ✅ **Open-weight backbone** — done and then some, but with a **narrower family spread than planned**: 4 vendors (DeepSeek, Qwen, Kimi, Z.AI) across 20 records. Llama, Mistral and MiniMax are all still `backlog`, so "one representative per design point" is only half-true — the set is deep on Chinese-lab MoE and thin on Western dense models.
3. ✅ **Multimodal extension** — well past 2–3 entries. Native-VL (Qwen 3.x, Kimi K2.5/K2.6/K3) is thoroughly covered. The *projection-fusion* comparison point the step was written for (Qwen-VL, MiniCPM-V, GLM-V) is still missing — every multimodal record so far is native-early fusion.
4. ⬜ **Closed-model inference (3 models)** — **not started, and now the single biggest gap.** `inferred_fields` is empty across all 20 records, which means the mechanism the schema was designed around has never been exercised once. `qwen3.7-max` is the cheapest entry point (see `../tasks/ROADMAP.md`).
5. ⬜ **First synthesis report** — not started. No longer blocked: the ≥10-extraction bar it was waiting on has been met twice over.

Exit criteria for M1:

- ✅ ≥10 models extracted, all validating against `schema.py` — **20 as of 2026-08**, enforced by `scripts/validate_extractions.py` in CI.
- ⬜ At least one synthesis report published in `data/reports/` — the directory does not exist yet. **This is now the critical-path item for closing M1.**
- 🟡 Schema has been through at least one breaking-change cycle and the changelog process works — the changelog process is proven (v1 → v7, all recorded in `conventions.md`), but every bump since v2 has been *backwards-compatible*. The migration discipline has been exercised (`scripts/migrate_*.py`); a genuinely breaking change has not. Treat this criterion as satisfied in spirit — don't manufacture a breaking change to tick it.

## M2 — Diffusion / image / video (future)

Not started. Will require:

- Schema extension for diffusion-specific fields (UNet vs DiT, noise schedule, VAE, conditioning, sampler).
- Different sourcing strategy — diffusion configs are less standardized than HF `config.json` for LLMs.

Defer until M1 exit criteria are met.

## Cross-cutting initiatives

These are not tied to a specific milestone:

- **Schema versioning** — establish the changelog discipline (`docs/conventions.md`) before the first breaking change.
- **Reproducible sourcing** — every `data/sources/<model>/manifest.json` should let someone re-fetch the same files. Verify before extending sourcing logic.
- **Skill library growth** — `.claude/skills/extract-model` is the seed. Add `compare-models` and `synthesize-trend` skills only when usage patterns justify them.
- **TODO: `add-model-source` skill** — wrap the "create manifest entry + fetch + record sha256" workflow currently exposed as `python -m llm_tech_matrix.sourcing add ...`. **The deferral condition has been met** — 20 models have been onboarded by hand, and the friction is now clear and repetitive: the same 4–5 HF asset URLs per slug (config / tokenizer_config / preprocessor_config / README / blog), varying only by repo name, plus a boilerplate `tasks/models/<slug>.md`. Worth building whenever sourcing next feels tedious.
- **Glossary as proto-synthesis** — the "Used by" tables in `docs/glossary/` are hand-maintained cross-model comparisons, i.e. exactly the output Layer 3 is supposed to generate. When synthesis starts, generating (or at least verifying) those tables from `data/extracted/*.json` is the highest-value first target, and it retires an ongoing manual cost.
