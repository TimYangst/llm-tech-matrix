# Session start: picking up the project

Read this when you (or a fresh Claude Code agent) need to pick up where we left off.

## Three-step orientation

1. **Read [`tasks/ROADMAP.md`](../tasks/ROADMAP.md)** — `Current focus` at top + per-model status table.
2. **Skim [`data/extracted/README.md`](../data/extracted/README.md)** — the generated model index (family, date, size, techniques). Every model has `<slug>.json` (canonical data), `<slug>.md` and `<slug>.zh.md` (readable summaries). For the cross-model view start at [`data/reports/technique-index.md`](../data/reports/technique-index.md); for which engines serve or train each model, [`data/reports/engine-support-matrix.md`](../data/reports/engine-support-matrix.md).
3. **Pick a task** — if `Current focus` recommends a next model, do that. Otherwise see *How to pick a next task* below.

## The 60-second project description

Schema-driven AI extraction-and-synthesis pipeline for analyzing mainstream AI models.
Three decoupled layers: **sourcing → extraction → synthesis**. Open-weight models are
analyzed deeply via HF `config.json` + tech reports; closed models are inferred from
public signals (paper leaks, public talks) with explicit `inferred_fields` annotations.

Three load-bearing rules:

- **No hallucination.** Missing data → the literal string `"[Unknown/Not Disclosed]"`.
- **Schema-strict.** LLM/VL, engine and media JSON use `schema.py`, `engine_schema.py` and `media_schema.py` respectively.
- **Public-source-only.** No paywall or privileged/nonpublic access. Ordinary HF-account access follows the [source convention](conventions.md#source-assets-committed-vs-cached).

For depth: [`docs/vision.md`](./vision.md), [`docs/schema.md`](./schema.md),
[`docs/pipeline.md`](./pipeline.md), [`docs/conventions.md`](./conventions.md).

## File map

| Location                                   | Purpose                                                                       |
| ------------------------------------------ | ----------------------------------------------------------------------------- |
| `CLAUDE.md`                                | Always loaded by Claude Code. Cardinal rules + pointers.                      |
| `docs/`                                    | Authoritative reference docs.                                                 |
| `docs/schema.md`                           | Field-by-field extraction spec (current version).                             |
| `docs/conventions.md`                      | Naming, file layout, **schema changelog**.                                    |
| `docs/glossary/`                           | Per-technique wiki — short entries, "Used by" tables.                         |
| `docs/roadmap.md`                          | Strategic milestones (M1/M2 scope).                                           |
| `tasks/ROADMAP.md`                         | Per-model status table + **Current focus**.                                   |
| `tasks/models/<slug>.md`                   | Per-model notes, sources, open questions.                                     |
| `data/sources/<slug>/manifest.json`        | Source URLs + sha256 (**committed**).                                         |
| `data/sources/<slug>/<file>`               | Cached source files (gitignored).                                             |
| `data/extracted/<slug>.json`               | Schema-validated extraction (**committed**).                                  |
| `data/extracted/<slug>.md`                 | Rendered readable summary (**committed**; deterministic from .json).          |
| `src/llm_tech_matrix/schema.py`            | Pydantic schema (executable spec; wins over docs/schema.md on conflict).      |
| `src/llm_tech_matrix/sourcing/`            | Fetch CLI, manifest schema, pdf_to_text.                                      |
| `src/llm_tech_matrix/extraction/render.py` | JSON → Markdown renderer.                                                     |
| `.claude/skills/extract-model/`            | The Senior AI Researcher skill — invoke when extracting.                      |
| `docs/glossary/registry.json`              | Controlled vocabulary: typed field values → glossary entries.                 |
| `src/llm_tech_matrix/synthesis/index.py`   | Generates the model index, technique matrix and coverage report.              |
| `scripts/validate_extractions.py`          | The schema gate — run it separately from formatting hooks before pushing.     |
| `scripts/migrate_v*.py`                    | One-off schema migrations, one per version bump.                              |
| `docs/engines/overview.md`                 | Engines track design: roles, snapshots, evidence rules, current contract.     |
| `tasks/ENGINES.md`                         | Engines track status + quarterly snapshot calendar.                           |
| `docs/media/overview.md`                   | Media workflow and independent schema/renderer/index.                         |
| `data/extracted/media/`                    | Media JSON and bilingual summaries/index.                                     |
| `src/llm_tech_matrix/engine_schema.py`     | Engine snapshot schema (independent version). Spec: `docs/engines/schema.md`. |
| `.claude/skills/extract-engine/`           | Engine snapshot procedure — invoke when recording an engine release.          |

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

4. **Use the existing synthesis surfaces.** `synthesis/index.py` already generates
   the model index, technique/coverage reports and engine-support/adoption reports.
   An interpretive trend report remains outstanding; choose one question before
   expanding infrastructure. Audio/video generation has its own [media track](media/overview.md)
   and [index](../data/extracted/media/README.md), separate from LLM technique edges.

5. **The other standing gap is closed models.** `inferred_fields` is empty across the LLM
   records, so the mechanism the schema was designed around has never run. A closed LLM requires a schema check first: v8 cannot represent an unknown
   FFN type. `qwen3.7-max` is one candidate (see
   [`tasks/ROADMAP.md`](../tasks/ROADMAP.md)).

### Engines track

The engines track (vLLM, SGLang, verl, VeOmni, Megatron-LM, Megatron-Bridge) runs in parallel to the model queue and has
its own status file. If the user asks for engine work, or the quarterly snapshot is due,
start from [`tasks/ENGINES.md`](../tasks/ENGINES.md) and
[`docs/engines/overview.md`](./engines/overview.md) instead of the priority list above.

### Active DeepSeek / MiniMax refresh

Start from [the sole coordination state](../tasks/deepseek-minimax-refresh.md)
when continuing this phase. It records scope, permissions, review evidence and the
next action; do not create a second task table.

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

# 6. Update tasks/ROADMAP.md, model notes, glossary rows and registry aliases.

# 7. Regenerate browse surfaces and validate both contracts and registry:
uv run python -m llm_tech_matrix.synthesis.index
uv run python scripts/validate_extractions.py
uv run python scripts/validate_registry.py
```

### Iterate the schema

When real extractions surface a structural gap (not just an unknown value):

1. Bump `SCHEMA_VERSION` in `src/llm_tech_matrix/schema.py`.
2. Update `docs/schema.md` to match.
3. Document the change in `docs/conventions.md` "Schema changelog" (newest first).
4. Migrate existing `data/extracted/*.json` files. Re-validate. Re-render `.md` files
   via `python -m llm_tech_matrix.extraction.render --all`.

### Snapshot an engine release

Full procedure: [`.claude/skills/extract-engine/SKILL.md`](../.claude/skills/extract-engine/SKILL.md).
Sources go through `python -m llm_tech_matrix.sourcing --track engines add <slug> ...`
(pinned to the tag commit). Records live in `data/extracted/engines/`, are validated by
`scripts/validate_extractions.py` and rendered with
`python -m llm_tech_matrix.extraction.render_engine <slug>`.

### Extract a media generation release

Read the [media guide](media/overview.md) and [schema](media/schema.md).
Register public sources under `data/sources/<slug>/`, then write
`data/extracted/media/<slug>.json` with field-level evidence.

```bash
uv run python -m llm_tech_matrix.extraction.render_media <slug>
uv run python -m llm_tech_matrix.synthesis.media
uv run python scripts/validate_extractions.py
uv run python scripts/validate_registry.py
```

### Add or update a glossary entry

- New technique: copy `docs/glossary/_template.md` → `<slug>.md`, fill in, link from
  `docs/glossary/README.md` index.
- Existing technique referenced by a new extraction: add a row to that entry's
  "Used by" table with the model-specific variant/details.

## What just happened (recent context)

See `tasks/ROADMAP.md` "Current focus" for the one-line summary, and `git log --oneline`
for the change history. Don't re-derive from this doc — it'll go stale.
