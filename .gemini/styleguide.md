# Code Review Style Guide

This document is the rubric Gemini Code Assist uses when reviewing pull
requests in this repository. Reviewers — human and bot — should weight these
project-specific rules above generic style preferences.

## Project context

This repo is a schema-driven extraction-and-synthesis pipeline for analyzing
mainstream AI models. Three decoupled layers — **sourcing → extraction →
synthesis** — communicate only through validated JSON files in `data/`. See
`CLAUDE.md` and `docs/` for full context.

## Cardinal rules (load-bearing — flag any violation)

1. **No hallucination.** Missing source information must be the literal string
   `"[Unknown/Not Disclosed]"`. The codebase uses `UNKNOWN` from
   `src/llm_tech_matrix/schema.py` for this. **Never** infer values from
   training-data priors, plausible defaults, or "what the field probably
   should be." If a PR introduces guessed values into `data/extracted/*.json`,
   flag it as a critical issue.
2. **Schema strictness.** Every `data/extracted/<model>.json` must validate
   against `src/llm_tech_matrix/schema.py` (Pydantic, `extra="forbid"`). PRs
   must not invent fields, rename fields, or skip required groups. The CI
   `validate_extractions.py` step enforces this — flag manual workarounds.
3. **Closed-model inferences belong in `inferred_fields`.** When a value is
   inferred (not directly disclosed), the primary field stays `UNKNOWN` and
   the inference is recorded under `inferred_fields[]` with `basis` and
   `confidence`. Synthesis tools opt in to inferred values.
4. **Schema changes are versioned.** Any breaking change to
   `schema.py` must bump `SCHEMA_VERSION` and add a changelog entry in
   `docs/conventions.md`.

## Layer boundaries (architectural — flag if blurred)

- **Sourcing** writes raw bytes + `manifest.json`. No interpretation.
- **Extraction** reads `data/sources/<slug>/`, writes one validated JSON.
- **Synthesis** reads only `data/extracted/*.json`. **Never** re-triggers
  extraction or reaches back into sources.

A PR that, for example, has the synthesis layer call extraction code, or has
the sourcing layer parse content into structured fields, breaks the contract.
Flag it.

## Python style

We follow the
[Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
with these pragmatic adjustments enforced by `ruff`:

- **Line length 100** (Google's 80 relaxed for readability with type hints).
- **Docstrings**: Google convention (`Args:`, `Returns:`, `Raises:`) when
  present. Docstrings are not required on every symbol yet — but if one
  exists, it must follow Google style. Reviewers should suggest docstrings
  on **public** entry points (CLI commands, exported classes), not on every
  helper.
- **Imports** sorted by `ruff` (`I` rules). Don't reorder manually.
- **Modern Python 3.13**: prefer `X | Y` over `Union[X, Y]`,
  `list[T]` over `List[T]`, `from collections.abc import Iterable`.
- **Naming** (PEP 8 / pyguide): `snake_case` functions, `PascalCase` classes,
  `UPPER_SNAKE` module constants. Single-letter names only in tight scopes.
- **No bare `except:`**. Catch the narrowest exception that's right.
- **Pydantic models** in `schema.py` use `model_config = ConfigDict(extra="forbid")`
  via the `_Strict` base. Don't loosen this in new models.

## Markdown style

We follow the
[Google Markdown Style Guide](https://google.github.io/styleguide/docguide/style.html),
formatted by `mdformat` + `mdformat-gfm` + `mdformat-tables`. Source style
(line breaks, padding) is dictated by the formatter; **review focuses on
content**, not formatting.

What to flag in `.md` content:

- Broken or stale relative links between `docs/` files.
- Out-of-date pointers to `tasks/ROADMAP.md` (the live "where we are").
- Hard-coded status that should defer to the roadmap.
- New per-model details in CLAUDE.md instead of `tasks/models/<slug>.md`.

## What to comment on (and what not to)

**Do** comment on:

- Cardinal-rule violations (especially #1 and #2 above) — critical severity.
- Layer-boundary leaks between sourcing/extraction/synthesis.
- Subtle bugs (off-by-one, missing async/await, wrong default values).
- Naming that obscures meaning (e.g. `data` for a typed model object).
- Public APIs lacking docstrings or type hints.
- Changes to `schema.py` without a corresponding `docs/conventions.md`
  changelog entry.

**Don't** comment on:

- Formatter output (line wrapping, table padding, list markers) — `mdformat`
  and `ruff format` own these.
- Style preferences not codified here or in pyguide.
- Test coverage (no test suite exists yet — flagging missing tests is noise
  until that changes).
- Adding speculative future-proofing or abstractions for hypothetical needs.
