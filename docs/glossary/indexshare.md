# IndexShare / IndexCache (cross-layer index reuse)

> 中文版：[indexshare.zh.md](./indexshare.zh.md)

**Slug:** `indexshare`
**Category:** attention
**One-line:** Run the sparse-attention indexer on only a minority of layers and let the rest reuse the nearest computed top-k selection, exploiting the fact that consecutive layers pick nearly the same tokens.
**First introduced in:** [IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse (Bai, Dong, Jiang, Lv, Du, Zeng, Tang, Li — Tsinghua + Z.ai, 2026)](https://arxiv.org/abs/2603.12201)

## Description

[DSA](./dsa.md) cuts core attention from `O(L²)` to `O(Lk)` with a lightweight *lightning
indexer* that picks the top-k relevant tokens per query. But the indexer itself is still
`O(L²)`, and it runs independently at every layer — so as context grows, the mechanism
introduced to remove the quadratic cost becomes the quadratic cost.

IndexCache's observation is that this per-layer work is largely redundant: **consecutive
layers' top-k selections are highly similar.** So layers are partitioned into a small set of
**Full** layers that run their own indexer, and a majority of **Shared** layers that simply
reuse the nearest Full layer's indices. The core attention still runs everywhere; only the
*selection* is shared.

The paper gives two ways to choose and optimize that partition:

- **Training-free IndexCache** — a greedy search that picks which layers keep indexers by
  directly minimizing language-modeling loss on a calibration set. No weight updates. This
  tends to produce an *irregular* layer set, and the paper is explicit that uniform
  interleaving is suboptimal without training.
- **Training-aware IndexCache** — a multi-layer distillation loss trains each retained
  indexer against the **averaged** attention distributions of all the layers it serves.
  With this, even a simple interleaved pattern matches full-indexer accuracy.

Measured on a 30B DSA model: 75% of indexer computation removed with negligible quality
degradation, 1.82× prefill and 1.48× decode speedup. On production-scale GLM-5 at 50%
removal, ~1.2× end-to-end.

**The technique's limit is where its premise fails.** Cross-layer similarity is what makes
sharing free — so it is strongest in a homogeneous stack where every layer is full
attention, and weakest in a hybrid stack where the full-attention layers are separated by
linear-attention layers. Qwen's Qwen3.8-Flash-Next report tests exactly this and takes the
other branch: at equal indexer latency its [QSA](./qsa.md) (within-layer micro-block
compression) matches the full-attention RULER baseline at 0.25 relative latency while
IndexShare is still below baseline at 0.5. GLM's own model line then demonstrates the same
boundary from the inside — GLM-5.2 is a pure-MLA stack and uses IndexShare; GLM-5.3-Flash is
a KDA/DSA hybrid and drops per-layer sharing for key pooling instead.

**A note on the name.** The paper is titled *IndexCache*; the GLM-5.2 model card calls the
technique *IndexShare*; Qwen's report cites it as *"IndexShare (Bai et al., 2026)"*. All
three refer to this mechanism.

## Reference materials

- Original paper: <https://arxiv.org/abs/2603.12201>
- Reference implementation: — (config keys `indexer_types`, `index_topk_freq`, `index_skip_topk_offset`, `index_share_for_mtp_iteration`)

## Used by

| Model | Variation / details |
| ----- | ------------------- |
| GLM-5.2 | **21 Full / 57 Shared** of 78 layers. Layers 0-2 (the dense-FFN layers) are Full; from layer 3 the pattern is period-4 with a Full layer every fourth (`index_topk_freq=4`, `index_skip_topk_offset=3`). Ships the **training-aware** variant — the fixed regular pattern is what that route enables, where the training-free greedy search would yield an irregular set. Reported **2.9× fewer per-token FLOPs at 1M context**. `index_share_for_mtp_iteration=true` extends the reuse into MTP speculative-decoding steps. |
| GLM-5.3-Flash | **Per-layer sharing dropped.** All 11 sparse-attention layers compute their own selection; the `indexer_types` Full/Shared partition is gone, replaced by within-layer key pooling (`index_kpool=4`) — see [QSA](./qsa.md) for the same trade at Qwen. Only `index_share_for_mtp_iteration=true` survives, i.e. reuse across MTP steps rather than across layers. A clean demonstration of the technique's boundary: the model is a 3:1 KDA/DSA hybrid, exactly the regime where cross-layer similarity is weakest. |

## Related techniques

- [DeepSeek Sparse Attention (DSA)](./dsa.md) — the mechanism whose indexer cost this addresses.
- [Qwen Sparse Attention (QSA)](./qsa.md) — the competing answer: compress the indexer's input within a layer instead of sharing across layers.
- [Speculative-decoding modules](./speculative-decoding.md) — `index_share_for_mtp_iteration` reuses selections across draft steps; Qwen3.8-Flash-Next credits GLM for this trick.
