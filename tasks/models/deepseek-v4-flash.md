# DeepSeek-V4-Flash

Slug: `deepseek-v4-flash`
Family: `deepseek`
Status: `extracted`

Extracted 2026-05-10 against schema_version=5. JSON at `data/extracted/deepseek-v4-flash.json` validates cleanly. Bilingual rendered Markdown at `data/extracted/deepseek-v4-flash.md` and `…/deepseek-v4-flash.zh.md`.

## Sources

The authoritative list is `data/sources/deepseek-v4-flash/manifest.json`:

- `config` (`hf_config`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/config.json` ✓
- `paper` (`tech_report`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf` ✓ (single family-shared report)
- `readme` (`model_card`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/README.md` ✓ (byte-identical to V4-Pro README)
- `tokenizer_config` (`other`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/tokenizer_config.json` ✓ (byte-identical to V4-Pro)
- `generation_config` (`other`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash/raw/main/generation_config.json` ✓ (byte-identical to V4-Pro)
- `blog_hf` (`blog_html`) — `https://huggingface.co/blog/deepseekv4` ✓

The third-party `deepseek4.hk` blogs registered under V4-Pro are not registered here — they're family-level coverage, not Flash-specific.

## Deltas vs V4-Pro

V4-Flash is the smaller sibling sharing the V4 architecture family. The architectural differences are localized to scale knobs:

| Knob                      | V4-Flash                    | V4-Pro            |
| ------------------------- | --------------------------- | ----------------- |
| Layers                    | 43                          | 61                |
| Hidden dim                | 4096                        | 7168              |
| Attention query heads n_h | 64                          | 128               |
| First-2-layer attention   | Pure SWA (compress_ratio=0) | Pure HCA (m'=128) |
| CSA top-k                 | 512                         | 1024              |
| Query latent d_c          | 1024                        | 1536              |
| Output groups g           | 8                           | 16                |
| Routed experts            | 256                         | 384               |
| Per-expert intermediate   | 2048                        | 3072              |
| Routed scaling factor     | 1.5                         | 2.5               |
| Total params              | 284B                        | 1.6T              |
| Active params             | 13B                         | 49B               |
| Pre-train tokens          | 32T                         | 33T               |
| Peak LR                   | 2.7e-4                      | 2.0e-4            |
| Max batch size (tokens)   | 75.5M                       | 94.4M             |

Identical between Flash and Pro: KV-head count (1 for shared-KV MQA), head_dim (512), HCA compression rate m' (128), CSA compression rate m (4), indexer config (n_I_h=64, c_I=128), output intermediate d_g (1024), sliding-window n_win (128), mHC config (n_hc=4, Sinkhorn t_max=20), Hash-routing layer count (3), MTP depth (1), context window (1M), YaRN config, vocab (129,280), tokenizer, all post-training pipeline (specialist + GRPO + multi-teacher OPD), 3 reasoning modes, FP4 QAT recipe, all training stability tricks (Anticipatory Routing + SwiGLU Clamping).

The first-2-layer attention difference (SWA vs HCA) is the only non-scale architectural divergence — paper Section 4.2.1 specifies it tersely without ablation.

## Schema validation

This extraction is the schema v5 validation pass — V4-Flash was extracted *after* the v5 design (residual_connections + stability_notes) was landed. The schema held without modification: mHC (residual_connections.kind="mhc") and Anticipatory Routing + SwiGLU Clamping (training.stability_notes) populated cleanly using the new slots.

## Open questions (about V4-Flash itself)

These are unknowns in the source material; they mostly mirror V4-Pro:

- [ ] FIM rate not restated in V4 paper (inherited PSM from V3, rate=Unknown).
- [ ] Pre-training data percentage breakdown undisclosed (only qualitative).
- [ ] SFT data scale undisclosed for V4-Flash.
- [ ] Number of OPD teacher models given as ">10" but not exact.
- [ ] Hardware platform for V4-Flash actual production pre-training not specified.
- [ ] Pre-training start date and total wall-clock undisclosed.
- [ ] Per-mode evaluation context windows (Non-think 8K / Think High 128K / Think Max 384K) — trained limits or eval-only is ambiguous.
- [ ] Why first-2-layer attention differs between V4-Flash (pure SWA) and V4-Pro (pure HCA) — paper does not motivate.
- [ ] config.compress_ratios array length 44 (vs num_hidden_layers=43) — trailing 0 inferred to be the MTP head.
- [ ] V4-Flash README is byte-identical to V4-Pro README — the same family-level model card serves both releases.

## Resolved

- ✓ Sources fetched and sha256-verified (6 assets, ~4.6 MB; paper shared with V4-Pro registration).
- ✓ PDF → text derivation (paper.txt, identical content to V4-Pro's).
- ✓ Extraction passes Pydantic validation against schema_version=5.
- ✓ Bilingual Markdown rendered.
- ✓ Schema v5 (residual_connections + stability_notes) validated by this second-pass extraction.

## Notes

V4-Flash is the smaller efficiency-optimized sibling of V4-Pro and serves as the schema v5 second-pass validation: every gap surfaced by V4-Pro that produced a v5 schema slot (mHC residual_connections, Anticipatory Routing + SwiGLU Clamping in training.stability_notes) populated cleanly into the same slots without revision. The only structural difference between the two extractions sits in the variants[] list (Flash starts with pure SWA at layers 0,1; Pro with pure HCA), which is a layer-pattern detail not a schema concern.

Family-shared aspects (DeepSeek-V3-inherited tokenizer, identical README, identical tokenizer_config + generation_config, single technical report) make this extraction tightly coupled to V4-Pro by sourcing structure — the README and tokenizer files are byte-for-byte equal. Future deltas (e.g. if DeepSeek ships V4-Pro-1.1 with a refreshed tokenizer) will need cross-checking both Pro and Flash sources.
