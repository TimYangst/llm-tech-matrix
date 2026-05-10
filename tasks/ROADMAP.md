# Per-Model Roadmap

Tactical, model-by-model status. For strategic milestones (M1/M2 scope, sequencing), see [`../docs/roadmap.md`](../docs/roadmap.md). For how to pick up the project from a fresh session, see [`../docs/session-start.md`](../docs/session-start.md).

## Current focus

**Phase:** M1 — schema v6 landed (cross-vendor *release-strategy* and *runtime-mode*
comparison). Driven by a Qwen3.5/3.6 sub-model exploration that surfaced three gaps
the v5 schema couldn't express cleanly: (1) the *variant policy* is invisible — Qwen
3.5/3.6's deliberate move away from Qwen2.5's separate Math/Coder/VL/Thinking siblings
toward unified weights with chat-template kwargs has no field to record it; (2)
`inference_modes[].trigger` is free text — the actual chat-template kwargs
(`enable_thinking`, `preserve_thinking`) and per-mode sampling presets are buried in
prose, not machine-queryable; (3) tool-call wire formats vary meaningfully (Qwen3-Coder
XML-like with `qwen3_coder` parser; DeepSeek-V4 `|DSML|` namespaced XML) and were
unstructured. Schema v6 adds `metadata.variant_policy`, dual `inference_modes[].kwargs`
and `sampling_recommended` companions, and `alignment.tool_call_protocol` — all
backwards-compatible. All 9 prior v5 records migrated and now carry real content
in the new fields where sources document it.

**Previous phase (v5):** DeepSeek-V4 batch landed. Both V4-Pro (1.6T total / 49B
active) and V4-Flash (284B / 13B) are extracted against schema v5 (which added
`architecture.residual_connections` for mHC / Hyper-Connections, and
`training.stability_notes` for Anticipatory Routing / SwiGLU Clamping). V4 is the
first repo entry to use the **Muon optimizer**, **mHC residual connections**, the
**hybrid CSA + HCA attention** with KV compression, **FP4 QAT (MXFP4)** for MoE
expert weights + indexer QK path, **multi-teacher On-Policy Distillation**, and a
3-mode reasoning effort axis (Non-think / Think High / Think Max). Schema v5 was
backwards-compatible — all 7 prior v4 records migrated cleanly with a one-line
`schema_version` bump.

**In progress (sourcing → extracting):**

- ✅ `deepseek-v4-pro` — DeepSeek-V4 Pro (Apr 2026) — **extracted** (first MLA-replacement architecture: hybrid CSA + HCA with KV compression; mHC residuals; Muon optimizer; FP4 QAT; multi-teacher OPD; 3-mode reasoning; schema v5 driven by this extraction)
- ✅ `deepseek-v4-flash` — DeepSeek-V4 Flash (Apr 2026) — **extracted** (smaller V4 sibling, second-pass schema v5 validation; layers 0-1 use pure SWA instead of pure HCA, otherwise architectural shape identical)
- ✅ `qwen3.5-27b` — Qwen3.5 dense (Feb 2026) — **extracted** (first hybrid-backbone validation; schema v4 holds)
- ✅ `qwen3.5-35b-a3b` — Qwen3.5 MoE smaller (Feb 2026) — **extracted** (hybrid attention + MoE-FFN combo; shared-expert reintroduction; reverts to classic aux-loss)
- ✅ `qwen3.6-27b` — Qwen3.6 dense (Apr 2026) — **extracted** (post-training-only refresh of 3.5-27B; adds `preserve_thinking` 3rd inference mode + agentic-coding focus)
- ✅ `qwen3.6-35b-a3b` — Qwen3.6 MoE smaller (Apr 2026) — **extracted** (post-training-only refresh of 3.5-35B-A3B; same `preserve_thinking` + agentic-coding deltas as 3.6-27B)

**Schema gaps — resolved by v6 (2026-05):**

- ✅ Vendor variant policy — `metadata.variant_policy` (free-text). Captures Qwen3.5/3.6's "unified weights, modes via kwargs" stance vs Qwen2.5's "separate Math/Coder/VL siblings" vs DeepSeek's "Reasoner sibling → 3 reasoning-effort modes on one model" trajectory.
- ✅ Per-mode kwargs and sampling — `inference_modes[].kwargs: dict[str, str]` + `sampling_recommended: dict[str, str]`. Qwen3.5/3.6 README "Best Practices" sampling presets are now machine-readable; the `enable_thinking` / `preserve_thinking` toggles are no longer buried in prose.
- ✅ Tool-call wire format — `alignment.tool_call_protocol` (None when undisclosed). Qwen3-Coder XML-like protocol (`<tool_call><function=...><parameter=...></parameter></function></tool_call>` with `--tool-call-parser qwen3_coder`) and DeepSeek-V4's `|DSML|`-namespaced XML format are both now structured. Earlier deferred from v5 changelog ("structured tool-call protocol slot") — V4 + Qwen3.5/3.6 give us 3 protocol records to validate against.

