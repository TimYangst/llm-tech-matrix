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

| Model                          | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GLM-5.2                        | **21 Full / 57 Shared** of 78 layers. Layers 0-2 (the dense-FFN layers) are Full; from layer 3 the pattern is period-4 with a Full layer every fourth (`index_topk_freq=4`, `index_skip_topk_offset=3`). Ships the **training-aware** variant — the fixed regular pattern is what that route enables, where the training-free greedy search would yield an irregular set. Reported **2.9× fewer per-token FLOPs at 1M context**. `index_share_for_mtp_iteration=true` extends the reuse into MTP speculative-decoding steps. |
| GLM-5.3-Flash (dropped)        | **Per-layer sharing dropped.** All 11 sparse-attention layers compute their own selection; the `indexer_types` Full/Shared partition is gone, replaced by within-layer key pooling (`index_kpool=4`) — see [QSA](./qsa.md) for the same trade at Qwen. Only `index_share_for_mtp_iteration=true` survives, i.e. reuse across MTP steps rather than across layers. A clean demonstration of the technique's boundary: the model is a 3:1 KDA/DSA hybrid, exactly the regime where cross-layer similarity is weakest.          |
| DeepSeek-V4.1-Flash (via CSA2) | **Generalized to KV sharing** in [CSA2](./csa2.md), whose report cites IndexCache (arXiv:2603.12201) as an index-reuse-only precedent. Reuse layers (30 of 40) take the latest top-k like Shared layers here, but CSA2 additionally shares main KV and indexer K, and adds a Reindex mode that re-scores the shared keys with its own indexer Q. Static assignment: Full at layers 2/8/14/20, Reindex at 24/28/32/36. In the decoder, Reindex layers search only a candidate pool built by layer 20.                         |

<!-- BEGIN GENERATED: implemented-by-engines (synthesis.index) -->

## Implemented by (engines)

Generated from `technique_support[]` in the engine snapshots under [`data/extracted/engines/`](../../data/extracted/engines/) — do not edit. "Used by" above records models adopting the technique; this table records engines implementing it.

| Engine snapshot                                                                        | Roles                                 | Implementation                                                                                                                                                                                                 | Flags                                                                                                                                               | Evidence                                                                                                                                                                                                                                                                                                                                                                                           |
| -------------------------------------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`sglang-v0.5.19`](../../data/extracted/engines/sglang-v0.5.19.md)                     | inference                             | Cross-layer top-k reuse read from the model config (index_topk_freq / index_topk_pattern); the HiSparse guide calls it native in GLM-5.2 as IndexShare and prefetches skip layers' working sets automatically. | —                                                                                                                                                   | [model_config.py#L237](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L237), [model_config.py#L241](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L241)                                                                             |
| [`vllm-v0.29.0`](../../data/extracted/engines/vllm-v0.29.0.md)                         | inference                             | IndexCache: layers marked F compute and cache top-k indices, layers marked S reuse the previous layer's indices; configured per layer or by frequency.                                                         | `--hf-overrides '{"use_index_cache": true, "index_topk_freq": 4}'`<br>`--hf-overrides '{"use_index_cache": true, "index_topk_pattern": "FFSF..."}'` | [index_cache.md#L3](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/docs/features/index_cache.md#L3), [index_cache.md#L26](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/docs/features/index_cache.md#L26)                                                                                                                 |
| [`megatron-bridge-v0.6.0`](../../data/extracted/engines/megatron-bridge-v0.6.0.md)     | training                              | GLM-5.2 IndexShare-style index reuse: index_topk_freq and index_skip_topk_offset are read from the HF config into the DSA provider.                                                                            | `dsa_indexer_topk_freq`<br>`dsa_indexer_skip_topk_offset`                                                                                           | [glm5_bridge.py#L136](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py#L136), [glm5.md#L11](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/glm/glm5.md#L11)                                                                            |
| [`megatron-lm-core_v0.19.0`](../../data/extracted/engines/megatron-lm-core_v0.19.0.md) | training, rl_post_training, inference | DSA index sharing: with index_topk_freq > 1, layers without their own top-k reuse a previous indexer layer's selection; pipeline splits are validated so shared indices stay on one stage.                     | `dsa_indexer_topk_freq > 1`                                                                                                                         | [dsa.py#L1564](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/experimental_attention_variant/dsa.py#L1564), [experimental_attention_variant_module_specs.py#L339](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/models/gpt/experimental_attention_variant_module_specs.py#L339) |

<!-- END GENERATED: implemented-by-engines -->

## Related techniques

- [DeepSeek Sparse Attention (DSA)](./dsa.md) — the mechanism whose indexer cost this addresses.
- [Qwen Sparse Attention (QSA)](./qsa.md) — the competing answer: compress the indexer's input within a layer instead of sharing across layers.
- [Speculative-decoding modules](./speculative-decoding.md) — `index_share_for_mtp_iteration` reuses selections across draft steps; Qwen3.8-Flash-Next credits GLM for this trick.
