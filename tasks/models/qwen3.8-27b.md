# Qwen3.8-27B

Slug: `qwen3.8-27b`
Family: `qwen`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/qwen3.8-27b/manifest.json` (committed).
This section is for human notes — links to register, candidates considered, rationale.

Registered sources:

- [x] `config` (`hf_config`) — `https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/config.json`
- [x] `tokenizer_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/tokenizer_config.json`
- [x] `preprocessor_config` (`other`) — `https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/preprocessor_config.json`
- [x] `readme` (`model_card`) — `https://huggingface.co/Qwen/Qwen3.8-27B/raw/main/README.md`
- [x] `blog` (`blog_html`) — `https://qwen.ai/blog?id=qwen3.8`

Considered but excluded:

- No arXiv paper. Qwen has now shipped 3.5, 3.6 and 3.8 with no technical report.
- `Qwen/Qwen3.8-27B-FP8` — quantized derivative of the same weights, not a separate
  architecture. No `training.quantization` record is warranted: FP8 here is a
  post-hoc serving conversion, not QAT.

## Open questions

See `data/extracted/qwen3.8-27b.json` `open_questions` for the authoritative list. The
load-bearing one: **fresh pre-train vs post-training-only refresh is undetermined.**
`config.json` is byte-identical to Qwen3.6-27B except `transformers_version`, which
proves the architecture is frozen but says nothing about the weights — and the benchmark
deltas (QwenSWEBench 49.3 → 79.0, DeepSWE 1.1 13.3 → 42.2) are large for a
post-training-only release.

## Resolved

- ✅ **Does Qwen3.6 have later sizes we missed?** No. HF `Qwen` org search for `Qwen3.6`
  returns exactly the four April 2026 repos (27B, 35B-A3B, and their FP8 variants).
  Nothing shipped after 2026-04-21.
- ✅ **What happened to Qwen3.7?** No open weights at all — `Qwen3.7` returns zero HF
  repos under the `Qwen` org. 3.7 shipped as hosted API models only (Qwen3.7-Max
  2026-05, Qwen3.7-Plus 2026-06). The open-weight lineage runs 3.6 → 3.8.
- ✅ **Schema fits the new `reasoning_effort` axis** — v6's
  `inference_modes[].kwargs` carries it with no schema change, following the
  DeepSeek-V4 and Kimi K3 precedent of one mode entry per effort level.

## Inferred fields (closed models only)

N/A — Qwen3.8-27B is open-weight (Apache 2.0).

## Notes

**Config diff vs Qwen3.6-27B** — the entire diff:

```
120c120
<     "transformers_version": "4.57.1",
---
>     "transformers_version": "5.8.0.dev0",
```

`tokenizer_config.json` is likewise identical outside `chat_template`, and
`preprocessor_config.json` is byte-identical (sha256 `27225450ac9c…`) all the way back
to Qwen3.5-27B.

**Chat-template deltas vs Qwen3.6-27B** (the entire release delta, as far as artifacts show):

1. **`reasoning_effort` added** — `xhigh` (default) / `medium` / `low`, injected as
   system-message instruction text. `medium` injects nothing. Unsupported values raise.
2. **`preserve_thinking` default flips OFF → ON** — condition changes from
   `preserve_thinking is defined and ... is true` to `preserve_thinking is undefined or ... is true`.
3. Removed the fallback that split `<think>` / `</think>` out of historical content strings.
4. Tool-call arg loop now also skips empty-string arguments.

**Benchmarks vs Qwen3.6-27B** (from the model card; comparison columns are Qwen3.6-27B,
Qwen3.7-Plus, Muse Glimmer-30B, Opus 4.6 Max):

| Benchmark | 3.6-27B | 3.8-27B |
| --- | --- | --- |
| Terminal Bench 2.1 (Terminus) | 63.4 | 73.0 |
| SWE-bench Pro | 53.5 | 61.7 |
| NL2Repo-Bench | 36.2 | 42.3 |
| DeepSWE 1.1 | 13.3 | 42.2 |
| QwenSWEBench | 49.3 | 79.0 |
| CoWorkBench | 61.0 | 70.7 |
| JobBench | 21.8 | 33.4 |
| Agents' Last Exam (pass@1 / score) | 10.6 / 27.3 | 20.4 / 42.9 |

**Open vs hosted**: the README says a hosted Qwen3.8-27B is coming on Qwen Cloud with
1M context by default and official built-in tools. The open weights are the same model
with a smaller productized envelope — a split the schema does not currently model.
