# 因果编码器-解码器（Causal Encoder-Decoder, CED）

> English: [causal-encoder-decoder.md](./causal-encoder-decoder.md)

**Slug:** `causal-encoder-decoder`
**类别：** attention
**一句话概括：** 把一个 decoder-only 栈对半切开，让上半部分的*全局* KV 缓存由下半部分最后一层的隐状态投影得到——prefill 只需跑下半部分，于是每个 prompt token 激活的参数大约只有每个生成 token 的一半。

**首次提出：** [DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression（DeepSeek-AI, 2026）](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/DeepSeek_V41_Tech_Report.pdf) §2.2，"受 YOCO 启发"（Sun et al., 2024）。

## 概述

Agent 工作负载是输入密集型的：每次工具调用返回的文本都要 prefill，而缓存未命中会让 prefill 很贵。YOCO 让上半部分的层直接共享下半部分产出的 KV 缓存，从而减少 prefill。CED 保留了这个思路，但按报告的说法做了结构性改动，"同时提升整体 KV 缓存容量和 KV 生成的计算深度"。

底部 `L/2` 层是**因果编码器（causal encoder）**。对于**全局**注意力，每个 decoder 层 `l > L/2` 都不从自己的隐状态推导 KV；它的 KV 条目 `C_l` 与压缩权重 `Z_l` 由编码器最后一层的隐状态 `H_{L/2}` 经层相关的权重投影得到：`C_l = H_{L/2} W^KV_l`、`Z_l = H_{L/2} W^Z_l`。因此整段 prompt 的 decoder 全局 KV 只需跑编码器就能得到。报告给出的 prefill 复杂度从 `O(NL)` 降到约 `O(NL/2)`。

对于**滑窗**注意力，CED 刻意*不*共享：每一层（包括 decoder 层）都从自己的隐状态计算局部 KV。这保住了局部 KV 生成的深度，但也意味着最初几步 decode 需要的 decoder SWA KV，严格来说得把 `n_win × L/2` 个 prompt token 在 decoder 里重放一遍。CED 用 **SWA 有界重放（SWA Bounded Replay）** 来解决：

- **Decoder SWA 有界重放** —— 每次 prefill 只把最后 `n_win` 个 prompt token 送进 decoder 重放，并把 SWA 截断在这段重放区间内。得到的状态是近似的；报告发现"对回答质量的影响可以忽略"，并在后训练中模拟同样的重放做 train-aware 适配。
- **Encoder SWA 有界重放** —— 当前缀缓存命中、但其 SWA KV 已被淘汰时，只重放缓存前缀的最后 `n_win` 个 token 来重建 SWA KV。这让前缀缓存只依赖全局 KV，从而可以把 SWA KV 从持久化（SSD）缓存中彻底移除。

报告把"SWA 有界重放中的近似状态重建"列为该模型尚未刻画清楚的鲁棒性边界之一。

## 参考资料

- 原始论文：DeepSeek-V4.1-Flash 技术报告 §2.2、§3.2.1（持久化 KV 缓存管理）、§3.2.2（SWA 有界重放）
- 参考实现：<https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/tree/main/inference>
- 相关博客 / 文章：<https://api-docs.deepseek.com/news/news260910/>（"非对称架构……输入仅激活 8B 参数，输出 16B"）

## 使用此技术的模型

| 模型                | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4.1-Flash | 40 层 = 20 层 encoder（0–19）+ 20 层 decoder（20–39）；**prefill 每 token 激活 8B，decode 激活 16B**。与 [CSA2](./csa2.zh.md) 搭配，因此只有 decoder 的 Full 模式层（第 20 层）真正由编码器输出生成 decoder 全局 KV。`n_win=128`。持久化 KV 缓存约为 DeepSeek-V4 的 1/8：SWA KV 不再持久化（改放到占每台机器 10% 主机内存、TTL 仅数分钟的 DRAM 池，未命中时回退到 Encoder SWA 有界重放），全局 KV 约为 V4 的 1/4。全局 KV 仍留在持久化缓存中，保证至少 72 小时的生命周期。 |

## 相关技术

- [压缩稀疏注意力 2（CSA2）](./csa2.zh.md) —— V4.1 中与 CED 组合使用的跨层 KV / 索引共享方案。
- [CSA + HCA](./csa-hca.zh.md) —— DeepSeek-V4 的注意力栈；有界重放正是为了消除它的 SWA 持久化开销而设计的。
