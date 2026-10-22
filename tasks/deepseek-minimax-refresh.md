# DeepSeek / MiniMax collection — coordination state

## Goal and scope

Collect officially released DeepSeek and MiniMax checkpoints through 2026-10-22,
prioritizing the missing recent DeepSeek releases, the MiniMax language-model
lineage, and MiniMax multimodal, audio and video generation. Preserve unknowns,
pin public sources, validate structured records, regenerate bilingual browse
surfaces, and obtain independent review. Other vendors' audio/video models are
follow-up work. Do not download weights or run GPU inference.

This is the sole coordination state for this refresh. The model inventory stays
in [ROADMAP.md](ROADMAP.md); model-specific facts stay in `models/` and canonical
extractions. General loop: the externally maintained `coordinate-feature` skill;
no finfer runtime, notes branch, deployment or background automation is involved.

| Field | Value |
| --- | --- |
| project_id | `deepseek-minimax-refresh-20261022` |
| state_home | `collect/deepseek-minimax-20261022:tasks/deepseek-minimax-refresh.md` |
| code_base | `main`, `065be9e535eec4eb3725fbbc2c72e34d62c91d77` |
| coordinator | Current Codex chat; only coordinator updates this file |
| updated_at | 2026-10-22, America/Los_Angeles |
| delivery | Reviewable PR targeting `main`; no merge authorization |

## Authorization and decisions

| ID | Source | Scope and decision |
| --- | --- | --- |
| A01 | User's initial request, 2026-10-22 | Collect DeepSeek updates and fill MiniMax records, using coordinate-feature tracking and independent review; implement, validate, commit and prepare PR. Merge remains `manual`. |
| D01 | Official HF release inventory | Requested “V4 Flash 1017” resolves to `DeepSeek-V4.1-Flash-1017`. Also check Pro-0813 and Flash-Vision-Exp. |
| A02 | User: “多模态，音、视频生成给补齐”; scope reply | Include structured audio/video generation for DeepSeek/MiniMax now; other vendors go to follow-up backlog. |
| D02 | Existing model schema v8 assumes autoregressive LLMs | Add an independent media schema and `data/extracted/media/` track, analogous to engine snapshots; keep the LLM schema unchanged. H3 must distinguish released base checkpoints from hosted Context-IR / Regenerate-2K. |

## Tasks

Dependencies can consume validated artifacts on this explicitly shared feature
branch before merge. Merge-required delivery tasks remain `awaiting_merge` until
the user merges the PR.

| ID | Deliverable / acceptance | Type / priority | Dependency | State | Executor / evidence |
| --- | --- | --- | --- | --- | --- |
| T01 | Verify official inventories; pinned source manifests, gaps classified by modality/openness | unblocker / P0 | — | running | coordinator + vendor agents; `tasks/models/` |
| T02 | Missing recent DeepSeek checkpoint JSON + bilingual render; exact-version source attribution | required / P1 | T01: validated inventory | running | `deepseek` agent; disjoint new DeepSeek files |
| T03 | MiniMax language and native-VL lineage JSON + bilingual render; no guessed inherited training | required / P1 | T01: validated inventory | running | `minimax_llm` agent; disjoint MiniMax LLM files |
| T04 | Strict media schema v1, bilingual renderer, validator and media browse index | unblocker / P0 | A02 | running | `media_schema` agent; media-specific implementation |
| T05 | H3 and Music3 structured media records with pinned configs/cards/license and release boundaries | required / P1 | T04: validated schema | running | coordinator; `data/extracted/media/` |
| T06 | Refresh indexes, glossary, model roadmap, bilingual README and session entry | required / P1 | T02/T03/T05: validated artifacts | planned | coordinator |
| T07 | Independent review and read-only cumulative cleanup inventory; fix and re-review blockers | required / P1 | T02–T06: fixed commit | planned | independent reviewer, not yet assigned |
| T08 | Final checks, summary, checkpoint and reviewable PR | required / P1 | T07: accepted artifacts | planned | coordinator; merge `manual` |
| F01 | Other vendors' audio/video generation coverage | enhancement / P2 | Current scope delivered | planned | Unassigned; explicitly deferred by user |

## Validation / review

- Baseline: `uv sync --locked` installed Python 3.13 dependencies without lock changes.
- Baseline: `scripts/validate_extractions.py` passed for 24 LLMs + 6 engines;
  `scripts/validate_registry.py` passed (123 structured edges, generated surfaces current).
- Final checks and independent review: `NOT_RUN`.
- Review entry: final PR description will contain reviewer identity, fixed
  base/head, findings, fixes and re-review result; recording it there avoids
  modifying the reviewed commit just to store its own review result.

## Impact and checkpoint

| Metric | Before | After / evidence |
| --- | --- | --- |
| LLM vendors | 4; MiniMax absent | Pending |
| Media generation structured records | 0 | Pending |
| Latest DeepSeek record | September V4.1-Flash | Pending October checkpoint |

- Main was clean and matched fetched origin/main at the full base SHA above;
  local main was already up to date before creating the feature branch.
- Active agents share the feature checkout with non-overlapping file ownership.
  No jobs, GPU runs, deployments or finfer changes exist.
- Next action: finish source registration and media extraction, integrate the
  vendor artifacts, then review the fixed complete diff.
- Scope gaps must be retained with evidence; “collected”, “extracted”,
  “reviewed” and “merged” are distinct states.

## Closeout

Not closed. Summary and retrospective will be recorded here after validation;
PR approval and merge remain with the user.
