# Engine Snapshot Schema (engine schema v2)

The contract for `data/extracted/engines/<slug>.json`. The executable version is
[`src/llm_tech_matrix/engine_schema.py`](../../src/llm_tech_matrix/engine_schema.py); if the
two diverge, the Pydantic model wins and this page must be updated. Design rationale:
[`overview.md`](./overview.md). Changelog: [`../conventions.md`](../conventions.md#engine-schema-changelog).

The engine schema version is **independent** of the model schema (`schema_version`, currently
v8). A record declares `engine_schema_version`.

## Cardinal rules

- **No hallucination.** Unsourced values are `"[Unknown/Not Disclosed]"`.
- **Evidence on every claim.** Evidence entries are URLs pinned to the snapshot commit —
  `https://github.com/<org>/<repo>/blob/<sha>/<path>#L<n>` — or the tag's release page for
  release-note claims. Validation rejects:
  - a populated `serving` field with no `serving.evidence[<field>]` entry (and evidence keys
    for fields that are not populated);
  - a `parallelism.<dim>.supported` value other than UNKNOWN with no evidence;
  - any `integrations[]`, `model_support[]` or `technique_support[]` row without evidence.
- **Cross-links are checked** by `scripts/validate_extractions.py`:
  - the filename is `<engine>-<release_tag>` (lowercase);
  - `commit_sha` is a full 40-character SHA;
  - every `model_slugs` entry has a `data/extracted/<slug>.json`;
  - every `glossary_slug` has a `docs/glossary/<slug>.md`.

## Fields

### `metadata`

- `name`, `engine` (lowercase id used in the slug), `organization`, `repository` (upstream,
  never a fork), `license` (SPDX)
- `release_tag`, `commit_sha`, `release_date` (`YYYY-MM-DD` or UNKNOWN), `snapshot_date`
- `roles` — list of `"inference"` / `"training"` / `"rl_post_training"`. **v2 implements only
  `inference`**; a record claiming the other two fails validation until their subobjects exist.
- `hardware` — platforms the snapshot's own sources name
- `sources` — every URL in the snapshot's manifest

### `parallelism`

Six dimensions — `tensor`, `pipeline`, `data`, `expert`, `context`, `sequence` — each
`{supported, implementation, notes, evidence}`. `supported` is `true` / `false` with evidence,
or UNKNOWN.

### `serving` (role `inference`)

- Prose, summarizing design docs: `scheduler`, `kv_cache_management`, `prefix_caching`,
  `disaggregation`
- Lists, copied from the engine's own registries at the pinned commit (reproducible, not
  curated): `api_surfaces`, `speculative_decoding_methods`, `quantization_methods`,
  `kv_cache_dtypes`, `attention_backends`, `reasoning_parsers`, `tool_call_parsers`
- `notes` — including how each list was derived
- `evidence` — `{field_name: [urls]}` for every populated field

A parser or backend *name* matching a model family is not a model mapping — mappings live
in `model_support[]` and only where docs state them.

### `integrations[]`

`{name, relation, engine_slug, notes, evidence}`. `relation` ∈ `kernel_library` /
`kv_transfer` / `rollout_backend` / `training_backend` / `other`. `engine_slug` is set when
the counterpart is itself a tracked engine snapshot.

### `model_support[]`

One row per HF architecture (`architectures[0]`), the join key to model records. "Native
registry" means the engine's built-in model list, whatever form it takes: vLLM's static
`registry.py` table, or SGLang's `EntryClass` declarations under `srt/models/`.

- `hf_architecture`, `model_slugs` (model records using it)
- `in_native_registry` — bool. **Absent architectures get a row too**, with whole-file
  evidence; absence from the native registry is a snapshot fact, not a claim the model
  cannot run through another path.
- `implementation` — module / class the registry maps to
- `documented` — covered by the engine's supported-models docs (docs can lag code; vLLM's are
  architecture-level, SGLang's family-level — say which in `notes`)
- `features` — per-model doc columns, e.g. `{"lora": "marked", "pp": "not marked"}`
- `speculative_decoding` — methods with model-specific handling in code or docs
- `model_details[]` **(v2)** — per-model facts that do not follow from the architecture,
  `{model_slug, since_version, reasoning_parser, tool_call_parser, notes, evidence}`.
  `model_slug` must be one of the row's `model_slugs`, and appear at most once. Parsers only
  when docs map *that model*; `since_version` only when release notes or history state it for
  *that model*. (v1 had these three fields on the row, which broke as soon as two models shared
  an architecture — see the changelog.)
- `notes`, `evidence`

### `technique_support[]`

`{glossary_slug, implementation, flags, since_version, notes, evidence}` — an engine-side
implementation of a glossary technique. Assertions only: a backend named `*_DSV4` does not
assert CSA/HCA; a quantization method named `mxfp4` does not assert the `fp4-qat` training
recipe. Unassertable near-misses belong in `open_questions`.

### `open_questions[]`

Doc/code disagreements, name-based near-misses, reproducibility caveats, and things a later
snapshot should settle.

## Not in v2 (deliberately)

- `training` and `rl` role subobjects — arrive with the first snapshots that need them
  (`verl-v0.9.0`, `veomni-v0.1.12`, phase E3).
- Registry slots / generated "Implemented by (engines)" tables / support matrix — phase E4.
- Assessing non-native loading paths (Transformers modeling backend, plugins) for absent
  architectures.