**Schema gaps — resolved by v4 (2026-05):**

- ✅ Hybrid attention layout — `Attention.variants[]` + `layer_pattern` (see [conventions changelog v4](../docs/conventions.md#schema-changelog)).
- ✅ Native-VL encoder details — structured `Multimodal.vision_encoder` (HF `vision_config` keys) + `vision_token_anchors`.
- ✅ mRoPE — `RoPEType` includes `"mrope"`; `mrope_section` / `partial_rotary_factor` go in `rope.scaling` dict.
- ✅ Chat-template `enable_thinking` / `preserve_thinking` — initial v3 home was `alignment.inference_modes[].trigger` (free-form). v6 adds the structured `kwargs` companion.
- ✅ Multi-step MTP — `MTPConfig.depth` (semantic match: "D additional tokens"); `mtp_num_hidden_layers` (head depth) goes in `shared_modules`.

**Vendor-fact corrections (against initial roadmap notes):**

- Qwen3.5 also drops the `/think` soft switch — both 3.5 and 3.6 use `enable_thinking` chat-template kwarg.
- Qwen3.5 already has MTP (README: "MTP: trained with multi-steps"; config: `mtp_num_hidden_layers=1`). The 3.6 delta is `preserve_thinking` (multi-turn reasoning carryover), not MTP.

**Recommended next (after this batch):** Now even *more* important to break out of the Qwen / DeepSeek duopoly — 9 of 9 extractions are Qwen or DeepSeek. Cross-family dense baseline: `llama-3.1-70b` (reference dense GQA + RoPE), `mistral-large-2` (European reference), or `glm-4` (Chinese-language design choices). Then a closed model (`gpt-4o` or `claude-sonnet-4`) to exercise `inferred_fields`. A non-Qwen/non-DeepSeek model would also stress-test the new v6 `variant_policy` / `tool_call_protocol` fields against a third vendor's release strategy. Lower-priority deferred schema-iteration candidates from V4 extraction: structured CompressedAttentionConfig (pending second compressed-attention model), structured QuantizationConfig (pending second FP4-QAT model), structured RewardModel slot (pending recurrence of Generative Reward Model design).

> Note on the Qwen3 family: it ships as 6 dense sizes (0.6B–32B) + 2 MoE flagships
> (30B-A3B, 235B-A22B). We extracted two slugs only — the 32B dense and 235B-A22B MoE
> flagships — since dense siblings share architecture and training recipe modulo
> width/depth. If a per-size scaling analysis becomes useful later, schema can grow a
> `metadata.size_variants` field then.

> Note on Qwen3.5/3.6: each generation ships ~7 sizes (0.8B–397B for Qwen3.5; only
> 27B + 35B-A3B open-weight for Qwen3.6 so far). We're extracting four total: the
> dense 27B + smaller MoE 35B-A3B from each generation. Same-size cross-version
> compare is the cleanest signal for the Qwen3.5→3.6 delta.

**Recently completed (2026-05-10):**

- Schema v6 — Qwen3.5/3.6-sub-model-exploration-driven, **backwards-compatible**. Three additions: (a) `metadata.variant_policy` — free-text describing how the vendor partitions capabilities across weight checkpoints vs. runtime modes (Qwen3.5/3.6: unified weights with chat-template kwargs; Qwen2.5: separate Math/Coder/VL/Audio/Omni siblings; DeepSeek-V4: 3 reasoning-effort modes via system prompt collapsing what was V3+R1 split). (b) `training.alignment.inference_modes[].kwargs: dict[str, str]` + `sampling_recommended: dict[str, str]` — make chat-template kwargs and per-mode sampling presets machine-queryable instead of buried in trigger/description prose. (c) `training.alignment.tool_call_protocol` — optional `ToolCallProtocol` subobject `{format, start_token, end_token, arguments_schema, parser_flags, notes}` capturing the wire format (Qwen3-Coder XML-like with `qwen3_coder` parser; DeepSeek-V4 `|DSML|`-namespaced XML). All 9 prior v5 records migrated; the 4 Qwen3.5/3.6 records and the 2 DeepSeek-V4 records carry full content, the 2 Qwen3 records and DeepSeek-V3 carry only `variant_policy` (no documented tool-call wire format in their sources). Renderer extended with a `Variant policy` row, per-mode kwargs/sampling sub-bullets, and a `Tool-call protocol` section. Migration script left in `scripts/migrate_v5_to_v6.py` for posterity.
- Sub-model exploration of Qwen3.5/3.6 confirmed (with sources) the absence of separate Thinking/Math/VL/Coder weight checkpoints in this generation. Chat-template byte-diff between 3.5 and 3.6: only 2 lines change — (1) `preserve_thinking` kwarg (controls whether historical `<think>` blocks render in past assistant turns), (2) tool-call argument JSON-encoding fix (`tojson` now applied to non-string scalars, fixing 'True'/'False' → 'true'/'false'). 27B and 35B-A3B within the same generation have byte-identical templates.
- Schema v5 — DeepSeek-V4-driven, **backwards-compatible**: `architecture.residual_connections` adds optional `ResidualConfig` subobject `{kind, expansion_factor, constraint, iterations, dynamic_parameterization, notes}` for inter-layer residual-stream topology beyond standard residual (mHC / Hyper-Connections); `training.stability_notes` adds an optional free-text field for training-stability tricks distinct from optimizer / lr_schedule / mixed_precision (Anticipatory Routing, SwiGLU Clamping). All 7 prior v4 records migrated cleanly with a one-line `schema_version` bump. Renderer extended to surface the two new sections; mdformat row-wrap quirk in conventions.md changelog (unescaped `|` inside `Foo | None` syntax) discovered and worked around.
- DeepSeek-V4-Pro extraction (1.6T total / 49B active / 33T pre-train tokens; 61 layers; hybrid CSA+HCA attention with shared-KV MQA, Lightning Indexer top-1024, query latent d_c=1536, output groups g=16; mHC `n_hc=4` Sinkhorn `t_max=20`; Muon optimizer with hybrid Newton-Schulz; SqrtSoftplus aux-loss-free routing on 384 routed × 1 shared experts top-6, no node-limited routing; Hash routing for first 3 MoE layers; FP4 QAT MXFP4 on MoE expert weights + indexer QK path; multi-teacher On-Policy Distillation replacing V3.2's mixed-RL stage; 3 reasoning modes Non-think / Think High / Think Max; 1M context curriculum-trained). First repo extraction with mHC, Muon, CSA/HCA, FP4 QAT, OPD.
- DeepSeek-V4-Flash extraction (284B / 13B / 32T; smaller V4 sibling; layers 0-1 use pure SWA instead of pure HCA, otherwise architectural family-shared; 256 routed × 1 shared experts; CSA top-512; query latent d_c=1024; output groups g=8; routed_scaling 1.5 vs Pro's 2.5). Second-pass schema v5 validation — all new slots populated cleanly without revision.
- 5 new glossary entries: mHC, Muon, FP4 QAT (MXFP4), On-Policy Distillation, CSA + HCA. Existing entries updated with V4 "Used by" rows: aux-loss-free-routing, deepseekmoe, mtp, fim, yarn-rope, grpo, dualpipe, fp8-mixed-precision.

**Recently completed (2026-05-09):**

- Schema v4 — Qwen3.5/3.6-driven: `Attention.variants[]` + `layer_pattern` for hybrid stacks; structured `Multimodal` (vision_encoder, vision_token_anchors); `RoPEType` adds `"mrope"`. All three v3 extractions (DeepSeek-V3, Qwen3-32B, Qwen3-235B-A22B) re-validated as v4 (multimodal: null → no migration needed).
- Sourced 4 Qwen3.5/3.6 slugs (config + HF README + blog).
- Qwen3.5-27B extraction (Qwen3.5 dense; hybrid 16×(3 GatedDeltaNet + 1 GatedAttention) backbone, partial RoPE 0.25, mRoPE, native VL with shared 248320 vocab; opt-in YaRN 262K→1010K; first stress-test of v4 hybrid-attention shape — schema held without modification).
- Qwen3.5-35B-A3B extraction (Qwen3.5 MoE; same hybrid backbone at 40 layers / hidden 2048, 256 routed × 512 width with 1 shared expert at 512 width, classic aux-loss `router_aux_loss_coef=0.001` reverting from Qwen3's global-batch LB and DeepSeek-V3's aux-loss-free; first hybrid-attention + MoE-FFN combo — schema held).
- Qwen3.6-27B extraction (post-training-only refresh of Qwen3.5-27B; same architecture, MTP, vision encoder, YaRN; deltas: a third runtime mode `preserve_thinking` for multi-turn reasoning carry-over, plus agentic-coding-focused post-training).
- Qwen3.6-35B-A3B extraction (post-training-only refresh of Qwen3.5-35B-A3B; HF model class is still `Qwen3_5MoeForConditionalGeneration`; same MoE topology + same classic aux-loss; same `preserve_thinking` + agentic-coding deltas as 3.6-27B).
- 2 new glossary entries: Gated DeltaNet, mRoPE; "Used by" rows added across GQA, MTP, YaRN, Hybrid Thinking, DeepSeekMoE for the full Qwen3.5/3.6 family.

**Phase complete:** all 4 native-VL Qwen3.5/3.6 slugs extracted (7 extractions total in repo). Schema v4 held throughout — designed up front, no in-flight changes needed. The 3.6 → 3.5 deltas turned out to be post-training-only (same backbone weights presumed; only HF class names differ at the metadata-level).

**Recommended next:** Cross-family dense baseline to break the Qwen monoculture in extracted set. Per the M1 backlog: `llama-3.1-70b` (reference dense GQA + RoPE), `mistral-large-2` (European reference), or `glm-4` (Chinese-language design choices). Then a closed model (`gpt-4o` or `claude-sonnet-4`) to exercise `inferred_fields`.

**Recently completed (2026-05-03):**

- Schema v3 (`backbone.context_extension`, `alignment.stages`, `alignment.inference_modes`); DeepSeek-V3 migrated
- Qwen3-32B extraction (Qwen flagship dense, GQA + QK-Norm + ABF/YaRN+DCA + four-stage post-training)
- Qwen3-235B-A22B extraction (Qwen flagship MoE — 128 experts/8 active, no shared experts, global-batch load balancing; same four-stage pipeline as 32B)
- 5 new glossary entries: GQA, QK-Norm, Hybrid Thinking, Dual Chunk Attention, Global-batch load balancing; YaRN, GRPO, DeepSeekMoE, and Aux-loss-free entries updated with Qwen3 cross-references

**Recently completed (2026-05-02):**

- Schema v2 + DeepSeek-V3 migration + glossary scaffold (9 seed entries) + Markdown renderer
- DeepSeek-V3 M1 pilot extraction (originally v1; the 7 schema gaps it surfaced drove v2)
- Source manifest + fetcher + pdf_to_text infrastructure
- Project scaffolding (docs/, src/, tasks/, .claude/skills/)

## Status enum

| Status       | Meaning                                                           |
| ------------ | ----------------------------------------------------------------- |
| `backlog`    | Identified as a target, no work started                           |
| `sourcing`   | Fetching `config.json`, papers, blogs into `data/sources/<slug>/` |
| `extracting` | Sources collected, extraction in progress                         |
| `extracted`  | `data/extracted/<slug>.json` written and schema-validates         |
| `reviewed`   | Human-reviewed, open questions resolved or accepted               |
| `blocked`    | Waiting on external info (e.g. paper not yet released)            |

## M1 — Open-weight text models

| Slug                | Family   | Status      | Notes file                                                     | Sources priority                                                                                                  |
| ------------------- | -------- | ----------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `deepseek-v3`       | DeepSeek | `extracted` | [`models/deepseek-v3.md`](./models/deepseek-v3.md)             | **M1 pilot** — extensive paper, exercises MLA + MoE + FP8. Surfaced 7 schema gaps.                                |
| `deepseek-v4-pro`   | DeepSeek | `extracted` | [`models/deepseek-v4-pro.md`](./models/deepseek-v4-pro.md)     | **Schema-v5 driver.** Hybrid CSA+HCA, mHC residuals, Muon, FP4 QAT, multi-teacher OPD, 1M ctx. 1.6T / 49B active. |
| `deepseek-v4-flash` | DeepSeek | `extracted` | [`models/deepseek-v4-flash.md`](./models/deepseek-v4-flash.md) | Schema-v5 second-pass validation. Same V4 architecture family at 284B / 13B; layers 0-1 use SWA instead of HCA.   |
| `deepseek-r1`       | DeepSeek | `backlog`   | —                                                              | RL-focused, exercises `alignment.rl_method`                                                                       |
| `llama-3.1-70b`     | Llama    | `backlog`   | —                                                              | Reference dense model with GQA                                                                                    |
| `llama-3.1-405b`    | Llama    | `backlog`   | —                                                              | Largest open dense model                                                                                          |
| `qwen-2.5-72b`      | Qwen     | `backlog`   | —                                                              | Strong tech report                                                                                                |
| `qwen3-32b`         | Qwen     | `extracted` | [`models/qwen3-32b.md`](./models/qwen3-32b.md)                 | Dense flagship — GQA, hybrid thinking                                                                             |
| `qwen3-235b-a22b`   | Qwen     | `extracted` | [`models/qwen3-235b-a22b.md`](./models/qwen3-235b-a22b.md)     | MoE flagship — compare routing with DeepSeek-V3                                                                   |
| `glm-4`             | GLM      | `backlog`   | —                                                              | Chinese-language design choices                                                                                   |
| `kimi-k2`           | Kimi     | `backlog`   | —                                                              | Long-context architecture                                                                                         |
| `minimax-text-01`   | MiniMax  | `backlog`   | —                                                              | Linear attention variant                                                                                          |
| `mistral-large-2`   | Mistral  | `backlog`   | —                                                              | European reference point                                                                                          |

## M1 — Multimodal extension

Qwen3.5/3.6 are *natively* multimodal (LM + vision encoder ship together), unlike the
older projection-fusion multimodal models below them. They sit in this table because
their primary characterization includes vision, not because they're a "VL extension"
of a text-only LM.

| Slug              | Family  | Status      | Notes file                                                 | Source priority                                                                                                                                                              |
| ----------------- | ------- | ----------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `qwen3.5-35b-a3b` | Qwen    | `extracted` | [`models/qwen3.5-35b-a3b.md`](./models/qwen3.5-35b-a3b.md) | Qwen3.5 MoE — hybrid (10×(3 DeltaNet + 1 GatedAttn)) + 256-expert MoE (top-8 + 1 shared, w 512); native VL                                                                   |
| `qwen3.5-27b`     | Qwen    | `extracted` | [`models/qwen3.5-27b.md`](./models/qwen3.5-27b.md)         | Qwen3.5 dense — hybrid backbone (16×(3 DeltaNet + 1 GatedAttn)), FFN dense 17408, native VL                                                                                  |
| `qwen3.6-35b-a3b` | Qwen    | `extracted` | [`models/qwen3.6-35b-a3b.md`](./models/qwen3.6-35b-a3b.md) | Qwen3.6 MoE — architecturally identical to Qwen3.5-35B-A3B (same `Qwen3_5MoeForConditionalGeneration` HF class); deltas: `preserve_thinking` 3rd mode + agentic-coding focus |
| `qwen3.6-27b`     | Qwen    | `extracted` | [`models/qwen3.6-27b.md`](./models/qwen3.6-27b.md)         | Qwen3.6 dense — architecturally identical to Qwen3.5-27B; deltas: `preserve_thinking` 3rd inference mode + agentic-coding post-training focus                                |
| `qwen-2.5-vl-72b` | Qwen    | `backlog`   | —                                                          | Vision encoder + projection fusion                                                                                                                                           |
| `minicpm-v-2.6`   | MiniCPM | `backlog`   | —                                                          | Compact multimodal                                                                                                                                                           |
| `glm-4v`          | GLM     | `backlog`   | —                                                          | Native vs projected fusion comparison                                                                                                                                        |

## M1 — Closed models (inference)

| Slug              | Family    | Status    | Notes file | Inference confidence                                    |
| ----------------- | --------- | --------- | ---------- | ------------------------------------------------------- |
| `gpt-4o`          | OpenAI    | `backlog` | —          | Architecture from leaks/papers, training mostly unknown |
| `claude-sonnet-4` | Anthropic | `backlog` | —          | Mostly closed; high `[Unknown]` rate expected           |
| `gemini-2.0-pro`  | Google    | `backlog` | —          | Some details public via Google papers                   |

## M2 — Diffusion (deferred)

Not started. Add entries when M1 exit criteria are met (see [`../docs/roadmap.md`](../docs/roadmap.md)).

## How to update this file

When you start work on a model:

1. Move the row's status from `backlog` → `sourcing` (or further along).
2. If it doesn't have a notes file yet, create `models/<slug>.md` from the template (`models/_template.md`) and link it.
3. On completion, update to `extracted` and commit `data/extracted/<slug>.json`.
