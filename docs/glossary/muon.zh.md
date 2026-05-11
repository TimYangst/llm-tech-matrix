# Muon 优化器

> English: [muon.md](./muon.md)

**Slug:** `muon`
**类别：** optimizer
**一句话概括：** 对融合动量后的梯度做"按矩阵"的 Newton-Schulz 正交化更新——把 Adam/AdamW 的逐元素二阶矩量替换成"白化奇异值"的矩阵感知更新；在万亿参数 transformer 上收敛更快、稳定性更好。
**首次提出：** [Muon (Jordan et al., 2024)](https://kellerjordan.github.io/posts/muon/)；大规模训练配方见 [Liu et al., 2025](https://arxiv.org/abs/2502.16982)。

## 概述

对每个逻辑独立的权重矩阵 `W ∈ R^(n×m)`：

1. 累积动量 `M_t = μ·M_{t-1} + G_t`（Nesterov trick：实际喂入 `μ·M_t + G_t`）。
2. 用 Newton-Schulz 迭代正交化得到 `O' = NS(μ·M_t + G_t)`——逼近 SVD `M = U·Σ·V^T` 中的 `U·V^T`。所有奇异值被推向 1。
3. 重缩放 `O = O' · √max(n,m) · γ`，让更新 RMS 达到固定目标值（这样可直接复用 AdamW 的学习率）。
4. 应用 weight decay + 更新：`W_t = W_{t-1} · (1 - η·λ) - η·O`。

不同于跟踪逐元素二阶矩量的 Adam/AdamW，Muon 尊重权重的矩阵结构——当同一行 / 列中的元素紧耦合时，逐元素学习率自适应未必合适。Newton-Schulz 正交化只用矩阵乘（BF16 即可稳定）、5-10 次迭代就收敛，避免显式 SVD。

DeepSeek-V4 采用**混合 Newton-Schulz** 调度：前 8 步用 `(a,b,c)=(3.4445, -4.7750, 2.0315)` 让奇异值快速收敛，后 2 步切换到 `(2, -1.5, 0.5)` 把奇异值精确稳定在 1。Embedding、预测头、RMSNorm 权重以及 mHC 的静态参数仍走 AdamW。由于注意力路径上加了逐头 Q/KV RMSNorm，V4 不再需要早期 Muon 训练（Liu et al., 2025）用来防注意力 logit 爆炸的 QK-Clip。

与 Zero Redundancy Optimizer (ZeRO) 的结合较复杂：Muon 需要完整梯度矩阵来算正交更新，这与 ZeRO 给逐元素优化器分片矩阵的设计冲突。DeepSeek-V4 用混合分桶策略：dense 参数用 knapsack 分配 + 并行度上限；MoE 参数把所有专家的下投影 / 上投影 / 门控展平后无上限分发；MoE 梯度用 BF16 + 随机舍入同步以减半带宽。

## 参考资料

- 原始 Muon 博客：<https://kellerjordan.github.io/posts/muon/>
- Muon 大规模训练（Liu et al., 2025）：<https://arxiv.org/abs/2502.16982>
- DeepSeek-V4 技术报告第 2.4 节（算法）+ 3.4.1 节（ZeRO 集成）。

## 使用此技术的模型

| 模型                                    | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V4-Pro                         | 主体参数走 Muon；embedding、预测头、RMSNorm 权重以及 mHC 的静态偏置 + gating 走 AdamW。Muon momentum=0.95，weight_decay=0.1，更新 RMS rescale 到 0.18。混合 Newton-Schulz：8 步 (3.4445, -4.7750, 2.0315) + 2 步 (2, -1.5, 0.5)。注意力侧已用 Q/KV RMSNorm 故无需 QK-Clip。                                                                                                                                                                                                                                                                                                                                                                                                                            |
| DeepSeek-V4-Flash                       | Muon 配置与 V4-Pro 完全相同（只有 LR 调度不同：峰值 2.7e-4 vs Pro 的 2.0e-4）。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| Kimi K2 家族（K2-Thinking、K2.5、K2.6） | 使用 **MuonClip** = Muon + **QK-Clip**（用于稳定训练）——同时贯穿 K2 基础预训练、K2.5 联合预训练、以及 RL 后训练（K2.5 论文 §4.1、§4.4.2）。与 DeepSeek-V4 形成对比：V4 在注意力路径加了逐头 Q/KV RMSNorm（见 [QK-Norm](./qk-norm.zh.md)）所以丢掉了 QK-Clip；K2 家族沿用 QK-Clip，因为 K2 的 MLA 注意力没有 Q/KV RMSNorm。具体 (a,b,c) 系数、动量、weight decay 未在 K2.5 论文中重述（推迟到尚未发表的 K2 技术报告）。                                                                                                                                                                                                                                                                                 |
| GLM-4.7                                 | Muon 应用于除 word embedding、bias、RMSNorm 权重以外的所有参数（GLM-4.5 ARC paper §2.4）。Newton-Schulz 迭代步数 N=5，momentum µ=0.95，更新 RMS rescale 到 0.2。Cosine LR decay（前期实验发现 WSD schedule 在 SimpleQA / MMLU 上欠拟合）。峰值 LR 2.5e-4，衰减尾 2.5e-5。Batch size warmup 16M → 64M tokens（前 500B tokens）。                                                                                                                                                                                                                                                                                                                                                                        |
| GLM-5 / GLM-5.1                         | 继承 GLM-4.7 的 Muon 配方但加了关键调整：**Muon Split**（论文 §2.1）。原始 Muon 把 up-projection 矩阵 W_UQ / W_UK / W_UV 当单个矩阵做正交化；Muon Split 把它们按 attention head 切开，每个独立做正交化，允许不同 head 以不同尺度更新。这个调整闭合了 MLA-vs-GQA-8 的质量差距（论文 Table 1：MLA-256 + Muon Split 匹配 GQA-8），并去掉了 QK-Clip 的需要——预训练期间 attention logit 自然稳定，无需 clipping，这是 GLM-5 与 Kimi K2 家族（仍用 MuonClip）的关键区别。分布式 Muon 实现使用零冗余通信：每个 rank 只 all-gather 自己的 parameter shard（不广播完整参数）并与本地计算重叠（论文 §2.4.1）。GLM-5.1 是 post-training-only refresh，继承同一 base optimizer，RL 阶段的 optimizer 没有单独说明。 |

## 相关技术

- [QK-Norm](./qk-norm.zh.md) — V4 用逐头 Q/KV RMSNorm 替代了 Muon 训练里防注意力 logit 爆炸的 QK-Clip。
