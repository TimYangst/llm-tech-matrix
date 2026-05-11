# QK-Norm

> English: [qk-norm.md](./qk-norm.md)

**Slug:** `qk-norm`
**类别：** attention
**一句话概括：** 在注意力点积之前对 query 和 key 投影做归一化（通常是 RMSNorm 或 LayerNorm），用以约束 attention logit 量级、稳定训练。
**首次提出：** [Scaling Vision Transformers to 22 Billion Parameters (Dehghani et al., 2023)](https://arxiv.org/abs/2302.05442)

## 概述

在标准注意力中，原始 query 和 key 投影在训练过程中可能涨到很大的量级，使 attention logit 进入 softmax 饱和区，梯度因此塌缩。QK-Norm 在 Q 和 K 上各插一个 norm 算子（按头施加，发生在算 `Q · K^T / √d` 之前），结构上保证 logit 量级有界。代价很小——每个注意力多一个 norm——却消除了一类训练不稳定性，省去了 attention scaling、embedding clipping、Q/KV bias 这些原本要靠的补救。

最初在 ViT-22B 上提出，QK-Norm 被 LLM 训练者逐步采纳为大规模训练的"无悔"稳定剂。Qwen3 明确把它当作 Qwen2 中 QKV-bias 的替代。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2302.05442>

## 使用此技术的模型

| 模型              | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3-32B         | 注意力块内使用 RMSNorm 风格的 QK-Norm。替代 Qwen2 中的 QKV-bias（config 设 `attention_bias=false`）。Qwen3 论文明确把它作为更深 / 更大 Qwen3 架构的稳定性必备。                                                                                                                                                                                                                                                                                                                                                                                      |
| Qwen3-235B-A22B   | 与 Qwen3 其余模型一致（dense 和 MoE 共享 QK-Norm + 无 QKV-bias 的设计）。                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| DeepSeek-V4-Pro   | 在 core attention 之前对每个 query head 和单一共享 KV head 做 RMSNorm（论文 §2.3.3）。明确说明其作用是替代 QK-Clip。                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| DeepSeek-V4-Flash | 与 V4-Pro 相同的逐头 Q/KV RMSNorm 配方。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| GLM-4.7           | 每个注意力块都用 RMSNorm 风格的 QK-Norm（`config.use_qk_norm=true`）。GLM-4.5 ARC paper §2.1："We also incorporate QK-Norm to stabilize the range of attention logits."。论文 Table 1 对比的四个模型中（GLM-4.5、GLM-4.5-Air、DeepSeek-V3、Kimi K2），只有 GLM-4.5 标 QK-Norm=Yes——其他三个用别的稳定性技巧（DSV3：未公开；K2：MuonClip QK-Clip）。注意 GLM-4.7 同时用 QK-Norm *和* `attention_bias=true`，与 Qwen3 不同（Qwen3 只用 QK-Norm，无 QKV bias）。GLM-5 之后丢掉了 QK-Norm，因为 Muon Split 已经能稳定 logit（见 [Muon](./muon.zh.md)）。 |

## 相关技术

- [GQA](./gqa.md) — 与 QK-Norm 正交：GQA 决定 KV cache 形状，QK-Norm 修正 logit 量级
