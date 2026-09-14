# Engine Snapshot Schema (engine schema v3)

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
- `roles` — list of `"inference"` / `"training"` / `"rl_post_training"`. each role has exactly one subobject —
  `inference` → `serving`, `training` → `training`, `rl_post_training` → `rl` — present exactly
  when the role is claimed. Claim a role only when the snapshot's own sources document it.
  List the primary role first: synthesis groups snapshots by it (Megatron-LM ships an inference
  engine, but it is a training library, so `training` comes first).
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

### `training` (role `training`, v2)

- Lists: `workloads` (pre-training, SFT, DPO, RL trainer backend…), `backends` (as the config
  names them, e.g. `fsdp2`, `megatron`), `optimizers`
- Prose: `mixed_precision`, `quantization_aware_training`, `checkpointing`, `lora`, `kernels`
- `notes`, `evidence` (same per-field rule as `serving`)

### `rl` (role `rl_post_training`, v2)

- Lists: `algorithms` (advantage-estimator / algorithm identifiers from code), `policy_losses`,
  `rollout_backends`, `trainer_modes`, `weight_sync_backends`
- Prose: `weight_sync`, `routing_replay`, `reward`, `distillation`
- `notes`, `evidence` (same per-field rule)

### `integrations[]`

`{name, relation, engine_slug, version_constraints, notes, evidence}`. `relation` is the
counterpart's role relative to *this* engine: `kernel_library` / `kv_transfer` /
`rollout_backend` / `training_backend` / `used_by` / `other` (verl lists vLLM as
`rollout_backend`; VeOmni lists verl as `used_by`). `engine_slug` is set when the counterpart
is itself a tracked engine snapshot, and must exist. `version_constraints` (v2) records each
source's version requirement side by side, naming the source — they often disagree (verl v0.9.0:
`setup.py` pins SGLang 0.5.8, Docker uses 0.5.12, docs say 0.4.8).

### `model_support[]`

One row per HF architecture (`architectures[0]`), the join key to model records.

- `hf_architecture`, `model_slugs` (model records using it)
- `support` (v2) — one of:
  - `registered`: in the engine's built-in model registry, whatever form it takes — vLLM's
    static `registry.py`, SGLang's `EntryClass` declarations, VeOmni's `MODELING_REGISTRY` keyed
    by model_type, Megatron-Bridge's `register_bridge(source=<architecture>)`;
  - `model_specific`: no registry entry (or no registry at all, like verl), but code or docs
    written for this architecture or its model_type exist at the commit;
  - `delegated` (v3): the engine maps no HF architectures itself, and its own sources name
    another tracked engine that does. `delegated_to` holds that engine's snapshot slug (it must
    exist, and must not be the record itself). Megatron-LM leaves HF conversion to
    Megatron-Bridge. Delegation records responsibility, not a tested pairing: the delegate's
    own row says whether the model is supported, and synthesis shows it through the delegation.
    Use it only when the snapshot has no in-repo signal for the architecture (otherwise
    `model_specific`), and verify the architecture string is absent tree-wide;
  - `not_found`: neither, verified across the whole repository at the commit. **Absent
    architectures get a row too**, with whole-file evidence; this is a snapshot fact, not a
    claim the model cannot run through a generic path (HF Transformers backends, FSDP).
- `delegated_to` (v3) — engine snapshot slug; set exactly when `support` is `delegated`
- `implementation` — module / class / patch that implements it
- `documented` — covered by the engine's supported-models docs (docs can lag code; vLLM's are
  architecture-level, SGLang's family-level — say which in `notes`)
- `features` — per-model doc columns, e.g. `{"lora": "marked", "pp": "not marked"}`
- `speculative_decoding` — methods with model-specific handling in code or docs
- `model_details[]` — per-model facts that do not follow from the architecture,
  `{model_slug, since_version, reasoning_parser, tool_call_parser, notes, evidence}`.
  `model_slug` must be one of the row's `model_slugs`, and appear at most once. Parsers only
  when docs map *that model*; `since_version` only when release notes or history state it for
  *that model*. These are per model because models sharing an architecture differ: SGLang
  v0.5.19 maps Kimi K2 Thinking, but not DeepSeek-V3, to the `kimi_k2` parsers (both
  `DeepseekV3ForCausalLM`), and lists Qwen3.8-27B as new on an already-supported
  `Qwen3_5ForConditionalGeneration`.
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

- Registry slots / generated "Implemented by (engines)" tables / support matrix — phase E4.
- Assessing non-native loading paths (Transformers modeling backend, plugins) for absent
  architectures.
