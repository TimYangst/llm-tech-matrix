# Fill-in-Middle (FIM)

> English: [fim.md](./fim.md)

**Slug:** `fim`
**类别：** training-objective
**一句话概括：** 一种预训练数据增强——把一部分文档随机改写成"给定前缀和后缀，预测中间"的形式，让自回归 LM 不需架构改动就具备 fill-in-the-blank 能力。
**首次提出：** [Efficient Training of Language Models to Fill in the Middle (Bavarian et al., OpenAI, 2022)](https://arxiv.org/abs/2207.14255)

## 概述

把一部分训练文档改写后，自回归目标在被包装的前缀和后缀给定下预测中间一段。两种标准格式：

- **PSM (Prefix-Suffix-Middle)：** `<fim_begin> prefix <fim_hole> suffix <fim_end> middle <eos>`
- **SPM (Suffix-Prefix-Middle)：** 顺序互换，有时在工具链中更受欢迎。

原论文表明，在代码数据上以 ~50% 的比例加入 FIM，可以在不损害 next-token-prediction 质量的前提下整合进预训练。后续工作（如 DeepSeekCoder-V2、DeepSeek-V3）以更低比例（~10%）在数据 packing 阶段做文档级 FIM。

这个能力对代码编辑器很重要——"补全这段区域"比"从光标继续"是更常见的操作。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2207.14255>
- DeepSeek-V3 应用：<https://arxiv.org/abs/2412.19437>（§4.1）

## 使用此技术的模型

| 模型        | 变体 / 细节                                                                  |
| ----------- | ---------------------------------------------------------------------------- |
| DeepSeek-V3 | PSM 格式，比例 0.1，预 packing 阶段在文档级别施加（不做跨样本注意力 mask）。 |

## 相关技术

- _（本仓库暂无）_
