# Multi-Token Prediction (MTP)

> 中文版：[mtp.zh.md](./mtp.zh.md)

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

| Model             | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V3       | Sequential variant, D=1 (one extra prediction depth). Embedding + output head shared with main model. Loss weight λ=0.3 for first 10T tokens, then 0.1 for remaining 4.8T. MTP modules discarded at inference (or repurposed for speculative decoding).                                                                                                                                                                                                                                                                                                                                                                                                                              |
| Qwen3.5-27B       | "Trained with multi-steps" per HF model card; exact step depth D not disclosed. Config exposes `mtp_num_hidden_layers=1` (head depth) and `mtp_use_dedicated_embeddings=false` (shares input embeddings with main model). Serving recipes use the head for **speculative decoding**: vLLM `qwen3_next_mtp` with `num_speculative_tokens=2`; sglang NEXTN with `speculative-num-steps=3`, `speculative-num-draft-tokens=4`. Suggests effective inference draft depth of at least 2-4.                                                                                                                                                                                                 |
| Qwen3.5-35B-A3B   | Identical MTP setup to the 27B sibling: `mtp_num_hidden_layers=1`, `mtp_use_dedicated_embeddings=false`, "trained with multi-steps" per README. Same vLLM/sglang speculative-decoding recipes apply. The MoE FFN does not change MTP topology; the head sits on top of the shared backbone.                                                                                                                                                                                                                                                                                                                                                                                          |
| Qwen3.6-27B       | Identical MTP setup to Qwen3.5-27B — `mtp_num_hidden_layers=1`, `mtp_use_dedicated_embeddings=false`, "trained with multi-steps" per README, same speculative-decoding serving recipes. No 3.6-specific MTP changes disclosed.                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Qwen3.6-35B-A3B   | Identical MTP setup to Qwen3.5-35B-A3B — same head depth, embedding-sharing, multi-step training claim, and serving recipes. The full Qwen3.5/3.6 family converges on the same MTP topology.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| DeepSeek-V4-Pro   | Same MTP configuration as DeepSeek-V3 (paper Section 2.1: 'we adopt the same strategy for DeepSeek-V4 series without modification'). D=1, `config.num_nextn_predict_layers=1`. Loss weight λ=0.3 for most of training, decayed to 0.1 at LR-decay onset. Embedding + output head shared with main model; DualPipe co-location preserved.                                                                                                                                                                                                                                                                                                                                             |
| DeepSeek-V4-Flash | Identical MTP setup to V4-Pro and V3 — D=1, same loss-weight schedule, same shared modules. The MTP head is the only place that lives outside the 43-layer count (config.compress_ratios array length 44 with trailing 0 marks the MTP head's compression slot).                                                                                                                                                                                                                                                                                                                                                                                                                     |
| GLM-4.7           | D=1, `config.num_nextn_predict_layers=1`. Paper §2.1 implementation note: "we add an MoE layer as the MTP layer" — the MTP module reuses the MoE FFN topology rather than a smaller dense head. Loss weight λ=0.3 for the first 15T tokens then 0.1 for the remaining (paper §2.4). vLLM speculative decoding: `--speculative-config.method mtp --speculative-config.num_speculative_tokens 1`; SGLang: EAGLE 3-step.                                                                                                                                                                                                                                                                |
| GLM-5 / GLM-5.1   | D=3 reported (paper §2.1: "we propose sharing the parameters of 3 MTP layers during training") realized via a single physical module (`config.num_nextn_predict_layers=1`) parameter-shared across 3 sequential speculative-step predictions. Memory cost matches DeepSeek-V3's single-MTP design while the model predicts 3 additional tokens. Reported accept length 2.76 vs DeepSeek-V3.2's 2.55 at 4 speculative steps (paper Table 2). MTP output layer co-located with the main output head on the final pipeline stage to enable parameter sharing; embedding+transformer components placed on the preceding stage to balance memory (paper §2.4.1 'Flexible MTP placement'). |

## Related techniques

- _Speculative decoding (EAGLE, Medusa)_ — a related-but-distinct use of multi-future-token heads, focused on inference acceleration rather than training-signal density
