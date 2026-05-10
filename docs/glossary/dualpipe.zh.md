# DualPipe pipeline scheduling

> English: [dualpipe.md](./dualpipe.md)

**Slug:** `dualpipe`
**类别：** infra
**一句话概括：** 一种双向的流水线并行调度——把 forward / backward 计算与 expert-parallel 的 all-to-all 通信重叠，消除大规模 MoE 训练中大部分通信停顿气泡。
**首次提出：** [DeepSeek-V3 Technical Report (DeepSeek-AI, 2024)](https://arxiv.org/abs/2412.19437)（§3.2.1）

## 概述

对跨节点专家并行训练的大型 MoE 来说，专家 dispatch / combine 的 all-to-all 通信占了主要开销——在 DeepSeek-V3 的设置下大致与计算 1:1。标准的 1F1B 流水线调度无法隐藏这种成本；ZeroBubble 等推动了前沿但仍留有气泡。

DualPipe 把每个 chunk 切成四个部分——attention、all-to-all dispatch、MLP、all-to-all combine——并对反向 chunk 进一步切成 "backward for input" 和 "backward for weights"。然后 **从流水线两端同时调度 micro-batch**，把一个 micro-batch 的 forward chunk 与另一个 micro-batch 的 backward chunk 重叠。配合手动在计算和通信之间分配 SM，只要计算 / 通信比维持在大致 1:1，all-to-all 和 PP 通信都能被完全隐藏。

DualPipe 的代价：需要为流水线每个方向各保留一份模型参数；峰值激活内存 2× + 1（vs 1F1B 的 1×）。DeepSeek-V3 能吃下这一代价，是因为主导的内存占用是专家权重而不是激活。

## 参考资料

- DeepSeek-V3 论文 §3.2.1 + 图 4-5：<https://arxiv.org/abs/2412.19437>
- 背景——ZeroBubble：<https://arxiv.org/abs/2401.10241>；1F1B：<https://arxiv.org/abs/1806.03377>

## 使用此技术的模型

| 模型        | 变体 / 细节                                                                                                                                                          |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3 | 16-way PP，64-way EP（跨 8 节点），ZeRO-1 DP，无 Tensor Parallelism。2048 张 H800 GPU。跨节点 all-to-all kernel 用 20 个 SM（10 个 channel），warp-specialized PTX。 |

## 相关技术

- _1F1B、ZeroBubble (ZB1P)、Chimera_ — 流水线调度的前驱 / 替代方案
