# Conventions

## Naming

- **Model slug** — kebab-case, lowercase, version included. `deepseek-v3`, `llama-3.1-70b-instruct`, `qwen-2.5-72b`. Used as directory names and JSON filenames.
- **Family slug** — kebab-case family root: `deepseek`, `llama`, `qwen`. Used for grouping in synthesis.
- **Date format** — `YYYY-MM` for release dates (day-precision is rarely meaningful for model releases). Use full `YYYY-MM-DD` only inside `manifest.json` for fetch dates.

## File layout per model

```
data/sources/<model-slug>/
  manifest.json            # what was fetched, from where, when
  config.json              # from HuggingFace
  paper.pdf                # tech report (if any)
  blog-<n>.html            # additional sources, numbered
data/extracted/
  <model-slug>.json        # final extracted JSON, schema-validated
```

## Marking unknowns

Always use the literal string `"[Unknown/Not Disclosed]"` — exact spelling, exact brackets. Synthesis tools rely on this string to detect missing data. Do not use `null`, `""`, `"unknown"`, `"N/A"`, or omit the field.

## Inferred values (closed models)

If a value is **public-but-not-officially-confirmed** (leaks, papers reverse-engineering closed models, vendor presentations):

- The primary field still uses `"[Unknown/Not Disclosed]"`.
- An entry is added to `inferred_fields` with `{field, basis, confidence}`.
- Synthesis tools can opt into using inferred values, but the default is to ignore them.

## Schema changelog

Schema changes are recorded here, newest first. The Pydantic models in `src/llm_oss_summary/schema.py` carry a `schema_version: int` field — bump it on any breaking change.

| Version | Date | Change |
|---|---|---|
| 1 | 2026-05 | Initial schema (M1 text + multimodal). |

## Commit conventions

- Each model extraction is its own commit: `extract: deepseek-v3`.
- Schema changes are their own commit: `schema: add MoE shared_experts field (v2)`.
- Synthesis reports: `report: optimizer evolution adam→muon`.
- Avoid mixing extraction and code changes in one commit — review of the JSON is faster when the diff is just JSON.

## When unsure, leave a question

Add an entry to `open_questions` in the extracted JSON rather than guessing. These get reviewed periodically and resolved either by re-reading the source or by accepting "we don't know."
