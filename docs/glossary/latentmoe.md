# Stable LatentMoE (LatentMoE + SiTU-GLU + Quantile Balancing)

> 中文版：[latentmoe.zh.md](./latentmoe.zh.md)

**Slug:** `latentmoe`
**Category:** ffn / moe
**One-line:** Runs the *routed* experts in a compact latent space narrower than the model hidden dim, so expert count and routing multiplicity can scale without dispatch traffic scaling with them — plus the three stabilizers (RMSNorm before up-projection, SiTU-GLU, Quantile Balancing) that make it trainable at extreme sparsity.
**First introduced in:** LatentMoE (Gao et al., 2026), cited as ref. [32] of the [Kimi K3 technical report §2.3](https://arxiv.org/abs/2607.24653), where the "Stable" variant is introduced and scaled to 896 experts.

## Description

In a conventional MoE, every selected expert receives the full `d`-dimensional token
representation, so communication volume and expert-weight traffic grow with routing
multiplicity `k`. That caps how far you can push either the expert pool or the active count.
LatentMoE breaks the coupling by separating **model width** from **routed-expert width**:
shared experts keep a full-width path for common transformations, while routed experts operate
in a compact latent space of width `ℓ`.

```
u = Σ_{i ∈ Top-k(x)} p_i · E_routed_i(W_down · x)        # routed branch, width ℓ
y = Σ_j E_shared_j(x) + W_up · RMSNorm(u)                # shared branch stays width d
```

Kimi K3 uses `ℓ = 3584 = 0.5 × d` and reaches **896 routed experts with 16 active per token**,
a sparsity of 56 — roughly 2.3× the expert pool and 2× the active count of Kimi K2, at a
per-expert FFN width that also grew (2048 → 3072).

That sparsity amplifies two failure modes, and "Stable" LatentMoE is the three fixes:

1. **RMSNorm before the up-projection** (Normalized LatentMoE, `latent_moe_use_norm=true`).
   The aggregated routed representation `u` varies in scale with which experts fired and with
   their routing weights; normalizing before `W_up` desensitizes the routed branch to that
   variation before it merges with the full-width shared branch. Beyond stability it
   consistently improved validation loss and downstream benchmarks.
2. **SiTU-GLU** (Sigmoid Tanh Unit GLU), replacing SwiGLU. The routed path composes `W_down`,
   a gated multi-branch expert FFN, and `W_up` into a chain of nearly four consecutive matmuls;
   that ill-conditioned structure at 2.8T scale produces exploding activations, and SwiGLU's
   two multiplicative factors are both unbounded. SiTU-GLU applies a smooth cap
   `softcap(x, β) = β·tanh(x/β)` to the linear factor of the Swish gate *and* independently to
   the up branch:
   `SiTU-GLU(x) = [β₁·tanh(W_g x / β₁) ⊙ σ(W_g x)] ⊙ [β₂·tanh(W_u x / β₂)]`.
   K3 uses β₁ = 4 (gate) and β₂ = 25 (up), bounding the output at β₁β₂ = 100. Near the origin
   it tracks SwiGLU; at large magnitude it saturates instead of running away in low precision.
3. **Quantile Balancing (QB)**, replacing the fixed-step bias update of aux-loss-free routing.
   See [aux-loss-free routing](./aux-loss-free-routing.md) for the base scheme. The original
   update `b ← b + γ·sign(mean_load − load)` trades slow adaptation against load oscillation,
   and at ~10³ experts per layer neither setting behaves. QB instead derives each expert's bias
   directly from the **router-score quantile matching its target load** `q = mk/n`: routing runs
   Top-(k+1) on the biased score so the (k+1)-th entry gives each token's cutoff `α_i` for free,
   and the new bias is `−quantile_{1−k/n}(s_{:,j} − α)`, mean-centered. Because the quantile
   spans a global batch of millions of margins sharded across ranks, it is estimated from a
   per-expert **histogram** reduced by a single all-reduce of bin counts — additive counts make
   the estimate whole-batch-exact up to bin width, at a few hundred bins per expert. The bias
   regulates dispatch only (excluded from the mixture weights `p_i,j`, so router gradients are
   untouched), applies from the next step, and is frozen at inference.

## Reference materials

- Kimi K3 technical report §2.3 (Stable LatentMoE, SiTU-GLU §2.3.2, Quantile Balancing §2.3.3, appendices B–D): <https://arxiv.org/abs/2607.24653>
- Base MoE organization: [DeepSeekMoE](./deepseekmoe.md) — shared + fine-grained routed experts
- Base balancing scheme: [auxiliary-loss-free routing](./aux-loss-free-routing.md)

## Used by

| Model   | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K3 | 896 routed experts, 16 active (sparsity 56), 2 full-width shared experts fixed in every layer. Routed latent width 3584 (`config.routed_expert_hidden_size`, = 0.5× hidden 7168); per-expert FFN width 3072 (`moe_intermediate_size`). Sigmoid router, `topk_method='noaux_tc'`, `moe_renormalize=true`, `routed_scaling_factor=1.0`, no grouped/node-limited routing. All three stabilizers active: `latent_moe_use_norm=true`, `hidden_act='situ'` with β₁=4 / β₂=25 (`activation_situ_beta` / `activation_situ_linear_beta`), and QB for balancing. Only the routed experts are MXFP4-quantized — the latent projections, shared experts and routers stay in higher precision. |

## Related techniques

- [DeepSeekMoE (fine-grained + shared experts)](./deepseekmoe.md) — the shared/routed organization LatentMoE builds on. The delta is that routed experts no longer read and write full model width.
- [Auxiliary-loss-free routing](./aux-loss-free-routing.md) — QB is a drop-in replacement for its bias-update rule, not for the scheme itself.
- [FP4 QAT (MXFP4)](./fp4-qat.md) — the narrow latent width and the 4-bit expert weights are complementary attacks on the same cost: expert memory and dispatch traffic.
- [Attention Residuals (AttnRes)](./attnres.md) and [KDA](./kda.md) — the depth and sequence axes of the same three-axis scaling argument.
