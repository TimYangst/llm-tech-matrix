# Public accelerator catalog — coordination state

## Goal and completion criteria

Build an independently versioned, public-source hardware track for representative
AI accelerators. Initial delivery: ten exact variants, architecture, memory,
qualified peak compute, interconnect, power and software facts; registered public
webpage/PDF references; deterministic bilingual views/index; validation and
independent review. This is a representative first batch, not a complete market
inventory. No internal measurements, private notes, weights or hardware jobs.

This file is the sole mutable coordination state. Device-specific extraction
notes belong in `tasks/hardware/`; the record contract and procedure belong in
`docs/hardware/`. The externally maintained `coordinate-feature` workflow supplies
tracking and review only; no finfer runtime or private hardware data is involved.

| Field | Value |
| --- | --- |
| project_id | `public-hardware-catalog-20261022` |
| design_ref | [Hardware procedure](../../docs/hardware/overview.md), [schema](../../docs/hardware/schema.md) |
| state_home | `feat/public-hardware-catalog:tasks/projects/public-hardware-catalog.md` |
| code_base | `main`, `5175098bf8432dbcd73fda3c703c270f2b7aa5df` (PR #22 merged) |
| coordinator | Current Codex chat; coordinator alone updates this state |
| updated_at | 2026-10-22, America/Los_Angeles |
| constraints | Public primary sources only; preserve units, variants, scope and unknowns; manual merge |

## Authorization and decisions

| ID | Source | Scope / decision |
| --- | --- | --- |
| A01 | User's hardware request, 2026-10-22 | Collect typical GPUs, TPUs and other accelerators with public webpage/PDF references; use coordinate-feature tracking and review. Internal measurements must not be disclosed or consulted. |
| A02 | User's scope reply | Datacenter GPUs, TPU, Trainium/Gaudi and similar accelerators first; one consumer GPU comparison is acceptable. |
| A03 | Existing repository publication instruction | Continue implementation, checks, commits, push and reviewable PR in `TimYangst/llm-tech-matrix`, using repository-scoped `TimYangst` login (`git gh`). Merge remains `manual`; no merge authorization. |
| D01 | Hardware facts do not fit LLM/media contracts | Add hardware schema v1 and a separate sources/extractions/index subtree; preserve existing record contracts. |
| D02 | Vendor tables mix units and scopes | Keep single-accelerator/system, matrix/vector, dense/sparse, precision, and GB/GiB explicit; never silently divide system totals or halve sparse figures. Vendor theoretical peaks are not measured performance. |

## Tasks

All implementation uses `feat/public-hardware-catalog` with disjoint ownership.
Dependencies below accept validated artifacts in this branch; they do not require
separate intermediate merges. Merge permission is manual/A03 for every task.

| ID | Deliverable / acceptance | Type / priority | Dependency / ready condition | State | Executor |
| --- | --- | --- | --- | --- | --- |
| H01 | Exact ten-variant inventory, public source policy and task state | unblocker / P0 | A01/A02 | done | coordinator |
| H02 | Schema v1, sourcing track, renderer/index, CI validation and meaningful regressions | unblocker / P0 | H01 accepted scope | running | hardware_pipeline |
| H03 | Five GPU records, manifests and per-device evidence notes | required / P1 | H01; H02 schema contract available | running | hardware_gpus |
| H04 | Five TPU/ASIC records, manifests and per-device evidence notes | required / P1 | H01; H02 schema contract available | running | hardware_asics |
| H05 | Bilingual navigation, current roadmap/procedures and generated browse surfaces | required / P1 | H02–H04 validated artifacts | running | coordinator |
| H06 | Independent fixed-head review, cumulative cleanup inventory and bounded repairs | required / P1 | H02–H05 fixed commit and checks | planned | unassigned |
| H07 | Final checks, impact, recovery checkpoint and reviewable PR | required / P1 | H06 accepted review | planned | coordinator |
| F01 | Additional vendors, generations and form factors | enhancement / P2 | Select a bounded comparison question and primary references | planned | unassigned |
| F02 | Published benchmark records | enhancement / P2 | Public reproducible workload, system and methodology available | planned | unassigned |

Initial variants: `nvidia-h100-sxm-80gb`, `nvidia-b200-sxm`, `nvidia-rtx-5090`,
`amd-instinct-mi300x`, `amd-instinct-mi355x`, `google-tpu-v5p`,
`google-tpu7x-ironwood`, `aws-trainium2`, `aws-inferentia2`, `intel-gaudi3-oam`.
Broader candidates include later NVIDIA/AMD variants, TPU generations, Trainium3,
Cerebras, Groq and publicly documented regional accelerators. These are not
claimed sourced or extracted in this phase.

## Acceptance and review evidence

- H02: schema rejects missing/unregistered evidence, invalid units/scopes and
  non-public URLs; validator checks manifests and generated freshness; sourcing
  supports `--track hardware`. Existing contracts and outputs still pass.
- H03/H04: each populated fact has a primary public citation registered with
  fetched-byte SHA256 metadata; exact SKU, chip/module scope and qualifications
  are visible. Unavailable or contradictory facts remain explicit unknowns or
  open questions. No private source inspection or performance runs.
- H05: English/Chinese entry points, hardware procedure/schema, source policy,
  inventory and recovery instructions agree with actual artifacts.
- H06: independent reviewer checks fixed base/head, source fidelity, tooling,
  generated output and cleanup candidates. Findings are repaired and rechecked.
  Final review evidence belongs in the PR description to avoid a moving-head
  review loop caused by this state file recording its own commit.
- Required checks: all pre-commit hooks; unittest discovery; extraction validator;
  registry validator; source-cache/hash audit and changed-document link check.
- Current validation: NOT_RUN; implementation is in progress.

## Impact

| Metric | Before | Current / target | Evidence |
| --- | --- | --- | --- |
| Structured hardware variants | 0 | target 10 | hardware JSON/index and validator |
| Public hardware source manifests | 0 | target 10 | `data/sources/hardware/` |
| Hardware contract / generated browse surfaces | None | v1 / bilingual | H02 acceptance |
| Hardware speed or quality measurements | None | NOT_MEASURED | Public specifications only |

## Recovery checkpoint

- Base verified: PR #22 merged as `5175098bf8432dbcd73fda3c703c270f2b7aa5df`;
  local main fast-forwarded before creating `feat/public-hardware-catalog`.
- Active agents: hardware_pipeline owns runtime/tests/hardware docs;
  hardware_gpus and hardware_asics own disjoint record/source/note slugs;
  coordinator owns shared documentation and this state. Check agents and Git
  status before restarting work. No new worktree or hardware process exists.
- Publication account remains repository-local `TimYangst`; do not change the
  global finfer login. No credentials belong in tracked files.
- Next action: finish H02–H05, validate, freeze a commit for H06, then publish H07.
  Merge remains manual. No background automation is configured.

## Phase closure

Not closed. Final checks, independent review, cleanup inventory and retrospective
will be recorded before publication; final fixed-head review and CI live in the PR.
