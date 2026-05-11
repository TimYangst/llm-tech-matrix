# DeepSeekMoE (fine-grained + shared experts)

> 中文版：[deepseekmoe.zh.md](./deepseekmoe.zh.md)

**Slug:** `deepseekmoe`
**Category:** ffn / moe
**One-line:** A Mixture-of-Experts variant that uses many fine-grained experts plus a small number of always-active "shared" experts, improving expert specialization without sacrificing common-knowledge coverage.
**First introduced in:** [DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models (Dai et al., 2024)](https://arxiv.org/abs/2401.06066)

## Description

Compared with traditional MoE designs (e.g. GShard, Switch Transformer) that use a
small number of large experts, DeepSeekMoE makes two structural changes:

1. **Fine-grained experts** — many more, smaller experts. Each token activates a small
   number (top-K) of them. This gives more flexibility in routing combinations and
   encourages each expert to specialize narrowly.
2. **Shared experts** — a separate small set of experts that every token uses
   unconditionally. They absorb common knowledge that would otherwise be redundantly
   replicated across many routed experts.

The math sums shared expert outputs and gated routed expert outputs. The gating value
is the (normalized) routing affinity — sigmoid in DeepSeek-V3, softmax in earlier work.

## Reference materials

- Original paper: <https://arxiv.org/abs/2401.06066>
- Used in DeepSeek-V2 and DeepSeek-V3.

## Used by

| Model                                    | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3                              | 256 routed experts + 1 shared expert, top-8 routing, per-expert intermediate size 2048. First 3 layers are dense, remaining 58 are MoE.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| Qwen3-235B-A22B                          | Adopts the **fine-grained expert segmentation** half (128 experts × 1536 width, 8 active) but **excludes shared experts** (paper §2 explicitly contrasts this with Qwen2.5-MoE and DeepSeek-V3). All 94 layers are MoE. Combined with global-batch load balancing instead of aux-loss-free routing.                                                                                                                                                                                                                                                                                                                     |
| Qwen3.5-35B-A3B                          | Reintroduces shared experts after Qwen3 dropped them: **256 routed × 512 width, top-8** plus **1 always-on shared expert** (also width 512). All 40 FFN positions are MoE. Reverts further to a **classic auxiliary load-balance loss** (`router_aux_loss_coef=0.001`), abandoning Qwen3's global-batch LB and DeepSeek-V3's aux-loss-free routing. The same fine-grained-experts-plus-shared-expert template as DeepSeek-V3, but at much smaller per-expert width (512 vs DeepSeek-V3's 2048) and on a hybrid Gated DeltaNet + Gated Attention backbone. Vendor sources don't explain the design reversion.            |
| Qwen3.6-35B-A3B                          | Identical MoE topology to Qwen3.5-35B-A3B — same 256 routed × 512 + 1 shared × 512, same `router_aux_loss_coef=0.001`. The post-training-only refresh keeps Qwen3.5's load-balancing reversion in place.                                                                                                                                                                                                                                                                                                                                                                                                                |
| DeepSeek-V4-Pro                          | **384 routed × 1 shared, top-6**, per-expert intermediate size 3072. All 61 layers MoE (no dense prefix); first 3 MoE layers use deterministic **Hash routing** (`config.num_hash_layers=3`) — token-ID hash determines target experts. Routing affinity changes from V3's Sigmoid to **SqrtSoftplus(·)**. **Removes V3's node-limited routing**. Routed-scaling factor 2.5. Expert weights stored in FP4 after post-training QAT.                                                                                                                                                                                      |
| DeepSeek-V4-Flash                        | **256 routed × 1 shared, top-6**, per-expert intermediate size 2048. All 43 layers MoE; same first-3-layer Hash routing pattern as V4-Pro. Same SqrtSoftplus affinity, same node-limited removal, same FP4 expert quantization. Routed-scaling factor 1.5 (vs Pro's 2.5).                                                                                                                                                                                                                                                                                                                                               |
| Kimi K2 family (K2-Thinking, K2.5, K2.6) | **384 routed × 1 shared, top-8**, per-expert intermediate size 2048 (sparsity 48 — K2.5 paper §4.1). First 1 of 61 layers is dense (intermediate_size=18432); remaining 60 layers are MoE. Identical fine-grained-experts + 1-shared-expert template as DeepSeek-V3, at the same per-expert width (2048) but 1.5× more experts (384 vs 256) and a single dense prefix instead of V3's three. Combined with Sigmoid-based aux-loss-free routing (no expert grouping). MoE expert weights deployed at INT4 via [native INT4 QAT](./int4-qat.md) for K2-Thinking + K2.5 + K2.6.                                            |
| GLM-4.7                                  | **160 routed × 1 shared, top-8**, per-expert intermediate size 1536 (sparsity 20). First 3 of 92 layers are dense (intermediate_size=12288); remaining 89 are MoE. GLM-4.5 ARC paper §2.1 explicitly contrasts the GLM-4.5 family's design philosophy with DeepSeek-V3 / Kimi K2: "we reduce the width (hidden dimension and number of routed experts) of the model and increase its height (number of layers), as we found that deeper models exhibited better reasoning capacity." 96 attention heads at hidden 5120 = 2.5x more heads-per-hidden than DSV3, motivated by reasoning-benchmark gains.                  |
| GLM-5 / GLM-5.1                          | **256 routed × 1 shared, top-8**, per-expert intermediate size 2048 (sparsity 32). First 3 of 78 layers are dense (intermediate_size=12288); remaining 75 are MoE. GLM-5 paper §2.1 reverses GLM-4.5's "deeper, narrower" philosophy: "scales to 256 experts and reduces its layer count to 80 to minimize expert parallelism communication overhead". Same fine-grained-experts + 1-shared-expert template as DeepSeek-V3 with the same per-expert width (2048), but 78 layers vs DSV3's 61 (still deeper) and combined with [DSA](./dsa.md) sparse attention + [MLA](./mla.md) latent KV instead of DSV3's plain MLA. |

## Related techniques

- [Auxiliary-loss-free routing](./aux-loss-free-routing.md) — DeepSeek-V3's load-balancing strategy on top of DeepSeekMoE
- [Global-batch load balancing](./global-batch-load-balancing.md) — Qwen3's load-balancing strategy on top of fine-grained MoE
