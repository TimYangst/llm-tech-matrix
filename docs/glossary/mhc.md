# Manifold-Constrained Hyper-Connections (mHC)

> 中文版：[mhc.zh.md](./mhc.zh.md)

**Slug:** `mhc`
**Category:** other (residual-stream topology)
**One-line:** Replaces standard residual connections with an `n_hc`-wide hyper-connection residual stream whose between-layer mixing matrix is constrained to the doubly-stochastic manifold via Sinkhorn-Knopp, ensuring non-expansive (∥B∥₂ ≤ 1) signal propagation across deep stacks.
**First introduced in:** Hyper-Connections (Zhu et al., 2025) introduces the HC residual expansion; the manifold constraint and Sinkhorn projection are added in the dedicated mHC paper (Xie et al., 2026), cited by DeepSeek-V4 Section 2.2.

## Description

Standard transformers use a single `R^d` residual stream. **Hyper-Connections (HC)** expand it to `R^(n_hc × d)` and update via three small linear maps per layer:
`X_{l+1} = B_l · X_l + C_l · F_l(A_l · X_l)`
where `A_l ∈ R^(1×n_hc)` projects the residual into the layer input, `F_l` is the layer (e.g. attention or MoE), `C_l ∈ R^(n_hc×1)` writes the output back, and `B_l ∈ R^(n_hc×n_hc)` mixes the residual stream itself across the `n_hc` slots. This decouples residual width from hidden dim with negligible compute overhead, but stacking many HC layers tends to be numerically unstable.

**mHC's contribution** is constraining `B_l` to the manifold of doubly stochastic matrices (the Birkhoff polytope). After producing an unconstrained `B̃_l`, mHC takes `M^(0) = exp(B̃_l)` and runs `t_max ≈ 20` Sinkhorn-Knopp iterations of alternating row/column normalization, converging to `B_l` with row sums = column sums = 1. This gives `∥B_l∥₂ ≤ 1` (non-expansive forward + backward), and the manifold is closed under multiplication so deep stacks remain stable. `A_l` and `C_l` are additionally constrained non-negative + bounded via Sigmoid (`A = σ(Ã)`, `C = 2·σ(C̃)`).

Mappings are dynamically parameterized: the raw `Ã, B̃, C̃` are produced from a static learnable bias plus an input-dependent term `α·RMSNorm(vec(X_l))·W` so the residual mixing adapts per token. DeepSeek-V4 wall-time overhead is ~6.7% of the 1F1B-overlapped pipeline stage thanks to fused kernels and a recomputation strategy that re-derives most inter-layer hidden states.

## Reference materials

- mHC paper (Xie et al., 2026) — cited as the canonical reference in DeepSeek-V4 Section 2.2.
- Hyper-Connections (Zhu et al., 2025) — the underlying HC residual-expansion idea.
- DeepSeek-V4 Technical Report Section 2.2 + Section 3.4.2 (implementation).

## Used by

| Model             | Variation / details                                                                                                                                                                                                   |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Pro   | n_hc=4 (config.hc_mult), Sinkhorn t_max=20 (config.hc_sinkhorn_iters), tolerance hc_eps=1e-6. Static + dynamic parameterization. AdamW (not Muon) used to update the static biases and gating factors of mHC modules. |
| DeepSeek-V4-Flash | Identical mHC config to V4-Pro: n_hc=4, t_max=20, hc_eps=1e-6, dynamic parameterization on. The only V4-family component without scale-knob differences between Flash and Pro.                                        |

## Related techniques

- [DualPipe](./dualpipe.md) — V4's mHC implementation adjusts the DualPipe 1F1B overlap to absorb the added pipeline communication.
