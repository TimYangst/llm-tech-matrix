# Kimi Delta Attention (KDA)

> English: [kda.md](./kda.md)

**Slug:** `kda`
**类别：** attention
**一句话概括：** 在 delta-rule 递推上加了**逐通道**遗忘门的线性注意力层，以 O(L) 成本完成长序列混合，并隐式携带位置信息 —— 因此基于它搭建的模型可以完全不用 RoPE。
**首次提出：** [Kimi Linear（Moonshot AI, 2025）](https://arxiv.org/abs/2510.26692)；在 [Kimi K3 技术报告 §2.1.1（Moonshot AI, 2026）](https://arxiv.org/abs/2607.24653) 中被扩展并首次用到旗舰规模。

## 概述

线性注意力把 softmax 注意力的 O(L²) 分数矩阵换成一个每 token 更新一次的递推状态
`S_t ∈ R^{d_k × d_v}`，从而使开销随序列长度线性增长。其中 *delta rule* 变体以关联记忆的方式写入状态
—— `S_t = (I − β_t k_t k_tᵀ) S_{t−1} + β_t k_t v_tᵀ` —— 使得新 key 能够覆盖此前相似 key 写入的内容。
KDA 在此基础上引入**逐通道保留因子** `α_t ∈ (0,1)^{d_k}`，让每个 key 通道以各自学到的速率遗忘，而不是整个状态统一衰减：

```
S_t = (I − β_t k_t k_tᵀ) · Diag(α_t) · S_{t−1} + β_t k_t v_tᵀ
```

Q/K/V 由 ShortConv 接 Swish 产生，并对 Q、K 做 L2Norm；`β_t = σ(W_β x_t)` 控制写入强度；
衰减 logit 来自一个低秩投影加逐头 bias。整层按 chunk 计算 —— chunk 之间递推、chunk 内部并行。

**Kimi K3 的两项改动**（§2.1.1）都是为了让 chunkwise 形式在 1M token 规模下既快又数值安全：

1. **下界化衰减（lower-bounded decay）。** Kimi Linear 用无界的 negative-Softplus 映射衰减 logit，
   于是 chunk 内用于重新缩放 key 的倒数累积衰减 `1/Γ` 可能溢出。K3 改用
   `g = g_min · σ(e^A z)`，其中 `A` 是可学习的逐头 log 尺度、`g_min = −5` 固定。这样每个保留因子都
   `> e^{−5}`，16-token tile 上的累积 log 衰减落在 `(−80, 0)`，缩放因子始终在 BF16 动态范围内。
   收益不止于稳定性：范围有界之后，对角与非对角 chunk tile *都* 能走稠密 Tensor Core 矩阵乘，
   从而彻底去掉 Kimi Linear 里显式的 position-pair 对角路径 —— 那正是 chunk 内的主要瓶颈。
2. **全秩输出门。** 输出门从低秩参数化改为依赖输入的全秩投影：`y = W_o[σ(W_g x) ⊙ RMSNorm(õ)]`。

从跨模型比较的角度，最值得记的架构后果是：由于 KDA 的衰减递推本身就对位置敏感，
把 KDA 与全局层交错堆叠的模型可以直接跑 **NoPE** —— 不用 RoPE、不用 YaRN、不用插值 —— 依然能外推到 1M token。
Kimi K3 正是这么做的，这也是它 `rope.type` 为 `"none"` 的原因。

## 参考资料

- Kimi Linear 论文：<https://arxiv.org/abs/2510.26692>
- Kimi K3 技术报告 §2.1.1：<https://arxiv.org/abs/2607.24653>
- 参考实现：`flash-linear-attention`（FLA）—— KDA kernel 与 KDA context parallelism 在 FLA PR #691 中上游合入

## 使用此技术的模型

| 模型    | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K3 | 93 层中有 69 层是 KDA，与 Gated MLA 按 3:1 交错（`config.linear_attn_config.kda_layers` / `full_attn_layers`）。96 头、head_dim 128、`short_conv_kernel_size=4`、`gate_lower_bound=-5.0`、`use_full_rank_gate=true`。K3 相对 Kimi Linear 的两项改动都在这里：下界化的 scaled-sigmoid 衰减（消掉 position-pair 对角路径）与全秩输出门。它使整个模型得以采用 NoPE。部署侧需要专门工作 —— 融合 kernel、支撑 1M token 训练的 KDA Context Parallelism，以及 KDA 感知的 prefix cache 管理（K3 论文 §5.1.1 / §5.1.2 / §5.4.1）。 |

## 相关技术

- [Gated DeltaNet](./gated-deltanet.zh.md) —— 最接近的同类。Qwen3.5/3.6 以**相同的** 3:1 比例交错 Gated DeltaNet 与 Gated Attention；两者主要差别在门控参数化，以及混合搭档是否保留 RoPE（Qwen 保留，K3 不保留）。
- [MLA（Multi-head Latent Attention）](./mla.zh.md) —— KDA 在 Kimi K3 中的混合搭档，负责周期性的全局注意力层。
- [Attention Residuals（AttnRes）](./attnres.zh.md) —— 同一模型中对应"深度轴"的机制。
