# Vision

## Mission

Build a structured, continuously updatable knowledge base that tracks and decomposes the technical stacks of mainstream AI models. The output supports two complementary analyses:

- **Horizontal comparison** — how do different vendors solve the same problem (attention variant, MoE routing, optimizer choice)?
- **Vertical analysis** — how does a single technique evolve over time (e.g. optimizers Adam → AdamW → Muon, attention MHA → GQA → MLA)?

The project's value depends on **uniformity** of extracted data. Schema-strict extraction (see `schema.md`) is what makes both analyses possible.

## Milestones

### M1 — Text and multimodal LLMs (current focus)

Open-weight models analyzed deeply via HuggingFace `config.json` + tech reports. Closed models inferred from public signals (papers, blog posts, leaks) and clearly marked as inferred.

Target families:

- Qwen, Llama, DeepSeek, GLM, Kimi, MiniMax (open weights / open source)
- GPT-4, Claude, Gemini (closed — inferred from public signals)

Live model list and per-model status: see `../tasks/ROADMAP.md`.

### M2 — Diffusion and image/video generation (future)

Stable Diffusion family, Flux, Sora (inferred), Veo, Midjourney (inferred). Schema will need extension for diffusion-specific concepts (UNet vs DiT backbone, noise schedule, conditioning, etc.) — defer schema design until M1 is stable.

## Tracks beyond models

### Engines — inference, training and RL systems (design stage)

A second record type for the systems that run the models: inference engines (vLLM, SGLang),
training frameworks (VeOmni) and RL post-training systems (verl). The value is the
**model ↔ technique ↔ engine** triangle: which engine versions serve or train which extracted
models, and how long a technique takes to go from a model release to engine support. Engine
records are quarterly release snapshots, plus on-demand refreshes, in their own subtrees
with an independent schema version. Design: `engines/overview.md`; live status:
`../tasks/ENGINES.md`.

## Non-goals

- **Reproducing models** — this is an analysis project, not a training project.
- **Benchmark leaderboards** — eval results change weekly; we focus on architecture and training methodology, which change less.
- **Real-time tracking** — extractions are snapshots tied to a model release (or, for engines, a quarterly release snapshot), not a live feed.
