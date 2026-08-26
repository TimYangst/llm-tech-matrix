# Qwen 稀疏注意力（QSA）

> English: [qsa.md](./qsa.md)

**Slug:** `qsa`
**类别：** attention
**一句话概括：** 一种源自 DSA 的稀疏注意力，在*微块（micro-block）*粒度上用压缩过的轻量 indexer 打分，使得 indexer 自身的开销随序列变长而下降，而不是二次增长。

**首次提出：** [On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability（Qwen Team, 2026）](https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf) §2.1.2

## 概述

[DSA](./dsa.zh.md) 让稀疏注意力变得可以「后装」：训练一个轻量 indexer 去模仿模型自己的注意力分布，然后只对 indexer 选出的 top-k token 做注意力。QSA 保留了这个结构，并解决了 DSA 留下的问题——**indexer 本身是 O(n²) 的**，上下文越长，这条打分路径就越会变成它本来要消除的那个瓶颈。

QSA 的做法是给*压缩后的块*打分，而不是给 token 打分。key 被切成 `r` 个 token 一组的非重叠微块，平均池化成每块一个代表 key——关键在于这一步发生在**位置编码之前**，因此每个块先被总结为内容表示，再被赋予一个块级位置，而不是把处在不同旋转相位上的表示直接平均。随后一个 MQA indexer（H 个 query 头、1 个共享 key 头）在块因果掩码下用 `I_ib = Σ_h ReLU(⟨q_i^h, k̄_b⟩)` 给每个块打分，每个 query 取 top `⌈K/r⌉` 个块。选中的块展开回 token 下标、截断到 token 预算 `K`，再并上最后一个不完整块里始终包含的尾部 token。先按 `r` 压缩再打分，把索引开销从 `O(n²)` 降到 `O(n²/r)`。

训练是在继续预训练阶段做的两段式后装，形态承袭自 DSA：**稠密蒸馏**只训练 indexer，用 KL 对齐骨干自身的注意力分布（对齐到块粒度时用 max-pool 而非 mean-pool，以免稀释显著的 token 级信号）；随后**稀疏训练**在 indexer 的选择下解冻骨干，KL 损失只在选中的块上计算。

效果不只是「不掉点」。带 QSA 的 Qwen3.8-Flash-Next 在 8 个短上下文基准里有 7 个持平或超过全注意力基线，而且上下文越长优势越大——RULER 在 512K 以上从 90.08 → 93.00，8-needle MRCR 在 512K 从 30.66 → 40.53。报告认为长上下文上的增益来自 indexer 起到了学习出来的检索先验的作用，而不是一个有损近似。

还有一个专属于混合架构的设计点：QSA 是在*层内*做压缩，而主要的替代方案（IndexShare）是在相邻的全注意力层*之间*共享索引。在 3:1 的 GDN 混合结构里，这些层之间隔着三层线性注意力，层间相似度很低——报告实测 QSA 在相对 indexer 延迟 0.25 时即可持平 RULER 基线，而 IndexShare 在 0.5 时仍低于基线。

## 参考资料

- 原始论文：<https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf>（§2.1.2）
- 前身机制：[DSA](./dsa.zh.md)（DeepSeek-V3.2-Exp）
- 参考实现：报告中描述的融合 QSA kernel；配套的线性注意力库在 <https://github.com/QwenLM/FlashQLA>

## 使用此技术的模型

| 模型 | 变体 / 细节 |
| ---- | ----------- |
| Qwen3.8-Flash-Next | 微块大小 `r=4`，token 预算 `K=2048`（512 块），indexer 为 MQA 结构、4 个 query 头 + 1 个共享 key 头、head_dim 128，对 indexer 的 128 维中的 64 维施加 partial RoPE，刻意与核心注意力的旋转维度对齐。应用于**所有**全注意力层——骨干 48 层里的 12 层，外加 MTP 模块的注意力层。在 CPT 阶段以 256K 序列长度后装：先 1,000 步只训 indexer（约 2B token，lr 1e-3），再 8,000 步联合训练（约 200B token，lr 2.5e-5）。1M 上下文下的 kernel 级加速：**prefill 7.6×，decode 4.9×**。 |

## 相关技术

- [DeepSeek 稀疏注意力（DSA）](./dsa.zh.md) —— 直系前身；QSA 的贡献是压缩 indexer 自身的输入。
- [CSA + HCA](./csa-hca.zh.md) —— DeepSeek-V4 对 DSA 的后继方案，走的是压缩 KV 条目本身的路线。
- [Gated DeltaNet](./gated-deltanet.zh.md) —— 与 QSA 交错排布的线性注意力层，也是这里「层内压缩优于跨层索引共享」的原因。
