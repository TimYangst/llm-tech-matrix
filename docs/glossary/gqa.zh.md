# Grouped Query Attention (GQA)

> English: [gqa.md](./gqa.md)

**Slug:** `gqa`
**类别：** attention
**一句话概括：** 多头注意力的一种变体——多个 query 头共享一个 key/value 头，按分组倍数缩小 KV cache，同时保留接近完整 MHA 的建模质量。
**首次提出：** [GQA: Training Generalized Multi-Query Transformer Models from Multi-Head Checkpoints (Ainslie et al., 2023)](https://arxiv.org/abs/2305.13245)

## 概述

在标准多头注意力（MHA）中，每个 query 头都有自己独立的 K 和 V 头，所以 KV cache 体积是 `2 × num_heads × head_dim × seq_len × batch`。Multi-Query Attention（MQA）走另一极端——所有头共享一对 K/V，cache 很小但质量明显下滑。GQA 是中间路线：把 query 头分成 G 组，每组共享一对 K/V 头，于是 `num_kv_heads = num_heads / group_size`。

两个实战收益：

- **KV cache 缩减**：随 `num_heads / num_kv_heads` 线性下降。这是长上下文服务的关键——推理时 KV cache 通常才是显存瓶颈，而不是权重。
- **升级路径**：原论文证明可以从已有 MHA checkpoint 通过对每组 KV 头做均值池化、再短期微调，转换成 GQA，无需从头重训。

GQA 已成为 ~7B 以上几乎所有开源 dense LLM 的默认注意力形态（Llama 2/3、Mistral、Qwen2.5/3 等）。MLA（DeepSeek）走得更远——把 K/V 进一步压缩到低秩 latent，是另一条权衡路径。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2305.13245>

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                            |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3-32B       | 64 个 query 头，8 个 KV 头（group size 8），`head_dim=128`。配合注意力块内的 **QK-Norm**；移除 QKV-bias（config 设 `attention_bias=false`）。所有 Qwen3 dense 模型不论规模都用 8 个 KV 头；MoE 模型用 4 个。                                                                                                                                                                           |
| Qwen3-235B-A22B | 64 个 query 头，**4 个 KV 头**（group size 16，比 dense 的 32B 激进一倍），`head_dim=128`。与 Qwen3 其余模型一致：QK-Norm + 无 QKV-bias。这种规模下 KV cache 的服务压力占主导，所以分组更大合理。                                                                                                                                                                                      |
| Qwen3.5-27B     | **仅在 1/4 的层里使用**（混合骨干中的 "Gated Attention" 槽）。24 个 query 头，4 个 KV 头，`head_dim=256`（是 Qwen3 head_dim 的两倍）。加了输出门控（config `attn_output_gate=true`）和 **partial RoPE**——256 维头中只有 64 维做 rotary（`partial_rotary_factor=0.25`）。其余 3/4 的层是 Gated DeltaNet（线性注意力），所以 KV cache 压力集中在 16 个 GQA 层，而非 64 个 dense GQA 层。 |
| Qwen3.5-35B-A3B | Gated Attention 形状与 27B 同款但更窄：**16 个 query 头，2 个 KV 头**（group size 8，比 27B 的 24:4 又激进一倍），`head_dim=256`。40 层中用了 10 层（每 4 层 1 层）。同样的输出门控 + partial RoPE 0.25。KV cache 占用极小：仅 10 个 GQA 层 × 2 个 KV 头 × 256 head_dim。                                                                                                              |
| Qwen3.6-27B     | 与 Qwen3.5-27B 完全相同——24Q、4KV、head_dim 256、输出门控、partial RoPE 0.25、64 层中 16 层。仅是后训练刷新，注意力形状未变。                                                                                                                                                                                                                                                          |
| Qwen3.6-35B-A3B | 与 Qwen3.5-35B-A3B 完全相同——16Q、2KV、head_dim 256、输出门控、partial RoPE 0.25、40 层中 10 层。仅是后训练刷新。                                                                                                                                                                                                                                                                      |

## 相关技术

- [MLA](./mla.md) — DeepSeek 的另一条路：低秩 KV 压缩，而非分组共享
- [QK-Norm](./qk-norm.md) — Qwen3 在 GQA 之上叠加的正交稳定性手段
