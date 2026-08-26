# Gated DeltaNet

> 中文版：[gated-deltanet.zh.md](./gated-deltanet.zh.md)

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

| Model              | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3.5-27B        | Used in **3 of every 4** layers (`config.layer_types` lists `linear_attention` 3× then `full_attention` 1×, repeated 16 times — 48 of 64 layers). Asymmetric heads: `linear_num_value_heads=48` × `linear_value_head_dim=128` (V state width 6144) but `linear_num_key_heads=16` × `linear_key_head_dim=128` (K state width 2048). 1D causal conv pre-DeltaNet with `linear_conv_kernel_dim=4`. State is kept in `mamba_ssm_dtype=float32` for numerical stability. The output-gate activation function is not exposed by this config (only the Qwen3.6-27B config in the same family explicitly sets `output_gate_type=swish`). No RoPE — positional information lives in the recurrent state update.                                               |
| Qwen3.5-35B-A3B    | Same hybrid pattern but **narrower V state**: `linear_num_value_heads=32` × `linear_value_head_dim=128` (V state width 4096) with K state still `16 × 128 = 2048`. 30 of 40 layers (10 outer blocks of 3 DeltaNet + 1 GatedAttn). The MoE-FFN companion (256 experts, 8 routed + 1 shared) makes the per-token compute roughly cost-matched to 27B's dense FFN despite a smaller V state per linear-attention layer.                                                                                                                                                                                                                                                                                                                                 |
| Qwen3.6-27B        | Identical Gated DeltaNet shape to Qwen3.5-27B (V 48×128=6144, K 16×128=2048, conv kernel 4, swish output gate) — Qwen3.6-27B inherits the backbone wholesale. The 3.6 release is a post-training-only refresh; nothing in the linear-attention machinery changed.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| Qwen3.6-35B-A3B    | Identical Gated DeltaNet shape to Qwen3.5-35B-A3B (V 32×128=4096, K 16×128=2048, conv kernel 4) — Qwen3.6-35B-A3B inherits the backbone wholesale (config still reports `architectures="Qwen3_5MoeForConditionalGeneration"` and `model_type="qwen3_5_moe"`).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Kimi K3 (via KDA)  | Not Gated DeltaNet itself, but its closest relative at flagship scale — [Kimi Delta Attention](./kda.md) is a delta-rule recurrence with a **channel-wise** forget gate, versus Gated DeltaNet's scalar-per-head gate. Worth noting for cross-vendor comparison: Kimi K3 and Qwen3.5/3.6 independently arrived at the **same 3:1 linear-to-global layer ratio**. The divergence is what the hybrid partner does — Qwen keeps RoPE on its Gated Attention layers, K3 runs NoPE on its Gated MLA layers and lets the linear layers carry position entirely.                                                                                                                                                                                            |
| Qwen3.8-27B        | Byte-identical Gated DeltaNet block to Qwen3.6-27B (V 48×128=6144, K 16×128=2048, conv kernel 4, swish output gate). Third consecutive generation on a frozen linear-attention backbone.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Qwen3.8-2.4T-A95B  | First Gated DeltaNet deployment at trillion scale — 69 of 92 layers. The **V-head count scales with model width** (48 at hidden 5120 → **128** at hidden 8192, a 16384-dim V state) while the **QK-head count stays pinned at 16** (2048-dim K state) exactly as in every smaller sibling. Same conv kernel 4, same swish output gate, same 3:1 cadence.                                                                                                                                                                                                                                                                                                                                                                                             |
| Qwen3.8-Flash-Next | Same head geometry as the 27B (V 48×128, K 16×128, conv kernel 4), but the tech report documents two formulation changes: the output gate becomes a **bounded sigmoid** instead of SiLU (`output_gate_type=sigmoid`, vs swish in every earlier Qwen 3.x config) — 'consistent improvements across our experiments' — and **zero-centered RMSNorm** is applied throughout to constrain norm-weight growth. 36 of 48 layers. The report's own ablation justifies the hybrid for the first time with numbers: at 25B-A3B the GDN hybrid beats a full-attention Transformer on 8 of 9 benchmarks and an SWA-128 hybrid on 7 of 9 (avg 53.81 / 49.87 / 51.15). Kernel: **FlashQLA** (TileLang), 2–3× forward and ~2× backward over the FLA Triton kernel. |

## Related techniques

- [GQA](./gqa.md) — the softmax-attention companion in Qwen3.5's hybrid stack (1 in every 4 layers)
