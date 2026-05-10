# DeepSeekMoE（细粒度 + 共享专家）

> English: [deepseekmoe.md](./deepseekmoe.md)

**Slug:** `deepseekmoe`
**类别：** ffn / moe
**一句话概括：** 一种 MoE 变体——使用大量细粒度专家加少量始终激活的"共享专家"，在不牺牲共有知识覆盖的前提下提升专家的专业化程度。
**首次提出：** [DeepSeekMoE: Towards Ultimate Expert Specialization in Mixture-of-Experts Language Models (Dai et al., 2024)](https://arxiv.org/abs/2401.06066)

## 概述

相比传统 MoE 设计（如 GShard、Switch Transformer）使用少量大专家，DeepSeekMoE 做了两个结构性改动：

1. **细粒度专家**——更多、更小的专家。每个 token 只激活其中少数（top-K）。这给路由组合留下更多空间，并促使每个专家更窄地专业化。
2. **共享专家**——一组独立的小专家，每个 token 都无条件经过它们。它们承载共有知识，避免被多个路由专家重复存储。

数学上，输出 = 共享专家输出之和 + 路由专家输出加权和。门控值是（归一化后的）路由 affinity——DeepSeek-V3 用 sigmoid，早期工作用 softmax。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2401.06066>
- DeepSeek-V2、DeepSeek-V3 中均有应用。

## 使用此技术的模型

| 模型              | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V3       | 256 路由专家 + 1 共享专家，top-8 路由，单专家中间维度 2048。前 3 层为 dense，剩余 58 层为 MoE。                                                                                                                                                                                                                                                                                                                                                                                |
| Qwen3-235B-A22B   | 采用 **细粒度专家分割**这一半（128 专家 × 1536 宽度，激活 8 个），但 **不采用共享专家**（论文 §2 明确与 Qwen2.5-MoE 和 DeepSeek-V3 做对比）。94 层全部为 MoE。配合 global-batch 负载均衡损失，而非 aux-loss-free routing。                                                                                                                                                                                                                                                     |
| Qwen3.5-35B-A3B   | 在 Qwen3 抛弃共享专家之后又把它请回来：**256 个路由 × 512 宽度，top-8** 加 **1 个常驻共享专家**（同样宽度 512）。40 个 FFN 位全部为 MoE。负载均衡进一步退回到 **经典辅助损失**（`router_aux_loss_coef=0.001`），放弃了 Qwen3 的 global-batch LB 与 DeepSeek-V3 的 aux-loss-free routing。和 DeepSeek-V3 一样的"细粒度专家 + 共享专家"模板，但单专家宽度小得多（512 vs DeepSeek-V3 的 2048），骨干换成了混合 Gated DeltaNet + Gated Attention。厂商资料里没有解释这次设计回退。 |
| Qwen3.6-35B-A3B   | MoE 拓扑与 Qwen3.5-35B-A3B 完全相同——同样的 256 路由 × 512 + 1 共享 × 512，同样的 `router_aux_loss_coef=0.001`。这次纯后训练刷新沿用 Qwen3.5 的负载均衡回退。                                                                                                                                                                                                                                                                                                                  |
| DeepSeek-V4-Pro   | **384 路由 × 1 共享，top-6**，单专家中间维度 3072。61 层全部 MoE（无 dense 前缀）；前 3 个 MoE 层用确定性 **Hash routing**（`config.num_hash_layers=3`）——按 token-ID 哈希决定目标专家。路由 affinity 由 V3 的 Sigmoid 改为 **SqrtSoftplus(·)**。**移除了 V3 的 node-limited routing 约束**。Routed-scaling 因子 2.5。专家权重在后训练 QAT 后存为 FP4。                                                                                                                        |
| DeepSeek-V4-Flash | **256 路由 × 1 共享，top-6**，单专家中间维度 2048。43 层全部 MoE；前 3 层 Hash routing 配方与 V4-Pro 相同。SqrtSoftplus affinity、移除 node-limited、FP4 专家量化均与 V4-Pro 一致。Routed-scaling 因子 1.5（vs Pro 的 2.5）。                                                                                                                                                                                                                                                  |

## 相关技术

- [Auxiliary-loss-free routing](./aux-loss-free-routing.md) — DeepSeek-V3 在 DeepSeekMoE 之上采用的负载均衡策略
- [Global-batch load balancing](./global-batch-load-balancing.md) — Qwen3 在细粒度 MoE 之上采用的负载均衡策略
