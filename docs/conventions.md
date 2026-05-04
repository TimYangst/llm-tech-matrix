# Conventions

## Naming

- **Model slug** — kebab-case, lowercase, version included. `deepseek-v3`, `llama-3.1-70b-instruct`, `qwen-2.5-72b`. Used as directory names and JSON filenames.
- **Family slug** — kebab-case family root: `deepseek`, `llama`, `qwen`. Used for grouping in synthesis.
- **Date format** — `YYYY-MM` for release dates (day-precision is rarely meaningful for model releases). Use full `YYYY-MM-DD` only inside `manifest.json` for fetch dates.

## File layout per model

```
data/sources/<model-slug>/
  manifest.json            # COMMITTED — URLs + sha256, the reproducibility contract
  config.json              # gitignored — local cache of HF config
  paper.pdf                # gitignored — local cache of tech report
  paper.txt                # gitignored — derived from paper.pdf (via pdf_to_text)
  blog-<n>.html            # gitignored — local cache of blog HTML
data/extracted/
  <model-slug>.json        # COMMITTED — schema-validated extraction output
```

The `.txt` siblings are derived artifacts produced by
`python -m llm_tech_matrix.sourcing.pdf_to_text <slug>`. They are cheap to regenerate
from the cached PDFs, so they are gitignored alongside the source files. LLM extraction
reads the `.txt` rather than re-rendering the PDF.

## Source assets: committed vs. cached

The `manifest.json` for each model **is committed**. The actual source files
(config, paper, blog HTML) **are not** — they're gitignored and re-fetched on demand
by `python -m llm_tech_matrix.sourcing fetch <slug>`. Two reasons:

1. PDFs and configs can be tens of MB and we don't need to mirror them — HF and
   arxiv are the canonical hosts.
2. The manifest's sha256 lets us detect if upstream silently changed, which is
   more useful than a frozen copy.

**Only public, openly-accessible sources qualify.** If an asset requires payment,
login, or non-public credentials beyond an HF account, do not list it — extract
that model only from public materials, or skip it. This is a hard rule.

For URL rot, optionally record an `archive_url` (web.archive.org snapshot) in the
manifest entry. If an upstream URL dies and there's no archive, the asset can be
re-sourced from any equivalent public location and the manifest updated.

### Adding a new source asset

```
uv run python -m llm_tech_matrix.sourcing add <slug> \
  --name <logical-name> \
  --kind <hf_config|arxiv_pdf|tech_report|blog_html|model_card|other> \
  --url <public-url> \
  [--filename <local-name>] \
  [--description "<human description>"] \
  [--archive-url <web-archive-url>]
```

The CLI downloads the file, computes its sha256, and appends to `manifest.json`.

## Marking unknowns

Always use the literal string `"[Unknown/Not Disclosed]"` — exact spelling, exact brackets. Synthesis tools rely on this string to detect missing data. Do not use `null`, `""`, `"unknown"`, `"N/A"`, or omit the field.

## Inferred values (closed models)

If a value is **public-but-not-officially-confirmed** (leaks, papers reverse-engineering closed models, vendor presentations):

- The primary field still uses `"[Unknown/Not Disclosed]"`.
- An entry is added to `inferred_fields` with `{field, basis, confidence}`.
- Synthesis tools can opt into using inferred values, but the default is to ignore them.

## Schema changelog

Schema changes are recorded here, newest first. The Pydantic models in `src/llm_tech_matrix/schema.py` carry a `schema_version: int` field — bump it on any breaking change.

| Version | Date | Change |
|---|---|---|
| 3 | 2026-05 | Qwen3-driven additions for context extension + multi-stage post-training. (a) `architecture.backbone` adds optional `context_extension` subobject `{method, trained_max, extended_max, factor, original_max, notes}` to capture trained-vs-deployed context gaps (YaRN, DCA, LongRoPE, etc.). None when a model uses its trained length without scaling tricks. (b) `training.alignment` adds `stages: list[{name, method, description}]` for multi-stage post-training pipelines (Qwen3's four-stage flow, DeepSeek-R1's stages). Empty list when flat `sft`/`rl_method` suffices. (c) `training.alignment` adds `inference_modes: list[{name, trigger, description}]` for runtime-switchable behaviors produced by post-training (Qwen3 thinking vs non-thinking, thinking-budget). Empty list for single-mode models. **Backwards-compatible**: all new fields are optional/default-empty. v2 records remain valid as v3 if you bump `schema_version` and leave new fields at their defaults. |
| 2 | 2026-05 | Pilot-driven additions/refactors. (a) `architecture.ffn` adds `"hybrid"` type, splits dense vs MoE intermediate sizes (`dense_intermediate_size` + `moe.expert_intermediate_size`), adds `layer_partition`. **Breaking**: v1's `ffn.intermediate_size` is removed; for MoE models its value moves into `ffn.moe.expert_intermediate_size`. (b) `architecture.attention` adds optional `mla` subobject mirroring HF config keys; `num_kv_heads` and `head_dim` may be UNKNOWN for MLA. (c) `architecture.backbone` adds `context_window_notes`. (d) `training.objectives` (with `multi_token_prediction`, `fill_in_middle`, `other`) becomes a first-class subobject. (e) `training.data_mix_notes` added. (f) RLAIF definition tightened: a model-based reward model trained on human preferences is RLHF, not RLAIF. |
| 1 | 2026-05 | Initial schema (M1 text + multimodal). |

## Commit conventions

- Each model extraction is its own commit: `extract: deepseek-v3`.
- Schema changes are their own commit: `schema: add MoE shared_experts field (v2)`.
- Synthesis reports: `report: optimizer evolution adam→muon`.
- Avoid mixing extraction and code changes in one commit — review of the JSON is faster when the diff is just JSON.

## When unsure, leave a question

Add an entry to `open_questions` in the extracted JSON rather than guessing. These get reviewed periodically and resolved either by re-reading the source or by accepting "we don't know."
