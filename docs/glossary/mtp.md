# Multi-Token Prediction (MTP)

**Slug:** `mtp`
**Category:** training-objective
**One-line:** A pre-training objective that predicts not just the next token but the next D tokens via shallow extra modules, densifying the training signal and (optionally) supplying speculative-decoding heads at inference.
**First introduced in:** [Better & Faster Large Language Models via Multi-token Prediction (Gloeckle et al., 2024)](https://arxiv.org/abs/2404.19737)

## Description

In standard autoregressive pre-training, each token contributes a single next-token
prediction loss. MTP attaches `D` additional small heads (one per future-position
offset 1..D) and adds their cross-entropy losses to the main loss with a weight λ.
This roughly multiplies the per-token training signal by `1 + D · λ`, often improving
benchmarks at fixed compute.

Different variants differ in head topology:

- **Parallel (Gloeckle et al.)** — `D` independent heads predicting positions 2..D+1
  in one shot.
- **Sequential (DeepSeek-V3)** — heads chained so head `k`'s prediction conditions on
  head `k-1`'s representation, preserving the causal chain. Implementation reuses the
  main model's embedding and output head to keep parameter overhead small.

At inference time the MTP modules can be discarded (recovering the base model) or
repurposed as speculative-decoding draft heads.

## Reference materials

- Original paper: <https://arxiv.org/abs/2404.19737>
- DeepSeek-V3 implementation details and ablations: <https://arxiv.org/abs/2412.19437> (Section 2.2, Table 4)

## Used by

| Model           | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V3     | Sequential variant, D=1 (one extra prediction depth). Embedding + output head shared with main model. Loss weight λ=0.3 for first 10T tokens, then 0.1 for remaining 4.8T. MTP modules discarded at inference (or repurposed for speculative decoding).                                                                                                                                                                                                                              |
| Qwen3.5-27B     | "Trained with multi-steps" per HF model card; exact step depth D not disclosed. Config exposes `mtp_num_hidden_layers=1` (head depth) and `mtp_use_dedicated_embeddings=false` (shares input embeddings with main model). Serving recipes use the head for **speculative decoding**: vLLM `qwen3_next_mtp` with `num_speculative_tokens=2`; sglang NEXTN with `speculative-num-steps=3`, `speculative-num-draft-tokens=4`. Suggests effective inference draft depth of at least 2-4. |
| Qwen3.5-35B-A3B | Identical MTP setup to the 27B sibling: `mtp_num_hidden_layers=1`, `mtp_use_dedicated_embeddings=false`, "trained with multi-steps" per README. Same vLLM/sglang speculative-decoding recipes apply. The MoE FFN does not change MTP topology; the head sits on top of the shared backbone.                                                                                                                                                                                          |
| Qwen3.6-27B     | Identical MTP setup to Qwen3.5-27B — `mtp_num_hidden_layers=1`, `mtp_use_dedicated_embeddings=false`, "trained with multi-steps" per README, same speculative-decoding serving recipes. No 3.6-specific MTP changes disclosed.                                                                                                                                                                                                                                                       |
| Qwen3.6-35B-A3B | Identical MTP setup to Qwen3.5-35B-A3B — same head depth, embedding-sharing, multi-step training claim, and serving recipes. The full Qwen3.5/3.6 family converges on the same MTP topology.                                                                                                                                                                                                                                                                                         |

## Related techniques

- _Speculative decoding (EAGLE, Medusa)_ — a related-but-distinct use of multi-future-token heads, focused on inference acceleration rather than training-signal density
