# Gated DeltaNet

**Slug:** `gated-deltanet`
**Category:** attention
**One-line:** A linear-attention variant that maintains a recurrent key-value state updated by a delta rule and produces output via a learned multiplicative gate, giving softmax-quality recall at constant per-token cost.
**First introduced in:** [Gated Delta Networks: Improving Mamba2 with Delta Rule (Yang et al., 2024)](https://arxiv.org/abs/2412.06464)

## Description

Linear attention replaces the softmax-attention dot product with a kernelized form
that admits a constant-size recurrent state, dropping the per-token cost from O(N) at
position N to O(1) — but vanilla linear attention loses recall on long contexts because
the state cannot selectively forget stale keys.

Gated DeltaNet combines two ideas:

- **Delta rule** (DeltaNet, Yang et al. 2024): each step updates the recurrent state
  by a *correction* `Δ = β·(v − Sₜ k) kᵀ` rather than an outer-product `vkᵀ`. This
  performs an online linear-regression-style fit of values to keys, letting newer
  keys overwrite older ones at the same address rather than accumulating noise.
- **Output gating**: a sigmoid (or swish-gated) per-channel gate is applied to the
  attention output, mirroring the gating in modern SSMs (Mamba2). The gate suppresses
  channels whose recurrent state is no longer relevant, recovering selective forgetting.

In transformer stacks, Gated DeltaNet is typically interleaved with a small number of
full-softmax-attention layers (the "globally-correct" channel), so the model gets the
near-O(1) cost of recurrent layers on most steps with the long-range recall of softmax
on a few. This is the layout Qwen3.5 adopts: 3 Gated DeltaNet layers per 1 Gated
Attention layer, repeated 16 times across a 64-layer stack.

## Reference materials

- Original paper: <https://arxiv.org/abs/2412.06464>
- DeltaNet (delta rule baseline): <https://arxiv.org/abs/2102.11174>

## Used by

| Model           | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3.5-27B     | Used in **3 of every 4** layers (`config.layer_types` lists `linear_attention` 3× then `full_attention` 1×, repeated 16 times — 48 of 64 layers). Asymmetric heads: `linear_num_value_heads=48` × `linear_value_head_dim=128` (V state width 6144) but `linear_num_key_heads=16` × `linear_key_head_dim=128` (K state width 2048). 1D causal conv pre-DeltaNet with `linear_conv_kernel_dim=4`. Output gate uses swish (`output_gate_type=swish`). State is kept in `mamba_ssm_dtype=float32` for numerical stability. No RoPE — positional information lives in the recurrent state update. |
| Qwen3.5-35B-A3B | Same hybrid pattern but **narrower V state**: `linear_num_value_heads=32` × `linear_value_head_dim=128` (V state width 4096) with K state still `16 × 128 = 2048`. 30 of 40 layers (10 outer blocks of 3 DeltaNet + 1 GatedAttn). The MoE-FFN companion (256 experts, 8 routed + 1 shared) makes the per-token compute roughly cost-matched to 27B's dense FFN despite a smaller V state per linear-attention layer.                                                                                                                                                                         |

## Related techniques

- [GQA](./gqa.md) — the softmax-attention companion in Qwen3.5's hybrid stack (1 in every 4 layers)
