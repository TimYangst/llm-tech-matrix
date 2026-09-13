# 压缩稀疏注意力 2（Compressed Sparse Attention 2, CSA2）

> English: [csa2.md](./csa2.md)

**Slug:** `csa2`
**类别：** attention
**一句话概括：** DeepSeek-V4 CSA 的简化后继：通过三种静态的逐层模式（Full、Reindex、Reuse），*跨层*共享 main KV 与 indexer key，并且（与之解耦地）允许层复用其他层的 top-k 选择。

**首次提出：** [DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression（DeepSeek-AI, 2026）](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/resolve/dba1be0a40aa45a94ad051997016db3960a90277/DeepSeek_V41_Tech_Report.pdf) §2.3。源自 [CSA + HCA](./csa-hca.zh.md)（DeepSeek-V4），后者又建立在 [DSA](./dsa.zh.md) 之上。

## 概述

报告把长上下文的 KV 开销拆成三个相乘的维度：**单条目大小**（减少 KV head，如 GQA；或共享 latent，如 MLA）、**序列维**（每 `m` 个 token 压成一条，如 CSA/HCA）、**层维**（让部分层复用其他层的缓存或选择）。此前的工作只零散地触及层维——IndexCache 只复用 top-k 索引（[IndexShare](./indexshare.zh.md)），另一些工作共享 KV 或路由——而用报告的话说，"这些方法都没有同时覆盖三个维度"。CSA2 是 DeepSeek 一次性覆盖三个维度的尝试。

**三种静态模式。** 每个 CSA2 层都计算自己的 main Q 和自己的层内滑窗 KV；模式之间的区别只在于借用什么。

- **Full** —— 计算自己的 main KV，从该 main KV 投影出 indexer K，计算 indexer Q 并选出新的 top-k。完整路径，等价于 V4 的一个 CSA 层。
- **Reindex** —— 复用最近一个 Full 层的 main KV *和* indexer K，但计算自己的 indexer Q 重新打分；缓存存储保持共享，而选择可以变化。
- **Reuse** —— 复用 main KV *和* 最新的 top-k 索引，完全不跑 indexer。

于是缓存共享和索引复用被**解耦**了——这正是它与"只复用索引"方案的关键区别：共享 main KV 真正减少存储，而复用索引只省 indexer 计算。

**简化的压缩器。** CSA2 去掉了 CSA 中重叠的 `2m` 条目压缩窗口和压缩器内部的绝对位置编码，并且直接由 main KV 投影得到 indexer K，不再走单独的压缩路径。压缩比 `m=1`（不压缩的 main KV）是合法的特例。

**层级稀疏索引器（Hierarchical Sparse Indexer）。** Reindex 层仍然要对整个可见上下文打分。因此在 [因果编码器-解码器](./causal-encoder-decoder.zh.md) 的 decoder 里，第一个 Full 层还会构建一个**候选池**：每个位置块取其中最大的索引分数，保留分数最高的块（2,048 块 × 每块 8 个位置 = 最多 16,384 个候选），之后的 Reindex 层*只在这个池子里*挑自己的 top-k。它们每个 query 的索引开销因此与上下文长度无关。这一限制是 training-aware 的：在后训练阶段引入，训练与推理时完全一致地施加。

配合 FP4 main KV 缓存，DeepSeek-V4.1-Flash 报告的全局 KV 占用为**每 token 890 字节，约为 DeepSeek-V4-Flash 的 1/4**。厂商自己把"CSA2 潜在的选择错误"列为尚未刻画清楚的鲁棒性边界之一。

## 参考资料

- 原始论文：DeepSeek-V4.1-Flash 技术报告 §2.3（图 4、图 5）、§3.1.2（训练基础设施：shadow indexer、pipeline payload 扩展、micro-batch 级共享状态管理）
- 参考实现：<https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash/tree/main/inference>（config 键为 `kv_source_layer_ids`、`index_source_layer_ids`、`candidate_source_layer_id`、`candidate_topk_blocks`、`candidate_block_size`、`compress_ratios`）
- 相关博客 / 文章：<https://api-docs.deepseek.com/news/news260910/>

## 使用此技术的模型

| 模型                | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4.1-Flash | 纯 CSA2——没有 HCA 层。共 40 层：第 0–1 层仅 SWA；**encoder** 第 2–19 层 `m=2`，分三组每组六层，均为 `[Full, Reuse×5]`；**decoder** 第 20–39 层 `m=1`（不压缩），分五组每组四层，先 `[Full, Reuse×3]`，后四组 `[Reindex, Reuse×3]`。合计 4 个 Full（`kv_source_layer_ids=[2,8,14,20]`）、4 个 Reindex（24/28/32/36）、30 个 Reuse。indexer 32 头 × 128 维，top-k 512；每层还保留 128 token 的 SWA 分支。层级稀疏索引器只用于 decoder，以第 20 层为根（`candidate_topk_blocks=2048`、`candidate_block_size=8`）。稀疏注意力在 64K 下从零训练，没有 dense 预热。 |

## 相关技术

- [CSA + HCA](./csa-hca.zh.md) —— CSA2 取代的 DeepSeek-V4 设计；V4.1 去掉了重度压缩层这一类型。
- [DeepSeek 稀疏注意力（DSA）](./dsa.zh.md) —— 两者底下共用的 lightning indexer top-k 机制。
- [IndexShare / IndexCache](./indexshare.zh.md) —— 只做跨层索引复用；CSA2 把 IndexCache（arXiv:2603.12201）列为先例，并把复用扩展到 KV 缓存本身。
- [Qwen 稀疏注意力（QSA）](./qsa.zh.md) —— 针对同一个 indexer 开销的另一种打法：在层内压缩 indexer 的输入。
- [因果编码器-解码器（CED）](./causal-encoder-decoder.zh.md) —— V4.1 中与 CSA2 搭配使用的层拓扑。
