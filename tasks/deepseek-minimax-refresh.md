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

| Field       | Value                                                                 |
| ----------- | --------------------------------------------------------------------- |
| project_id  | `deepseek-minimax-refresh-20261022`                                   |
| state_home  | `collect/deepseek-minimax-20261022:tasks/deepseek-minimax-refresh.md` |
| code_base   | `main`, `065be9e535eec4eb3725fbbc2c72e34d62c91d77`                    |
| coordinator | Current Codex chat; only coordinator updates this file                |
| updated_at  | 2026-10-22, America/Los_Angeles                                       |
| delivery    | Reviewable PR targeting `main`; no merge authorization                |

## Authorization and decisions

| ID  | Source                                               | Scope and decision                                                                                                                                                                                                     |
| --- | ---------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A01 | User's initial request, 2026-10-22                   | Collect DeepSeek updates and fill MiniMax records, using coordinate-feature tracking and independent review; implement, validate, commit and prepare PR. Merge remains `manual`.                                       |
| D01 | Official HF release inventory                        | Requested “V4 Flash 1017” resolves to `DeepSeek-V4.1-Flash-1017`. Also check Pro-0813 and Flash-Vision-Exp.                                                                                                            |
| A02 | User: “多模态，音、视频生成给补齐”; scope reply      | Include structured audio/video generation for DeepSeek/MiniMax now; other vendors go to follow-up backlog.                                                                                                             |
| D02 | Existing model schema v8 assumes autoregressive LLMs | Add an independent media schema and `data/extracted/media/` track, analogous to engine snapshots; keep the LLM schema unchanged. H3 must distinguish released base checkpoints from hosted Context-IR / Regenerate-2K. |

## Tasks

Dependencies consumed validated artifacts on this shared feature branch before
merge. Delivery is a reviewable PR; merge-required tasks stay `awaiting_merge`
until the user merges. This is the latest on-branch snapshot; the linked PR's
review section records the final head without another self-referencing commit.

| ID  | Deliverable / acceptance                                                             | Type / priority  | Dependency                               | State          | Executor / evidence                                                                              |
| --- | ------------------------------------------------------------------------------------ | ---------------- | ---------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------ |
| T01 | Official inventory and pinned sources; remaining candidates classified               | unblocker / P0   | —                                        | done           | 15 manifests /100 cached assets; model notes and ROADMAP follow-up inventory                     |
| T02 | Three recent DeepSeek checkpoints, exact-version attribution, bilingual views        | required / P1    | T01: accepted inventory                  | awaiting_merge | `deepseek`; commits f019d6a /b7b71cb /6603436                                                    |
| T03 | Eight MiniMax LLM/VL core records and M3.1 source-only note                          | required / P1    | T01: accepted inventory                  | awaiting_merge | `minimax_llm`; commits b8f7c96 through f44c588; M1 source repair c39a920                         |
| T04 | Media schema v1, bilingual renderer/index, evidence validation, CI regression checks | unblocker / P0   | A02                                      | awaiting_merge | `media_schema`; 881e7a6                                                                          |
| T05 | H3, Music3 and closed Speech 2.8 media records with public/hosted scope              | required / P1    | T04: validated schema artifact           | awaiting_merge | coordinator; b2fc180 /9b83045 /fd319e2                                                           |
| T06 | Registry/glossary, generated indexes, roadmap and bilingual entry points             | required / P1    | T02/T03/T05: validated artifacts         | awaiting_merge | coordinator; 928c996, ab72b27, 088ca08, 6681cff                                                  |
| T07 | Independent review, cumulative cleanup inventory and bounded repairs                 | required / P1    | T02–T06: fixed commits                   | reviewing      | Two independent reviews completed; final state/document-only review pending in PR review section |
| T08 | Final checks, summary, checkpoint and reviewable PR                                  | required / P1    | T07: accepted review evidence            | running        | coordinator; PR entry below; merge manual/A01                                                    |
| F01 | Other vendors' audio/video generation                                                | enhancement / P2 | Current scope delivered                  | planned        | Explicitly deferred by user; select representative checkpoints first                             |
| F02 | Historical/specialized DeepSeek and MiniMax inventory; precision/packaging siblings  | enhancement / P2 | Choose comparison question               | planned        | ROADMAP follow-up inventory; not counted as extracted                                            |
| F03 | Closed LLM unknown FFN support, then M3.1 canonical extraction                       | enhancement / P2 | Schema design and fresh weight/API audit | planned        | M3.1 source-only notes; no guessed MoE label                                                     |

## Validation and independent review

- Baseline: `uv sync --locked`, Python 3.13; no lockfile changes. Main and fetched
  origin/main both `065be9e535eec4eb3725fbbc2c72e34d62c91d77` before branch creation.
- `scripts/validate_extractions.py`: PASS, **35 LLM/VL + 6 engine + 3 media**.
- `scripts/validate_registry.py`: PASS, **25 typed techniques /161 edges**;
  generated reports are current. Historical coverage gaps remain distinguished
  from the new records.
