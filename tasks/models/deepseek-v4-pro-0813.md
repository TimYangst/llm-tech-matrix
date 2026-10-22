# DeepSeek-V4-Pro-0813

Status: extracted (schema v8). Collected 2026-10-22; pending independent review.

## Identity and source boundary

[Official checkpoint](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro-0813),
revision `72e1d3230f6c080a530b0a1d46f8eb4602340597`.
The [API changelog](https://api-docs.deepseek.com/updates/) dates the GA release to
2026-08-13. The current card explicitly says the Preview architecture is retained
and a DSpark module attached.

The manifest pins current config, card, tokenizer, encoder documentation/code,
inference config/code and a date-of-collection release/metadata snapshot.
Revision-scoped HF metadata includes mutable activity counters; config/code URLs
are immutable. The earlier family report is separately named `predecessor_report`:
its original Pro URL now returns 404, so the shared official V4 report is pinned
in the Flash repository at `ad664d5e83023a67c735992e8fe612aeab3c52d2`.

## Current versus Preview

- Same 61-layer, width-7168 Pro backbone; 384 routed experts, top-6 + 1 shared;
  CSA/HCA ratios 4/128; mHC expansion 4. The family's 1.6T/49B counts are attributed
  to the linked earlier architecture report and exclude DSpark.
- Attached DSpark uses block size 5, target layers 58/59/60, Markov rank 512;
  both vLLM and SGLang activation commands are in the current card.
- Current card reports Terminal-Bench 2.1 72.1 → 87.9 and DeepSWE 12.8 → 62.7
  against Preview. Code-agent evaluation uses minimal DeepSeek Harness, effort
  max, temperature 1.0 and top_p 0.95. These are vendor-reported results.
- Low/high/max are runtime effort modes on the same weights; low default and
  exact high/max text and invalid-value assertion verified in the current encoder.
- GA training optimizer, tokens, GRPO/OPD, expert QAT recipe and stages are not
  disclosed by the current release. No Preview training recipe is silently copied.

## Open questions and checks

`config.num_nextn_predict_layers=1` differs from reference
`inference/config.json n_mtp_layers=3`; the latter and `Transformer` construct
three DSpark draft blocks. The three trailing zero compression ratios also fit
that implementation, but the vendor does not reconcile the HF key. This is not
used to assert an MTP training objective.

Schema validation, bilingual deterministic rendering and source SHA verification
passed. Exact UNKNOWN leaf count: 12; no `inferred_fields` entries. Full current
post-training recipe, budget, optimizer and schedule remain unknown.

## Integration handoff

Proposed ROADMAP row: `DeepSeek-V4-Pro-0813 | extracted | 2026-08 |`
with notes: official Pro GA, Preview architecture plus shipped DSpark,
post-training recipe undisclosed.

Glossary edges: CSA/HCA, DeepSeekMoE, auxiliary-loss-free routing, mHC,
reasoning effort, hybrid thinking, YaRN and speculative decoding. Do not add
GA GRPO, Muon, OPD or FP4-QAT training edges without current evidence.
