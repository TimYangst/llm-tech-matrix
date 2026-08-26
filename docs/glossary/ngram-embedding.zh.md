# N-gram 嵌入（N-gram Embedding）

> English: [ngram-embedding.md](./ngram-embedding.md)

**Slug:** `ngram-embedding`
**类别：** other
**一句话概括：** 一张以短 n-gram（而非单个 token）为键的大型嵌入表，以近乎零的每 token FLOPs 增加参数量——而且由于寻址是确定性的，便宜到可以把表放在主机内存里预取。

**首次提出：** 没有单一出处。以 n-gram 为键的形式是 unigram 查表的推广，谱系很长；而「用可卸载的嵌入表来扩容量」这一现代表述与 per-layer / 卸载式嵌入的工作（Google DeepMind, 2025）及其后续（Cheng et al., 2026）相关。Qwen 的实现记录在 [On the Design of Qwen3.8-Next Architecture（Qwen Team, 2026）](https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf) §2.3。

## 概述

MoE 靠增加专家来扩参数，但每多一个专家都要占加速器显存，其路由也要吃带宽。嵌入表沿另一个维度扩参数：查表不是矩阵乘，所以容量增长带来的**每 token 额外 FLOPs 可以忽略**。而且因为地址是由输入 token 算出来的、而不是由激活算出来的，这次查找是*确定的、可以提前知道的*——这正是为什么可以放心把表留在主机内存里，在加速器计算前面几层的同时异步预取。

N-gram 嵌入把普通的 unigram 嵌入推广为：以*结束于*每个 token 的那个短 n-gram 为键，而不只是以 token 身份为键，因此取回的向量是以局部上下文为条件的。取回的向量在某一个选定的层上增强 token 表示。

这个词条真正值得读的地方，在于 Qwen 的消融对其局限说得相当坦率：

- **放在哪一层几乎可以随便选。** 没有哪个深度区间占优；前两层最强，但中层和深层也有竞争力，而且放置位置基本不受注意力机制影响。Qwen 选**第 2 层，是为了让主机内存预取与第 1 层的计算重叠**——这是工程理由，不是质量理由。
- **一层就够。** 把同样的参数预算拆到多层没有稳定收益。
- **loss 和 benchmark 明显打架。** 把 n-gram 词表从基础 tokenizer 词表的 20 倍扩到 200 倍，loss *单调*下降，而下游准确率却饱和或波动。只盯着 loss 调这个超参的人会把表扩过头。
- **中文基准是例外**——C-Eval 和 CMMLU 随词表规模持续提升，而其他基准趋于平台。
- **它不是 MoE 的替代品。** 在*固定*总参数预算下，用专家换 n-gram 槽位会把 loss 最优点推到约 10 倍词表（占参数 25%），但下游相比纯 MoE 基线没有明显收益。报告的结论是「N-gram 嵌入与 MoE 专家在扩容量上扮演不同角色」——所以诚实的用法是把 n-gram 表当作*额外*参数，而不是挪用来的参数。

Qwen 还报告了一组在他们的配方里**没有奏效**的参数效率技巧：用 token 归一化压缩词表、在不同 n-gram 阶数间做非均匀分配、以及按频率划分嵌入槽位。这种具体程度的负面结果很少见，值得记下来。

## 参考资料

- 原始论文：<https://github.com/QwenLM/Qwen3.8-Flash-Next/blob/main/tech_report.pdf>（§2.3）
- 参考实现：—（config 键为 `ngram_size`、`ngram_vocab_size_base`、`heads_per_ngram`、`ple_layer_ids`）

## 使用此技术的模型

| 模型 | 变体 / 细节 |
| ---- | ----------- |
| Qwen3.8-Flash-Next | **单个** n-gram 嵌入层，位于**第 2 层**，在 20,000,000 条目的表中持有 **51B 参数**（`ngram_size=3`——bigram/trigram，`heads_per_ngram=8`，嵌入维度 2560，深度可分离卷积核 4，`split_ngram_parts=128`）。表**放在加速器之外的主机内存中并异步预取**，因此这 51B 与 125B 骨干参数分开统计。用 Adam 训练且关闭 weight decay；该层的 key/value 投影走 [Muon](./muon.zh.md)。 |

## 相关技术

- [DeepSeekMoE](./deepseekmoe.zh.md) —— 另一条扩容量的轴，报告明确指出本技术*不是*它的替代品。
- [Stable LatentMoE](./latentmoe.zh.md) —— Kimi K3 让专家轴变便宜的做法，可作对照：它压缩的是专家所处的空间，而不是把容量整个搬出骨干。
