---
name: extract-model
description: Run a schema-strict extraction for one AI model. Reads sources from data/sources/<slug>/, produces data/extracted/<slug>.json validated against src/llm_tech_matrix/schema.py plus a rendered <slug>.md, and updates tasks/ROADMAP.md. Use when the user asks to "extract <model>", "do the deepseek-v3 extraction", "run the pilot extraction", or similar per-model extraction work.
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

## Pre-flight: populate the cache

Before starting extraction, ensure the cache is populated, sha256s match, and PDF text is derived:

```bash
uv run python -m llm_tech_matrix.sourcing verify <slug>
# If anything is MISSING or MISMATCH:
uv run python -m llm_tech_matrix.sourcing fetch <slug>
# Derive .txt from any PDF assets (cheap text for the rest of the run):
uv run python -m llm_tech_matrix.sourcing.pdf_to_text <slug>
```

If the manifest itself doesn't exist, the model isn't ready for extraction yet. Stop and ask the user to register sources via `python -m llm_tech_matrix.sourcing add ...` (see `docs/conventions.md`).

If a sha256 mismatches and re-fetch keeps failing, **do not edit the manifest to make it pass** — that destroys reproducibility. Investigate whether upstream genuinely changed (new paper revision, vendor edited the config) and surface to the user.

## Procedure

1. **Read context**:
   - `docs/schema.md` — the field-by-field spec (current SCHEMA_VERSION wins over older extractions).
   - `docs/conventions.md` — naming, formatting, and the schema changelog.
   - `tasks/models/<slug>.md` — model-specific sources and prior open questions.
   - `src/llm_tech_matrix/schema.py` — the executable schema you must validate against.
   - `docs/glossary/README.md` — scan to know which techniques have entries; you'll touch this in step 7.

2. **Read sources** in `data/sources/<slug>/`:
   - `manifest.json` — every asset's URL goes into the extracted JSON's `metadata.sources` field.
   - `config.json` (kind: `hf_config`) — primary source for architecture. High-confidence.
   - `<paper>.txt` (derived from `arxiv_pdf` / `tech_report` PDFs by pdf_to_text) — primary source for training, optimizer, data, alignment.
   - Blog HTML (kind: `blog_html`) — supporting context. Lower confidence than papers.

3. **Extract** field by field, following the four schema groups in this order:
   1. Model metadata (name, family, release_date, openness, params, sources)
   2. Architecture (backbone, attention incl. `mla` subobject if MLA, ffn incl. `dense_intermediate_size`/`moe`/`layer_partition` for hybrids, components, parallelism_notes)
   3. Training (optimizer, lr_schedule, data_total_tokens, data_mix, data_mix_notes, **objectives** (MTP/FIM/other), alignment, advanced)
   4. Multimodal (only if the model is multimodal — otherwise omit the section / set to null)

   For each field, prefer the most authoritative source. If two sources disagree, pick the official one and add an `open_questions` entry noting the discrepancy. Schema gaps belong in `open_questions` too — flag them; don't paper over with awkward field reuse.

4. **Write** `data/extracted/<slug>.json`. Pretty-print with 2-space indent. Set `schema_version` to match `SCHEMA_VERSION` in `src/llm_tech_matrix/schema.py`.

5. **Validate** the JSON:
   ```bash
   uv run python -c "import json; from llm_tech_matrix.schema import ExtractedModel; ExtractedModel.model_validate(json.load(open('data/extracted/<slug>.json'))); print('OK')"
   ```
   If validation fails, fix the JSON. **Do not loosen the schema to accommodate extraction shortcuts** — if the schema genuinely needs a new field, that's a separate change (bump `schema_version`, update `docs/schema.md`, document in `docs/conventions.md` schema changelog).

6. **Render the human-readable Markdown:**
   ```bash
   uv run python -m llm_tech_matrix.extraction.render <slug>
   ```
   This produces `data/extracted/<slug>.md` deterministically from the JSON. Both files are committed.

7. **Touch the glossary** (`docs/glossary/`):
   - For every distinctive technique referenced in your extraction (a new attention variant, MoE routing trick, training objective, optimizer, quantization recipe, etc.):
     - If an entry already exists, **add a row to its "Used by" table** for this model with the model-specific variant/details.
     - If no entry exists and the technique is meaningfully novel (not just a one-off naming difference), **create a new glossary entry** from `_template.md` and add it to `README.md`'s index.
   - Skip techniques that are universal commodities (e.g. "transformer block", "softmax") — the glossary is for things worth comparing across vendors.

8. **Update tasks**:
   - In `tasks/ROADMAP.md`, change the model's status to `extracted`.
   - In `tasks/models/<slug>.md`, move resolved questions to "Resolved" with the source; add any new questions surfaced during extraction.

9. **Report back** to the user with:
   - Path to the extracted JSON and rendered Markdown.
   - Count of `[Unknown/Not Disclosed]` fields (signals disclosure quality).
   - New glossary entries created (if any).
   - Any new open questions worth their attention.
   - For closed models: the `inferred_fields` summary so they can sanity-check the inferences.

## Common pitfalls

- **MoE per-expert vs total FFN width.** In v2, per-expert width is `ffn.moe.expert_intermediate_size`; the field is per-expert by definition. Don't put a total/sum here.
- **Hybrid dense+MoE FFNs.** Set `ffn_type: "hybrid"`, fill both `dense_intermediate_size` and `moe`, and describe the layer split in `layer_partition`.
- **MLA models.** Set `attention.num_kv_heads` and `attention.head_dim` to UNKNOWN; capture the real architecture in the `mla` subobject (field names mirror HF config keys).
- **`params_active` ≠ `params_total`** for MoE. Check the paper.
- **RoPE scaling** is often only partially documented — capture what's there, flag gaps.
- **Training data mix** (`code/math/text` percentages) is frequently undisclosed. Don't infer; use `data_mix_notes` for qualitative descriptions.
- **RLAIF.** Set `rlaif: true` ONLY if AI generates the preference labels themselves (e.g. Constitutional AI). A model-based reward model trained on human preferences is RLHF, not RLAIF.
- **Closed models.** It's tempting to fill GPT-4 / Claude architecture from leaks. Resist — those go in `inferred_fields`, not the primary fields.

## When to push back on the user

- If they ask you to fill an unknown field with a "reasonable guess" — refuse. Cite this skill's cardinal rule.
- If they ask you to skip validation — refuse. Schema-strict is the contract.
- If they ask you to extract a model with no source files — ask them to run the sourcing step first or provide URLs.
- If they ask you to commit `data/extracted/<slug>.md` without regenerating from the JSON — refuse. The .md is deterministic; if they want different content, change the JSON or the renderer.
