# Per-Model Roadmap

Tactical, model-by-model status. For strategic milestones (M1/M2 scope, sequencing), see [`../docs/roadmap.md`](../docs/roadmap.md). For how to pick up the project from a fresh session, see [`../docs/session-start.md`](../docs/session-start.md). Engine snapshots (vLLM, SGLang, verl, VeOmni) are tracked separately in [`ENGINES.md`](./ENGINES.md).

## Current focus

**October DeepSeek / MiniMax refresh:** 35 LLM/VL records across 5 vendors,
plus 3 media-generation records and the existing 6 engine snapshots. LLM schema
remains v8; media schema v1 is independent. Validation and independent review are
tracked in the sole [refresh state](deepseek-minimax-refresh.md).

New DeepSeek checkpoints: V4.1-Flash-1017 (the exact official name), V4-Pro-0813,
and V4-Flash-Vision-Exp. MiniMax core coverage now spans Text-01, VL-01, M1-80k,
M2, M2.1, M2.5, M2.7 and M3. M3.1 Flash is sourced but API-only with future weights
announced; unknown FFN type also prevents an honest v8 canonical extraction.

The [media index](../data/extracted/media/README.md) covers H3's released base and
hosted pipeline boundary, open-weight Music3, and closed Speech 2.8. These are
source-derived technical records, not inference or quality benchmarks. Historical
Speech/Music/Hailuo releases and research extras remain explicit follow-ups below;
other vendors' audio/video models are outside this refresh by user choice.

## Next work

The active [refresh state](deepseek-minimax-refresh.md) owns this phase's tasks,
review, authorization and PR #21 handoff. After that delivery, select one bounded
question from the inventory below: remaining DeepSeek lineage, a cross-vendor
dense baseline, a closed LLM, an interpretive report, or historical media coverage.
Closed LLMs first need a schema check: v8 cannot represent an unknown FFN type.