- `python -m unittest discover -s tests -v`: PASS, six media regressions covering
  evidence requirements, unknowns, schema/modality rejection, table escaping,
  manifest consistency, generated freshness and JSON-only indexing.
- `pre-commit run --all-files --show-diff-on-failure`: PASS (all hooks).
- Source audit: all **100 cached assets in 15 manifests** match recorded SHA256;
  mutable announcements/API activity snapshots retain fetched-byte identities,
  while HF configs/code and arXiv reports use pinned revisions.
- All changed local Markdown link targets exist. Data reviewer independently
  checked 28 bilingual record renders against deterministic output.
- No weights, GPU inference, quality benchmarks or speed measurements were run.

| Reviewer                         | Fixed scope                                                                                            | Finding and disposition                                                                                                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `review_data` (independent)      | base `065be9e535eec4eb3725fbbc2c72e34d62c91d77` → data head `fd319e27fd450d2d3164b20edb7ae2686f586e0f` | P2: M1 explicitly cited MiniMax-01 architecture paper without registering it. Fixed c39a920; independently rechecked by pipeline reviewer. No other data blockers.                           |
| `review_pipeline` (independent)  | same base → `088ca08e68e3830940f66d7f5af4140366e0060b`                                                 | P2: interleaved tool reasoning was incorrectly mapped to thinking/non-thinking fusion. Removed four M2-family glossary rows in both languages; repair reviewed, no remaining P1/P2 findings. |
| Final documentation/state review | incremental `088ca08..final PR head`                                                                   | Evidence entry is the final PR description's review section; no claim of completion before that review.                                                                                      |

## Impact

| Metric                     | Before               | After                        | Evidence                                             |
| -------------------------- | -------------------- | ---------------------------- | ---------------------------------------------------- |
| LLM/VL records             | 24                   | 35 (+3 DeepSeek, +8 MiniMax) | Schema validator and generated model index           |
| LLM vendors                | 4                    | 5 (MiniMax added)            | Generated model index                                |
| Media structured records   | 0                    | 3 (H3, Music3, Speech 2.8)   | Media validator and bilingual media index            |
| Typed techniques /edges    | 23 /123              | 25 /161                      | Registry validator                                   |
| Latest DeepSeek checkpoint | September V4.1-Flash | V4.1-Flash-1017              | Pinned October checkpoint and dated official release |
| Media regression coverage  | None                 | Six cases enforced in CI     | tests/test_media.py and workflow                     |

## Recovery checkpoint

- Last reconciled implementation head:
  `6681cffeb165b99bf2846b2be91d7df3ba7e9df5`; this state snapshot follows it.
- Branch: `collect/deepseek-minimax-20261022`; target: `main`; merge mode: `manual`.
- PR locator: the open PR for this branch in this repository; its description
  links this state and contains the final fixed-head review. Resolve the live
  PR/head before resuming; do not assume the snapshot proves remote publication.
- All implementation agents have returned; no running jobs, deployments, GPU
  workloads or finfer changes. No dedicated worktrees were created to remove.
- Current limitation: awaiting final documentation/state review and PR
  publication at this snapshot; final checks/review evidence is recorded in PR.
- Next action: read the PR review section and checks for its exact head; address
  user feedback, or merge only after explicit authorization. Do not re-extract
  completed records when continuing F01–F03.
- Scope gaps and undisclosed values remain explicit; sourced, extracted,
  independently reviewed and merged are separate states.

## Closeout

**Summary report:** this refresh adds 14 structured records: 11 LLM/VL and three
media releases, while preserving the six engine snapshots. MiniMax's core open
language/VL lineage and current H3/Music3/Speech media surface now have comparison
entries. H3's 768p base is kept separate from its hosted Context-IR/2K system;
Music3 keeps its conflicting Qwen initialization, sample-rate and duration
statements with exact sources. M3.1 weights are promised, not published; no
canonical LLM architecture was guessed. Historical products, specialized
research and packaging/precision variants remain explicit F02 inventory, and
other vendors' media remain F01 under the user's scope choice.

**Cumulative cleanup:** independent data review found no data refactor or source
migration needed. Pipeline review identified stale session/development/roadmap
claims, reconciled in 6681cff. The pre-existing long extraction history is labeled
as earlier context rather than rewritten. No speculative runtime refactor or
finfer/anywiki migration is warranted; canonical records and linked model notes
already hold the reusable findings. Nothing remains only in personal notes.

**Retrospective:** source collection must distinguish checkpoint configurations,
predecessor training reports, and hosted product features. The M1 source omission
was repaired by registering its actually cited predecessor report. Tool-use
interleaving and toggleable thinking fusion require separate evidence, so the
incorrect glossary adoption rows were removed. The glossary's existing parser
expects plain model names; adapting the new rows avoided a needless parser change.
These lessons are reflected in the final records, source notes and media schema
evidence checks. No shared skill changes or background monitoring were introduced.

Implementation is locally validated; publication/review status follows the PR.
Main has not been merged, and this snapshot does not claim merge acceptance.
