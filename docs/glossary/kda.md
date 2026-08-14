# Kimi Delta Attention (KDA)

> 中文版：[kda.zh.md](./kda.zh.md)

**Slug:** `kda`
**Category:** attention
**One-line:** A linear-attention layer that extends the delta-rule recurrence with a *channel-wise* forget gate, giving O(L) long-sequence mixing that carries positional information implicitly — so a model built on it can drop RoPE entirely.
**First introduced in:** [Kimi Linear (Moonshot AI, 2025)](https://arxiv.org/abs/2510.26692); extended and scaled to a flagship in the [Kimi K3 technical report §2.1.1 (Moonshot AI, 2026)](https://arxiv.org/abs/2607.24653).

## Description

Linear attention replaces softmax attention's O(L²) score matrix with a recurrent state
`S_t ∈ R^{d_k × d_v}` updated once per token, making cost linear in sequence length. The
*delta rule* variant writes into that state associatively — `S_t = (I − β_t k_t k_tᵀ) S_{t−1} + β_t k_t v_tᵀ`
— which lets a new key overwrite what an old, similar key wrote. KDA adds a **channel-wise
retention factor** `α_t ∈ (0,1)^{d_k}`, so each key channel forgets at its own learned rate
rather than the whole state decaying uniformly:

```
S_t = (I − β_t k_t k_tᵀ) · Diag(α_t) · S_{t−1} + β_t k_t v_tᵀ
```

Q/K/V come from a ShortConv followed by Swish, with L2Norm on Q and K; `β_t = σ(W_β x_t)`
controls write strength; the decay logit comes from a low-rank projection plus a per-head bias.
The layer is computed chunkwise — recurrent across chunks, parallel within a chunk.

**Kimi K3's two changes** (§2.1.1) are both about making the chunkwise form fast and
numerically safe at 1M-token scale:

1. **Lower-bounded decay.** Kimi Linear mapped decay logits through an unbounded
   negative-Softplus, so the reciprocal cumulative decay `1/Γ` used to rescale keys within a
   chunk could overflow. K3 uses `g = g_min · σ(e^A z)` with a learnable per-head log-scale `A`
   and fixed `g_min = −5`. Every retention factor is then `> e^{−5}`, cumulative log-decay over a
   16-token tile stays in `(−80, 0)`, and the rescaling factor stays inside BF16 range. The
   payoff is not just stability: with a bounded range, *both* diagonal and off-diagonal chunk
   tiles can use dense Tensor Core matmuls, eliminating Kimi Linear's explicit position-pair
   diagonal path — which was the main intra-chunk bottleneck.
2. **Full-rank output gate.** The output gate moves from a low-rank parameterization to an
   input-dependent full-rank projection: `y = W_o[σ(W_g x) ⊙ RMSNorm(õ)]`.

The architectural consequence worth noting for cross-model comparison: because KDA's decay
recurrence is inherently position-sensitive, a stack that interleaves KDA with global layers
can run **NoPE** — no RoPE, no YaRN, no interpolation — and still extrapolate to 1M tokens.
Kimi K3 does exactly this, which is why its `rope.type` is `"none"`.

## Reference materials

- Kimi Linear paper: <https://arxiv.org/abs/2510.26692>
- Kimi K3 technical report §2.1.1: <https://arxiv.org/abs/2607.24653>
- Reference implementation: `flash-linear-attention` (FLA) — the KDA kernels and KDA context parallelism were upstreamed in FLA PR #691

## Used by

| Model   | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K3 | 69 of 93 layers are KDA, interleaved 3:1 with Gated MLA (`config.linear_attn_config.kda_layers` / `full_attn_layers`). 96 heads, head_dim 128, `short_conv_kernel_size=4`, `gate_lower_bound=-5.0`, `use_full_rank_gate=true`. Both K3 deltas vs Kimi Linear live here: lower-bounded scaled-sigmoid decay (kills the position-pair diagonal path) and the full-rank output gate. Enables NoPE across the whole model. Serving needed dedicated work — fused kernels, KDA Context Parallelism for 1M-token training, and KDA-aware prefix-cache management (K3 paper §5.1.1 / §5.1.2 / §5.4.1). |

## Related techniques

- [Gated DeltaNet](./gated-deltanet.md) — the closest sibling. Qwen3.5/3.6 interleave Gated DeltaNet with Gated Attention at the *same* 3:1 ratio; the mechanisms differ mainly in gating parameterization and in whether the hybrid partner keeps RoPE (Qwen does, K3 does not).
- [MLA (Multi-head Latent Attention)](./mla.md) — KDA's hybrid partner in Kimi K3, where MLA supplies the periodic global-attention layers.
- [Attention Residuals (AttnRes)](./attnres.md) — the depth-axis counterpart in the same model.
