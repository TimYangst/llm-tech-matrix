# Group Relative Policy Optimization (GRPO)

> English: [grpo.md](./grpo.md)

**Slug:** `grpo`
**类别：** alignment
**一句话概括：** PPO 家族的一种 RL 算法——去掉独立的 value/critic 网络，改用对每个 prompt 采样一组 completion 并以它们的组内相对 reward 作为 advantage 的基线。
**首次提出：** [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (Shao et al., DeepSeek-AI, 2024)](https://arxiv.org/abs/2402.03300)

## 概述

标准 PPO 要训练一个与策略大致同等规模的 critic，由它给出每 token 的 value 估计来算 advantage。对超大策略模型来说，critic 让 RL 服务成本翻倍。GRPO 把 critic 砍了。

对每个 prompt，GRPO 从旧策略采样 `G` 个 completion，用 reward model 打分，取组均值作为基线。第 `i` 个 completion 的 advantage 是 `(reward_i − group_mean) / group_std`（组内归一化）。然后照常优化 PPO 的 clipped surrogate 目标，并对参考模型加一个 KL 惩罚。

直觉是：你本来就要为每个 prompt 采样多个 completion，组内相对 reward 顺手就提供了一个低方差的基线，critic 是冗余的。

## 参考资料

- 原始论文（DeepSeekMath）：<https://arxiv.org/abs/2402.03300>
- DeepSeek-V3 应用：<https://arxiv.org/abs/2412.19437>（§5.2.2）
- DeepSeek-R1 应用：<https://arxiv.org/abs/2501.12948>

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                                                                                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3     | Reward 信号混合规则型 RM（数学最终答案校验、代码 / LeetCode 编译器测试）和模型型 RM（基于 V3 SFT checkpoints 训练，输出 chain-of-thought reward 以缓解 reward hacking）。                                                                                                             |
| Qwen3-32B       | 用在 **Reasoning RL** 阶段，3,995 条筛选过的 query-verifier 对（未用于 cold-start、可学、有挑战、子领域多样）。大 batch + 多 rollout + off-policy 训练；熵被引导稳定增长以平衡 exploration / exploitation。报告例子：235B-A22B 的 AIME'24 在 170 步内从 70.1 → 85.1，没有人工调超参。 |
| Qwen3-235B-A22B | 与 Qwen3-32B 的 Reasoning RL 食谱相同（四阶段 pipeline 在两个旗舰间共享）。报告中 AIME'24 在 170 个 RL step 内 70.1 → 85.1 的跃迁就是这个模型上的。                                                                                                                                   |

## 相关技术

- _PPO、DPO_ — 相关但不同的对齐阶段算法（待补条目占位）