Per-model notes and canonical JSON retain extraction findings and unresolved
source disagreements. Prior phase narratives and superseded queues are available
in the [pre-cleanup roadmap snapshot](https://github.com/TimYangst/llm-tech-matrix/blob/1b72ed94d6ba7378e3da805d6ff498bfd2a13881/tasks/ROADMAP.md);
this page maintains current inventory and next actions.

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

| Slug                     | Family   | Status      | Notes file                                                               | Sources priority                                                                                                                                                                                                                     |
| ------------------------ | -------- | ----------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `deepseek-v4-pro-0813`   | DeepSeek | `extracted` | [models/deepseek-v4-pro-0813.md](./models/deepseek-v4-pro-0813.md)       | Official Pro release with DSpark; unchanged Preview architecture.                                                                                                                                                                    |
| `minimax-m1-80k`         | MiniMax  | `extracted` | [models/minimax-m1-80k.md](./models/minimax-m1-80k.md)                   | Lightning/GQA reasoning model; representative 80K reasoning-budget variant.                                                                                                                                                          |
| `minimax-m2`             | MiniMax  | `extracted` | [models/minimax-m2.md](./models/minimax-m2.md)                           | 230B/10B sparse MoE; GQA and agentic post-training.                                                                                                                                                                                  |
| `minimax-m2.1`           | MiniMax  | `extracted` | [models/minimax-m2.1.md](./models/minimax-m2.1.md)                       | M2 architecture lineage; multilingual coding and agentic refresh.                                                                                                                                                                    |
| `minimax-m2.5`           | MiniMax  | `extracted` | [models/minimax-m2.5.md](./models/minimax-m2.5.md)                       | 230B/10B; wider agent/environment post-training coverage.                                                                                                                                                                            |
| `minimax-m2.7`           | MiniMax  | `extracted` | [models/minimax-m2.7.md](./models/minimax-m2.7.md)                       | 230B/10B; 204800-position config and self-evolution claims.                                                                                                                                                                          |
| `deepseek-v3`            | DeepSeek | `extracted` | [`models/deepseek-v3.md`](./models/deepseek-v3.md)                       | **M1 pilot** — extensive paper, exercises MLA + MoE + FP8. Surfaced 7 schema gaps.                                                                                                                                                   |
| `deepseek-v4-pro`        | DeepSeek | `extracted` | [`models/deepseek-v4-pro.md`](./models/deepseek-v4-pro.md)               | **Schema-v5 driver.** Hybrid CSA+HCA, mHC residuals, Muon, FP4 QAT, multi-teacher OPD, 1M ctx. 1.6T / 49B active.                                                                                                                    |
| `deepseek-v4-flash`      | DeepSeek | `extracted` | [`models/deepseek-v4-flash.md`](./models/deepseek-v4-flash.md)           | Schema-v5 second-pass validation. Same V4 architecture family at 284B / 13B; layers 0-1 use SWA instead of HCA.                                                                                                                      |
| `deepseek-v3.2-exp`      | DeepSeek | `extracted` | [`models/deepseek-v3.2-exp.md`](./models/deepseek-v3.2-exp.md)           | **DSA origin.** 671B/37B; config diff vs V3 is exactly 3 indexer keys. Two-stage bolt-on recipe; single mixed RL stage.                                                                                                              |
| `deepseek-v4-flash-0731` | DeepSeek | `extracted` | [`models/deepseek-v4-flash-0731.md`](./models/deepseek-v4-flash-0731.md) | Official V4-Flash. Architecturally frozen vs preview; ships the DSpark speculative-decoding module in-checkpoint.                                                                                                                    |
| `deepseek-r1`            | DeepSeek | `backlog`   | —                                                                        | RL-focused, exercises `alignment.rl_method`                                                                                                                                                                                          |
| `deepseek-v3.1`          | DeepSeek | `backlog`   | —                                                                        | The V3 → V3.2-Exp missing link (V3.1 / V3.1-Terminus is the dense checkpoint DSA was retrofitted onto)                                                                                                                               |
| `llama-3.1-70b`          | Llama    | `backlog`   | —                                                                        | Reference dense model with GQA                                                                                                                                                                                                       |
| `llama-3.1-405b`         | Llama    | `backlog`   | —                                                                        | Largest open dense model                                                                                                                                                                                                             |
| `qwen-2.5-72b`           | Qwen     | `backlog`   | —                                                                        | Strong tech report                                                                                                                                                                                                                   |
| `qwen3-32b`              | Qwen     | `extracted` | [`models/qwen3-32b.md`](./models/qwen3-32b.md)                           | Dense flagship — GQA, hybrid thinking                                                                                                                                                                                                |
| `qwen3-235b-a22b`        | Qwen     | `extracted` | [`models/qwen3-235b-a22b.md`](./models/qwen3-235b-a22b.md)               | MoE flagship — compare routing with DeepSeek-V3                                                                                                                                                                                      |
| `glm-4.7`                | GLM      | `extracted` | [`models/glm-4.7.md`](./models/glm-4.7.md)                               | GLM-4.5 ARC architecture (358B MoE, GQA + QK-Norm + partial RoPE + 160-expert MoE) — predecessor anchor for GLM-5                                                                                                                    |
| `glm-5`                  | GLM      | `extracted` | [`models/glm-5.md`](./models/glm-5.md)                                   | First non-DeepSeek vendor to ship DSA. 744B / 40B active. MLA + DSA + 256-expert MoE + Muon Split. Schema-v6 4th vendor.                                                                                                             |
| `glm-5.1`                | GLM      | `extracted` | [`models/glm-5.1.md`](./models/glm-5.1.md)                               | Post-training-only refresh of GLM-5 (config byte-identical except `transformers_version`); long-horizon agentic delta.                                                                                                               |
| `kimi-k2-thinking`       | Kimi     | `extracted` | [`models/kimi-k2-thinking.md`](./models/kimi-k2-thinking.md)             | K2 text-only Thinking sibling — native INT4 QAT origin, 200–300 sequential tool calls, Heavy Mode aggregation                                                                                                                        |
| `qwen3.8-2.4t-a95b`      | Qwen     | `extracted` | [`models/qwen3.8-2.4t-a95b.md`](./models/qwen3.8-2.4t-a95b.md)           | **First open-weight Qwen-Max-class model** and the repo's largest record. 2.4T / 95B active, 92L, 512 experts top-10 + 1 shared, classic aux-loss. Text-only and thinking-only — both properties of the open release, not the model. |
| `glm-5.2`                | GLM      | `extracted` | [`models/glm-5.2.md`](./models/glm-5.2.md)                               | **IndexShare** cross-layer indexer reuse (21 Full / 57 Shared of 78 layers, 2.9× fewer per-token FLOPs at 1M) + 1M context + reasoning-effort axis. MIT. Not a refresh — a real architecture change on the GLM-5 topology.           |
| `minimax-text-01`        | MiniMax  | `extracted` | [models/minimax-text-01.md](./models/minimax-text-01.md)                 | Lightning/GQA hybrid anchor; 456B/45.9B.                                                                                                                                                                                             |
| `mistral-large-2`        | Mistral  | `backlog`   | —                                                                        | European reference point                                                                                                                                                                                                             |

## M1 — Multimodal extension

Qwen3.5/3.6 are *natively* multimodal (LM + vision encoder ship together), unlike the
older projection-fusion multimodal models below them. They sit in this table because
their primary characterization includes vision, not because they're a "VL extension"
of a text-only LM.

| Slug                           | Family   | Status      | Notes file                                                                         | Source priority                                                                                                                                                                                                                                                                             |
| ------------------------------ | -------- | ----------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `deepseek-v4.1-flash`          | DeepSeek | `extracted` | [models/deepseek-v4.1-flash.md](models/deepseek-v4.1-flash.md)                     | September architecture anchor: native image/text CED, CSA2 and Engram.                                                                                                                                                                                                                      |
| `deepseek-v4.1-flash-1017`     | DeepSeek | `extracted` | [models/deepseek-v4.1-flash-1017.md](./models/deepseek-v4.1-flash-1017.md)         | Same pinned backbone config as September; October self-feedback RL update.                                                                                                                                                                                                                  |
| `minimax-m3`                   | MiniMax  | `extracted` | [models/minimax-m3.md](./models/minimax-m3.md)                                     | Native image/text; GQA + MSA; production training distinct from 109B paper experiment.                                                                                                                                                                                                      |
| `qwen3.5-35b-a3b`              | Qwen     | `extracted` | [`models/qwen3.5-35b-a3b.md`](./models/qwen3.5-35b-a3b.md)                         | Qwen3.5 MoE — hybrid (10×(3 DeltaNet + 1 GatedAttn)) + 256-expert MoE (top-8 + 1 shared, w 512); native VL                                                                                                                                                                                  |
| `qwen3.5-27b`                  | Qwen     | `extracted` | [`models/qwen3.5-27b.md`](./models/qwen3.5-27b.md)                                 | Qwen3.5 dense — hybrid backbone (16×(3 DeltaNet + 1 GatedAttn)), FFN dense 17408, native VL                                                                                                                                                                                                 |
| `qwen3.6-35b-a3b`              | Qwen     | `extracted` | [`models/qwen3.6-35b-a3b.md`](./models/qwen3.6-35b-a3b.md)                         | Qwen3.6 MoE — architecturally identical to Qwen3.5-35B-A3B (same `Qwen3_5MoeForConditionalGeneration` HF class); deltas: `preserve_thinking` 3rd mode + agentic-coding focus                                                                                                                |
| `qwen3.6-27b`                  | Qwen     | `extracted` | [`models/qwen3.6-27b.md`](./models/qwen3.6-27b.md)                                 | Qwen3.6 dense — architecturally identical to Qwen3.5-27B; deltas: `preserve_thinking` 3rd inference mode + agentic-coding post-training focus                                                                                                                                               |
| `kimi-k2.5`                    | Kimi     | `extracted` | [`models/kimi-k2.5.md`](./models/kimi-k2.5.md)                                     | Kimi K2.5 — native multimodal continual-pretrain on K2-base; MoonViT-3D + MLP projector; Agent Swarm via PARL; zero-vision SFT; INT4 QAT inherited from K2-Thinking                                                                                                                         |
| `kimi-k3`                      | Kimi     | `extracted` | [`models/kimi-k3.md`](./models/kimi-k3.md)                                         | Kimi K3 — 2.8T/104B, KDA + Gated MLA 3:1, AttnRes, Stable LatentMoE 896/16, SiTU-GLU, NoPE, MXFP4/MXFP8 QAT, MoonViT-V2 from scratch. Full rewrite of the K2 architecture; schema-v7 driver                                                                                                 |
| `kimi-k2.6`                    | Kimi     | `extracted` | [`models/kimi-k2.6.md`](./models/kimi-k2.6.md)                                     | Kimi K2.6 — post-training-only refresh of K2.5; adds `preserve_thinking` 3rd kwarg-only mode; Agent Swarm scaled to 300 sub-agents × 4000 steps; long-horizon coding focus                                                                                                                  |
| `glm-5.3-flash`                | GLM      | `extracted` | [`models/glm-5.3-flash.md`](./models/glm-5.3-flash.md)                             | **New GLM architecture line** (`glm5_next`). 320B / 18B active, first natively multimodal GLM-5-series model. 3:1 KDA + NoPE-MLA/DSA hybrid, mHC (Sinkhorn-20), key-pooled DSA indexer, 288 experts, FP8-primary.                                                                           |
| `qwen3.8-flash-next`           | Qwen     | `extracted` | [`models/qwen3.8-flash-next.md`](./models/qwen3.8-flash-next.md)                   | **Qwen4 architecture preview** under a 3.8 name (`Qwen4ExpForConditionalGeneration`). 125B / 6B active + 51B host-memory n-gram embeddings + 4B MTP. QSA micro-block sparse attention, Gated Residual (4 branches, no `H_res`), Muon/AdamW split. **First Qwen record with a tech report.** |
| `qwen3.8-27b`                  | Qwen     | `extracted` | [`models/qwen3.8-27b.md`](./models/qwen3.8-27b.md)                                 | Qwen3.8 dense — `config.json` byte-identical to Qwen3.6-27B except `transformers_version`; frozen backbone across 3.5 → 3.6 → 3.8. Deltas: `reasoning_effort` 3 levels, `preserve_thinking` default ON.                                                                                     |
| `qwen-2.5-vl-72b`              | Qwen     | `backlog`   | —                                                                                  | Vision encoder + projection fusion                                                                                                                                                                                                                                                          |
| `minicpm-v-2.6`                | MiniCPM  | `backlog`   | —                                                                                  | Compact multimodal                                                                                                                                                                                                                                                                          |
| `glm-4v`                       | GLM      | `backlog`   | —                                                                                  | Native vs projected fusion comparison                                                                                                                                                                                                                                                       |
| `deepseek-v4-flash-vision-exp` | DeepSeek | `extracted` | [models/deepseek-v4-flash-vision-exp.md](./models/deepseek-v4-flash-vision-exp.md) | Vision adaptor and continued training on V4-Flash; image/text understanding.                                                                                                                                                                                                                |
| `minimax-vl-01`                | MiniMax  | `extracted` | [models/minimax-vl-01.md](./models/minimax-vl-01.md)                               | Vision encoder/projector on Text-01 lineage.                                                                                                                                                                                                                                                |

## M1 — Closed models (inference)

| Slug              | Family    | Status    | Notes file | Inference confidence                                                                                                                                                                             |
| ----------------- | --------- | --------- | ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `gpt-4o`          | OpenAI    | `backlog` | —          | Architecture from leaks/papers, training mostly unknown                                                                                                                                          |
| `claude-sonnet-4` | Anthropic | `backlog` | —          | Mostly closed; high `[Unknown]` rate expected                                                                                                                                                    |
| `gemini-2.0-pro`  | Google    | `backlog` | —          | Some details public via Google papers                                                                                                                                                            |
| `qwen3.7-max`     | Qwen      | `backlog` | —          | **Highest-value closed candidate.** Fills the one unobservable generation in the Qwen lineage (API-only, 2026-05); same-family priors make `inferred_fields` cheap to justify and easy to bound. |

## Media generation — DeepSeek / MiniMax scope

Independent [media schema](../docs/media/schema.md) and
[bilingual index](../data/extracted/media/README.md). No DeepSeek open audio/video
foundation-generation checkpoint was identified in the inspected official model
inventory; its image-understanding models remain LLM/VL records.

| Slug                 | Family  | Status      | Notes file                                                   | Scope                                                                            |
| -------------------- | ------- | ----------- | ------------------------------------------------------------ | -------------------------------------------------------------------------------- |
| `minimax-h3`         | MiniMax | `extracted` | [models/minimax-h3.md](models/minimax-h3.md)                 | Joint video/stereo audio; open 768p base, hosted Context-IR and 2K regeneration. |
| `minimax-music3`     | MiniMax | `extracted` | [models/minimax-music3.md](models/minimax-music3.md)         | Open text-to-music; Hybrid-LM + Flow Matching + Flow-VAE.                        |
| `minimax-speech-2.8` | MiniMax | `extracted` | [models/minimax-speech-2.8.md](models/minimax-speech-2.8.md) | Closed text-to-speech/voice cloning; architecture unknown.                       |

## Follow-up inventory

These are known coverage gaps, not completed extractions. Representative checkpoint
selection avoids duplicating repackagings; all current core open MiniMax families
are covered above. Historical products and specialized research remain separate.

| Candidate                                                                        | Scope / reason                                                                              | Evidence / next action                                                                                                                                                                                                                        |
| -------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `minimax-m3.1-flash`                                                             | `blocked`: hosted October 19 release; weights promised later; v8 FFN cannot express unknown | [Sourced task](models/minimax-m3.1-flash.md); recheck weights and closed-model schema before extraction.                                                                                                                                      |
| DeepSeek-V3.2 / Speciale, Math-V2, OCR / OCR-2, VL2, Janus / Janus-Pro           | Older/specialized releases                                                                  | [Inventory notes](models/deepseek-v4.1-flash-1017.md); source/extract separately. Existing R1/V3.1 backlog remains above.                                                                                                                     |
| MiniMax-M1-40k and HF-compatible repackaging                                     | Variant, not separate core architecture                                                     | M1 [variant policy](../data/extracted/minimax-m1-80k.json); source a separate record if budget comparison requires it.                                                                                                                        |
| MiniMax-M3-MXFP8                                                                 | Precision sibling                                                                           | [Official repository](https://huggingface.co/MiniMaxAI/MiniMax-M3-MXFP8); future quantization comparison, not claimed extracted.                                                                                                              |
| Speech01 / Speech02 HD & Turbo / Speech2.5 / Speech2.6                           | Historical hosted speech lineage; open test dataset is not open weights                     | [Speech02 launch](https://www.minimax.io/news/speech-02-series), [Speech2.5](https://www.minimax.io/news/minimax-speech-25), [official research index](https://www.minimax.io/research). Register version-specific sources before extraction. |
| Music2.0 / Music2.5 / Music2.5+; earlier Hailuo and Image-01                     | Historical hosted media products                                                            | [Official research index](https://www.minimax.io/research); distinguish product API from released weights.                                                                                                                                    |
| SynLogic / VTP                                                                   | Specialized reasoning and vision-pretraining research                                       | [Official HF inventory](https://huggingface.co/MiniMaxAI/models); outside core chat/media checkpoint selection.                                                                                                                               |
| Kimi Linear / Kimi family roots; GLM-V / GLM-OCR                                 | Additional architecture-origin and multimodal comparison records                            | Source official checkpoints before adding records; not part of this refresh.                                                                                                                                                                  |
| Reward-model structure, pretraining stages, open-checkpoint/hosted-product split | Unresolved LLM schema-design candidates                                                     | Recheck canonical open_questions and actual comparison needs before versioning; reasoning_effort already exists in v8.                                                                                                                        |
| Other vendors' image/audio/video generators                                      | User deferred to next phase                                                                 | Choose official checkpoints and representative comparison questions before sourcing.                                                                                                                                                          |

## How to update this file

When you start work on a model:

1. Move the row's status from `backlog` → `sourcing` (or further along).
2. If it doesn't have a notes file yet, create `models/<slug>.md` from the template (`models/_template.md`) and link it.
3. On completion, update to `extracted` and commit `data/extracted/<slug>.json`.
