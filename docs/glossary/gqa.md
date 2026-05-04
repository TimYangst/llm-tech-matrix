# Grouped Query Attention (GQA)

**Slug:** `gqa`
**Category:** attention
**One-line:** Multi-head attention variant where multiple query heads share a single key/value head, shrinking the KV cache by the grouping factor while preserving most of the modeling quality of full multi-head attention.
**First introduced in:** [GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints (Ainslie et al., 2023)](https://arxiv.org/abs/2305.13245)

## Description

In Multi-Head Attention (MHA) every query head has its own key and value head, so the
KV cache size is `2 × num_heads × head_dim × seq_len × batch`. Multi-Query Attention
(MQA) collapses to a single shared K/V across all heads — small cache, but quality
drops. GQA is the middle ground: queries are partitioned into G groups, and each group
shares one K/V head, giving `num_kv_heads = num_heads / group_size`.

Two practical wins:
- **KV cache shrink**: linear in `num_heads / num_kv_heads`. Critical for long-context
  serving — KV cache is often the memory bottleneck at inference, not weights.
- **Up-conversion path**: the paper shows you can up-convert an existing MHA checkpoint
  to GQA with a short fine-tune by mean-pooling the KV heads in each group, so you
  don't have to retrain from scratch.

GQA has become the default attention shape for nearly all open dense LLMs above ~7B
(Llama 2/3, Mistral, Qwen2.5/3, etc.). MLA (DeepSeek) is a different tradeoff that
goes further by compressing K/V into a low-rank latent.

## Reference materials

- Original paper: <https://arxiv.org/abs/2305.13245>

## Used by

| Model | Variation / details |
|---|---|
| Qwen3-32B | 64 query heads, 8 KV heads (group size 8), `head_dim=128`. Combined with **QK-Norm** inside the attention block; QKV-bias removed (config sets `attention_bias=false`). All Qwen3 dense models use 8 KV heads regardless of size; MoE models use 4. |

## Related techniques

- [MLA](./mla.md) — DeepSeek's alternative: low-rank KV compression instead of head sharing
- [QK-Norm](./qk-norm.md) — orthogonal stability trick Qwen3 layers on top of GQA
