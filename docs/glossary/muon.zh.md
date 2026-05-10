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

| 模型              | 变体 / 细节                                                                                                                                                                                                                                                                 |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Pro   | 主体参数走 Muon；embedding、预测头、RMSNorm 权重以及 mHC 的静态偏置 + gating 走 AdamW。Muon momentum=0.95，weight_decay=0.1，更新 RMS rescale 到 0.18。混合 Newton-Schulz：8 步 (3.4445, -4.7750, 2.0315) + 2 步 (2, -1.5, 0.5)。注意力侧已用 Q/KV RMSNorm 故无需 QK-Clip。 |
| DeepSeek-V4-Flash | Muon 配置与 V4-Pro 完全相同（只有 LR 调度不同：峰值 2.7e-4 vs Pro 的 2.0e-4）。                                                                                                                                                                                             |

## 相关技术

- [QK-Norm](./qk-norm.zh.md) — V4 用逐头 Q/KV RMSNorm 替代了 Muon 训练里防注意力 logit 爆炸的 QK-Clip。
