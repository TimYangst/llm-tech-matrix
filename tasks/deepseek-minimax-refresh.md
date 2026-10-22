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

Publication authorization A03 (2026-10-22): user explicitly replied “好的，推送并创建吧”
after being shown destination `TimYangst/llm-tech-matrix`. This authorizes pushing
`collect/deepseek-minimax-20261022` and creating a PR targeting `main`; merge
remains manual. The earlier automatic approval block is superseded by A03.

Account instruction A04: user specified the `yt0701@gmail.com` account for this
repository and completed browser authorization. The repository-scoped CLI login
is verified as `TimYangst` with admin/push permission; use `git gh` here. Its
configuration is local to the Git directory and is not part of this PR.

Additional instruction A05 (2026-10-22): user requested checking project progress,
README and related documentation for stale information, cleanup and synchronization.
T09 covers this documentation-only extension within PR #21; A03/A04 continue to
permit updates and pushes. Merge remains manual.

## Tasks

Dependencies consumed validated artifacts on this shared feature branch before
merge. Delivery is a reviewable PR; merge-required tasks stay `awaiting_merge`
until the user merges. This is the latest on-branch snapshot; the linked PR's
review section records the final head without another self-referencing commit.

| ID  | Deliverable / acceptance                                                             | Type / priority  | Dependency                               | State          | Executor / evidence                                                                                                 |
| --- | ------------------------------------------------------------------------------------ | ---------------- | ---------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------- |
| T01 | Official inventory and pinned sources; remaining candidates classified               | unblocker / P0   | —                                        | done           | 15 manifests /100 cached assets; model notes and ROADMAP follow-up inventory                                        |
| T02 | Three recent DeepSeek checkpoints, exact-version attribution, bilingual views        | required / P1    | T01: accepted inventory                  | awaiting_merge | `deepseek`; commits f019d6a /b7b71cb /6603436                                                                       |
| T03 | Eight MiniMax LLM/VL core records and M3.1 source-only note                          | required / P1    | T01: accepted inventory                  | awaiting_merge | `minimax_llm`; commits b8f7c96 through f44c588; M1 source repair c39a920                                            |
| T04 | Media schema v1, bilingual renderer/index, evidence validation, CI regression checks | unblocker / P0   | A02                                      | awaiting_merge | `media_schema`; 881e7a6                                                                                             |
| T05 | H3, Music3 and closed Speech 2.8 media records with public/hosted scope              | required / P1    | T04: validated schema artifact           | awaiting_merge | coordinator; b2fc180 /9b83045 /fd319e2                                                                              |
| T06 | Registry/glossary, generated indexes, roadmap and bilingual entry points             | required / P1    | T02/T03/T05: validated artifacts         | awaiting_merge | coordinator; 928c996, ab72b27, 088ca08, 6681cff                                                                     |
| T07 | Independent review, cumulative cleanup inventory and bounded repairs                 | required / P1    | T02–T06: fixed commits                   | done           | Prior reviews accepted through 34d98c3; final publication checkpoint evidence is in PR #21 description.             |
| T08 | Final checks, summary, checkpoint and reviewable PR                                  | required / P1    | T07: accepted review evidence            | awaiting_merge | PR #21 created under A03/A04; remote CI running at snapshot; manual merge.                                          |
| T09 | Audit and synchronize project progress, README, procedures and related docs          | required / P1    | T02–T08: reviewed/published artifacts    | reviewing      | T09 doc cleanup implemented; independent P2 inventory omission repaired; final fixed-head review evidence in PR #21 |
| F01 | Other vendors' audio/video generation                                                | enhancement / P2 | Current scope delivered                  | planned        | Explicitly deferred by user; select representative checkpoints first                                                |
| F02 | Historical/specialized DeepSeek and MiniMax inventory; precision/packaging siblings  | enhancement / P2 | Choose comparison question               | planned        | ROADMAP follow-up inventory; not counted as extracted                                                               |
| F03 | Closed LLM unknown FFN support, then M3.1 canonical extraction                       | enhancement / P2 | Schema design and fresh weight/API audit | planned        | M3.1 source-only notes; no guessed MoE label                                                                        |

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
- Published PR: [#21](https://github.com/TimYangst/llm-tech-matrix/pull/21),
  open and ready for review, targeting `main`; author `TimYangst`. Verified
  initial remote head `34d98c38f7ff35c8b5ed78d0cb4fe44a969d5366`; this checkpoint
  follows it. Final reviewed head and CI outcome are recorded in the PR description.
- Initial PR-triggered CI run `39864994914` is in progress at this snapshot.
  No human or bot review comments existed on the initial readback.
- Account-permission blocker is resolved: `git gh api user` returns `TimYangst`,
  and repository permissions include admin/push. Local `git gh` uses a scoped
  GitHub CLI configuration; SSH already authenticates the same account. Other
  projects' default GitHub login is unchanged. No credentials are committed.
- Local PR body copy: `.claude/drafts/pr/2026-10-22-deepseek-minimax-media.md`;
  the remote PR description is the published review evidence entry.
- No running jobs, deployments, GPU workloads or finfer changes. No dedicated
  worktrees were created to remove. Remote CI is the only tracked operation.
- Next action: read PR #21's exact head, checks and new review comments. Address
  actual feedback; merge only with explicit user authorization. A03/A04 remain
  valid for pushes and PR updates; do not request them again. Do not re-extract
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
claims, reconciled in 6681cff. T09 removes superseded progress narratives from live model/engine roadmaps and
links fixed pre-cleanup commit 1b72ed9 plus preserved canonical notes/changelog. No speculative runtime refactor or
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

Implementation and independent review are complete; PR #21 is published under
A03/A04 with the intended repository account. Earlier publication/account blocks
are resolved. Remote checks are recorded against their actual head in the PR;
main remains unmerged and merge authorization remains manual.

## T09 documentation synchronization

A05 expanded the final cleanup to current project documentation. Independent
inventory by `review_pipeline` identified stale media/engine progress claims,
obsolete next-task queues, placeholder Quickstart, missing synthesis-regeneration
steps, unsafe whole-tree Markdown formatting instructions, and inconsistent
track/unknown/default guidance. The documentation-only repair covers 19 maintained
files; model/engine/media records, source manifests and generated outputs are
unchanged. Native multimodal 1017 and M3 entries now sit in the multimodal table.

The model roadmap keeps current inventory and one next-work entry; older narratives
are available at fixed Git history rather than as actionable instructions. Engine
status now reflects E5 complete and distinguishes historical mapping gaps from
unsupported models. README, vision, pipeline and procedures route all three record
contracts correctly. Default null/empty structures follow the executable schemas.

Validation: changed-file pre-commit hooks, both data/registry validators and local
link/incoming-anchor checks pass. Existing media tests and remote CI passed before
this documentation-only addition; no GPU or new data extraction is required.
Independent review of the concrete T09 commit is pending at this snapshot; its
fixed-head result and remote CI outcome belong in PR #21's review section.
