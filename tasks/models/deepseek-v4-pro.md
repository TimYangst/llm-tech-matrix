# DeepSeek-V4-Pro

Slug: `deepseek-v4-pro`
Family: `deepseek`
Status: `extracted`

Extracted 2026-05-10 against schema_version=4. JSON at `data/extracted/deepseek-v4-pro.json` validates cleanly. Bilingual rendered Markdown at `data/extracted/deepseek-v4-pro.md` and `…/deepseek-v4-pro.zh.md`.

## Sources

The authoritative list is `data/sources/deepseek-v4-pro/manifest.json`:

- `config` (`hf_config`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/raw/main/config.json` ✓
- `paper` (`tech_report`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf` ✓ (shared with V4-Flash)
- `readme` (`model_card`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/raw/main/README.md` ✓
- `tokenizer_config` (`other`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/raw/main/tokenizer_config.json` ✓
- `generation_config` (`other`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/raw/main/generation_config.json` ✓
- `blog_hf` (`blog_html`) — `https://huggingface.co/blog/deepseekv4` ✓ (release-day, datePublished 2026-04-24)
- `blog_preview` (`blog_html`) — `https://deepseek4.hk/blog/deepseek-v4-preview-million-context-era/` ✓ (third-party)
- `blog_release` (`blog_html`) — `https://deepseek4.hk/blog/deepseek-v4-officially-released/` ✓ (third-party)

> The two `deepseek4.hk` blogs are NOT an official DeepSeek domain. Registered for completeness; no unique facts in the extraction depend on them. Authoritative ranking when fields conflict: paper > config/README/tokenizer_config > HF blog > deepseek4.hk blogs.

Per-variant relationship: V4-Pro and V4-Flash share the single technical report. The HF release-day model collection lists four checkpoints — V4-Pro-Base + V4-Flash-Base (FP8 Mixed) and V4-Pro + V4-Flash (FP4 + FP8 Mixed); this extraction targets the post-FP4-QAT V4-Pro deployment release.

## Schema gaps surfaced (for v5 design pass)

These are real schema deficiencies, not unknowns about DeepSeek-V4-Pro itself. They are mirrored in the extracted JSON's `open_questions`. Resolution will come through a schema_version=5 design pass before extracting V4-Flash, so the second extraction can validate the new shapes.

- [ ] **Manifold-Constrained Hyper-Connections (mHC).** First-class structural innovation that replaces standard residual connections; expands residual stream from R^d to R^(n_hc·d) with three input/residual/output mappings A, B, C; constrains B to doubly-stochastic via 20 Sinkhorn iterations and A,C via Sigmoid. Currently encoded in `architecture.parallelism_notes`. Schema has no slot for inter-layer residual topology. Likely shape: `Architecture.residual_connections: ResidualConfig | None = None` with `kind` (`"standard" | "hyper-connections" | "mhc"`), `expansion_factor`, `constraint`, `iterations` fields.
- [ ] **Hybrid attention with KV compression (CSA + HCA).** Schema's `AttentionVariant.family` enum doesn't capture compression-rate / indexer / grouped-output-projection / sliding-window shape. CSA/HCA encoded with `family="other"` and very dense free-text `notes`. Likely shape: a `CompressedAttentionConfig` subobject mirroring the way MLA is structured, with `compression_rate`, `indexer_query_heads`, `indexer_head_dim`, `sparse_top_k`, `query_latent_dim`, `output_groups`, `output_group_dim`, `sliding_window_size`, `attention_sink: bool`.
- [ ] **FP4 / mixed-format quantization recipe.** Currently in `advanced.mixed_precision` free-text. Recurring across V4 and the gpt-oss FP4 weight release. Likely shape: structured `QuantizationConfig` with `target_components`, `format` (E4M3 / E2M1 / MXFP4 / NVFP4), block size, scale format, lossless-dequant lineage.
- [ ] **Training stability tricks.** Anticipatory Routing + SwiGLU Clamping are key V4 contributions but live in `architecture.parallelism_notes`. Likely shape: free-text `training.stability_tricks: str = ""` would be the smallest possible win.
- [ ] **Generative Reward Model (GRM).** Captured only in alignment.stages[].description. Lower priority — schema's `rl_method` is free-text so it absorbs descriptions, but a structured `reward_model` slot would surface this for cross-vendor compare.
- [ ] **Tool-call protocol / agent-token schema.** `|DSML|` token + XML tool-call format and Quick Instruction tokens are in `components.embedding_notes`. Lower priority — useful when more vendors ship structured tool protocols.

## Open questions (about V4-Pro itself, not schema)

These are unknowns in the source material:

- [ ] FIM rate not restated in V4 paper; recorded as inherited PSM format from V3 with rate=Unknown. (V3 used 0.1.)
- [ ] Pre-training data percentage breakdown undisclosed (only qualitative descriptions).
- [ ] SFT data scale undisclosed for V4. Paper says pipeline mirrors V3.2 but doesn't restate sample counts.
- [ ] Number of OPD teacher models given as ">10" but not exact; per-teacher importance weights `w_i` qualitative only.
- [ ] Hardware platform for actual production V4 pre-training not specified (paper validates EP scheme on both NVIDIA + Huawei Ascend, doesn't say which was used in production).
- [ ] Pre-training start date and total wall-clock undisclosed.
- [ ] Per-mode evaluation context windows (Non-think 8K / Think High 128K / Think Max 384K) — whether trained limits or only eval-time configuration is ambiguous.
- [ ] DeepSeek-V3.2 (the immediate baseline V4 compares against throughout) is not in this repo's extracted set. Future cross-model compare will need a V3.2 sourcing+extraction pass.
- [ ] config.compress_ratios array length 62 (vs num_hidden_layers=61) — trailing 0 inferred to be the MTP head; not explicitly described in the paper.

## Resolved

- ✓ Sources fetched and sha256-verified (8 assets, 4.7 MB total).
- ✓ PDF → text derivation (paper.txt, 2,984 lines).
- ✓ Extraction passes Pydantic validation against schema_version=4.
- ✓ Bilingual Markdown rendered.

## Notes

V4-Pro is the second DeepSeek extraction in the repo (after V3). Architecturally it diverges from V3 along three axes: (1) attention — MLA replaced by hybrid CSA+HCA with KV compression; (2) residual connections — standard residual replaced by mHC; (3) optimizer — AdamW+QK-Clip replaced by Muon+(Q/KV-RMSNorm). MoE topology kept (DeepSeekMoE family) but routing scoring moves Sigmoid → SqrtSoftplus, expert count grows 256 → 384, top-k 8 → 6, shared experts unchanged at 1, expert width 2048 → 3072. Hash routing is added for the first 3 MoE layers. MTP unchanged (depth=1). Pre-training tokens 14.8T → 33T. Post-training restructured: V3's "SFT + GRPO RL with mixed reward" replaced by "per-domain SFT + GRPO specialists → multi-teacher On-Policy Distillation". Three reasoning modes (Non-think / Think High / Think Max) replace V3's single mode. FP4 QAT (MXFP4) added on top of inherited FP8. Native 1M context (vs V3's 4K-trained YaRN-stretched-to-128K).

The biggest schema event of the extraction was mHC: it's first-class in the paper (full Section 2.2, dedicated implementation infrastructure section, dedicated paper citation) but has no analog in the v4 schema. Worth a v5 schema slot before extracting V4-Flash so both V4 entries record mHC the same way. Hybrid CSA+HCA is similarly under-served — currently using AttentionVariant.notes as a kitchen sink for ~10 numeric knobs.
