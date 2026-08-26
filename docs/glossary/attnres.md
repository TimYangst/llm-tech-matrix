# Attention Residuals (AttnRes)

> 中文版：[attnres.zh.md](./attnres.zh.md)

**Slug:** `attnres`
**Category:** residual connections
**One-line:** Replaces the residual stream's uniform accumulation over depth with *attention over depth* — each layer uses a learned pseudo-query to selectively retrieve representations from all preceding layers.
**First introduced in:** [Attention Residuals (Kimi Team, 2026)](https://arxiv.org/abs/2603.15031); deployed at scale in the [Kimi K3 technical report §2.2](https://arxiv.org/abs/2607.24653).

## Description

A standard residual connection compresses everything the network has computed so far into a
single state `h_l` — a bottleneck the AttnRes paper explicitly compares to an RNN over time.
The Transformer already solved that problem along the *sequence* axis by replacing recurrence
with attention. AttnRes applies the same move along the *depth* axis.

Each layer `l` holds a **learnable pseudo-query** `q_l = w_l ∈ R^d` (static per layer). The keys
and values are the actual outputs of all preceding layers, with the token embedding as source 0
so it is always reachable:

```
α_{i→l} = φ(q_l, k_i) / Σ_j φ(q_l, k_j),   φ(q,k) = exp(qᵀ · RMSNorm(k))
h_l = Σ_{i<l} α_{i→l} · v_i
```

The RMSNorm on keys is load-bearing: without it, layers with large-magnitude outputs would
dominate the depth-attention weights regardless of relevance. Note that although the query is
static, the weights are input-dependent through the keys — so the source selection *is* dynamic.

**Block AttnRes is what actually ships.** Full AttnRes costs O(L²d) arithmetic (affordable at
L < 100) but O(Ld) memory and cross-stage pipeline communication to keep every layer output
alive. The block variant partitions L layers into N blocks; within a block, layer outputs are
summed into one block representation `b_n` (with `b_0` = the token embedding), and full attention
runs only over the N block-level representations — the first layer of block n sees
`[b_0 … b_{n−1}]`, later layers additionally see the running partial sum. Memory and
communication drop from O(Ld) to O(Nd), inference-time state becomes bounded, and parallel
inter-block results can be merged with sequential intra-block partial sums via online softmax.
The paper reports N ≈ 8 recovers most of the benefit across model scales.

Contrast with [mHC](./mhc.md), the other post-2025 attack on the residual stream: mHC *widens*
the stream into `R^{n_hc × d}` and constrains the inter-layer mapping to doubly stochastic
matrices; AttnRes keeps the stream at width `d` and instead makes **which prior layers you read**
data-dependent. Both are "the residual connection is a bottleneck" arguments arriving at
different answers.

## Reference materials

- Original paper: <https://arxiv.org/abs/2603.15031>
- Kimi K3 technical report §2.2 (block variant, deployment): <https://arxiv.org/abs/2607.24653>
- Kimi K3 §5.2.2 — the memory-efficient implementation: block representations generated once at the boundary layer and shared, AttnRes computation wrapped in checkpointing so per-layer saved activations match a standard residual architecture, plus cache-based pipeline communication transferring only newly generated blocks between stages

## Used by

| Model                                 | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K3                               | Block AttnRes with a 12-layer block size (`config.attn_res_block_size=12`) over 93 layers — the paper describes this as 8 blocks with a partial final block, 9 sources counting the embedding layer. The final output layer aggregates all N block representations. Also load-bearing downstream: the EAGLE-3 draft model's input fuses low/mid/high-level features taken from the outputs of the **1st, 4th and final AttnRes blocks** (§4.1.4), so the block structure doubles as a feature-extraction interface for speculative decoding. |
| Qwen3.8-Flash-Next (compared against) | Does not use AttnRes, but Qwen benchmarks against it head-to-head at 28 layers (report Tab. 6): full AttnRes reaches 1.762 final training loss and GR (n_r=4) matches it at 1.762, with Block AttnRes at S=2/S=4 slightly behind (1.766 / 1.768 with GatedNorm). The two represent different answers to the same question — AttnRes attends over earlier layers' outputs to form the read; [GR](./gated-residual.md) gates a widened stream.                                                                                                 |

## Related techniques

- [Manifold-Constrained Hyper-Connections (mHC)](./mhc.md) — the DeepSeek-V4 answer to the same bottleneck, by widening the stream rather than attending over it.
- [Kimi Delta Attention (KDA)](./kda.md) — the sequence-axis counterpart in the same model. Kimi K3 frames its architecture as scaling information flow along three axes: sequence (KDA), depth (AttnRes), width (Stable LatentMoE).
- [Stable LatentMoE](./latentmoe.md) — the width axis.
