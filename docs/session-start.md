# Session start: picking up the project

Read this when you (or a fresh Claude Code agent) need to pick up where we left off.

## Three-step orientation

1. **Read [`tasks/ROADMAP.md`](../tasks/ROADMAP.md)** — `Current focus` at top + per-model status table.
2. **Skim [`data/extracted/`](../data/extracted/)** — every extracted model has both `<slug>.json` (canonical data) and `<slug>.md` (readable summary).
3. **Pick a task** — if `Current focus` recommends a next model, do that. Otherwise see *How to pick a next task* below.

## The 60-second project description

Schema-driven AI extraction-and-synthesis pipeline for analyzing mainstream AI models.
Three decoupled layers: **sourcing → extraction → synthesis**. Open-weight models are
analyzed deeply via HF `config.json` + tech reports; closed models are inferred from
public signals (paper leaks, public talks) with explicit `inferred_fields` annotations.

Three load-bearing rules:

- **No hallucination.** Missing data → the literal string `"[Unknown/Not Disclosed]"`.
- **Schema-strict.** Every extracted JSON validates against `src/llm_tech_matrix/schema.py`.
- **Public-source-only.** No paywalled or login-gated material.

For depth: [`docs/vision.md`](./vision.md), [`docs/schema.md`](./schema.md),
[`docs/pipeline.md`](./pipeline.md), [`docs/conventions.md`](./conventions.md).

## File map

| Location | Purpose |
|---|---|
| `CLAUDE.md` | Always loaded by Claude Code. Cardinal rules + pointers. |
| `docs/` | Authoritative reference docs. |
| `docs/schema.md` | Field-by-field extraction spec (current version). |
| `docs/conventions.md` | Naming, file layout, **schema changelog**. |
| `docs/glossary/` | Per-technique wiki — short entries, "Used by" tables. |
| `docs/roadmap.md` | Strategic milestones (M1/M2 scope). |
| `tasks/ROADMAP.md` | Per-model status table + **Current focus**. |
| `tasks/models/<slug>.md` | Per-model notes, sources, open questions. |
| `data/sources/<slug>/manifest.json` | Source URLs + sha256 (**committed**). |
| `data/sources/<slug>/<file>` | Cached source files (gitignored). |
| `data/extracted/<slug>.json` | Schema-validated extraction (**committed**). |
| `data/extracted/<slug>.md` | Rendered readable summary (**committed**; deterministic from .json). |
| `src/llm_tech_matrix/schema.py` | Pydantic schema (executable spec; wins over docs/schema.md on conflict). |
| `src/llm_tech_matrix/sourcing/` | Fetch CLI, manifest schema, pdf_to_text. |
| `src/llm_tech_matrix/extraction/render.py` | JSON → Markdown renderer. |
| `.claude/skills/extract-model/` | The Senior AI Researcher skill — invoke when extracting. |

## How to pick a next task

In rough priority order:

1. **Resolve open schema gaps first.** If the most recent extraction's `open_questions`
   include schema deficiencies (look in the JSON or the model's notes file), do a schema
   iteration *before* the next extraction. Working around the same gap in five
   extractions compounds the cleanup cost.

2. **Add a model from a different family** than the most recent one. Cross-family data
   points stress-test the schema better than re-extracting a sibling. If the last few
   extractions are all Qwen / DeepSeek, rotate to Llama / Mistral / GLM / Kimi before
   adding another sibling in the same family.

3. **Pick what stresses a different schema region.** Just did MoE? Do a dense model
   next. Just did open weights? Do a closed model to exercise `inferred_fields`. Just
   did text-only? Do a multimodal one.

4. **Don't build the synthesis layer yet.** Don't write cross-model reports until
   ≥10 models are extracted (per [`docs/roadmap.md`](./roadmap.md) M1 exit criteria).

## Common workflows

### Extract a new model

Full procedure: [`.claude/skills/extract-model/SKILL.md`](../.claude/skills/extract-model/SKILL.md). Quick version:

```bash
# 1. Register source URLs (downloads + sha256 + writes manifest):
uv run python -m llm_tech_matrix.sourcing add <slug> --name config --kind hf_config --url <url> --filename config.json --description "..."
uv run python -m llm_tech_matrix.sourcing add <slug> --name paper  --kind arxiv_pdf --url <url> --filename paper.pdf  --description "..."

# 2. Derive .txt from PDFs (cheap text for downstream reading):
uv run python -m llm_tech_matrix.sourcing.pdf_to_text <slug>

# 3. Read sources, fill data/extracted/<slug>.json per docs/schema.md.

# 4. Validate against the Pydantic schema:
uv run python -c "import json; from llm_tech_matrix.schema import ExtractedModel; ExtractedModel.model_validate(json.load(open('data/extracted/<slug>.json'))); print('OK')"

# 5. Render the human-readable Markdown:
uv run python -m llm_tech_matrix.extraction.render <slug>

# 6. Update tasks/ROADMAP.md status, tasks/models/<slug>.md notes, and glossary "Used by" tables.
```

### Iterate the schema

When real extractions surface a structural gap (not just an unknown value):

1. Bump `SCHEMA_VERSION` in `src/llm_tech_matrix/schema.py`.
2. Update `docs/schema.md` to match.
3. Document the change in `docs/conventions.md` "Schema changelog" (newest first).
4. Migrate existing `data/extracted/*.json` files. Re-validate. Re-render `.md` files
   via `python -m llm_tech_matrix.extraction.render --all`.

### Add or update a glossary entry

- New technique: copy `docs/glossary/_template.md` → `<slug>.md`, fill in, link from
  `docs/glossary/README.md` index.
- Existing technique referenced by a new extraction: add a row to that entry's
  "Used by" table with the model-specific variant/details.

## What just happened (recent context)

See `tasks/ROADMAP.md` "Current focus" for the one-line summary, and `git log --oneline`
for the change history. Don't re-derive from this doc — it'll go stale.
