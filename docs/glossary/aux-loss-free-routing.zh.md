# Auxiliary-loss-free routing（无辅助损失路由）

> English: [aux-loss-free-routing.md](./aux-loss-free-routing.md)

**Slug:** `aux-loss-free-routing`
**类别：** ffn / moe
**一句话概括：** 用每个专家的可学习偏置项（按观测到的专家利用率在线调整）来平衡 MoE 专家负载，替代传统的辅助负载均衡损失，避免后者把对抗主目标的梯度信号注入训练过程。
**首次提出：** [Auxiliary-Loss-Free Load Balancing Strategy for Mixture-of-Experts (Wang et al., 2024)](https://arxiv.org/abs/2408.15664)

## 概述

标准 MoE 训练会加一个辅助损失（如 Switch Transformer / GShard 中的 "load balancing loss"），鼓励 token 在专家间均匀分布。但这个损失会产生对抗主任务的梯度——太强了模型质量下降，太弱了路由会塌缩。

无辅助损失路由保留一个小的逐专家偏置 `b_i`。Top-K 路由选择用 `(affinity + bias)` 作判据，但门控值（与 FFN 输出相乘的那个）用 *原始* affinity。每个训练步之后，偏置在主反向传播 *之外* 被微调：欠载的专家 `b_i` 增加，过载的减小。因为偏置从不进入梯度看到的损失曲面，它们就不会与模型质量竞争。

DeepSeek-V3 通常还配一个非常小的序列内辅助损失（α = 0.0001），仅用于防止单序列内的极端不平衡，但主导的均衡信号是偏置调整。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2408.15664>
- DeepSeek-V3 论文 Table 5 的消融，证明了相对辅助损失基线的提升。

## 使用此技术的模型

| 模型              | 变体 / 细节                                                                                                                                                                                                                                                                        |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3       | 偏置更新速率 γ=0.001 用于前 14.3T tokens，0 用于最后 500B；配合序列内均衡损失 α=0.0001；node-limited routing（M=4 节点，8 个专家组）。                                                                                                                                             |
| DeepSeek-V4-Pro   | 与 V3 相同的 noaux_tc 策略，但 affinity 评分由 Sigmoid(·) 改为 SqrtSoftplus(·)（config.scoring_func="sqrtsoftplus"）。偏置更新速率 0.001；序列均衡损失权重 0.0001。**移除了 V3 的 node-limited routing 约束**。前 3 个 MoE 层改用确定性 Hash routing（config.num_hash_layers=3）。 |
| DeepSeek-V4-Flash | noaux_tc + SqrtSoftplus + 前 3 层 Hash routing 配方与 V4-Pro 完全相同。仅规模不同（256 个可路由专家 × top-6 + 1 个共享）以及 routed-scaling 因子（1.5 vs Pro 的 2.5）。                                                                                                            |

## 相关技术

- [DeepSeekMoE](./deepseekmoe.md)
- [Global-batch load balancing](./global-batch-load-balancing.md) — Qwen3 的另一种均衡方式（仍是带梯度的辅助损失，但在全局 batch 上计算，而非每序列）
