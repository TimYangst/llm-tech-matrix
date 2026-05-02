# DualPipe pipeline scheduling

**Slug:** `dualpipe`
**Category:** infra
**One-line:** A bidirectional pipeline-parallel schedule that overlaps forward/backward computation with all-to-all expert-parallel communication, eliminating most communication-stall bubbles in large MoE training.
**First introduced in:** [DeepSeek-V3 Technical Report (DeepSeek-AI, 2024)](https://arxiv.org/abs/2412.19437) (Section 3.2.1)

## Description

For large MoE models trained with cross-node expert parallelism, the all-to-all
communication for expert dispatch/combine becomes a dominant cost — roughly 1:1 with
compute on DeepSeek-V3's setup. Standard 1F1B-style pipeline schedules cannot hide
this cost; ZeroBubble and similar advance the state of the art but still leave bubbles.

DualPipe splits each chunk into four components — attention, all-to-all dispatch,
MLP, all-to-all combine — and (for backward chunks) further into "backward for input"
and "backward for weights". It then **schedules micro-batches from both ends of the
pipeline simultaneously**, overlapping the forward chunk of one micro-batch with the
backward chunk of another. With manual SM allocation between compute and communication,
both the all-to-all and PP communications can be fully hidden as long as the
compute-to-communication ratio stays roughly 1:1.

DualPipe's cost: it requires keeping two copies of the model parameters (one per
pipeline direction), and 2× peak activation memory + 1 (vs 1× for 1F1B). DeepSeek-V3
absorbs this because the dominant memory cost is expert weights, not activations.

## Reference materials

- DeepSeek-V3 paper, Section 3.2.1 + Figures 4-5: <https://arxiv.org/abs/2412.19437>
- Background — ZeroBubble: <https://arxiv.org/abs/2401.10241>; 1F1B: <https://arxiv.org/abs/1806.03377>

## Used by

| Model | Variation / details |
|---|---|
| DeepSeek-V3 | 16-way PP, 64-way EP across 8 nodes, ZeRO-1 DP, no Tensor Parallelism. 2048 H800 GPUs. Cross-node all-to-all kernels use 20 SMs (10 channels) with warp-specialized PTX. |

## Related techniques

- _1F1B, ZeroBubble (ZB1P), Chimera_ — predecessors / alternatives in pipeline scheduling
