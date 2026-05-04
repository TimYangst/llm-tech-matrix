# Auxiliary-loss-free routing

**Slug:** `aux-loss-free-routing`
**Category:** ffn / moe
**One-line:** Balances MoE expert load via per-expert learnable bias terms (adjusted online based on observed expert utilization) instead of an auxiliary load-balancing loss, avoiding the gradient signal that auxiliary losses inject into the main objective.
**First introduced in:** [Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts (Wang et al., 2024)](https://arxiv.org/abs/2408.15664)

## Description

Standard MoE training adds an auxiliary loss (e.g. the "load balancing loss" from
Switch Transformer / GShard) to encourage even token distribution across experts.
This loss creates gradients that fight the main task — too strong and model quality
degrades; too weak and routing collapses.

Auxiliary-loss-free routing keeps a small per-expert bias `b_i`. The top-K routing
decision uses `(affinity + bias)` for selection, but the gating value (multiplied with
the FFN output) uses the raw affinity. After each training step, biases are nudged
*outside* of the main backward pass: increased for under-utilized experts, decreased
for overloaded ones. Because biases never enter the loss surface seen by gradients,
they don't compete with model quality.

DeepSeek-V3 typically pairs this with a tiny sequence-wise auxiliary loss (α = 0.0001)
just to prevent extreme intra-sequence imbalance, but the dominant balancing signal is
the bias adjustment.

## Reference materials

- Original paper: <https://arxiv.org/abs/2408.15664>
- DeepSeek-V3 ablation showing improvement over aux-loss-based baseline (paper Table 5).

## Used by

| Model       | Variation / details                                                                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V3 | bias update speed γ=0.001 for first 14.3T tokens, 0 for last 500B; complementary sequence-wise balance loss α=0.0001; node-limited routing (M=4 nodes, 8 expert groups). |

## Related techniques

- [DeepSeekMoE](./deepseekmoe.md)
- [Global-batch load balancing](./global-batch-load-balancing.md) — Qwen3's alternative balancing approach (gradient-flowing auxiliary loss, but computed over the global batch instead of per-sequence)
