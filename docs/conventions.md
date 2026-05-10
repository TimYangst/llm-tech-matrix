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

Schema changes are recorded here, newest first. The Pydantic models in `src/llm_tech_matrix/schema.py` carry a `schema_version: int` field — bump it on any change (breaking or backwards-compatible). On every bump, migrate **all** `data/extracted/*.json` files in the same commit so `scripts/validate_extractions.py` (the CI gate) stays green; for backwards-compat additions the migration is a one-line `schema_version` bump.

| Version | Date    | Change                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| ------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 6       | 2026-05 | Qwen3.5/3.6-driven additions for cross-vendor *release-strategy* and *runtime-mode* comparison. (a) `metadata.variant_policy` adds an optional free-text field describing how the vendor partitions capabilities across weight checkpoints vs. runtime modes (Qwen3.5/3.6: unified weights with chat-template kwargs; Qwen2.5: separate Math / Coder / VL / Audio / Omni checkpoints; DeepSeek-V4: 3 reasoning-effort modes via system prompt). UNKNOWN when not disclosed. (b) `training.alignment.inference_modes[]` adds optional `kwargs` and `sampling_recommended` (both `dict[str, str]`, default empty) to make the chat-template kwargs and per-mode sampling recommendations machine-queryable instead of buried in free-text trigger / description strings. (c) `training.alignment.tool_call_protocol` adds an optional `ToolCallProtocol` subobject (None when omitted) `{format, start_token, end_token, arguments_schema, parser_flags, notes}` to capture the wire format the model emits for tool calls plus the serving-stack parser flags that decode it (Qwen3.5/3.6 Qwen3-Coder XML-like protocol with `qwen3_coder` parser). **Backwards-compatible**: all new fields are optional with sensible defaults. v5 records remain valid as v6 if you bump `schema_version` and leave the new fields at defaults. |
| 5       | 2026-05 | DeepSeek-V4-driven additions for residual-stream topology and training stability tricks. (a) `architecture.residual_connections` adds optional `ResidualConfig` subobject (None when omitted) `{kind, expansion_factor, constraint, iterations, dynamic_parameterization, notes}` to capture inter-layer residual-stream topology beyond standard residual (DeepSeek-V4's Manifold-Constrained Hyper-Connections / mHC; HC variants). None when the model uses standard residual connections (the common case). (b) `training.stability_notes` adds an optional free-text field for training-stability tricks distinct from optimizer / lr_schedule / mixed_precision (DeepSeek-V4's Anticipatory Routing decouples routing-net synchronization from backbone updates with Δt-step lag; SwiGLU Clamping bounds linear and gate components). Empty string when no reported tricks. **Backwards-compatible**: both new fields are optional with defaults. v4 records remain valid as v5 if you bump `schema_version` and leave the new fields at defaults. CSA/HCA hybrid attention was considered for a structured slot in this round but deferred to schema iteration when a second model adopts compressed attention. FP4 QAT recipe similarly deferred until a second FP4-QAT model recurs.                                     |
| 4       | 2026-05 | Qwen3.5/3.6-driven additions for hybrid attention stacks + native VL. (a) `architecture.attention` adds optional `variants: list[{name, family, num_query_heads, num_kv_heads, head_dim, rope, notes}]` and `layer_pattern: str` to model multi-variant attention stacks (Qwen3.5/3.6 interleave Gated DeltaNet + Gated Attention 3:1). Empty list / empty string for single-variant stacks. (b) `RoPEType` Literal adds `"mrope"` for multimodal RoPE. (c) Top-level `multimodal` field is overhauled from 4 free strings to a structured object: `modalities`, `fusion` (refined enum: `native_early` / `projection_mlp` / `cross_attention` / `resampler` / `other` / UNKNOWN), `fusion_notes`, optional `vision_encoder` (depth, hidden_size, intermediate_size, num_heads, patch_size, in_channels, output_dim, spatial_merge_size, temporal_patch_size, notes — names mirror HF `vision_config` keys), optional `vision_token_anchors` (image / video / vision_start / vision_end token IDs), `audio_encoder` and `audio_notes` (free-form for now). **Breaking** for the Multimodal subobject; all v3 extractions had `multimodal: null` so the migration is a pure `schema_version` bump.                                                                                                                                 |
| 3       | 2026-05 | Qwen3-driven additions for context extension + multi-stage post-training. (a) `architecture.backbone` adds optional `context_extension` subobject `{method, trained_max, extended_max, factor, original_max, notes}` to capture trained-vs-deployed context gaps (YaRN, DCA, LongRoPE, etc.). None when a model uses its trained length without scaling tricks. (b) `training.alignment` adds `stages: list[{name, method, description}]` for multi-stage post-training pipelines (Qwen3's four-stage flow, DeepSeek-R1's stages). Empty list when flat `sft`/`rl_method` suffices. (c) `training.alignment` adds `inference_modes: list[{name, trigger, description}]` for runtime-switchable behaviors produced by post-training (Qwen3 thinking vs non-thinking, thinking-budget). Empty list for single-mode models. **Backwards-compatible**: all new fields are optional/default-empty. v2 records remain valid as v3 if you bump `schema_version` and leave new fields at their defaults.                                                                                                                                                                                                                                                                                                                                  |
| 2       | 2026-05 | Pilot-driven additions/refactors. (a) `architecture.ffn` adds `"hybrid"` type, splits dense vs MoE intermediate sizes (`dense_intermediate_size` + `moe.expert_intermediate_size`), adds `layer_partition`. **Breaking**: v1's `ffn.intermediate_size` is removed; for MoE models its value moves into `ffn.moe.expert_intermediate_size`. (b) `architecture.attention` adds optional `mla` subobject mirroring HF config keys; `num_kv_heads` and `head_dim` may be UNKNOWN for MLA. (c) `architecture.backbone` adds `context_window_notes`. (d) `training.objectives` (with `multi_token_prediction`, `fill_in_middle`, `other`) becomes a first-class subobject. (e) `training.data_mix_notes` added. (f) RLAIF definition tightened: a model-based reward model trained on human preferences is RLHF, not RLAIF.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 1       | 2026-05 | Initial schema (M1 text + multimodal).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |

## Commit conventions

- Each model extraction is its own commit: `extract: deepseek-v3`.
- Schema changes are their own commit: `schema: add MoE shared_experts field (v2)`.
- Synthesis reports: `report: optimizer evolution adam→muon`.
- Avoid mixing extraction and code changes in one commit — review of the JSON is faster when the diff is just JSON.

## When unsure, leave a question

Add an entry to `open_questions` in the extracted JSON rather than guessing. These get reviewed periodically and resolved either by re-reading the source or by accepting "we don't know."
