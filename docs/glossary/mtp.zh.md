# Multi-Token Prediction (MTP)

> English: [mtp.md](./mtp.md)

**Slug:** `mtp`
**类别：** training-objective
**一句话概括：** 一种预训练目标——通过若干个浅层附加模块同时预测下 D 个 token（不仅是下一个），在密化训练信号的同时（可选地）为推理提供 speculative decoding 的草稿头。
**首次提出：** [Better & Faster Large Language Models via Multi-token Prediction (Gloeckle et al., 2024)](https://arxiv.org/abs/2404.19737)

## 概述

标准自回归预训练中，每个 token 只贡献一次 next-token 预测损失。MTP 在主模型上挂 `D` 个额外的小头（每个对应未来位置偏移 1..D），把它们的交叉熵损失加权 λ 累入主损失。每 token 训练信号大致变成原来的 `1 + D · λ`，常常带来等算力下的指标提升。

不同变体在头的拓扑上有差异：

- **并行型（Gloeckle et al.）**——`D` 个独立头一次性预测位置 2..D+1。
- **串行型（DeepSeek-V3）**——头链式连接，第 `k` 个头基于第 `k-1` 个头的表示进行预测，保留因果链。实现上复用主模型的 embedding 和输出头以最小化参数开销。

推理时，MTP 模块可以丢弃（恢复基础模型），也可以转作 speculative decoding 的草稿头。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2404.19737>
- DeepSeek-V3 实现细节与消融：<https://arxiv.org/abs/2412.19437>（§2.2，Table 4）

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                           |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3     | 串行型，D=1（一个额外预测深度）。Embedding + 输出头与主模型共享。损失权重 λ=0.3 用于前 10T tokens，之后 0.1 用于剩余 4.8T。MTP 模块在推理时丢弃（或转作 speculative decoding 用）。                                                                                                                                                                                                                   |
| Qwen3.5-27B     | HF model card 称 "trained with multi-steps"；具体步深 D 未披露。Config 暴露 `mtp_num_hidden_layers=1`（头深度）和 `mtp_use_dedicated_embeddings=false`（与主模型共享 input embedding）。服务侧把这个头用作 **speculative decoding**：vLLM `qwen3_next_mtp` 配 `num_speculative_tokens=2`；sglang NEXTN 配 `speculative-num-steps=3`、`speculative-num-draft-tokens=4`。提示有效推理草稿深度至少 2-4。 |
| Qwen3.5-35B-A3B | MTP 设置与 27B 兄弟相同：`mtp_num_hidden_layers=1`、`mtp_use_dedicated_embeddings=false`、README 称 "trained with multi-steps"。同样的 vLLM/sglang speculative decoding 食谱适用。MoE FFN 不影响 MTP 拓扑——头位于共享骨干之上。                                                                                                                                                                       |
| Qwen3.6-27B     | MTP 设置与 Qwen3.5-27B 完全相同——`mtp_num_hidden_layers=1`、`mtp_use_dedicated_embeddings=false`、README 称 "trained with multi-steps"，同样的 speculative decoding 服务食谱。3.6 没有披露任何 MTP 相关变更。                                                                                                                                                                                         |
| Qwen3.6-35B-A3B | MTP 设置与 Qwen3.5-35B-A3B 完全相同——同样的头深度、embedding 共享、multi-step 训练声明、服务食谱。整个 Qwen3.5/3.6 家族在 MTP 拓扑上完全收敛。                                                                                                                                                                                                                                                        |

## 相关技术

- _Speculative decoding（EAGLE、Medusa）_ — 一种相关但不同的 multi-future-token 头用法，目标是推理加速而非训练信号密化
