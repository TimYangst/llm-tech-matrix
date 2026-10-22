# Roadmap

This document tracks the **strategic** roadmap (milestones, scope, sequencing). For tactical per-model status, see `../tasks/ROADMAP.md`.

## Where we are

This document covers strategic milestones (M1 / M2 scope and exit criteria). For the
**live tactical state** — current phase, recent completions, recommended next model
— see [`../tasks/ROADMAP.md`](../tasks/ROADMAP.md)'s **Current focus** block. That's
the single source of truth; this section deliberately does not restate it.

## M1 — Text + multimodal LLMs

**Goal**: 10–15 high-quality extractions across the major families, enough to support meaningful horizontal and vertical comparison. *(Volume goal exceeded; current coverage and pending families are maintained in the model roadmap.)*

Sequenced rollout:

1. ✅ **Pilot (1 model)** — DeepSeek-V3. Validated schema, extraction procedure, file layout; surfaced 7 schema gaps as intended.
2. ✅ **Open-weight backbone** — done and then some, but with a **narrower family spread than planned**: 5 vendors (DeepSeek, Qwen, Kimi, Z.AI, MiniMax) across 35 records. Llama and Mistral are still `backlog`, so "one representative per design point" is only half-true — the set is deep on Chinese-lab MoE and thin on Western dense models.
3. ✅ **Multimodal extension** — well past 2–3 entries. Native-VL (Qwen 3.x, Kimi K2.5/K2.6/K3) is thoroughly covered. MiniMax-VL-01 and DeepSeek-V4-Flash-Vision-Exp now provide the projection-fusion comparison point; Qwen-VL, MiniCPM-V and GLM-V remain backlog.
4. ⬜ **Closed-model inference (3 models)** — **not started, and now the single biggest gap.** `inferred_fields` is empty across the 35 LLM/VL records, which means the mechanism the schema was designed around has never been exercised once. Check the unknown-FFN schema limitation before selecting a closed LLM (see `../tasks/ROADMAP.md`).
5. 🟡 **First synthesis report** — the *index* half is built (`synthesis/index.py` generates the model index, technique matrix and coverage report from typed fields; `scripts/validate_registry.py` gates drift and staleness in CI). The *interpretive* half — a trend narrative driven by one real question — is still unwritten.

Exit criteria for M1:

- ✅ ≥10 models extracted, all validating against `schema.py` — enforced by `scripts/validate_extractions.py` in CI.
- 🟡 At least one synthesis report published in `data/reports/` — the directory now holds the generated `technique-index.md` and `coverage.md`. Whether a *generated index* satisfies a criterion written with a *written report* in mind is a judgement call; treat the interpretive report as still outstanding.
- ✅ Schema has been through at least one breaking-change cycle and the changelog process works — the changelog process is proven (v1 → v8, all recorded in `conventions.md`), including v4’s breaking structured multimodal contract; existing records migrated with `multimodal: null`. Versioned migrations and CI validation exercise the compatibility discipline.

## Media generation — initial scoped coverage

User-directed DeepSeek/MiniMax coverage starts alongside M1, without waiting for
its interpretive report. [Media schema v1](media/schema.md) separates generation
objective/scheduler, conditioning, VAE/codec, output and release scope from the
causal-LLM schema. H3, Music3 and Speech 2.8 exercise joint audio/video, hybrid
music synthesis, and closed speech respectively. Source evidence and bilingual
views are validated in CI. Current scope and historical gaps live in the
[model roadmap](../tasks/ROADMAP.md); coordination lives in the
[refresh state](../tasks/projects/deepseek-minimax-refresh.md).

Other vendors' image/audio/video generators remain future work. Media coverage
does not imply completion of M1's closed-LLM or interpretive-report goals.

## Engines track (parallel to M1)

**Goal**: record which engine versions serve or train which extracted models, and when each
engine implemented each glossary technique. This track is independent of M1/M2 and does not
block their exit criteria. Full design: [`engines/overview.md`](./engines/overview.md). Live
status and snapshot calendar: [`../tasks/ENGINES.md`](../tasks/ENGINES.md).

1. ✅ **E0: design.** Roles, layout, snapshot policy (quarterly, on-demand refresh), evidence
   rules, draft schema.
2. ✅ **E1: pilot `vllm-v0.29.0`.** Engine schema v1, `extract-engine` skill, `--track engines`
   sourcing, renderer, CI validation. First record: 15 architecture rows (2 absent), 8 technique
   rows.
3. ✅ **E2: `sglang-v0.5.19`.** Same role, used as a cross-engine stress test. It broke one v1
   assumption before landing (parsers and `since_version` are per model), folded into engine
   schema v1.
4. ✅ **E3: `verl-v0.9.0`, then `veomni-v0.1.12`.** Exercises the RL and training roles and
   integrations. Engine schema v2 adds the `training` / `rl` subobjects and the three-level
   model `support`.
5. ✅ **E4: first engine synthesis.** Generated model/technique support matrix,
   adoption-lag report and bilingual glossary engine tables, all checked in CI.
6. ✅ **E5: NVIDIA training stack.** Megatron-LM and Megatron-Bridge snapshots;
   engine schema v3 records delegated model support explicitly.

Exit criteria for the first cycle:

- All three role subobjects (`serving`, `training`, `rl`) exercised by at least one
  validating record.
- A support matrix covering every extracted model.
- Glossary technique entries carry an "Implemented by (engines)" table that is backed by
  typed engine fields.

## Cross-cutting initiatives

These are not tied to a specific milestone:

- **Schema versioning** — maintain the independent model/engine/media changelogs and migrate affected records on each bump.
- **Reproducible sourcing** — every `data/sources/<model>/manifest.json` should let someone re-fetch the same files. Verify before extending sourcing logic.
- **Skill library growth** — `.claude/skills/extract-model` is the seed. Add `compare-models` and `synthesize-trend` skills only when usage patterns justify them.
- **TODO: `add-model-source` skill** — wrap the "create manifest entry + fetch + record sha256" workflow currently exposed as `python -m llm_tech_matrix.sourcing add ...`. Source registration is already repetitive: the same 4–5 HF asset URLs per slug (config / tokenizer_config / preprocessor_config / README / blog), varying only by repo name, plus a boilerplate `tasks/models/<slug>.md`. Worth building whenever sourcing next feels tedious.
- **Glossary as proto-synthesis** — *partly done*. `data/reports/coverage.md` now verifies the hand-maintained "Used by" tables against typed fields and reports both directions of mismatch. Full generation is blocked on the schema, not on effort: 13 glossary entries have no typed slot to read (see the maintained `registry.json` `prose_only` inventory), so their tables cannot be generated until the training/alignment axis gets typed fields.
