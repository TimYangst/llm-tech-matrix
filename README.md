# LLM Tech Evolution Matrix

> 中文版：[README.zh.md](./README.zh.md)

A structured, continuously updatable knowledge base that tracks and decomposes the technical stacks of mainstream AI models — for **horizontal comparison** across vendors and **vertical analysis** of single techniques over time.

## Status

**M1 in progress.** 21 models extracted across 4 vendors (DeepSeek, Qwen, Kimi, Z.AI), all validating against schema v7. Newest records: Qwen3.8-Flash-Next (a Qwen4 architecture preview, and the first Qwen record backed by a technical report), Qwen3.8-2.4T-A95B (the first open-weight Qwen-Max-class model), Qwen3.8-27B. No synthesis layer yet — that starts once M1's extraction bar is met.

Current focus: **M1 — text and multimodal LLMs.** See [`docs/roadmap.md`](./docs/roadmap.md) for the strategic roadmap and [`tasks/ROADMAP.md`](./tasks/ROADMAP.md) for per-model status.

## Where to find things

| If you want to …                                      | Read                                           |
| ----------------------------------------------------- | ---------------------------------------------- |
| Understand why this project exists                    | [`docs/vision.md`](./docs/vision.md)           |
| Know exactly what fields get extracted                | [`docs/schema.md`](./docs/schema.md)           |
| Understand the sourcing → extraction → synthesis flow | [`docs/pipeline.md`](./docs/pipeline.md)       |
| Follow naming, file layout, schema-versioning rules   | [`docs/conventions.md`](./docs/conventions.md) |
| See the strategic roadmap (milestones, scope)         | [`docs/roadmap.md`](./docs/roadmap.md)         |
| See which models are queued / extracted / reviewed    | [`tasks/ROADMAP.md`](./tasks/ROADMAP.md)       |

## Repository layout

```
docs/                  Authoritative reference docs (vision, schema, pipeline, conventions, roadmap)
  glossary/            Per-technique wiki, bilingual — short entries with "Used by" tables
src/llm_tech_matrix/   Python package
  schema.py            Pydantic models — executable version of docs/schema.md
  sourcing/            Layer 1 — fetch HF configs, papers, blogs; manifest + sha256
  extraction/          Layer 2 — render.py (JSON → bilingual Markdown). Extraction itself
                       is driven by the .claude/skills/extract-model skill, not by code.
  synthesis/           Layer 3 — empty package; not started (see docs/roadmap.md)
scripts/               validate_extractions.py (the CI schema gate) + schema migrations
data/
  sources/<model>/     manifest.json (committed) + cached raw files (gitignored)
  extracted/<model>.json  Schema-validated extraction output (committed)
  extracted/<model>.md    Rendered English summary (committed, generated from the .json)
  extracted/<model>.zh.md Rendered Chinese summary (committed, generated from the .json)
  reports/             Generated synthesis reports — not created yet
tasks/
  ROADMAP.md           Per-model status table + Current focus
  models/<model>.md    Per-model notes, sources, open questions
.claude/skills/        Claude Code skills (extract-model, draft-pr)
```

No test suite yet — `scripts/validate_extractions.py` is the schema gate CI runs.

## Quickstart

This project is built with [`uv`](https://docs.astral.sh/uv/) on Python 3.13.

```bash
# Install / refresh the venv
uv sync

# Set up env vars
cp .env.example .env
# fill in HF_TOKEN

# Run the entry point
uv run python -m llm_tech_matrix
```

Adding a dependency:

```bash
uv add <package>
```

## Development setup

Once after cloning:

```bash
uv sync                       # install deps (runtime + dev)
uv run pre-commit install     # activate the git hook
```

Full guide — style, lint/format commands, CI, AI code review, PR
conventions — in [`docs/development.md`](./docs/development.md).

## Contributing a new model extraction

1. Add an entry to [`tasks/ROADMAP.md`](./tasks/ROADMAP.md) with status `backlog`, and
   create `tasks/models/<model-slug>.md` listing candidate source URLs.
2. Register the sources — this downloads them, records sha256, and writes the manifest:
   `uv run python -m llm_tech_matrix.sourcing add <slug> --name config --kind hf_config --url ... --filename config.json`
   (then `python -m llm_tech_matrix.sourcing.pdf_to_text <slug>` if any asset is a PDF).
3. Run the `extract-model` skill (or extract by hand following [`docs/schema.md`](./docs/schema.md))
   to produce `data/extracted/<model-slug>.json`.
4. Validate it against `src/llm_tech_matrix/schema.py` — this is what CI enforces.
5. Render the committed bilingual summaries:
   `uv run python -m llm_tech_matrix.extraction.render <slug>`. Never hand-edit the
   generated `.md` / `.zh.md` — change the JSON or the renderer instead.
6. Add "Used by" rows to the relevant [`docs/glossary/`](./docs/glossary/) entries (both
   `<entry>.md` and `<entry>.zh.md`), and update the roadmap status to `extracted`.

The full procedure lives in [`.claude/skills/extract-model/SKILL.md`](./.claude/skills/extract-model/SKILL.md).

## Cardinal rule

When information is not present in source material, the field value is the literal string `"[Unknown/Not Disclosed]"`. **Never hallucinate.** Half this project's value is data you can trust. See [`docs/schema.md`](./docs/schema.md#cardinal-rule-no-hallucination) for the full rule and the inferred-fields mechanism for closed models.
