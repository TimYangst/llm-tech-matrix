# Compressed Sparse Attention 2 (CSA2)

> 中文版：[csa2.zh.md](./csa2.zh.md)

**Slug:** `csa2`
**Category:** attention
**One-line:** A simplified successor to DeepSeek-V4's CSA that shares main KV and indexer keys *across layers* and, separately, lets layers reuse another layer's top-k selection, via three static per-layer modes — Full, Reindex and Reuse.
**First introduced in:** [DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression (DeepSeek-AI, 2026)](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/DeepSeek_V41_Tech_Report.pdf) §2.3. Descends from [CSA + HCA](./csa-hca.md) (DeepSeek-V4), which in turn builds on [DSA](./dsa.md).

## Description

The report frames long-context KV cost as three multiplicative dimensions: **entry size**
(fewer KV heads, as in GQA, or a shared latent, as in MLA), **sequence** (compress every `m`
tokens into one entry, as CSA/HCA do) and **layer** (let some layers reuse others' caches
or selections). Prior work touched the layer dimension piecemeal — IndexCache reuses only
top-k indices ([IndexShare](./indexshare.md)), and other work shares KV or routing — but,
in the report's words, "none of these methods covers all three multiplicative dimensions".
CSA2 is DeepSeek's attempt to cover all three at once.

**Three static modes.** Every CSA2 layer computes its own main Q and its own layer-local
sliding-window KV; the modes differ only in what they borrow.

- **Full** — computes its own main KV, projects indexer K from that main KV, computes
  indexer Q and selects fresh top-k. The complete path, equivalent to a V4 CSA layer.
- **Reindex** — reuses main KV *and* indexer K from the most recent Full layer, but
  computes its own indexer Q and re-scores, so the selection can change while cache storage
  stays shared.
- **Reuse** — reuses main KV *and* the latest top-k indices, computing no indexer at all.

Cache sharing and index reuse are thus **decoupled**, which is the key difference from
index-only reuse: sharing main KV actually shrinks storage, while reusing indices only
saves indexer compute.

**Simplified compressor.** CSA2 removes CSA's overlapping `2m`-entry compression windows
and the absolute positional embedding inside the compressor, and derives indexer K by
projecting main KV instead of from a separate compression path. A compression ratio of
`m=1` (uncompressed main KV) is a legal special case.

**Hierarchical Sparse Indexer.** Reindex layers still score the whole visible context.
In the decoder of a [Causal Encoder-Decoder](./causal-encoder-decoder.md), the first Full
layer therefore also builds a **candidate pool**: each block of positions takes its maximum
index score, the top blocks are kept (2,048 blocks × 8 positions = up to 16,384 candidates),
and later Reindex layers pick their own top-k *only inside that pool*. Their per-query
indexing cost becomes bounded independently of context length. The restriction is
training-aware: it is introduced in post-training and applied identically in training and
inference.

Combined with an FP4 main KV cache, DeepSeek-V4.1-Flash reports a global KV footprint of
**890 bytes per token, about 1/4 of DeepSeek-V4-Flash**. The vendor lists "potential
selection errors in CSA2" among its uncharacterized robustness boundaries.

## Reference materials

- Original paper: DeepSeek-V4.1-Flash technical report §2.3 (Figures 4 and 5), §3.1.2 (training infrastructure: shadow indexers, pipeline payload extensions, micro-batch shared-state management)
- Reference implementation: <https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/tree/main/inference> (config keys `kv_source_layer_ids`, `index_source_layer_ids`, `candidate_source_layer_id`, `candidate_topk_blocks`, `candidate_block_size`, `compress_ratios`)
- Relevant blog/post: <https://api-docs.deepseek.com/news/news260910/>

## Used by

| Model               | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4.1-Flash | Pure CSA2 — no HCA layers. 40 layers: layers 0–1 SWA-only; **encoder** layers 2–19 at `m=2` in three groups of six, each `[Full, Reuse×5]`; **decoder** layers 20–39 at `m=1` (uncompressed) in five groups of four, `[Full, Reuse×3]` then four `[Reindex, Reuse×3]`. Totals 4 Full (`kv_source_layer_ids=[2,8,14,20]`), 4 Reindex (24/28/32/36), 30 Reuse. Indexer 32 heads × 128 dim, top-k 512; every layer also keeps a 128-token SWA branch. Hierarchical Sparse Indexer in the decoder only, rooted at layer 20 (`candidate_topk_blocks=2048`, `candidate_block_size=8`). Trained from scratch with sparse attention at 64K, no dense warm-up. |

## Related techniques

- [CSA + HCA](./csa-hca.md) — the DeepSeek-V4 design CSA2 replaces; V4.1 drops the heavily-compressed layer type.
- [DeepSeek Sparse Attention (DSA)](./dsa.md) — the lightning-indexer top-k mechanism underneath both.
- [IndexShare / IndexCache](./indexshare.md) — cross-layer index reuse only; CSA2 cites IndexCache (arXiv:2603.12201) as a precedent and extends reuse to the KV cache itself.
- [Qwen Sparse Attention (QSA)](./qsa.md) — a different attack on the same indexer cost, compressing the indexer's input within a layer.
- [Causal Encoder-Decoder (CED)](./causal-encoder-decoder.md) — the layer topology CSA2 is paired with in V4.1.
