# DeepSeek-V4.1-Flash-1017

Status: extracted (schema v8). Collected 2026-10-22; pending independent review.

## Identity and sources

The official checkpoint is **DeepSeek-V4.1-Flash-1017**, not
DeepSeek-V4-Flash-1017. Released 2026-10-17 according to the
[official announcement](https://api-docs.deepseek.com/news/news261017/).
The [model repository](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash-1017)
is pinned to `1bae0e1088993b9b82de08f59de5be5a34e42170`.

`data/sources/deepseek-v4.1-flash-1017/manifest.json` records the current config,
card, tokenizer config, prompt encoder documentation/code, inference
configuration/code, vision code and Engram code. The family report and predecessor
config are separately named `predecessor_report` and `predecessor_config` and pin
the September checkpoint at `dba1be0a40aa45a94ad051997016db3960a90277`.

The public HF revision metadata and vendor release HTML are date-of-collection
snapshots: even a revision-scoped HF metadata endpoint contains mutable activity
counters. Its SHA-256 records the collected bytes; later refreshes may differ
without any checkpoint change. Weight/config/code URLs use immutable revisions.
No model weights were downloaded.

## Current versus earlier evidence

- Current config equals the cached September config as parsed JSON. Forty-layer
  topology, CSA2 source layers, Engram tables, vision sizes and DSpark parameters
  are unchanged. Parameter accounting (552B backbone + 196B memory; 8B prefill /
  16B decode) is explicitly attributed to the linked family architecture report.
  The current card labels this a minor update and links that report.
- The current release announcement specifically discloses **RL with self-feedback**
  for end-to-end projects. It does not disclose GRPO, reward implementation, label
  generation, token budget or optimizer. In particular, self-feedback alone does
  not justify setting `rlaif=true`.
- The current card reports DeepSWE v1.1 74.2 → 77.0 and Terminal-Bench 4.0
  31.2 → 42.3. It identifies Mini-SWE-V2 and Claude Code harnesses respectively;
  these vendor-reported results are not independent reproductions.
- Current encoder verifies numeric effort 1–100, aliases 50/75/100, high=75
  default, exact prompt prefix, and assertion on invalid values. No separate
  1017 effort-training recipe is disclosed.
- September 45T/Muon/GRPO/OPD training assertions are **not inherited**. The
  current minimal inference code runs all layers; optimized CED prefill/cache
  performance is background from the earlier report, not a new 1017 measurement.

## Validation and open questions

Schema validation, bilingual deterministic rendering and source SHA verification
passed. Exact UNKNOWN leaf count: 20. No `inferred_fields` entries.

Current-update training budget, optimizer, schedule, data mixture, SFT/distillation
and feedback semantics remain undisclosed. Full separate parameter accounting for
1017 and production performance of CED/FP4 caches are not restated.

## Release audit and bounded follow-up

[Official HF organization metadata](https://huggingface.co/api/models?author=deepseek-ai&sort=createdAt&direction=-1&limit=30)
was checked on 2026-10-22 against existing extracted slugs. The immediate recent
main-line gaps are covered by this checkpoint, `deepseek-v4-pro-0813` and
`deepseek-v4-flash-vision-exp`. Existing records already cover V4 Preview Pro/Flash,
V4-Flash-0731 and V4.1-Flash.

| Candidate                                     | Decision / reason                                                                                                                                              |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3.2 and V3.2-Speciale               | Real older official releases (2025-12); useful follow-up to existing V3.2-Exp. Deferred from this recent V4 refresh, not claimed complete.                     |
| DeepSeek-Math-V2                              | Real 2025-11 specialized reasoning release; separate follow-up extraction.                                                                                     |
| DeepSeek-OCR and OCR-2                        | Real 2025-10 / 2026-01 specialized vision/OCR releases; separate multimodal scope.                                                                             |
| V4 Pro/Flash Base                             | Already represented in current family variant descriptions; separate base-checkpoint extraction would be additional scope.                                     |
| V4 Pro/Flash DSpark                           | Auxiliary draft attachments for preview weights; current dated Pro/Flash records capture shipped DSpark. No extra full-model row for attachment-only variants. |
| eagle3/dflash/dspark Qwen3/Gemma4 checkpoints | Drafts for other backbone vendors, not new DeepSeek main-line models; retain as speculative-decoding follow-up, not duplicate backbone rows.                   |
| DeepSeek-V4.1-Pro                             | No checkpoint in the audited official release listing; not recorded as a released model.                                                                       |

## Integration handoff

Proposed ROADMAP row: `DeepSeek-V4.1-Flash-1017 | extracted | 2026-10 |`
with notes: dated minor update, unchanged V4.1 architecture, self-feedback RL;
current training details otherwise undisclosed.

Existing glossary adoption edges: CSA2, CED, n-gram embedding/Engram, mHC,
DeepSeekMoE, auxiliary-loss-free routing, reasoning effort, hybrid thinking,
YaRN and speculative decoding. Do not add current-update GRPO, Muon, OPD or
FP4-QAT training edges merely from the predecessor report.
