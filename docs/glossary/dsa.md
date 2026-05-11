# DeepSeek Sparse Attention (DSA)

> 中文版：[dsa.zh.md](./dsa.zh.md)

**Slug:** `dsa`
**Category:** attention
**One-line:** A token-level sparse attention scheme where a small "Lightning Indexer" scores all preceding tokens per query position and the core attention is restricted to the top-k highest-scored tokens — content-dependent (unlike sliding windows), lossless by construction (per the GLM-5 paper), and reducing long-context attention compute by roughly 1.5–2× at 128K contexts.

**First introduced in:** [DeepSeek-V3.2-Exp Technical Report (DeepSeek-AI, 2025)](https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp). The two-stage "dense warm-up + sparse adaptation" continual-pretraining recipe is the V3.2-Exp deliverable; the indexer architecture (per-token query × indexer-key dot product → top-k selection) is the core mechanism.

## Description

Standard `O(L^2)` dense attention becomes prohibitive at 128K+ contexts. Sliding-window attention reduces cost but is content-blind: relevant tokens outside the window are dropped regardless of their importance. DSA replaces dense attention with a content-dependent sparsifier:

1. **Lightning Indexer.** A small auxiliary attention path with `index_n_heads` heads of `index_head_dim` per head computes a relevance score `ReLU(q_indexer · k_indexer)` for every preceding token. The indexer queries reuse the main attention's query-side latent (the indexer is cheap because its KV path is independent of the main MLA / KV cache).
2. **Top-k selection.** For each query position, the indexer's top-`index_topk` scoring tokens are retained; the core attention is computed only over this sparse subset (typically `k=2048` for 128K contexts, leaving ~98% of attention entries dropped).
3. **Continued Pre-Training adaptation.** Rather than training from scratch, DSA is bolted onto a dense base model in two stages: a short *warmup* (1000 steps, indexer-only training while the base model is frozen) followed by a *sparse adaptation* phase where both the model and indexer co-train on a modest token budget. DeepSeek-V3.2 used 943.7B sparse-adaptation tokens; GLM-5 found 20B tokens sufficient to recover dense-baseline quality.

The GLM-5 paper (§2.1.2) compares DSA against SWA, search-based-pattern SWA, GDN, and SimpleGDN, and concludes DSA is *lossless* by construction at long contexts because the indexer adapts to content rather than committing to a fixed sparsity pattern. Under SFT loss curves, MLA-base and DSA-base models converge to identical loss (paper Figure 6).

**RL-stability caveat (GLM-5 §3.2).** During RL, the DSA indexer's top-k operator must be deterministic. Non-deterministic CUDA top-k implementations cause drastic RL training degradation with sharp entropy drops within a few steps. GLM-5 uses `torch.topk` (slightly slower but deterministic) and freezes indexer parameters by default during RL.

## Reference materials

- DeepSeek-V3.2-Exp report: <https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp>
- GLM-5 paper §2.1.1 / §2.1.2 / §3.2 / §3.6 (DSA continued-pretraining recipe, ablation vs SWA/GDN, RL stability with deterministic top-k): <https://arxiv.org/abs/2602.15763>
- GLM-5 cookbook (SGLang DSA Indexer optimization): <https://cookbook.sglang.io/autoregressive/GLM/GLM-5>
- Closely related: DeepSeek-V4's [CSA + HCA hybrid](./csa-hca.md), which builds on DSA's content-dependent sparsification by adding token-level KV compression.

## Used by

| Model   | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GLM-5   | First non-DeepSeek vendor to ship DSA. Indexer config: `index_n_heads=32`, `index_head_dim=128`, `index_topk=2048`, `indexer_rope_interleave=true`. Continued Pre-Training recipe (paper §2.1.1): indexer-only warmup 1000 steps × 14 sequences × 202752 tokens at max LR 5e-3 (≈2.84B tokens), then sparse adaptation 20B tokens (vs DSV3.2's 943.7B — much smaller budget proves sufficient). Long-context preserved (paper Table 3): MQ-NIAH-128k 100.0 vs MLA 100.0, MV-NIAH-128k 97.0 vs 95.5, SQuAD-128k 86.0 vs 79.7, HotpotQA-128k 63.0 vs 66.3. GLM-5 paper §2.1.2 ablation against SWA / search-based SWA / GDN / SimpleGDN concludes DSA is the only one *lossless by construction*. RL stability §3.2: deterministic `torch.topk` mandatory; CUDA top-k caused entropy collapse; indexer frozen by default during RL. SGLang-Ascend ships a fused Lightning Indexer kernel. |
| GLM-5.1 | Identical DSA architecture to GLM-5 (config byte-identical except `transformers_version`). Same indexer config, same RL-time deterministic top-k requirement. Post-training-only refresh inherits the GLM-5 indexer weights and DSA-frozen-during-RL discipline.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

> Note: DeepSeek-V3.2-Exp and DeepSeek-V4 (which extends DSA into the [CSA + HCA hybrid](./csa-hca.md)) are not yet extracted in this repo as separate slugs — V3.2 sits between V3 and V4-Pro/Flash chronologically, and V4's hybrid is captured under its own glossary entry. The DSA mechanism above is the contract those entries share.

## Related techniques

- [CSA + HCA hybrid](./csa-hca.md) — DeepSeek-V4 extends DSA's content-dependent sparsification by adding token-level KV compression (CSA = compressed-then-sparse, HCA = heavily-compressed dense). Same Lightning Indexer mechanism inside CSA.
- [MLA (Multi-head Latent Attention)](./mla.md) — DSA is layered *on top of* MLA in GLM-5 / DeepSeek-V3.2: MLA compresses the KV cache; DSA sparsifies which compressed-KV entries the core attention reads from.
- [Muon optimizer](./muon.md) — both GLM-5 and DSV4 train DSA with Muon-family optimizers; GLM-5 specifically uses Muon Split to keep MLA-with-DSA logit scale stable without QK-Clip.
