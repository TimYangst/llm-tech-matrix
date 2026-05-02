# Roadmap

This document tracks the **strategic** roadmap (milestones, scope, sequencing). For tactical per-model status, see `../tasks/ROADMAP.md`.

## Where we are

**Phase**: project inception. Scaffolding done, no extractions yet.

**Next milestone**: M1 first extraction — pick one open-weight model with a strong public tech report and run it through the full pipeline end-to-end. Recommended: **DeepSeek-V3** (extensive paper, novel MLA + MoE design, exercises most schema fields).

## M1 — Text + multimodal LLMs

**Goal**: 10–15 high-quality extractions across the major families, enough to support meaningful horizontal and vertical comparison.

Sequenced rollout:

1. **Pilot (1 model)** — DeepSeek-V3. Validate schema, extraction prompts, file layout. Expect schema iteration here.
2. **Open-weight backbone (5–7 models)** — pick representatives across families: Llama-3.1, Qwen-2.5, GLM-4, Kimi, MiniMax, Mistral. Each should test a different design point.
3. **Multimodal extension** — add 2–3 multimodal entries (Qwen-VL, MiniCPM-V, GLM-V) to exercise the multimodal section of the schema.
4. **Closed-model inference (3 models)** — GPT-4, Claude, Gemini. These are inference-heavy; goal is to stress-test the `inferred_fields` mechanism.
5. **First synthesis report** — pick one vertical thread (suggest: optimizer evolution or MoE routing algorithms) and produce the project's first report from extracted data.

Exit criteria for M1:

- ≥10 models extracted, all validating against `schema.py`.
- At least one synthesis report published in `data/reports/`.
- Schema has been through at least one breaking-change cycle and the changelog process works.

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
- **TODO: `add-model-source` skill** — wrap the "create manifest entry + fetch + record sha256" workflow currently exposed as `python -m llm_oss_summary.sourcing add ...`. Defer until we've onboarded several models manually and seen what the friction points actually are.
