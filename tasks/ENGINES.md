# Engines Roadmap

Tactical, snapshot-by-snapshot status for the engines track. For the design (roles, layout,
evidence rules, current schema, phases), see [`../docs/engines/overview.md`](../docs/engines/overview.md).
Model status stays in [`ROADMAP.md`](./ROADMAP.md).

## Current focus

**E0–E5 complete; maintenance mode.** Six 2026-Q3 engine snapshots use engine
schema v3. The [support matrix](../data/reports/engine-support-matrix.md),
[adoption report](../data/reports/engine-adoption.md) and generated glossary
engine tables exist and are checked by the registry validator.

The new DeepSeek/MiniMax and media records do not refresh engine evidence.
New LLMs without an explicit model mapping are unassessed in the historical
snapshots; media generation records are outside the current model/engine joins.
Use the matrix and each snapshot's notes to distinguish registered, model-specific,
delegated, not-found and unassessed support.

Next planned cycle is 2026-Q4 at quarter end; on-demand refreshes can start earlier
under the policy below. Choose a current upstream tag at execution time, not from
this Q3 list. Prioritize the new DeepSeek/MiniMax mapping gaps and existing
adoption-report refresh questions. No new engine snapshot was run in PR #21.

Per-snapshot findings are in `tasks/engines/` and the canonical records. Earlier
phase narratives remain in the [pre-cleanup snapshot](https://github.com/TimYangst/llm-tech-matrix/blob/1b72ed94d6ba7378e3da805d6ff498bfd2a13881/tasks/ENGINES.md).

## Snapshot policy

- **Quarterly.** At each quarter's snapshot, take the latest non-prerelease upstream tag for
  each tracked engine.
- **On-demand refreshes** in between, for three triggers only:
  - A newly extracted model needs engine-side support recorded.
  - A release changes a role subobject.
  - A synthesis question needs a version no snapshot has.
- Snapshots accumulate under their own slugs (`<engine>-<release-tag>`); none is overwritten.

## Tracked engines

| Engine          | Upstream                                                                        | Role(s)                                     | Licence                                 | Release cadence (from tag history)                                           |
| --------------- | ------------------------------------------------------------------------------- | ------------------------------------------- | --------------------------------------- | ---------------------------------------------------------------------------- |
| vLLM            | [`vllm-project/vllm`](https://github.com/vllm-project/vllm)                     | `inference`                                 | Apache-2.0                              | ~2 weeks (v0.27.1 08-11, v0.28.0 08-26, v0.29.0 09-09)                       |
| SGLang          | [`sgl-project/sglang`](https://github.com/sgl-project/sglang)                   | `inference`                                 | Apache-2.0                              | ~2 weeks (v0.5.17 08-08, v0.5.18 08-22, v0.5.19 09-05)                       |
| verl            | [`verl-project/verl`](https://github.com/verl-project/verl)                     | `training`, `rl_post_training`              | Apache-2.0                              | ~2–3 months (v0.7.1 03-16, v0.8.0 06-01, v0.9.0 08-14)                       |
| VeOmni          | [`ByteDance-Seed/VeOmni`](https://github.com/ByteDance-Seed/VeOmni)             | `training`                                  | Apache-2.0                              | irregular (v0.1.10 05-21, v0.1.11 05-26, v0.1.12 09-09)                      |
| Megatron-LM     | [`NVIDIA/Megatron-LM`](https://github.com/NVIDIA/Megatron-LM)                   | `training`, `rl_post_training`, `inference` | BSD-3-Clause (README badge says Apache) | ~monthly (core_v0.18.0 06-23, core_v0.18.2 07-21, core_v0.19.0 08-19)        |
| Megatron-Bridge | [`NVIDIA-NeMo/Megatron-Bridge`](https://github.com/NVIDIA-NeMo/Megatron-Bridge) | `training`                                  | Apache-2.0                              | ~monthly, same day as Megatron-LM (v0.5.0 06-22, v0.5.1 07-21, v0.6.0 08-19) |

Roles here are provisional, taken from each README's self-description. Each snapshot record
must re-establish its roles from its own sources.

Local checkouts may exist as sibling directories (`../vllm`, `../sglang`, `../verl`,
`../VeOmni`, `../Megatron-LM`). They are reading aids only. As of 2026-09-12, the local `vllm` and `verl`
clones track the `TimYangst` forks and have no release tags (`../Megatron-LM` tracks upstream; there is
no local Megatron-Bridge clone), so check out the snapshot SHA,
or read the pinned upstream URLs, before using them as evidence.

## Snapshot calendar

### 2026-Q3 (first snapshot)

Recorded Q3 releases, sourced during the initial snapshot cycle. These fixed
records are historical release evidence, not a list of today’s latest tags.

| Slug                       | Tag            | Released   | Phase | Status      |
| -------------------------- | -------------- | ---------- | ----- | ----------- |
| `vllm-v0.29.0`             | `v0.29.0`      | 2026-09-09 | E1    | `extracted` |
| `sglang-v0.5.19`           | `v0.5.19`      | 2026-09-05 | E2    | `extracted` |
| `verl-v0.9.0`              | `v0.9.0`       | 2026-08-14 | E3    | `extracted` |
| `veomni-v0.1.12`           | `v0.1.12`      | 2026-09-09 | E3    | `extracted` |
| `megatron-lm-core_v0.19.0` | `core_v0.19.0` | 2026-08-19 | E5    | `extracted` |
| `megatron-bridge-v0.6.0`   | `v0.6.0`       | 2026-08-19 | E5    | `extracted` |

Status values mirror the model track: `backlog` | `sourcing` | `extracting` | `extracted`
| `reviewed` | `blocked`.

## Seed questions for the pilot

These come from existing model records. They check that the schema can close real gaps; they
are not a to-do list. **Outcomes for `vllm-v0.29.0` are in
[`engines/vllm-v0.29.0.md`](./engines/vllm-v0.29.0.md)**:

- V4.1-Flash is absent at this tag.

- DSpark is implemented, but the γ mismatch is unresolved.

- DSA and IndexCache are implemented; CSA/HCA is not asserted.

- The parser gap is on the engine side too.

- **DSpark.** `deepseek-v4-flash-0731` records vendor serving flags for vLLM
  (`--speculative-config '{"method":"dspark"}'`) and SGLang (`--speculative-algorithm DSPARK`).
  Which engine versions implement DSpark, and does either engine document the
  `num_speculative_tokens: 7` vs trained γ=5 mismatch?

- **DeepSeek-V4.1-Flash.** Its record says no serving command was published. Does
  `vllm-v0.29.0` (released the day before V4.1) or a later snapshot list
  `DeepseekV41ForCausalLM`?

- **Sparse attention.** DSA (DeepSeek-V3.2-Exp, 2025-09), CSA/HCA (DeepSeek-V4) and IndexShare
  (GLM-5.2) all have glossary entries. (`vllm/docs/design/hisparse.md` turned out to post-date
  `v0.29.0`; it belongs to the next snapshot.)

- **Reasoning and tool parsers.** Model records note that no `--tool-call-parser` flag is
  published for DeepSeek-V4 / V4.1. The engine's parser registry is the authoritative place to
  check.
