# Global-batch load balancing loss（全局 batch 负载均衡损失）

> English: [global-batch-load-balancing.md](./global-batch-load-balancing.md)

**Slug:** `global-batch-load-balancing`
**类别：** ffn / moe
**一句话概括：** 在整个 global batch（所有 DP rank 上的所有序列）上计算的 MoE 负载均衡辅助损失，而不是按序列或按 micro-batch——既鼓励更丰富的专家专业化，又不强迫每个短序列都用上所有专家。
**首次提出：** [Demons in the Detail: On Implementing Load Balancing Loss for Training Specialized Mixture-of-Experts Models (Qiu et al., 2025)](https://arxiv.org/abs/2501.11873)

## 概述

标准辅助负载均衡损失（Switch Transformer、GShard）是 **在每个序列内**（或每个 micro-batch 内）计算的。这太激进了：一个 200 token 的对话片段被强制均匀分布到所有专家，专业化无从谈起，多专家的价值被稀释。Global-batch 形式累积 global batch 内所有序列的路由统计（通过对路由计数做 all-reduce 跨所有 DP rank），再计算不平衡惩罚。

效果：单个序列可以自由专业化（路由到一小撮相关专家），损失只惩罚远更宽分布上的系统性不平衡。实验上这把训练后的模型推向更尖锐的专家专业化，且推理时观察不到负载不均衡的代价。

它结构上仍是辅助损失（梯度流入 router），与 **auxiliary-loss-free routing**（DeepSeek-V3）形成对比——后者用一个不带梯度的逐专家偏置做均衡。两者是同一个问题的两套答案，目前 MoE 均衡的两大学派。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2501.11873>

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                                     |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3-235B-A22B | HF config 中 `router_aux_loss_coef=0.001`。128 专家 / 8 激活，无共享专家；论文 §2 中均衡是文档中唯一记录的路由均衡信号。配合 DeepSeekMoE 风格的细粒度专家分割。 |

## 相关技术

- [Auxiliary-loss-free routing](./aux-loss-free-routing.md) — 另一种均衡策略（DeepSeek-V3）：用不带梯度的逐专家偏置代替辅助损失
- [DeepSeekMoE](./deepseekmoe.md) — 正交的架构选择（细粒度专家 + 可选共享专家），Qwen3 部分采用（细粒度 yes，共享专家 no）
