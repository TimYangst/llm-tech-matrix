# Multi-head Latent Attention (MLA)

> English: [mla.md](./mla.md)

**Slug:** `mla`
**类别：** attention
**一句话概括：** 把注意力的 K/V 联合低秩压缩成一个小的 latent 向量，在保持接近 MHA 质量的同时显著缩小 KV cache。
**首次提出：** [DeepSeek-V2: A Strong, Economical, and Efficient Mixture-of-Experts Language Model (DeepSeek-AI, 2024)](https://arxiv.org/abs/2405.04434)

## 概述

MLA 用一个共享的下投影把每个 token 的 K/V 压成一个低维 latent 向量 `c_t^{KV}`（维度 `kv_lora_rank`，通常远小于 `num_heads × head_dim`）。推理时只缓存这一个 latent 向量，外加一个携带 RoPE 的小 key 向量——所以每个 token 的 KV cache 占用只是 `kv_lora_rank` 的一个小倍数，不再随头数线性增长。

为了保留位置信息，MLA 把每个头的 K/Q 维度切成两段：一段是非位置部分（`qk_nope_head_dim`），由 latent 上投影还原；另一段较小（`qk_rope_head_dim`），单独承载 RoPE。Query 也被低秩压缩（通过 `q_lora_rank`）以减少训练时的激活内存。Value 的 head dim（`v_head_dim`）独立于 KV cache 大小。

净效果：在质量相当的前提下，KV cache 比标准 MHA 缩小一个数量级——这正是让超大模型的长上下文推理在经济上做得起的关键。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2405.04434>
- DeepSeek-V3 中沿用并精化：<https://arxiv.org/abs/2412.19437>

## 使用此技术的模型

| 模型        | 变体 / 细节                                                                                                       |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3 | `kv_lora_rank=512`，`q_lora_rank=1536`，`qk_nope_head_dim=128`，`qk_rope_head_dim=64`，`v_head_dim=128`，128 个头 |

## 相关技术

- [GQA (Grouped-Query Attention)](./gqa.md) — _占位；KV cache 缩减的前驱方法_
- [YaRN RoPE scaling](./yarn-rope.md) — DeepSeek-V3 把 YaRN 仅施加在 MLA 中解耦出的 RoPE key 上
