# Compressed Sparse Attention (CSA) + Heavily Compressed Attention (HCA)

> English: [csa-hca.md](./csa-hca.md)

**Slug:** `csa-hca`
**类别：** attention
**一句话概括：** 混合注意力设计，交错使用两种 KV 压缩变体——CSA 把 `m` 个 token 聚合成一个 entry 后再用 DeepSeek Sparse Attention 做 top-k；HCA 把 `m' >> m` 个 token 聚合成一个 entry 后做 dense 注意力——在 1M 上下文下把 KV cache 降至 DeepSeek-V3.2 的 ~10%、单 token FLOPs 降至 ~27%。
**首次提出：** [DeepSeek-V4 技术报告 (DeepSeek-AI, 2026)](https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/resolve/main/DeepSeek_V4.pdf) 第 2.3 节。在 DeepSeek-V3.2 的 DSA（DeepSeek Sparse Attention）基础上演化而来。

## 概述

百万 token 上下文下注意力是计算瓶颈，DeepSeek-V4 用两种互补的 KV 压缩方案在不同层交错处理。

**Compressed Sparse Attention (CSA)：**

1. **Token 级压缩。** 每 `m=4` 个相邻 token 通过两个交错的 softmax 加权压缩器（重叠窗口，`2m` 个原始 entry 产出 `n/m` 个 entry）压成一个 KV entry。
2. **稀疏选择。** "Lightning Indexer" 用 `n_I_h=64` 个 indexer query head（head_dim `c_I=128`），按 `ReLU(q · K_indexer)` 给每个 token 排压缩块得分。query 侧低秩潜变量 `c^Q_t = h_t · W^DQ`（维度 `d_c`）与主注意力 query 共享，节省 query 侧一半算量。
3. **稀疏 Multi-Query 注意力。** 选 top-k=`{512 (Flash) | 1024 (Pro)}` 个压缩 entry，加上 `n_win=128` 个未压缩近期 token 的滑动窗分支（弥补压缩平滑掉的局部细粒度依赖），核心注意力是单 KV head 的 MQA。
4. **分组输出投影。** `n_h` 个 query head 输出按 `g={8|16}` 分组；每组投到 `d_g=1024` 后拼接，再投到 `hidden_dim`。比直接 `c·n_h × d` 投影便宜得多。

**Heavily Compressed Attention (HCA)：**

- 与 CSA 同款压缩机制，但 `m'=128` 且不重叠（压缩力度大得多）。
- 没有 lightning indexer，对全部 `n/m'` 个压缩 entry 做 dense MQA。
- 与 CSA 共享 shared-KV MQA、分组输出投影、滑动窗分支。

**混合层布局。** V4-Pro：第 0、1 层纯 HCA，第 2–60 层 CSA(m=4) / HCA(m'=128) 交替。V4-Flash：第 0、1 层纯 SWA（不压缩），第 2–42 层 CSA / HCA 交替。KV cache block 大小 = `lcm(m, m')=128` 个原始 token，每块产生 32 个 CSA 压缩 entry 和 1 个 HCA 压缩 entry。

**其他技巧**（论文第 2.3.3 节）：每个 Q / K / V 向量的最后 64 维做 partial RoPE；核心注意力输出的最后 64 维以位置 `-i` 再做一次 RoPE 以在 KV 聚合中保留相对位置语义；核心注意力前对每个 query head 与单一共享 KV head 各做一次 RMSNorm（替代 QK-Clip）；每个 head 加可学的 attention sink logit 进 softmax 分母。

## 参考资料

- DeepSeek-V4 技术报告第 2.3 节 + 图 3、图 4。
- DeepSeek Sparse Attention (DSA) 见 DeepSeek-V3.2。
- 开源实现：<https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/tree/main/inference>

## 使用此技术的模型

| 模型              | 变体 / 细节                                                                                                                                                                                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V4-Pro   | n_h=128 query head / head_dim=512 / KV head=1。CSA：m=4，top-k=1024，indexer (n_I_h=64, c_I=128)。HCA：m'=128。Query 潜变量 d_c=1536，输出分组 g=16 × d_g=1024，滑动窗 n_win=128。第 0、1 层纯 HCA；第 2–60 层 CSA/HCA 交替。        |
| DeepSeek-V4-Flash | n_h=64 query head / head_dim=512 / KV head=1。CSA：m=4，top-k=512，indexer (n_I_h=64, c_I=128)。HCA：m'=128。Query 潜变量 d_c=1024，输出分组 g=8 × d_g=1024，滑动窗 n_win=128。第 0、1 层纯 SWA（不压缩）；第 2–42 层 CSA/HCA 交替。 |

## 相关技术

- [MLA (Multi-head Latent Attention)](./mla.zh.md) — DeepSeek-V3 的 KV 压缩方案（把 K/V 压成 `kv_lora_rank` 维潜变量）；V4 用上述按块压缩取代之。CSA/HCA 通过 `d_c` 沿用了 MLA 的"低秩 query 潜变量"思路。
- [GQA](./gqa.zh.md) — V4 的 "shared KV" 核心注意力（`num_kv_heads=1`）是 GQA 的极限：所有 query 共享一个 KV head；KV 头复制在 MHA → GQA 中扮演的角色被压缩 KV 取代。
