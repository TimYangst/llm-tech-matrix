# Auxiliary-loss-free routing

> 中文版：[aux-loss-free-routing.zh.md](./aux-loss-free-routing.zh.md)

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

| Model                                    | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3                              | bias update speed γ=0.001 for first 14.3T tokens, 0 for last 500B; complementary sequence-wise balance loss α=0.0001; node-limited routing (M=4 nodes, 8 expert groups).                                                                                                                                                                                                                                                                                                                            |
| DeepSeek-V4-Pro                          | Same noaux_tc strategy as V3 but with SqrtSoftplus(·) replacing Sigmoid(·) for affinity scoring (config.scoring_func="sqrtsoftplus"). Bias update speed 0.001; sequence balance loss weight 0.0001. **Removes V3's node-limited routing constraint**. First 3 MoE layers use deterministic Hash routing (config.num_hash_layers=3) instead.                                                                                                                                                         |
| DeepSeek-V4-Flash                        | Identical noaux_tc + SqrtSoftplus + first-3-layer Hash routing recipe to V4-Pro. Differs only in scale (256 routed × top-6 + 1 shared, scaling factor 1.5) and routed-scaling factor (1.5 vs Pro's 2.5).                                                                                                                                                                                                                                                                                            |
| Kimi K2 family (K2-Thinking, K2.5, K2.6) | Same noaux_tc + Sigmoid affinity scoring as DeepSeek-V3 (`scoring_func='sigmoid'`); routed_scaling_factor=2.827. **Removes V3's expert grouping / node-limited routing entirely** (`n_group=1`) — closer to V4 in this respect, but keeps V3's Sigmoid (V4 switched to SqrtSoftplus). Retains a sequence-wise balance loss (`seq_aux=true`, `aux_loss_alpha=0.001`). Identical setup across all 3 K2 siblings (one shared K2 backbone). 384 routed × 1 shared, top-8.                               |
| GLM-4.7                                  | "Loss-free balance routing" with sigmoid gates (paper §2.1) — bias update rate scheduled 0.001 for the first 15T tokens then 0.0 for the remaining (vs DSV3's 14.3T/500B split). Sequence-level balance loss with weight 0.0001 retained as complementary signal. **No node-limited routing** (`n_group=1`, `topk_group=1` in config). 160 routed × 1 shared experts, top-8, routed_scaling_factor=2.5. The GLM-4.5 ARC paper's recipe is what GLM-5/5.1 inherit and apply to a different MoE size. |
| GLM-5 / GLM-5.1                          | Inherits GLM-4.7's loss-free balance routing recipe at 256 routed × 1 shared experts × top-8, sigmoid scoring, `topk_method='noaux_tc'`, `routed_scaling_factor=2.5`, `n_group=1` / `topk_group=1` (no node-limited routing). The bias-update / sequence-loss schedule from GLM-4.5 ARC paper §2.4 carries over (post-training-only refresh in GLM-5.1 doesn't touch the routing module).                                                                                                           |

## Related techniques

- [DeepSeekMoE](./deepseekmoe.md)
- [Global-batch load balancing](./global-batch-load-balancing.md) — Qwen3's alternative balancing approach (gradient-flowing auxiliary loss, but computed over the global batch instead of per-sequence)
