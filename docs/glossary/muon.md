# Muon optimizer

> 中文版：[muon.zh.md](./muon.zh.md)

**Slug:** `muon`
**Category:** optimizer
**One-line:** Per-matrix Newton-Schulz orthogonalization of the momentum-blended gradient — replaces the element-wise second-moment update used by Adam/AdamW with a matrix-aware update that whitens singular values, achieving faster convergence and better stability on transformer weights at trillion-parameter scale.
**First introduced in:** [Muon (Jordan et al., 2024)](https://kellerjordan.github.io/posts/muon/); scaled-up training recipe by [Liu et al., 2025](https://arxiv.org/abs/2502.16982).

## Description

For each logically independent weight matrix `W ∈ R^(n×m)`:

1. Accumulate momentum `M_t = μ·M_{t-1} + G_t` (Nesterov trick: feed `μ·M_t + G_t`).
2. Orthogonalize via Newton-Schulz iterations to produce `O' = NS(μ·M_t + G_t)` — approximating `U·V^T` from the SVD `M = U·Σ·V^T`. This drives all singular values toward 1.
3. Rescale `O = O' · √max(n,m) · γ` so the update RMS reaches a fixed target (lets you re-use AdamW's learning rate).
4. Apply weight decay + the update: `W_t = W_{t-1} · (1 - η·λ) - η·O`.

Unlike Adam/AdamW which track per-element second moments, Muon respects the matrix structure of weights — a single per-element learning-rate adaptation can be inappropriate when entries within a column or row are tightly coupled. The Newton-Schulz orthogonalization is cheap (matmuls only, BF16-stable), runs in 5-10 iterations, and avoids any explicit SVD.

DeepSeek-V4 uses a **hybrid Newton-Schulz** schedule: 8 steps with `(a,b,c)=(3.4445, -4.7750, 2.0315)` for rapid singular-value convergence, then 2 steps with `(2, -1.5, 0.5)` to stabilize singular values precisely at 1. Muon does not get applied to embedding, the prediction head, RMSNorm weights, or mHC's static parameters — those stay on AdamW. With per-head Q/KV RMSNorm in the attention path, V4 finds it does not need the QK-Clip trick that earlier Muon-trained models (Liu et al., 2025) used to prevent attention-logit explosion.

The combination with Zero Redundancy Optimizer (ZeRO) is non-trivial: Muon needs the full gradient matrix to compute the orthogonal update, conflicting with ZeRO's matrix-sharding for element-wise optimizers. DeepSeek-V4 uses a hybrid bucketing strategy (knapsack assignment for dense params with a parallelism cap; flatten-across-experts for MoE params with no cap; BF16 stochastic-rounding gradient sync to halve bandwidth).

## Reference materials

- Original Muon post: <https://kellerjordan.github.io/posts/muon/>
- Scaling Muon to large models (Liu et al., 2025): <https://arxiv.org/abs/2502.16982>
- DeepSeek-V4 Technical Report Section 2.4 (algorithm) + Section 3.4.1 (ZeRO integration).

## Used by

| Model             | Variation / details                                                                                                                                                                                                                                                                           |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Pro   | Muon for the majority of params; AdamW for embedding, prediction head, RMSNorm weights, and mHC static biases + gating. Muon momentum=0.95, weight_decay=0.1, RMS rescale to 0.18. Hybrid Newton-Schulz: 8 steps at (3.4445, -4.7750, 2.0315) + 2 steps at (2, -1.5, 0.5). No QK-Clip needed. |
| DeepSeek-V4-Flash | Identical Muon configuration to V4-Pro (only the LR schedule differs: peak 2.7e-4 vs Pro's 2.0e-4).                                                                                                                                                                                           |

## Related techniques

- [QK-Norm](./qk-norm.md) — V4 uses per-head Q/KV RMSNorm to avoid the attention-logit explosion that originally motivated QK-Clip in Muon training.
