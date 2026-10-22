# Media generation track

Media generation has an independent record type alongside causal language models and
engine snapshots. A video diffusion model's VAEs, joint audio/video prediction and
scheduler do not fit causal-LM fields such as KV heads and context windows. A music
model may combine autoregressive codebook prediction with flow matching; the record
must preserve both stages.

This track covers MiniMax H3, Music3 and closed Speech 2.8. Multimodal **understanding** models
continue to use the model schema when their architecture fits it. Media records cover
image, audio and video **generation**, including mixed autoregressive/diffusion systems.
Other vendors remain follow-up work in the active project plan.

## Files and commands

```text
src/llm_tech_matrix/media_schema.py              independent media schema v1
data/sources/<slug>/manifest.json                source URLs and hashes
data/extracted/media/<slug>.json                 validated extraction
data/extracted/media/<slug>.md / <slug>.zh.md     generated bilingual views
data/extracted/media/README.md / README.zh.md    generated release index
```

Sources reuse the existing CLI's default source root:

```bash
uv run python -m llm_tech_matrix.sourcing add <slug> --name <name> --kind hf_config --url <url>
uv run python -m llm_tech_matrix.extraction.render_media --all
uv run python -m llm_tech_matrix.synthesis.media
uv run python scripts/validate_extractions.py
```

Both generators support `--check`. The extraction validator also checks source-manifest
consistency, recorded fetch/hash metadata and generated view/index freshness. It reads committed
manifests without requiring cached downloads. Schema, field evidence and missing/stale
output validation therefore run through the existing CI command.

## Scope and evidence

A record describes the released checkpoints and their vendor-published design. Keep
hosted orchestration, preprocessing and regeneration stages visible under
`release.hosted_scope`; do not ascribe their capabilities to the released base weights.
For example, H3's open base and the complete hosted H3 workflow have different scope.
Use `metadata.variant_policy` to explain a shared FL2VA/Ref2VA record, and qualify
variant-specific facts within each field.

Only official public sources support extracted claims. Pin repository and model-hub
files to revisions, register the exact URLs and hashes in the manifest, and cite them
per field. Unknown values stay `[Unknown/Not Disclosed]`; absence of disclosed details
never becomes an inferred architecture. Closed service claims belong to the released
service's declared scope, with undisclosed internals left unknown.

The [schema specification](./schema.md) is the field contract. The independent version
and [changelog](../conventions.md#media-schema-changelog) leave model schema v8 and
engine schema v3 unchanged. Media records are excluded from existing model/engine
synthesis joins; the media index consumes only media JSON.
