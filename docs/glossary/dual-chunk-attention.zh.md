# Dual Chunk Attention (DCA)

> English: [dual-chunk-attention.md](./dual-chunk-attention.md)

**Slug:** `dual-chunk-attention`
**类别：** position-embedding
**一句话概括：** 一种免训练的长上下文扩展方法——通过在固定大小的 chunk 内 / chunk 间重新映射位置索引，让训练长度为 T 的模型在不重训的情况下处理 kT 长度的序列；通常与 YaRN 这类频率缩放方法配合使用。
**首次提出：** [Training-Free Long-Context Scaling of Large Language Models (An et al., 2024)](https://arxiv.org/abs/2402.17463)

## 概述

朴素的 RoPE 上下文扩展在极长序列上失效，因为位置索引远超 rotary embedding 训练时见过的范围。DCA 注意到 chunk *内* 与 *跨 chunk* 的相对位置可以重映射到模型实际见过的索引范围，让模型在任何位置都拿到有意义的位置信号，无需任何微调。

具体做法：把序列切成大小为 W（接近训练上下文长度）的 chunk，使用三种位置索引——chunk 内位置（intra-chunk）、跨 chunk 位置（inter-chunk），以及处理当前 chunk 与最近 past 边界的 successor 索引。每种索引都映射到模型见过的子区间，注意力得分始终保持在分布内。

生产中 DCA 通常与 YaRN 配对：YaRN 处理频段插值，DCA 处理原始位置重映射。两者合在一起，无需额外训练就能在乘性扩展（如 4×）下接近训练时的质量。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2402.17463>

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                            |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Qwen3-32B       | DCA + YaRN 在部署期把训练时的 32K 上下文提升到 128K（4× 扩展）。在推理时应用（vLLM/SGLang config），不烘焙进 HF `config.json`（`rope_scaling=null`）。 |
| Qwen3-235B-A22B | 与 Qwen3 家族中 1.7B 之上其余模型同样的 DCA + YaRN 部署食谱。                                                                                          |

## 相关技术

- [YaRN RoPE scaling](./yarn-rope.md) — DCA 通常与 YaRN 叠加以完整恢复长上下文质量
