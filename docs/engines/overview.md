# Engines track: design

Status: **E2 done** (`vllm-v0.29.0` pilot and `sglang-v0.5.19`). Engine schema v1 is implemented in
[`src/llm_tech_matrix/engine_schema.py`](../../src/llm_tech_matrix/engine_schema.py), with the
field spec in [`schema.md`](./schema.md). The first record is
[`vllm-v0.29.0`](../../data/extracted/engines/vllm-v0.29.0.md). The draft schema section below
is kept as the E0 design record; where the two differ, `schema.md` wins. Live status is in
[`../../tasks/ENGINES.md`](../../tasks/ENGINES.md).

## Why a second record type

The model track records what a *vendor* built. Engines are where those designs meet
production: inference servers (vLLM, SGLang), training frameworks (VeOmni) and RL
post-training systems (verl). The repo already shows the gap:

- `deepseek-v4-flash-0731` records vendor-published serving flags for vLLM and SGLang, but
  nothing in the repo says which engine version implements DSpark, or how.
- `deepseek-v4.1-flash` carries an open question that no serving command was published. It
  can only be closed from the engine side.
- The engine repos document model-specific work that has no home here, for example:
  - verl: `docs/advance/deepseek_v4_integration.rst`
  - VeOmni: `docs/design/deepseek_v4_indexer_loss.md`
  - vLLM: `docs/design/hisparse.md` (on `main` since 2026-09-12, so not in the `v0.29.0` snapshot)

So the goal is **not** to summarize engine documentation, which would duplicate upstream
and go stale. The goal is the **model ↔ technique ↔ engine** triangle, which neither the
model records nor the engines' own docs provide.

### Questions this track must answer

These are the questions the track is built to answer, in priority order:

1. **Support matrix.** For each extracted model, which engine versions can serve or train
   it, at what status (day-0 / supported / experimental), with which flags?
2. **Technique adoption lag.** For a technique in the glossary (DSA, MXFP4, DSpark, a
   reasoning parser), when did it first appear in a model, and when did each engine
   implement it?
3. **Cross-engine comparison.** How do engines in the same role implement the same
   technique? For example, speculative decoding in vLLM vs SGLang, or weight sync across
   RL systems.

Engine *internals* (scheduler design, memory manager) are recorded only as far as they
explain 1–3. They are not the product.

### Non-goals

- **Tracking HEAD.** vLLM and SGLang tag a release roughly every two weeks, while verl and
  VeOmni release months apart. Records are quarterly snapshots.
- **Benchmarks.** Throughput numbers depend on hardware and configuration and change with
  every release, the same reason model benchmarks are a non-goal.
- **Deployment guides.** Flags are recorded as evidence of support, not as recipes.

## Roles

Engines differ in what they do, so a single flat schema would be mostly `UNKNOWN`. Each
record carries a common core plus one or more role subobjects:

| Role               | Examples     | Role subobject                                                                                                                                                                             |
| ------------------ | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `inference`        | vLLM, SGLang | `serving`: scheduling, KV-cache manager, PD/EPD disaggregation, prefix caching, speculative decoding, quantization and KV dtypes, attention backends, tool/reasoning parsers, API surfaces |
| `training`         | VeOmni       | `training`: FSDP2 / Megatron backends, sequence parallelism, expert parallelism, checkpoint format, kernels, precision                                                                     |
| `rl_post_training` | verl         | `rl`: algorithms, rollout engines, training backends, weight sync / resharding, sync vs async, routing replay                                                                              |

A record may carry more than one role, but only when its own sources document each role.
A role is never inferred from how *other* projects use the engine, e.g. verl using SGLang for
rollouts.

## Layout

The engine track reuses the three layers and their contract, in parallel subtrees:

```
docs/engines/overview.md                     this document
docs/engines/schema.md                       field spec (created in E1)
src/llm_tech_matrix/engine_schema.py         Pydantic, ENGINE_SCHEMA_VERSION (created in E1)
data/sources/engines/<engine-slug>/manifest.json
data/extracted/engines/<engine-slug>.json    + .md / .zh.md, rendered like models
tasks/ENGINES.md                             tactical status + snapshot calendar
tasks/engines/<engine-slug>.md               per-snapshot notes and open questions
.claude/skills/extract-engine/SKILL.md       extraction procedure (created in E1)
```

- **Separate subtrees on purpose.** Every model-side glob is non-recursive:
  `data/extracted/*.json` in validation, rendering and synthesis, and
  `data/sources/*/manifest.json` in sourcing. Engine records under `engines/` are invisible
  to the model pipeline, so neither track can break the other.
- **Independent schema version.** Engine schema bumps never touch model records, and the
  other way round. Each track keeps its own changelog section in `docs/conventions.md`.
- **Layer boundaries still hold.** Model records keep only what the *vendor* states;
  engine records keep only what the *engine* states; the two meet in synthesis. Neither
  record type is ever back-filled from the other.

## Snapshots

- **Cadence: quarterly, plus on-demand refreshes.** At each quarter's snapshot, take the
  latest non-prerelease upstream tag. Refresh between quarters only when one of these
  happens:
  - A newly extracted model needs its engine-side support recorded (e.g. a day-0 launch).
  - An engine ships a release that changes a role subobject, for example a new
    speculative-decoding method or a new rollout backend.
  - A synthesis question needs a version that no snapshot has.
