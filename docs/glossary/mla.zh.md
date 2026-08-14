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

| 模型                                    | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3                             | `kv_lora_rank=512`，`q_lora_rank=1536`，`qk_nope_head_dim=128`，`qk_rope_head_dim=64`，`v_head_dim=128`，128 个头                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| Kimi K2 家族（K2-Thinking、K2.5、K2.6） | 三个兄弟 MLA 维度完全一致——`kv_lora_rank=512`，`q_lora_rank=1536`，`qk_nope_head_dim=128`，`qk_rope_head_dim=64`，`v_head_dim=128`，64 个头（DeepSeek-V3 的一半）。HF config 直接复用 `DeepseekV3ForCausalLM` 类作为 K2 的文本骨干，所以 MLA 几何形态除头数外与 V3 一致。                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| GLM-5 / GLM-5.1                         | 首个非 DeepSeek 厂商落地 MLA。维度：`kv_lora_rank=512`，`q_lora_rank=2048`（vs DSV3 的 1536），`qk_nope_head_dim=192`（vs DSV3 的 128），`qk_rope_head_dim=64`，`v_head_dim=256`（vs DSV3 的 128），64 个头。论文 §2.1 解释更宽的 head_dim（256 vs DSV3 的 192 总和）和减半的头数（64 vs DSV3 的 128）是面向非 H800 硬件的 roofline-aware 调整：保持训练 FLOPs 和参数量恒定，同时降低每步 decoding 的 dot product 宽度。**Muon Split** 优化器调整（论文 §2.1，见 [Muon](./muon.zh.md)）是让 MLA 在 Muon 下匹配 GQA-8 质量、并去掉 QK-Clip 的关键——把 W_UQ/W_UK/W_UV 按 head 切开，每个独立做正交化。MLA 与 [DSA (DeepSeek Sparse Attention)](./dsa.zh.md) 组合使用——DSA 决定 core MLA 注意力从压缩后的 KV entry 中读哪些。 |
| Kimi K3                                 | **Gated MLA** —— MLA 只保留在周期性的全局注意力层（93 层中的 24 层，与 KDA 按 3:1 交错），相对 K2/K2.5 有两处改动。(1) **所有 MLA 层用 NoPE**（`mla_use_nope=true`）：交错的 KDA 层提供位置敏感性，MLA 提供不受限的全局内容交互；两者解耦后，扩展上下文时无需再调 RoPE base 或套 YaRN。(2) 依赖输入的逐通道**全秩输出门** `y = W_o[σ(W_g x) ⊙ õ]`（`mla_use_output_gate=true`），与 KDA 的门控参数化一致。潜维与 K2 相同：kv_lora_rank=512、q_lora_rank=1536、qk_nope 128 / qk_rope 64、v_head_dim 128；query 头数 96（K2 为 64）。训练时注意力输出保持 FP32，以修正 flash attention 的有偏舍入误差。                                                                                                                      |
| DeepSeek-V3.2-Exp                       | MLA 配置与 DeepSeek-V3 逐字节相同（kv_lora_rank=512、q_lora_rank=1536、qk_nope 128 / qk_rope 64、v_head_dim 128、128 头、61 层）。变化在于其上叠加了 [DSA](./dsa.zh.md)，这迫使 MLA 全程走 **MQA 模式** —— V3.1-Terminus 训练与 prefill 用 MHA 模式、仅解码用 MQA，而 DSA 出于 kernel 效率要求每个潜 KV 条目被所有 query 头共享。                                                                                                                                                                                                                                                                                                                                                                                          |

## 相关技术

- [GQA (Grouped-Query Attention)](./gqa.md) — _占位；KV cache 缩减的前驱方法_
- [YaRN RoPE scaling](./yarn-rope.md) — DeepSeek-V3 把 YaRN 仅施加在 MLA 中解耦出的 RoPE key 上
