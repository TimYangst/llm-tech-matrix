# DeepSeek-V4-Flash-0731

Slug: `deepseek-v4-flash-0731`
Family: `DeepSeek`
Status: `extracted`

## Sources

Authoritative list in `data/sources/deepseek-v4-flash-0731/manifest.json`.

Registered:

- [x] `config` (`hf_config`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/config.json`
- [x] `readme` (`model_card`) — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731/raw/main/README.md`
- [x] `tokenizer_config` (`other`) — `.../tokenizer_config.json`
- [x] `generation_config` (`other`) — `.../generation_config.json`
- [x] `encoding_readme` (`other`) — `.../encoding/README.md` (the wire-format spec; replaces a Jinja chat template)
- [x] `paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2606.19348` (DeepSeek-V4 technical report)
- [x] `dspark_paper` (`arxiv_pdf`) — `https://arxiv.org/pdf/2607.05147` (DSpark)

## Open questions

- [ ] **No 0731-specific report** — the delta is attributed entirely to re-post-training; recipe undisclosed. All post-training fields carry the preview pipeline with an explicit caveat.
- [ ] **`compress_ratios` arithmetic** — 44 → 46 entries while `num_hidden_layers` stayed 43. Three trailing zeros read as DSpark's 3 uncompressed SWA-128 MoE layers, but 43 + 1 MTP + 3 DSpark = 47 ≠ 46, so at least one reading is incomplete.
- [ ] **MTP vs DSpark** — `num_nextn_predict_layers=1` unchanged, yet the DSpark paper positions MTP-1 as the baseline DSpark supersedes. Is the MTP head still shipped/usable?
- [ ] **`dspark_noise_token_id=128799`** — unexplained in both sources. Plausibly the mask token of the draft input, not confirmed.
- [ ] **`num_speculative_tokens: 7` > trained γ=5** — retrained at larger γ, or silently clamped?
- [ ] **DSpark measurements are preview-paired** — the 60–85% speedup was measured with draft models co-deployed with the *preview* targets; no numbers published for the 0731 pairing.
- [ ] **`developer` role** — documented as internal to DeepSeek's search-agent pipeline and rejected by the official API; capability in the open weights undisclosed.

### Schema gap surfaced (driver for v7)

- [ ] **No home for an attached speculative-decoding module.** DSpark is trained, shipped, weight-bearing (3 MoE layers with mHC + SWA-128, rank-256 Markov head, confidence head) yet is neither backbone nor training objective; it currently smears across `alignment.stages`, `objectives.other`, `ffn.layer_partition` and `parallelism_notes`. Kimi K3's EAGLE-3 draft has the same problem (recorded inside `MTPConfig.shared_modules`). Two independent occurrences → `architecture.auxiliary_modules` justified.

### Source drift (action needed on OTHER slugs)

- [ ] The tech-report URL in the `deepseek-v4-pro` and `deepseek-v4-flash` manifests — `https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf` — now **404s**. The same report is on arXiv as **2606.19348** (v1, 26 Apr 2026). Both preview manifests should be repointed; not done here because rewriting another slug's manifest is out of scope for this extraction.

## Resolved

- **Release date** — 2026-07-31 (recorded as `2026-07`); slug date is in the model name.
- **Architecture is byte-identical to the preview** except four new `dspark_*` keys and two extra trailing zeros in `compress_ratios`. Verified by config diff. Every architecture field is carried over verbatim with an "unchanged from the preview" marker.
- **DSpark ships inside the checkpoint** — README: "same model structure as DeepSeek-V4-Flash-DSpark, i.e. it comes with a speculative decoding module attached". SGLang docs confirm target and draft weights come from the same checkpoint (do *not* pass `--speculative-draft-model-path`).
- **DSpark mechanism** (arXiv:2607.05147) — semi-autoregressive: a parallel draft backbone (3 MoE layers, mHC, SWA-128) conditioned on target layers `[40, 41, 42]` via DFlash-style KV injection, plus a lightweight sequential **Markov head** (rank-256 low-rank factorization of a V×V transition matrix) that restores intra-block dependency and mitigates suffix acceptance decay. Block size γ=5. A **confidence head** predicts per-position survival probability, feeding a hardware-aware prefix scheduler that verifies the full block under light load and only the confident prefix under heavy load. Reported 60–85% faster per-user generation vs MTP-1 at matched throughput.
- **Every config key now has a source**: `dspark_block_size=5` → γ; `dspark_markov_rank=256` → r; `dspark_target_layer_ids=[40,41,42]` → the injected target layers.
- **Tool-call wire format fully pinned** — `encoding/README.md` gives the complete grammar, closing two gaps the preview extraction left open (`end_token` was UNKNOWN; argument encoding was deferred to the paper). The `string="true|false"` attribute is the type discriminator, and is precisely why XML beats JSON here: raw string arguments never get escaped.
- **Reasoning-effort levels shifted** — the preview's top mode ("Think Max", prefix *"Absolute maximum with no shortcuts permitted"*) is 0731's `high`; `max` is a **new**, stronger prefix (*"Beyond maximum — exhaustive, relentless, and uncompromising"*), and the unprefixed thinking mode is now called `low`. Cross-version "max vs max" comparisons are therefore not comparing the same prompt condition.
- **`thinking_mode` and `drop_thinking` are real encoder parameters**, not inferred behaviours: `thinking_mode="chat"` closes `</think>` immediately after the assistant prefix; `drop_thinking` (default true) is force-disabled whenever tools are declared.

## Notes

- This is the repo's cleanest **post-training-only refresh with a serving-module addition** — architecturally frozen, but with a new weight-bearing inference component. Contrast the two other refresh patterns already in the repo: GLM-5 → GLM-5.1 (config byte-identical except `transformers_version`) and Qwen3.5 → Qwen3.6 / K2.5 → K2.6 (config identical, chat template gains a kwarg).
- The post-training delta is unusually large for a refresh and is entirely agentic/coding: DeepSWE 7.3 → 54.4, Cybergym 38.7 → 76.7, Terminal Bench 2.1 61.8 → 82.7. On the published table it beats V4-Pro (Preview) at 13B vs 49B activated — but against an *older* post-training generation, not like-for-like.
- Cross-vendor echo worth tracking: Kimi K3 fine-tunes its pre-trained MTP layer into an EAGLE-3 draft; DeepSeek replaces MTP-1 with DSpark. Both vendors converged in mid-2026 on "MTP head → dedicated speculative-decoding module" within weeks of each other.