- **Snapshots accumulate; they are never overwritten.** Each is its own slug, so the
  adoption-lag question can be answered from the history of records.
- **Slug: `<engine>-<release-tag>`**, lowercase: `vllm-v0.29.0`, `sglang-v0.5.19`,
  `verl-v0.9.0`, `veomni-v0.1.12`. The tag is what pins the source; the record also stores
  the resolved commit SHA and the snapshot date.

## Sources and evidence

- **Cite upstream, pinned to the snapshot commit.** Use
  `https://raw.githubusercontent.com/<org>/<repo>/<sha>/<path>` for files and GitHub release
  pages for release notes. Upstream repos: `vllm-project/vllm`, `sgl-project/sglang`,
  `verl-project/verl`, `ByteDance-Seed/VeOmni`. Never cite a fork, and never cite a local
  path.
- **Local checkouts are reading aids, not sources.** A sibling clone such as `../vllm` makes
  code search cheap, but it may be a fork, may lack tags, and may sit at an arbitrary
  commit. Before using one, check it out at the snapshot SHA, or read the pinned upstream
  URLs instead.
- **Code is a primary source.** For models, `config.json` beats the blog. For engines,
  code at the pinned commit beats the docs, which often lag. Useful evidence, strongest
  first:
  1. Code, such as model registries, feature flags and CLI argument definitions.
  2. Design docs and API reference.
  3. Release notes.
  4. Vendor blog posts.
- **No hallucination, strictly.** Every support claim needs evidence: a pinned URL,
  optionally with a line range. With no evidence, the value is `"[Unknown/Not Disclosed]"`,
  never an inferred "probably supported". A model name in a README news item is weaker than
  the model's entry in the engine's model registry; when the two disagree, record both and
  add an open question.
- **Size.** Record URLs and hashes for the specific files used, not whole repositories. The
  `add` flow stays the same; E1 adds a way to target the `engines/` subtree.

## Draft schema (E1 finalizes)

The draft is deliberately small. Following the model track's rule, fields are promoted
when real snapshots need them.

```text
EngineRecord
  engine_schema_version
  metadata          name, slug, organization, repository, license, release_tag, commit_sha,
                    release_date, snapshot_date, roles[], hardware[], languages[]
  parallelism       tp / pp / dp / ep / cp / sp — each {supported, implementation, evidence}
  serving           (inference role)
  training          (training role)
  rl                (rl_post_training role)
  integrations[]    {engine_slug?, name, relation, evidence}
                    relation: rollout_backend | training_backend | kernel_library | other
  model_support[]   {model_slug?, hf_architecture, status, since_version?, flags, notes, evidence}
                    status: day0 | supported | experimental
  technique_support[] {glossary_slug, implementation, since_version?, flags, notes, evidence}
  open_questions[]
```

- `model_support[].model_slug` links to a record in `data/extracted/` when one exists. The
  architecture class string (e.g. `DeepseekV41ForCausalLM`) is the join key that works even
  when it doesn't.
- `since_version` is filled only when release notes or history show it. The version where
  a feature first appeared is otherwise computed in synthesis by comparing snapshots.
- `technique_support[].glossary_slug` must be a glossary/registry slug, so it produces
  typed edges exactly like the model side ("assertions, not mentions").

## Glossary and synthesis

- **One shared glossary.** Engine-specific techniques get entries in a new `serving` or
  `training-systems` category. Candidates: PagedAttention, RadixAttention, continuous
  batching, prefix caching, PD / EPD disaggregation, HybridFlow / 3D-HybridEngine, Ulysses
  sequence parallelism, FSDP2.
- **Two tables per technique entry.** The existing **Used by (models)** table stays, and a
  second **Implemented by (engines)** table is added. "A model uses DSA" and "vLLM
  implements DSA" are different claims and must not share rows. Decided in E1: that table is
  **generated in E4** from `technique_support[]` rows rather than hand-maintained, because
  engine snapshots accumulate every quarter and a hand-kept table would drift immediately.
- **Registry.** Engine slots are added to `registry.json` so `technique_support` produces
  engine→technique edges. The coverage report checks both tables.
- **First synthesis outputs (E4).**
  - `data/reports/engine-support-matrix.md`: extracted models × engine snapshots.
  - One adoption-lag report driven by a single real question, e.g. DSA from DeepSeek-V3.2-Exp
    (2025-09) to each engine's implementation.

## Phases

| Phase | Deliverable                                                                                                      | Exit criteria                                  |
| ----- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| E0    | This design; vision / roadmap / session-start / conventions updated; `tasks/ENGINES.md`                          | Merged                                         |
| E1    | Pilot `vllm-v0.29.0`: engine schema, `extract-engine` skill, sourcing `engines/` target, renderer, CI validation | One record validates in CI; schema gaps listed |
| E2    | `sglang-v0.5.19`, the same role as a cross-engine stress test                                                    | No schema field is vLLM-shaped                 |
| E3    | `verl-v0.9.0` (rl role, integrations), then `veomni-v0.1.12` (training role)                                     | All three role subobjects exercised            |
| E4    | Registry engine slots, "Implemented by" tables, support matrix, first adoption-lag report                        | Matrix covers all extracted models             |

vLLM goes first because its `docs/design/` is the most complete. The pilot is where the
schema gets tested against real material, just as DeepSeek-V3 was for models.
