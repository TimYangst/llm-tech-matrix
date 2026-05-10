# Per-Model Roadmap

Tactical, model-by-model status. For strategic milestones (M1/M2 scope, sequencing), see [`../docs/roadmap.md`](../docs/roadmap.md). For how to pick up the project from a fresh session, see [`../docs/session-start.md`](../docs/session-start.md).

## Current focus

**Phase:** M1 — pivoting into native-multimodal territory with Qwen3.5/3.6, the next
generation after our Qwen3 entries. These ship as **Causal LM + Vision Encoder** by
default (no text-only checkpoint), so this batch is the project's first real exercise
of the multimodal schema region — and they introduce a hybrid Gated DeltaNet + Gated
Attention backbone that doesn't fit cleanly in the current `architecture.attention`
shape. Expect a schema iteration during/after extraction.

**In progress (sourcing):**

- `qwen3.5-35b-a3b` — Qwen3.5 MoE smaller (Feb 2026)
- `qwen3.5-27b` — Qwen3.5 dense (Feb 2026)
- `qwen3.6-35b-a3b` — Qwen3.6 MoE smaller (Apr 2026, +MTP, removes /think soft switch)
- `qwen3.6-27b` — Qwen3.6 dense (Apr 2026, +MTP)

**Anticipated schema gaps (record before extraction starts):**

- `architecture.attention` is a single object; Qwen3.5/3.6 layout is
  `N × (3 × (Gated DeltaNet → FFN/MoE) → 1 × (Gated Attention → FFN/MoE))` — needs
  per-block-type variants or a layer-pattern field.
- `architecture.multimodal` currently is `{vision_encoder, audio_encoder, fusion, fusion_notes}` (4 strings). Native VL with shared backbone needs richer encoder
  details (params, patch size, native resolution, training data).
- `training.objectives.multi_token_prediction` exists, but Qwen3.6 trains with
  multi-step MTP — confirm the field captures step depth.
- Chat-template details (soft-switch `/think` + API-only `enable_thinking` +
  `preserve_thinking`) need somewhere structured to live; current
  `alignment.inference_modes.trigger` is free-form.

**Recommended next (after this batch):** Cross-family dense baseline — `llama-3.1-70b`
or `mistral-large-2` or `glm-4` to break out of the Qwen / DeepSeek duopoly. Then a
closed model (`gpt-4o` or `claude-sonnet-4`) to exercise `inferred_fields`.

> Note on the Qwen3 family: it ships as 6 dense sizes (0.6B–32B) + 2 MoE flagships
> (30B-A3B, 235B-A22B). We extracted two slugs only — the 32B dense and 235B-A22B MoE
> flagships — since dense siblings share architecture and training recipe modulo
> width/depth. If a per-size scaling analysis becomes useful later, schema can grow a
> `metadata.size_variants` field then.

> Note on Qwen3.5/3.6: each generation ships ~7 sizes (0.8B–397B for Qwen3.5; only
> 27B + 35B-A3B open-weight for Qwen3.6 so far). We're extracting four total: the
> dense 27B + smaller MoE 35B-A3B from each generation. Same-size cross-version
> compare is the cleanest signal for the Qwen3.5→3.6 delta.

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

| Slug              | Family   | Status      | Notes file                                                 | Sources priority                                                                |
| ----------------- | -------- | ----------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `deepseek-v3`     | DeepSeek | `extracted` | [`models/deepseek-v3.md`](./models/deepseek-v3.md)         | **Pilot** — extensive paper, exercises MLA + MoE + FP8. Surfaced 7 schema gaps. |
| `deepseek-r1`     | DeepSeek | `backlog`   | —                                                          | RL-focused, exercises `alignment.rl_method`                                     |
| `llama-3.1-70b`   | Llama    | `backlog`   | —                                                          | Reference dense model with GQA                                                  |
| `llama-3.1-405b`  | Llama    | `backlog`   | —                                                          | Largest open dense model                                                        |
| `qwen-2.5-72b`    | Qwen     | `backlog`   | —                                                          | Strong tech report                                                              |
| `qwen3-32b`       | Qwen     | `extracted` | [`models/qwen3-32b.md`](./models/qwen3-32b.md)             | Dense flagship — GQA, hybrid thinking                                           |
| `qwen3-235b-a22b` | Qwen     | `extracted` | [`models/qwen3-235b-a22b.md`](./models/qwen3-235b-a22b.md) | MoE flagship — compare routing with DeepSeek-V3                                 |
| `glm-4`           | GLM      | `backlog`   | —                                                          | Chinese-language design choices                                                 |
| `kimi-k2`         | Kimi     | `backlog`   | —                                                          | Long-context architecture                                                       |
| `minimax-text-01` | MiniMax  | `backlog`   | —                                                          | Linear attention variant                                                        |
| `mistral-large-2` | Mistral  | `backlog`   | —                                                          | European reference point                                                        |

## M1 — Multimodal extension

Qwen3.5/3.6 are *natively* multimodal (LM + vision encoder ship together), unlike the
older projection-fusion multimodal models below them. They sit in this table because
their primary characterization includes vision, not because they're a "VL extension"
of a text-only LM.

| Slug              | Family  | Status     | Notes file                                                 | Source priority                                                       |
| ----------------- | ------- | ---------- | ---------------------------------------------------------- | --------------------------------------------------------------------- |
| `qwen3.5-35b-a3b` | Qwen    | `sourcing` | [`models/qwen3.5-35b-a3b.md`](./models/qwen3.5-35b-a3b.md) | Qwen3.5 MoE — hybrid Gated DeltaNet + MoE w/ shared expert; native VL |
| `qwen3.5-27b`     | Qwen    | `sourcing` | [`models/qwen3.5-27b.md`](./models/qwen3.5-27b.md)         | Qwen3.5 dense — hybrid backbone, FFN dense; native VL                 |
| `qwen3.6-35b-a3b` | Qwen    | `sourcing` | [`models/qwen3.6-35b-a3b.md`](./models/qwen3.6-35b-a3b.md) | Qwen3.6 MoE — same arch as 3.5, +MTP, removes /think soft switch      |
| `qwen3.6-27b`     | Qwen    | `sourcing` | [`models/qwen3.6-27b.md`](./models/qwen3.6-27b.md)         | Qwen3.6 dense — same arch as 3.5, +MTP, agentic-coding RL             |
| `qwen-2.5-vl-72b` | Qwen    | `backlog`  | —                                                          | Vision encoder + projection fusion                                    |
| `minicpm-v-2.6`   | MiniCPM | `backlog`  | —                                                          | Compact multimodal                                                    |
| `glm-4v`          | GLM     | `backlog`  | —                                                          | Native vs projected fusion comparison                                 |

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
