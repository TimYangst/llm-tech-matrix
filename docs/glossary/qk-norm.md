# QK-Norm

**Slug:** `qk-norm`
**Category:** attention
**One-line:** Apply normalization (typically RMSNorm or LayerNorm) to the query and key projections inside attention before the dot product, to stabilize training by preventing attention-logit scale blow-ups.
**First introduced in:** [Scaling Vision Transformers to 22 Billion Parameters (Dehghani et al., 2023)](https://arxiv.org/abs/2302.05442)

## Description

In standard attention, raw query and key projections can grow to large magnitudes
during training, producing attention logits whose softmax saturates and gradients
collapse. QK-Norm inserts a normalization op on Q and K (per-head, before computing
`Q · K^T / √d`), so the logit magnitude is bounded by construction. The fix is cheap
(one extra norm per attention) and removes a class of training instabilities that
otherwise force tricks like attention scaling, embedding clipping, or Q/KV biases.

Originally proposed for ViT-22B, QK-Norm has been gradually adopted by LLM
trainers as a no-regret stabilizer when scaling. Qwen3 explicitly cites it as
the replacement for the QKV-bias used in Qwen2.

## Reference materials

- Original paper: <https://arxiv.org/abs/2302.05442>

## Used by

| Model | Variation / details |
|---|---|
| Qwen3-32B | RMSNorm-style QK-Norm inside each attention block. Replaces the QKV-bias used in Qwen2 (config `attention_bias=false`). Cited by Qwen3 paper as a stability requirement for the deeper / larger Qwen3 architectures. |
| Qwen3-235B-A22B | Same architectural choice as the rest of Qwen3 (dense and MoE share the QK-Norm + no-QKV-bias decision). |

## Related techniques

- [GQA](./gqa.md) — orthogonal: GQA shapes the KV cache, QK-Norm fixes logit magnitudes
