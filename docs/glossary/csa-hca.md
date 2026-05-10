# Compressed Sparse Attention (CSA) + Heavily Compressed Attention (HCA)

> 中文版：[csa-hca.zh.md](./csa-hca.zh.md)

**Slug:** `csa-hca`
**Category:** attention
**One-line:** Hybrid attention design that interleaves two KV-compressed variants — CSA aggregates `m` tokens into one entry then runs DeepSeek Sparse Attention top-k over compressed blocks, while HCA aggregates `m' >> m` tokens into one entry and does dense attention over the heavier compression — together delivering ~10% of DeepSeek-V3.2's KV cache size and ~27% of its single-token FLOPs at 1M context.
**First introduced in:** [DeepSeek-V4 Technical Report (DeepSeek-AI, 2026)](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf) Section 2.3. Builds on DeepSeek Sparse Attention (DSA) from DeepSeek-V3.2.

## Description

The attention dominates compute at million-token contexts. DeepSeek-V4 attacks this with two complementary KV-compression schemes used in different layers.

**Compressed Sparse Attention (CSA)** does:

1. **Token-level compression.** Each `m=4` consecutive tokens get compressed into one KV entry via two interleaved softmax-weighted compressors (overlapping windows producing `n/m` entries from `2m` raw entries each).
2. **Sparse selection.** A "Lightning Indexer" with `n_I_h=64` indexer query heads of head_dim `c_I=128` ranks compressed blocks via `ReLU(q · K_indexer)` per token. The query-side latent `c^Q_t = h_t · W^DQ` of dimension `d_c` is shared with the main attention queries, halving query-side compute.
3. **Sparse Multi-Query Attention.** Top-k=`{512 (Flash) | 1024 (Pro)}` compressed entries are selected; core attention is single-KV-head MQA over those entries plus an `n_win=128` sliding-window branch of uncompressed recent tokens (captures local fine-grained dependencies that the compression flattens out).
4. **Grouped output projection.** The `n_h` query-head outputs are split into `g={8|16}` groups; each group projected to `d_g=1024` then concatenated and projected to `hidden_dim`. Saves the cost of a full `c·n_h × d` projection.

**Heavily Compressed Attention (HCA)** does:

- Same compression mechanism but with `m'=128` non-overlapping (much heavier compression).
- No lightning indexer — does dense MQA over all `n/m'` compressed entries.
- Same shared-KV MQA + grouped output projection + sliding-window branch as CSA.

**Hybrid layout.** V4-Pro: layers 0–1 pure HCA, layers 2–60 alternate CSA(m=4)/HCA(m'=128). V4-Flash: layers 0–1 pure SWA (no compression), layers 2–42 alternate CSA/HCA. The cache block size is `lcm(m, m')=128` raw tokens, yielding 32 CSA compressed entries and 1 HCA compressed entry per block.

**Other tricks** (paper Section 2.3.3): partial RoPE on the last 64 dims of every Q/K/V; a `-i`-position RoPE applied to the last 64 dims of core-attention outputs to preserve relative-position semantics through KV aggregation; per-head RMSNorm on Q and on the single shared KV head before core attention (replaces QK-Clip); per-head learnable attention sink logit added to softmax denominator.

## Reference materials

- DeepSeek-V4 Technical Report Section 2.3 + Figures 3 & 4.
- DeepSeek Sparse Attention (DSA) reference inside DeepSeek-V3.2.
- Open-source implementation: <https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/tree/main/inference>

## Used by

| Model             | Variation / details                                                                                                                                                                                                                                                 |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Pro   | n_h=128 query heads / head_dim=512 / KV heads=1. CSA: m=4, top-k=1024, indexer (n_I_h=64, c_I=128). HCA: m'=128. Query latent d_c=1536, output groups g=16 of d_g=1024, sliding window n_win=128. Layer 0,1 pure HCA; layers 2-60 interleave CSA/HCA.               |
| DeepSeek-V4-Flash | n_h=64 query heads / head_dim=512 / KV heads=1. CSA: m=4, top-k=512, indexer (n_I_h=64, c_I=128). HCA: m'=128. Query latent d_c=1024, output groups g=8 of d_g=1024, sliding window n_win=128. Layer 0,1 pure SWA (no compression); layers 2-42 interleave CSA/HCA. |

## Related techniques

- [MLA (Multi-head Latent Attention)](./mla.md) — DeepSeek-V3's KV-compression approach (latent compression of K/V into `kv_lora_rank`-dim) that V4 replaces with the per-block compressors above. CSA/HCA shares MLA's "low-rank query latent" idea via `d_c`.
- [GQA](./gqa.md) — V4's "shared KV" core attention (`num_kv_heads=1`) is the limit case of GQA where all queries share one KV head; the compressed-KV trick takes over the role that KV-head replication played in MHA → GQA.
