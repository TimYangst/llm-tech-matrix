# Media schema v1

Implemented by [`media_schema.py`](../../src/llm_tech_matrix/media_schema.py).
Records live in `data/extracted/media/<slug>.json`. This version is independent of the
model and engine schemas.

## Validation and unknowns

- Required top-level groups: `metadata`, `generation`, `architecture`, `output`,
  `training`, `precision`, `release`. `media_schema_version` must explicitly equal `1`.
- Extra fields and coerced scalar types are rejected. All descriptive fields are
  strings; preserve source units and distinguish per-component/per-variant numbers.
- Unknown descriptive values use exactly `[Unknown/Not Disclosed]`. Blank strings and
  `null` are invalid. Empty optional lists mean no assertions were extracted, not that
  the capability is absent. Required input/output modality lists cannot be empty.
- Each group includes `evidence: {"field_name": ["source_url", ...]}`. Every known
  scalar and every populated list requires evidence. Evidence for unknown, empty or
  nonexistent fields is rejected. `metadata.sources` itself needs no evidence entry.
- Each evidence URL must match a `metadata.sources` URL after removing a fragment, so
  line anchors are supported. Sources must be public HTTP(S) URLs and cannot repeat.
- `metadata.sources` must exactly match `data/sources/<slug>/manifest.json` assets.
  Validation checks manifest slug and successful fetch metadata, including SHA-256.

## Fields

All fields below are strings unless indicated. Fields in `metadata` are required.
Other descriptive scalar fields default to the unknown marker; other lists default
empty unless explicitly marked required. Include the groups even when all their
details remain undisclosed.

| Group          | Fields                                                                                                               | Meaning                                                                                                                                                                                                                                                                                                                    |
| -------------- | -------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `metadata`     | `name`, `family`, `organization`, `release_date`, `openness`, `license`, `sources[]`, `variant_policy`               | Identity, official release month (`YYYY-MM`, or day when justified), license name and exact scope. `openness` is `open_weights`, `closed`, `mixed`, or the unknown marker. `sources` is a nonempty URL list. `variant_policy` names shared checkpoints and distinguishes hosted stages.                                    |
| `generation`   | `input_modalities[]`, `output_modalities[]`, `tasks[]`, `objective`, `scheduler`, `sampling`                         | Required nonempty modality lists use `text`, `image`, `video`, `audio`. Tasks name supported transformations. Objective preserves autoregressive, diffusion or flow-matching stages. Scheduler and sampling record actual released behavior, including per-modality schedules and published defaults.                      |
| `architecture` | `backbone`, `parameters`, `attention`, `conditioning`, `vae`, `audio_codec`, `multimodal_coupling`, `implementation` | Backbone names/classes and component sizes; attention and conditioning mechanisms; visual/audio VAE compression; discrete tokenizer/codebooks versus inference decoder; joint latent prediction; source-defined implementation components. Keep config key/value details in readable prose with the exact source citation. |
| `output`       | `resolution`, `frame_rate`, `duration`, `sample_rate`, `channels`, `formats[]`                                       | Limits of released generation. Distinguish temporal token rates from video FPS and waveform sampling frequency. Hosted enhancements belong in release scope.                                                                                                                                                               |
| `training`     | `data`, `pretraining`, `post_training`                                                                               | Disclosed corpus and training stages. A pretrained encoder does not imply its corpus is the generator's training corpus.                                                                                                                                                                                                   |
| `precision`    | `weights`, `compute`, `quantization`                                                                                 | Separate stored checkpoint types, example inference compute dtype and vendor-described quantization. An inference example does not establish training precision.                                                                                                                                                           |
| `release`      | `artifacts[]`, `hosted_scope`, `limitations[]`                                                                       | What can be downloaded, what remains hosted, licensing/reproduction limits and promised future releases. A hosted API is not an open implementation.                                                                                                                                                                       |

The optional top-level `open_questions[]` records unresolved source disagreements and
disclosure gaps, not positive technical assertions. It is not included in field evidence.

`openness` applies to the scope declared by `variant_policy`. Use `open_weights` for a
record of downloadable H3-Base checkpoints even though the complete H3 product also
uses hosted Context-IR and regeneration stages. Those stages must still appear under
`release.hosted_scope` and must not inflate the base output specifications. Use `mixed`
when the record explicitly covers both open and closed components as its primary
subject. A custom community license is still recorded verbatim; `open_weights` does
not assert an unrestricted or OSI-approved license. A service-only release uses `closed`
and leaves undisclosed architecture fields unknown.

## Rendering and synthesis

`extraction.render_media` renders all fields in a stable order, including unknowns,
into English and Chinese Markdown. Headers and field labels are bilingual; extracted
technical prose remains in its source language. `synthesis.media` generates a separate
bilingual index from validated media records. Neither changes the existing model
renderer or technique registry. `scripts/validate_extractions.py` checks both outputs
for freshness along with the independent media schema and source references.
