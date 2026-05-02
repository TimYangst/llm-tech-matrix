# Pipeline Architecture

Three decoupled layers. Each layer's input/output contract is the boundary — implementations can be swapped without touching neighbors.

```
┌─────────────────┐    raw files     ┌──────────────────┐    JSON     ┌─────────────────┐
│  1. Sourcing    │ ───────────────► │  2. Extraction   │ ──────────► │  3. Synthesis   │
│                 │  data/sources/   │                  │  data/      │                 │
│  HF, ArXiv,     │                  │  Schema-strict   │  extracted/ │  Reports,       │
│  Blog scrape    │                  │  LLM extraction  │             │  comparison     │
└─────────────────┘                  └──────────────────┘             └─────────────────┘
```

## Layer 1: Data sourcing

**Input**: a model identifier (e.g. `deepseek-v3`) plus optional URL hints.
**Output**: raw files written to `data/sources/<model>/`.

What lives here:

- HuggingFace `config.json` puller (uses `huggingface_hub`)
- ArXiv paper fetcher (PDF or HTML)
- Tech-blog HTML scraper (when needed)
- A `manifest.json` per model listing where each file came from + fetch date

What does **not** live here: any interpretation of file content. Sourcing's only job is "get the bytes, record where they came from."

Code: `src/llm_oss_summary/sourcing/`

## Layer 2: Information extraction

**Input**: `data/sources/<model>/` directory.
**Output**: `data/extracted/<model>.json` conforming to `docs/schema.md`.

This is the AI-driven layer. The extraction prompt frames the model as a "Senior AI Researcher" and enforces the no-hallucination rule (see `schema.md` cardinal rule).

What lives here:

- Prompt templates (one per source type: config.json, paper, blog)
- A merging step that reconciles fields extracted from multiple sources for the same model
- Pydantic validation of the final output against `schema.py`
- Logging of `[Unknown/Not Disclosed]` fields and `inferred_fields` notes

What does **not** live here: cross-model logic. One model in, one JSON out.

Code: `src/llm_oss_summary/extraction/` and `.claude/skills/extract-model/`

## Layer 3: Synthesis & analytics

**Input**: a set of `data/extracted/*.json` files.
**Output**: `data/reports/` — markdown reports, charts, diff tables.

What lives here:

- Cross-model comparison along a single dimension (e.g. "all MoE routing algorithms")
- Time-series trend reports (e.g. "optimizer evolution Adam → Muon")
- Static charts (matplotlib/plotly) saved alongside the report

This layer is intentionally last: it cannot work until enough extractions exist. **Don't over-build it early.** Start with one or two reports driven by real questions, not infrastructure-first.

Code: `src/llm_oss_summary/synthesis/`

## Why decoupled

- **Sourcing** breaks when websites change layout. Extraction shouldn't care.
- **Extraction** prompts evolve as we learn what works. Sourcing and synthesis shouldn't care.
- **Synthesis** asks new questions over time. It should re-read extracted JSON, not re-trigger extraction.

The contract is the JSON file. As long as `data/extracted/<model>.json` validates against `schema.py`, all three layers can iterate independently.
