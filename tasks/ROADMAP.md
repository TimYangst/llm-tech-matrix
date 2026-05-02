# Per-Model Roadmap

Tactical, model-by-model status. For strategic milestones (M1/M2 scope, sequencing), see [`../docs/roadmap.md`](../docs/roadmap.md).

## Status enum

| Status | Meaning |
|---|---|
| `backlog` | Identified as a target, no work started |
| `sourcing` | Fetching `config.json`, papers, blogs into `data/sources/<slug>/` |
| `extracting` | Sources collected, extraction in progress |
| `extracted` | `data/extracted/<slug>.json` written and schema-validates |
| `reviewed` | Human-reviewed, open questions resolved or accepted |
| `blocked` | Waiting on external info (e.g. paper not yet released) |

## M1 — Open-weight text models

| Slug | Family | Status | Notes file | Sources priority |
|---|---|---|---|---|
| `deepseek-v3` | DeepSeek | `extracted` | [`models/deepseek-v3.md`](./models/deepseek-v3.md) | **Pilot** — extensive paper, exercises MLA + MoE + FP8. Surfaced 7 schema gaps. |
| `deepseek-r1` | DeepSeek | `backlog` | — | RL-focused, exercises `alignment.rl_method` |
| `llama-3.1-70b` | Llama | `backlog` | — | Reference dense model with GQA |
| `llama-3.1-405b` | Llama | `backlog` | — | Largest open dense model |
| `qwen-2.5-72b` | Qwen | `backlog` | — | Strong tech report |
| `qwen-3-235b` | Qwen | `backlog` | — | MoE — compare with DeepSeek-V3 routing |
| `glm-4` | GLM | `backlog` | — | Chinese-language design choices |
| `kimi-k2` | Kimi | `backlog` | — | Long-context architecture |
| `minimax-text-01` | MiniMax | `backlog` | — | Linear attention variant |
| `mistral-large-2` | Mistral | `backlog` | — | European reference point |

## M1 — Multimodal extension

| Slug | Family | Status | Notes file | Source priority |
|---|---|---|---|---|
| `qwen-2.5-vl-72b` | Qwen | `backlog` | — | Vision encoder + projection fusion |
| `minicpm-v-2.6` | MiniCPM | `backlog` | — | Compact multimodal |
| `glm-4v` | GLM | `backlog` | — | Native vs projected fusion comparison |

## M1 — Closed models (inference)

| Slug | Family | Status | Notes file | Inference confidence |
|---|---|---|---|---|
| `gpt-4o` | OpenAI | `backlog` | — | Architecture from leaks/papers, training mostly unknown |
| `claude-sonnet-4` | Anthropic | `backlog` | — | Mostly closed; high `[Unknown]` rate expected |
| `gemini-2.0-pro` | Google | `backlog` | — | Some details public via Google papers |

## M2 — Diffusion (deferred)

Not started. Add entries when M1 exit criteria are met (see [`../docs/roadmap.md`](../docs/roadmap.md)).

## How to update this file

When you start work on a model:

1. Move the row's status from `backlog` → `sourcing` (or further along).
2. If it doesn't have a notes file yet, create `models/<slug>.md` from the template (`models/_template.md`) and link it.
3. On completion, update to `extracted` and commit `data/extracted/<slug>.json`.
