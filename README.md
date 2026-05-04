# LLM Tech Evolution Matrix

> 中文版：[README.zh.md](./README.zh.md)

A structured, continuously updatable knowledge base that tracks and decomposes the technical stacks of mainstream AI models — for **horizontal comparison** across vendors and **vertical analysis** of single techniques over time.

## Status

**Inception.** Scaffolding and design docs are in place; first extraction has not been run.

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
src/llm_tech_matrix/   Python package
  schema.py            Pydantic models — executable version of docs/schema.md
  sourcing/            Layer 1 — fetch HF configs, papers, blogs
  extraction/          Layer 2 — schema-strict LLM extraction
  synthesis/           Layer 3 — cross-model comparison and trend reports
data/
  sources/<model>/     Raw fetched files (config.json, paper.pdf, manifest.json)
  extracted/<model>.json  Schema-validated extraction output (committed)
  reports/             Generated synthesis reports
tasks/
  ROADMAP.md           Per-model status table
  models/<model>.md    Per-model notes, sources, open questions
.claude/skills/        Claude Code skills (extract-model, etc.)
tests/                 Schema validation and pipeline tests
```

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

## Contributing a new model extraction

1. Add an entry to [`tasks/ROADMAP.md`](./tasks/ROADMAP.md) with status `backlog`.
2. Create `tasks/models/<model-slug>.md` listing source URLs.
3. Run the `extract-model` skill (or manual extraction following [`docs/schema.md`](./docs/schema.md)).
4. Validate the output `data/extracted/<model-slug>.json` against `src/llm_tech_matrix/schema.py`.
5. Update the roadmap status to `extracted`.

## Cardinal rule

When information is not present in source material, the field value is the literal string `"[Unknown/Not Disclosed]"`. **Never hallucinate.** Half this project's value is data you can trust. See [`docs/schema.md`](./docs/schema.md#cardinal-rule-no-hallucination) for the full rule and the inferred-fields mechanism for closed models.
