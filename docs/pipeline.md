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

**Input**: a model identifier (e.g. `deepseek-v3`) plus public URLs to source assets.
**Output**: a `manifest.json` (committed) and locally cached files (gitignored) under
`data/sources/<model>/`.

What lives here:

- `manifest.py` — Pydantic schema for `SourceManifest` (committed) and `Asset` entries
  (URL, sha256, filename, kind, optional archive_url).
- `fetch.py` — CLI for downloading assets and verifying checksums:
  - `add` — register a new asset (downloads, computes sha256, appends to manifest)
  - `fetch` — re-download every asset listed in a manifest into the cache directory
  - `verify` — compare cached files against recorded sha256 without re-downloading
  - `list` — enumerate all manifests in the repo

What does **not** live here: any interpretation of file content. Sourcing's only job
is "get the bytes, record where they came from." Sources must be **publicly accessible**
(no paywalled or login-gated material — HF gated models with a personal token are OK,
but the requirement is that the asset is reachable without privileged access).

Why this split: papers and configs can be tens of MB; mirroring them in git wastes
space and adds nothing — the canonical hosts (HF, arxiv) are already authoritative.
The committed manifest plus sha256 gives us reproducibility without the bloat.

Code: `src/llm_tech_matrix/sourcing/`

## Layer 2: Information extraction

**Input**: `data/sources/<model>/` directory.
**Output**: `data/extracted/<model>.json` conforming to `docs/schema.md`.

This is the AI-driven layer. The extraction prompt frames the model as a "Senior AI Researcher" and enforces the no-hallucination rule (see `schema.md` cardinal rule).

What actually lives here today:

- `.claude/skills/extract-model/SKILL.md` — the extraction procedure itself. Extraction is
  agent-driven, not code-driven: there is no prompt-template module and no automated
  multi-source merge step. The skill reads the cached sources and writes the JSON.
- `src/llm_tech_matrix/extraction/render.py` — deterministic JSON → Markdown renderer,
  producing **two** committed files per model: `<slug>.md` (English chrome) and
  `<slug>.zh.md` (Chinese chrome). Field values stay in source-language English so the
  Markdown remains a faithful view of the JSON. Never hand-edit the output; change the
  JSON, or the `LABELS` dicts in `render.py`.
- `scripts/validate_extractions.py` — Pydantic validation of every extracted JSON against
  `schema.py`. This is the CI gate, and it is the real enforcement point for the contract.
- `docs/glossary/` — the shared vocabulary the rendered summaries lean on. Each entry
  carries a "Used by" table, so extraction has a step that writes *back* into the glossary.

Not built (and not currently missed): prompt templates per source type, an automated
merge/reconcile step, structured logging of `[Unknown/Not Disclosed]` rates.

What does **not** live here: cross-model logic. One model in, one JSON out.

Code: `src/llm_tech_matrix/extraction/`, `scripts/`, and `.claude/skills/extract-model/`

## Layer 3: Synthesis & analytics

**Input**: a set of `data/extracted/*.json` files.
**Output**: `data/reports/` — markdown reports, charts, diff tables.

What lives here:

- Cross-model comparison along a single dimension (e.g. "all MoE routing algorithms")
- Time-series trend reports (e.g. "optimizer evolution Adam → Muon")
- Static charts (matplotlib/plotly) saved alongside the report

This layer is intentionally last: it cannot work until enough extractions exist. **Don't over-build it early.** Start with one or two reports driven by real questions, not infrastructure-first.

**Status: not started.** `src/llm_tech_matrix/synthesis/` is an empty package and
`data/reports/` does not exist yet. The "enough extractions" bar M1 set (≥10) has been
met — see [`roadmap.md`](./roadmap.md) — so this layer is now unblocked rather than
premature. The glossary "Used by" tables are currently doing the cross-model comparison
job by hand, and they are the natural first thing a synthesis tool should generate
instead.

Code: `src/llm_tech_matrix/synthesis/`

## Why decoupled

- **Sourcing** breaks when websites change layout. Extraction shouldn't care.
- **Extraction** prompts evolve as we learn what works. Sourcing and synthesis shouldn't care.
- **Synthesis** asks new questions over time. It should re-read extracted JSON, not re-trigger extraction.

The contract is the JSON file. As long as `data/extracted/<model>.json` validates against `schema.py`, all three layers can iterate independently.
