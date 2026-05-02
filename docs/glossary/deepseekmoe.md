# DeepSeekMoE (fine-grained + shared experts)

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

| Model | Variation / details |
|---|---|
| DeepSeek-V3 | 256 routed experts + 1 shared expert, top-8 routing, per-expert intermediate size 2048. First 3 layers are dense, remaining 58 are MoE. |

## Related techniques

- [Auxiliary-loss-free routing](./aux-loss-free-routing.md) — DeepSeek-V3's load-balancing strategy on top of DeepSeekMoE
