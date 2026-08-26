# GLM-5.2

Slug: `glm-5.2`
Family: `glm`
Status: `extracted`

## Sources

The authoritative source list is `data/sources/glm-5.2/manifest.json` (committed).

- [x] `config` (`hf_config`) — `https://huggingface.co/zai-org/GLM-5.2/raw/main/config.json`
- [x] `chat_template` (`other`), `tokenizer_config` (`other`), `readme` (`model_card`)
- [x] `paper` (`arxiv_pdf`) — GLM-5 family report, `https://arxiv.org/pdf/2602.15763`
- [x] **`indexshare_paper` (`arxiv_pdf`)** — `https://arxiv.org/pdf/2603.12201`
- [x] `blog` (`blog_html`) — `https://z.ai/blog/glm-5.2` (SPA shell, 0 chars extractable)

Considered but excluded:

- `GLM-5.2-FP8` — quantized sibling of the same weights.

## Open questions

See the extracted JSON. The load-bearing one: **is 5.2 a continued pre-train, a fresh
pre-train, or an IndexShare retrofit onto GLM-5.1?** The card doesn't say. Evidence for
retrofit: IndexShare's training-aware route is a distillation onto existing indexers, and
the parameter count *drops* ~0.6B vs GLM-5.1. Evidence against: the 1M window and the
rope_theta change imply substantial continued training regardless.

## Resolved

- ✅ **Is 5.2 another post-training-only refresh like 5.1?** No. Three substantive config
  deltas: IndexShare indexer sharing, `max_position_embeddings` 202,752 → 1,048,576, and
  `rope_theta` 1e6 → 8e6.
- ✅ **Parameter count.** Card gives none. The bf16 safetensors index totals
  1,506,659,919,872 bytes ≈ 753B params, ~0.6B *fewer* than GLM-5.1 — the removed
  Shared-layer indexers.
- ✅ **`head_dim` 64 → 192 is not an architecture change.** `qk_head_dim` (256),
  `qk_nope_head_dim` (192) and `qk_rope_head_dim` (64) are all unchanged; 5.1 reported the
  rope dim in `head_dim`, 5.2 reports the nope dim.

## Inferred fields (closed models only)

N/A — open-weight under **MIT**, which Z.AI foregrounds as a product decision ("Pure Open:
an MIT open-source license — no regional limits").

## Notes

**IndexShare / IndexCache** (arXiv 2603.12201, Bai et al., Tsinghua + Z.ai) is the release's
architectural content. The premise: DSA cuts core attention to O(Lk) but its lightning
indexer still runs independently at every layer at O(L²) — while consecutive layers' top-k
selections are highly similar. IndexShare partitions layers into `Full` (own indexer) and
`Shared` (reuse nearest Full layer's indices). GLM-5.2 ships **21 Full / 57 Shared** of 78,
period-4 from layer 3 (`index_topk_freq=4`, `index_skip_topk_offset=3`).

Two routes in the paper; GLM-5.2 ships the **training-aware** one (multi-layer distillation
against averaged attention distributions of served layers). The training-free route is a
greedy calibration search — which would produce an *irregular* layer set, not the fixed
period-4 pattern the config shows.

Reported: **2.9× fewer per-token FLOPs at 1M** (card). Paper: 75% of indexer compute removed
on a 30B DSA model (1.82× prefill / 1.48× decode), ~1.2× end-to-end on GLM-5 at 50%.

**Naming is inconsistent across three documents** — model card says *IndexShare*, the paper
says *IndexCache* throughout, Qwen's report cites *"IndexShare (Bai et al., 2026)"*.

**Cross-vendor**: Qwen's Qwen3.8-Flash-Next report benchmarks against this by name and
rejects it for hybrid stacks, choosing within-layer micro-block compression (QSA) instead —
arguing cross-layer similarity is low when full-attention layers are separated by
linear-attention layers. GLM-5.2 is a pure-MLA stack, where that similarity is strongest.
**GLM then switched sides two months later**: GLM-5.3-Flash is a hybrid stack and uses
key-pooled compression, dropping the Full/Shared partition entirely.

**Benchmarks vs GLM-5.1**: DeepSWE 18 → 46.2, FrontierSWE (Dominance) 30.5 → 74.4, Terminal
Bench 2.1 (Terminus-2) 63.5 → 81.0, ProgramBench 50.9 → 63.7, SWE-Marathon 1.0 → 13.0,
HLE 31 → 40.5, SWE-bench Pro 58.4 → 62.1, NL2Repo 42.7 → 48.9, MCP-Atlas 71.8 → 76.8.
Gains this large are not attributable to an attention-efficiency change — there is
substantial unpublished post-training behind this release.

**New runtime axis**: `reasoning_effort` ∈ {high, max}, emitted as a `<|system|>Reasoning
Effort: Max` prompt prefix — the same mechanism family as DeepSeek-V4's prefix approach.
Unknown values silently fall back to `max` (the *most* expensive level), where Qwen3.8 raises.
