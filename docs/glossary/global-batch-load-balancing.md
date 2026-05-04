# Global-batch load balancing loss

**Slug:** `global-batch-load-balancing`
**Category:** ffn / moe
**One-line:** A MoE load-balancing auxiliary loss computed across the entire global batch (all sequences across all DP ranks) rather than per-sequence or per-micro-batch, encouraging richer expert specialization without forcing every short sequence to use all experts.
**First introduced in:** [Demons in the Detail: On Implementing Load Balancing Loss for Training Specialized Mixture-of-Experts Models (Qiu et al., 2025)](https://arxiv.org/abs/2501.11873)

## Description

Standard auxiliary load-balancing losses (Switch Transformer, GShard) are computed
**within each sequence** (or each micro-batch). This is too aggressive: a 200-token
chat fragment is forced to spread across all experts uniformly, which prevents
specialization and dilutes the value of having many experts. The global-batch
formulation accumulates routing statistics across all sequences in the global batch
(across all data-parallel ranks via an all-reduce of routing counts) before computing
the imbalance penalty.

The effect: any individual sequence is free to be specialist (route to a small set of
relevant experts), and the loss only penalizes systemic imbalance over the much wider
global distribution. Empirically this shifts the trained model toward sharper
expert specialization with no measurable load-imbalance penalty at inference.

It is structurally an auxiliary loss (gradients flow into the router), in contrast
to **auxiliary-loss-free routing** (DeepSeek-V3) which keeps a non-gradient per-expert
bias for balancing. The two are alternative answers to the same question and represent
the two main schools of MoE balancing currently in use.

## Reference materials

- Original paper: <https://arxiv.org/abs/2501.11873>

## Used by

| Model | Variation / details |
|---|---|
| Qwen3-235B-A22B | `router_aux_loss_coef=0.001` in HF config. 128 experts / 8 active, no shared experts; balancing is the only routing-balance signal documented in the paper (paper §2). Combined with fine-grained expert segmentation à la DeepSeekMoE. |

## Related techniques

- [Auxiliary-loss-free routing](./aux-loss-free-routing.md) — alternative balancing strategy (DeepSeek-V3): a non-gradient per-expert bias instead of an auxiliary loss
- [DeepSeekMoE](./deepseekmoe.md) — orthogonal architectural choice (fine-grained experts + optional shared experts) that Qwen3 partially adopts (fine-grained yes, shared experts no)
