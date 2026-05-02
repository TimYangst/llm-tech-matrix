# CLAUDE.md

Guidance for Claude Code when working in this repository. This file is always loaded into context — keep it short. For details, follow links into `docs/`.

## Picking up from a fresh session

Read [`docs/session-start.md`](./docs/session-start.md) first. It has the three-step orientation, file map, and decision tree for picking the next task. Then check [`tasks/ROADMAP.md`](./tasks/ROADMAP.md)'s "Current focus" for the one-line "where we are."

## Project status

M1 in progress. DeepSeek-V3 extracted (schema v2). Glossary scaffold seeded.

## What this project is

A schema-driven AI extraction-and-synthesis pipeline for analyzing mainstream AI models (text, multimodal, diffusion). Three decoupled layers: **sourcing → extraction → synthesis**.

- Vision and milestones: [`docs/vision.md`](./docs/vision.md), [`docs/roadmap.md`](./docs/roadmap.md)
- Extraction schema (the contract): [`docs/schema.md`](./docs/schema.md) ← read before any extraction work
- Pipeline architecture: [`docs/pipeline.md`](./docs/pipeline.md)
- Naming, file layout, schema versioning: [`docs/conventions.md`](./docs/conventions.md)
- Per-model status: [`tasks/ROADMAP.md`](./tasks/ROADMAP.md)

## Cardinal rules (load-bearing)

These rules underpin the project's value. Do not violate them, even if asked to "just fill it in":

1. **No hallucination.** Missing information is the literal string `"[Unknown/Not Disclosed]"`. Never guess from training-data priors. See [`docs/schema.md`](./docs/schema.md#cardinal-rule-no-hallucination).
2. **Schema strictness.** Every `data/extracted/<model>.json` must validate against `src/llm_tech_matrix/schema.py`. Do not invent fields, rename fields, or skip required groups.
3. **Closed-model inferences go in `inferred_fields`.** The primary field stays `"[Unknown/Not Disclosed]"`. Synthesis tools opt in to inferred values; default is to ignore them.
4. **Schema changes are versioned.** Bump `schema_version` and update [`docs/conventions.md`](./docs/conventions.md#schema-changelog) on any breaking change.

## Layer boundaries

When implementing, keep the three layers decoupled:

- **Sourcing** (`src/llm_tech_matrix/sourcing/`) writes raw bytes + a `manifest.json` to `data/sources/<model>/`. No interpretation.
- **Extraction** (`src/llm_tech_matrix/extraction/`, `.claude/skills/extract-model/`) reads `data/sources/<model>/`, writes one validated JSON to `data/extracted/<model>.json`. One model in, one JSON out.
- **Synthesis** (`src/llm_tech_matrix/synthesis/`) reads only `data/extracted/*.json` and produces reports in `data/reports/`. Never re-trigger extraction.

The contract between layers is the JSON file. As long as JSON validates, layers iterate independently.

## Tooling

- **Package manager**: `uv`. Source of truth is `pyproject.toml`.
- **Python**: 3.13 (pinned in `.python-version` and `pyproject.toml`).
- **Common commands**:
  - `uv sync` — install/refresh venv from lockfile
  - `uv run python -m llm_tech_matrix` — run entry point
  - `uv add <pkg>` — add a dependency

There is no test suite, lint config, or CI yet — add them as the project grows. Don't assume they exist.

## Working style notes for Claude

- The Python package layout is `src/llm_tech_matrix/`. Imports use that name.
- Per-model task files (`tasks/models/<model>.md`) are the right place to record open questions, not commit messages.
- When uncertain about a field during extraction, add to `open_questions` rather than guessing.
- Worktrees are useful for parallel model extractions or experimental schema changes — see `.worktreeinclude` (already configured to copy `.env` into worktrees).
