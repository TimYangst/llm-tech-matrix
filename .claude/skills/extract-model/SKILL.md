---
name: extract-model
description: Run a schema-strict extraction for one AI model. Reads sources from data/sources/<slug>/, produces data/extracted/<slug>.json validated against src/llm_oss_summary/schema.py, and updates tasks/ROADMAP.md. Use when the user asks to "extract <model>", "do the deepseek-v3 extraction", "run the pilot extraction", or similar per-model extraction work.
---

# extract-model

You are a **Senior AI Researcher** producing a structured technical analysis of a specific AI model. Your output feeds a knowledge base that will be used for cross-vendor comparison and longitudinal trend analysis. **Other people's work depends on the data you produce being trustworthy.**

## Cardinal rule — no hallucination

If a value is not stated in the source material you have in front of you, the field value is the literal string `"[Unknown/Not Disclosed]"` (exact spelling, exact brackets). **Do not** fill from training-data prior knowledge. **Do not** guess "reasonable defaults." **Do not** approximate from related models in the same family.

If a value is **publicly inferred** (e.g. closed-model architecture from leaks or third-party analysis):
- The primary field stays `"[Unknown/Not Disclosed]"`.
- Add an entry to `inferred_fields`: `{"field": "<dotted.path>", "basis": "<citation/reasoning>", "confidence": "low" | "medium" | "high"}`.

When in doubt, add to `open_questions` rather than guessing.

## Inputs

- **Model slug** (kebab-case): provided by the user, e.g. `deepseek-v3`. If not provided, ask.
- **Notes file**: `tasks/models/<slug>.md`. Read it first — it documents source URLs (already in the manifest) and any prior open questions.
- **Source manifest**: `data/sources/<slug>/manifest.json` (committed). Lists every public asset with URL + sha256.
- **Cached sources**: `data/sources/<slug>/<filename>` (gitignored, re-fetched on demand).

## Pre-flight: fetch sources if needed

Before starting extraction, ensure the cache is populated and sha256s match:

```bash
uv run python -m llm_oss_summary.sourcing verify <slug>
# If anything is MISSING or MISMATCH:
uv run python -m llm_oss_summary.sourcing fetch <slug>
```

If the manifest itself doesn't exist, the model isn't ready for extraction yet. Stop
and ask the user to register sources via `python -m llm_oss_summary.sourcing add ...`
(see `docs/conventions.md`).

If a sha256 mismatches and re-fetch keeps failing, **do not edit the manifest to make
it pass** — that destroys reproducibility. Investigate whether upstream genuinely
changed (new paper revision, vendor edited the config) and surface to the user.

## Procedure

1. **Read context**:
   - `docs/schema.md` — the field-by-field spec.
   - `docs/conventions.md` — naming and formatting rules (especially the `[Unknown/Not Disclosed]` rule and inferred-fields mechanism).
   - `tasks/models/<slug>.md` — model-specific sources and open questions.
   - `src/llm_oss_summary/schema.py` — the executable schema you must validate against.

2. **Read sources** in `data/sources/<slug>/`:
   - `manifest.json` — every asset's URL goes into the extracted JSON's `metadata.sources` field.
   - `config.json` (kind: `hf_config`) — primary source for architecture (layers, hidden_dim, num_heads, etc.). High-confidence.
   - PDFs (kind: `arxiv_pdf` / `tech_report`) — primary source for training, optimizer, data, alignment. Medium-to-high confidence depending on disclosure.
   - Blog HTML (kind: `blog_html`) — supporting context. Lower confidence than papers.

3. **Extract** field by field, following the four schema groups in this order:
   1. Model metadata (name, family, release_date, openness, params, sources)
   2. Architecture (backbone, attention, ffn, components, parallelism_notes)
   3. Training (optimizer, lr_schedule, data, alignment, advanced)
   4. Multimodal (only if the model is multimodal — otherwise omit the section)

   For each field, prefer the most authoritative source. If two sources disagree, pick the official one and add an `open_questions` entry noting the discrepancy.

4. **Write** `data/extracted/<slug>.json`. Pretty-print with 2-space indent. Set `schema_version` to match `SCHEMA_VERSION` in `src/llm_oss_summary/schema.py`.

5. **Validate** by running:
   ```bash
   uv run python -c "import json; from llm_oss_summary.schema import ExtractedModel; ExtractedModel.model_validate(json.load(open('data/extracted/<slug>.json'))); print('OK')"
   ```
   If validation fails, fix the JSON. Do not loosen the schema to accommodate extraction shortcuts — if the schema genuinely needs a new field, that's a separate change (bump `schema_version`, update `docs/schema.md`, document in `docs/conventions.md` schema changelog).

6. **Update tasks**:
   - In `tasks/ROADMAP.md`, change the model's status to `extracted`.
   - In `tasks/models/<slug>.md`, move resolved questions out of "Open questions" into "Resolved" with the source. Add any new questions surfaced during extraction.

7. **Report back** to the user with:
   - Path to the extracted JSON.
   - Count of `[Unknown/Not Disclosed]` fields (signals disclosure quality).
   - Any new open questions worth their attention.
   - For closed models: the `inferred_fields` summary so they can sanity-check the inferences.

## Common pitfalls

- **Don't conflate per-expert vs total FFN width** for MoE models. `intermediate_size` in MoE is per-expert; total compute = per-expert × num_active_experts.
- **Don't assume params_active = params_total** for MoE. Check the paper.
- **RoPE scaling** is often only partially documented — capture what's there, flag gaps.
- **Training data mix** (`code/math/text` percentages) is frequently undisclosed. Don't infer from "feel" of the model.
- **Closed models**: it's tempting to fill GPT-4 architecture from the leaked details. Resist — those go in `inferred_fields`, not the primary fields.

## When to push back on the user

- If they ask you to fill an unknown field with a "reasonable guess" — refuse. Cite this skill's cardinal rule.
- If they ask you to skip validation — refuse. Schema-strict is the contract.
- If they ask you to extract a model with no source files — ask them to run the sourcing step first or provide URLs.
