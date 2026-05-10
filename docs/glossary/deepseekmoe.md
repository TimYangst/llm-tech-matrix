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

| Model             | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V3       | 256 routed experts + 1 shared expert, top-8 routing, per-expert intermediate size 2048. First 3 layers are dense, remaining 58 are MoE.                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| Qwen3-235B-A22B   | Adopts the **fine-grained expert segmentation** half (128 experts × 1536 width, 8 active) but **excludes shared experts** (paper §2 explicitly contrasts this with Qwen2.5-MoE and DeepSeek-V3). All 94 layers are MoE. Combined with global-batch load balancing instead of aux-loss-free routing.                                                                                                                                                                                                                                                                                                          |
| Qwen3.5-35B-A3B   | Reintroduces shared experts after Qwen3 dropped them: **256 routed × 512 width, top-8** plus **1 always-on shared expert** (also width 512). All 40 FFN positions are MoE. Reverts further to a **classic auxiliary load-balance loss** (`router_aux_loss_coef=0.001`), abandoning Qwen3's global-batch LB and DeepSeek-V3's aux-loss-free routing. The same fine-grained-experts-plus-shared-expert template as DeepSeek-V3, but at much smaller per-expert width (512 vs DeepSeek-V3's 2048) and on a hybrid Gated DeltaNet + Gated Attention backbone. Vendor sources don't explain the design reversion. |
| Qwen3.6-35B-A3B   | Identical MoE topology to Qwen3.5-35B-A3B — same 256 routed × 512 + 1 shared × 512, same `router_aux_loss_coef=0.001`. The post-training-only refresh keeps Qwen3.5's load-balancing reversion in place.                                                                                                                                                                                                                                                                                                                                                                                                     |
| DeepSeek-V4-Pro   | **384 routed × 1 shared, top-6**, per-expert intermediate size 3072. All 61 layers MoE (no dense prefix); first 3 MoE layers use deterministic **Hash routing** (`config.num_hash_layers=3`) — token-ID hash determines target experts. Routing affinity changes from V3's Sigmoid to **SqrtSoftplus(·)**. **Removes V3's node-limited routing**. Routed-scaling factor 2.5. Expert weights stored in FP4 after post-training QAT.                                                                                                                                                                           |
| DeepSeek-V4-Flash | **256 routed × 1 shared, top-6**, per-expert intermediate size 2048. All 43 layers MoE; same first-3-layer Hash routing pattern as V4-Pro. Same SqrtSoftplus affinity, same node-limited removal, same FP4 expert quantization. Routed-scaling factor 1.5 (vs Pro's 2.5).                                                                                                                                                                                                                                                                                                                                    |

## Related techniques

- [Auxiliary-loss-free routing](./aux-loss-free-routing.md) — DeepSeek-V3's load-balancing strategy on top of DeepSeekMoE
- [Global-batch load balancing](./global-batch-load-balancing.md) — Qwen3's load-balancing strategy on top of fine-grained MoE
