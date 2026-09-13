# Engines Roadmap

Tactical, snapshot-by-snapshot status for the engines track. For the design (roles, layout,
evidence rules, draft schema, phases), see [`../docs/engines/overview.md`](../docs/engines/overview.md).
Model status stays in [`ROADMAP.md`](./ROADMAP.md).

## Current focus

**Phase:** E0 (design) is done in this branch. **Next: E1**, the `vllm-v0.29.0` pilot, which
builds engine schema v1, the `extract-engine` skill, a sourcing target for
`data/sources/engines/`, rendering and CI validation alongside the first record.

No engine records exist yet.

## Snapshot policy

- **Quarterly.** At each quarter's snapshot, take the latest non-prerelease upstream tag for
  each tracked engine.
- **On-demand refreshes** in between, for three triggers only:
  - A newly extracted model needs engine-side support recorded.
  - A release changes a role subobject.
  - A synthesis question needs a version no snapshot has.
- Snapshots accumulate under their own slugs (`<engine>-<release-tag>`); none is overwritten.

## Tracked engines

| Engine | Upstream                                                            | Role(s)            | Licence    | Release cadence (from tag history)                      |
| ------ | ------------------------------------------------------------------- | ------------------ | ---------- | ------------------------------------------------------- |
| vLLM   | [`vllm-project/vllm`](https://github.com/vllm-project/vllm)         | `inference`        | Apache-2.0 | ~2 weeks (v0.27.1 08-11, v0.28.0 08-26, v0.29.0 09-09)  |
| SGLang | [`sgl-project/sglang`](https://github.com/sgl-project/sglang)       | `inference`        | Apache-2.0 | ~2 weeks (v0.5.17 08-08, v0.5.18 08-22, v0.5.19 09-05)  |
| verl   | [`verl-project/verl`](https://github.com/verl-project/verl)         | `rl_post_training` | Apache-2.0 | ~2–3 months (v0.7.1 03-16, v0.8.0 06-01, v0.9.0 08-14)  |
| VeOmni | [`ByteDance-Seed/VeOmni`](https://github.com/ByteDance-Seed/VeOmni) | `training`         | Apache-2.0 | irregular (v0.1.10 05-21, v0.1.11 05-26, v0.1.12 09-09) |

Roles here are provisional, taken from each README's self-description. Each snapshot record
must re-establish its roles from its own sources.

Local checkouts may exist as sibling directories (`../vllm`, `../sglang`, `../verl`,
`../VeOmni`). They are reading aids only. As of 2026-09-12, the local `vllm` and `verl`
clones track the `TimYangst` forks and have no release tags, so check out the snapshot SHA,
or read the pinned upstream URLs, before using them as evidence.

## Snapshot calendar

### 2026-Q3 (first snapshot)

Candidate tags, checked against GitHub releases on 2026-09-12. Re-check at snapshot time,
because a newer tag may land before the quarter ends.

| Slug             | Tag       | Released   | Phase | Status    |
| ---------------- | --------- | ---------- | ----- | --------- |
| `vllm-v0.29.0`   | `v0.29.0` | 2026-09-09 | E1    | `backlog` |
| `sglang-v0.5.19` | `v0.5.19` | 2026-09-05 | E2    | `backlog` |
| `verl-v0.9.0`    | `v0.9.0`  | 2026-08-14 | E3    | `backlog` |
| `veomni-v0.1.12` | `v0.1.12` | 2026-09-09 | E3    | `backlog` |

Status values mirror the model track: `backlog` | `sourcing` | `extracting` | `extracted`
| `reviewed` | `blocked`.

## Seed questions for the pilot

These come from existing model records. They check that the schema can close real gaps; they
are not a to-do list.

- **DSpark.** `deepseek-v4-flash-0731` records vendor serving flags for vLLM
  (`--speculative-config '{"method":"dspark"}'`) and SGLang (`--speculative-algorithm DSPARK`).
  Which engine versions implement DSpark, and does either engine document the
  `num_speculative_tokens: 7` vs trained γ=5 mismatch?
- **DeepSeek-V4.1-Flash.** Its record says no serving command was published. Does
  `vllm-v0.29.0` (released the day before V4.1) or a later snapshot list
  `DeepseekV41ForCausalLM`?
- **Sparse attention.** DSA (DeepSeek-V3.2-Exp, 2025-09), CSA/HCA (DeepSeek-V4) and IndexShare
  (GLM-5.2) all have glossary entries. `vllm/docs/design/hisparse.md` is a candidate source
  for how vLLM implements sparse attention.
- **Reasoning and tool parsers.** Model records note that no `--tool-call-parser` flag is
  published for DeepSeek-V4 / V4.1. The engine's parser registry is the authoritative place to
  check.
