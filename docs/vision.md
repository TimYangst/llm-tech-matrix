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

### Media generation — audio, image and video

The [media track](media/overview.md) is implemented with an independent schema for
generation objective, scheduler, conditioning, VAE/codec, output and released/hosted
scope. Initial coverage is MiniMax H3, Music3 and Speech 2.8. Other vendors remain
future coverage; see the [model roadmap](../tasks/ROADMAP.md) for the current scope.

## Tracks beyond models

### Engines — inference, training and RL systems

An implemented record type for the systems that run the models: inference engines (vLLM, SGLang),
training frameworks (VeOmni, Megatron-LM / Megatron-Bridge) and RL post-training systems (verl). The value is the
**model ↔ technique ↔ engine** triangle: which engine versions serve or train which extracted
models, and how long a technique takes to go from a model release to engine support. Engine
records are quarterly release snapshots, plus on-demand refreshes, in their own subtrees
with an independent schema version. Design: `engines/overview.md`; live status:
`../tasks/ENGINES.md`.

## Non-goals

- **Reproducing models** — this is an analysis project, not a training project.
- **Benchmark leaderboards** — eval results change weekly; we focus on architecture and training methodology, which change less.
- **Real-time tracking** — extractions are snapshots tied to a model release (or, for engines, a quarterly release snapshot), not a live feed.
