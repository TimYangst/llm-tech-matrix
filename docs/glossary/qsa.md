# Qwen Sparse Attention (QSA)

> 中文版：[qsa.zh.md](./qsa.zh.md)

**Slug:** `qsa`
**Category:** attention
**One-line:** A DSA-descended sparse attention that scores context at *micro-block* granularity with a compressed lightweight indexer, so that the indexer's own cost falls with sequence length instead of growing quadratically.
**First introduced in:** [On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability (Qwen Team, 2026)](https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf) §2.1.2

## Description

[DSA](./dsa.md) made sparse attention retrofittable by training a lightweight indexer to
imitate the model's own attention distribution, then attending only to the indexer's
top-k tokens. QSA keeps that structure and attacks what DSA left on the table: **the
indexer is itself O(n²)**, so as context grows the scoring path becomes the bottleneck it
was introduced to remove.

QSA's fix is to score *compressed blocks* rather than tokens. Keys are partitioned into
non-overlapping micro-blocks of `r` tokens and average-pooled into one representative key
per block — crucially **before** positional encoding, so each block is first summarized as
content and only then assigned a single block-level position, rather than averaging
representations that sit at different rotary phases. A multi-query indexer (H query heads,
one shared key head) then scores each block with `I_ib = Σ_h ReLU(⟨q_i^h, k̄_b⟩)` under a
block-causal mask, and each query takes the top `⌈K/r⌉` blocks. Selected blocks expand back
to token indices, truncate to the token budget `K`, and union with the always-included tail
tokens of the final incomplete block. Compressing by `r` before scoring drops indexing from
`O(n²)` to `O(n²/r)`.

Training is a two-stage retrofit at continued-pretraining time, inherited in shape from
DSA: **dense distillation** trains the indexer alone by KL against the backbone's own
attention (max-pooled, not mean-pooled, to block granularity so salient token signal is not
diluted), then **sparse training** unfreezes the backbone under the indexer's selection with
the KL loss restricted to the selected blocks.

The result is not merely loss-neutral. Qwen3.8-Flash-Next with QSA matches or beats its
full-attention baseline on 7 of 8 short-context benchmarks, and *widens* the gap as context
grows — RULER beyond 512K goes 90.08 → 93.00, and 8-needle MRCR at 512K goes 30.66 → 40.53.
The report attributes the long-context gain to the indexer acting as a learned retrieval
prior rather than a lossy approximation.

One design note specific to hybrid stacks: QSA compresses *within* a layer, where the
main alternative (IndexShare) shares indices *across* adjacent full-attention layers. In a
3:1 GDN hybrid those layers are separated by three linear-attention layers, and inter-layer
similarity is low — the report measures QSA matching baseline RULER at 0.25 relative indexer
latency while IndexShare is still below baseline at 0.5.

## Reference materials

- Original paper: <https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf> (§2.1.2)
- Predecessor mechanism: [DSA](./dsa.md) (introduced in DeepSeek-V3.2-Exp)
- Reference implementation: fused QSA kernel described in the report; the companion linear-attention library is at <https://github.com/QwenLM/FlashQLA>

## Used by

| Model | Variation / details |
| ----- | ------------------- |
| Qwen3.8-Flash-Next | Micro-block size `r=4`, token budget `K=2048` (512 blocks), indexer MQA with 4 query heads + 1 shared key head, indexer head_dim 128, partial RoPE on 64 of 128 indexer dims to match the core attention's rotary dimension. Applied to **every** full-attention layer — 12 of 48 in the backbone, plus the MTP module's attention layer. Retrofitted during CPT at 256K: 1,000 indexer-only steps (~2B tokens, lr 1e-3), then 8,000 joint steps (~200B tokens, lr 2.5e-5). Kernel-level speedup at 1M context: **7.6× prefill, 4.9× decode**. |

## Related techniques

- [DeepSeek Sparse Attention (DSA)](./dsa.md) — the direct ancestor; QSA's contribution is compressing the indexer's own input.
- [CSA + HCA](./csa-hca.md) — DeepSeek-V4's successor to DSA, which instead compresses the KV entries themselves.
- [Gated DeltaNet](./gated-deltanet.md) — the linear-attention layers QSA is interleaved with, and the reason within-layer compression beats cross-layer index sharing here.
