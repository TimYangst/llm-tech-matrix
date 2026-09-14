# IndexShare / IndexCache（跨层索引复用）

> English: [indexshare.md](./indexshare.md)

**Slug:** `indexshare`
**类别：** attention
**一句话概括：** 只在少数层上真正运行稀疏注意力的 indexer，其余层直接复用最近一个已算出的 top-k 选择——利用相邻层选出的 token 几乎相同这一事实。

**首次提出：** [IndexCache: Accelerating Sparse Attention via Cross-Layer Index Reuse（Bai, Dong, Jiang, Lv, Du, Zeng, Tang, Li —— 清华 + Z.ai, 2026）](https://arxiv.org/abs/2603.12201)

## 概述

[DSA](./dsa.zh.md) 用一个轻量的 *lightning indexer* 为每个 query 选出 top-k 相关 token，把核心注意力从 `O(L²)` 降到 `O(Lk)`。但 indexer 自己仍然是 `O(L²)`，而且每一层都要独立跑一遍——于是上下文一长，这个为了消除二次开销而引入的机制，自己就变成了那个二次开销。

IndexCache 的观察是：这些逐层计算大部分是冗余的——**相邻层的 top-k 选择高度相似**。因此把层划分成少量 **Full** 层（各自跑 indexer）和多数 **Shared** 层（直接复用最近一个 Full 层的索引）。核心注意力仍然每层都算，被共享的只是*选择*。

论文给出两种确定并优化这个划分的方式：

- **Training-free IndexCache** —— 用贪心搜索，直接以校准集上的语言建模 loss 最小化为目标来挑哪些层保留 indexer，不更新任何权重。这通常会得到一个*不规则*的层集合；论文明确指出，在不训练的前提下均匀间隔是次优的。
- **Training-aware IndexCache** —— 用多层蒸馏损失，把每个保留下来的 indexer 对齐到它所服务的所有层的**平均**注意力分布上。有了这一步，即使是简单的均匀间隔模式也能达到全 indexer 的精度。

在 30B 的 DSA 模型上实测：去掉 75% 的 indexer 计算，质量几乎无损，prefill 加速 1.82×、decode 加速 1.48×。在生产规模的 GLM-5 上按 50% 去除，端到端约 1.2×。

**这项技术的边界，就在它的前提失效的地方。** 跨层相似性是共享得以免费的原因——所以它在每层都是全注意力的同构栈里最强，而在全注意力层被线性注意力层隔开的混合栈里最弱。Qwen 的 Qwen3.8-Flash-Next 报告正是测了这一点并选了另一条路：在同等 indexer 延迟下，它的 [QSA](./qsa.zh.md)（层内微块压缩）在相对延迟 0.25 时就追平了全注意力的 RULER 基线，而 IndexShare 到 0.5 仍低于基线。而 GLM 自己的产品线随后从内部印证了同一条边界——GLM-5.2 是纯 MLA 栈，用 IndexShare；GLM-5.3-Flash 是 KDA/DSA 混合栈，改用 key 池化，放弃了逐层共享。

**关于命名。** 论文标题是 *IndexCache*；GLM-5.2 的模型卡叫它 *IndexShare*；Qwen 的报告引用为 *"IndexShare (Bai et al., 2026)"*。三者指的是同一个机制。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2603.12201>
- 参考实现：—（config 键为 `indexer_types`、`index_topk_freq`、`index_skip_topk_offset`、`index_share_for_mtp_iteration`）

## 使用此技术的模型

| 模型                           | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GLM-5.2                        | 78 层中 **21 Full / 57 Shared**。第 0-2 层（即 dense FFN 那三层）为 Full；从第 3 层起以 4 为周期、每第四层一个 Full（`index_topk_freq=4`、`index_skip_topk_offset=3`）。上的是 **training-aware** 变体——固定的规则模式正是这条路线才成立的，training-free 的贪心搜索会给出不规则的层集合。官方称 1M 上下文下**每 token FLOPs 减少 2.9×**。`index_share_for_mtp_iteration=true` 把复用延伸到 MTP 投机解码的各步。 |
| GLM-5.3-Flash (dropped)        | **逐层共享被取消。** 11 个稀疏注意力层各自计算自己的选择，`indexer_types` 的 Full/Shared 划分消失，改为层内 key 池化（`index_kpool=4`）——同样的取舍见 Qwen 的 [QSA](./qsa.zh.md)。只有 `index_share_for_mtp_iteration=true` 保留下来，即跨 MTP 步复用而非跨层复用。这干净地展示了该技术的边界：这个模型是 3:1 的 KDA/DSA 混合栈，正是跨层相似性最弱的场景。                                                      |
| DeepSeek-V4.1-Flash (via CSA2) | 在 [CSA2](./csa2.zh.md) 中**被推广到 KV 共享**；其报告把 IndexCache（arXiv:2603.12201）列为只复用索引的先例。Reuse 层（40 层中 30 个）像这里的 Shared 层一样取最新的 top-k，但 CSA2 还额外共享 main KV 和 indexer K，并新增 Reindex 模式——用自己的 indexer Q 对共享的 key 重新打分。静态分配：Full 在第 2/8/14/20 层，Reindex 在第 24/28/32/36 层。decoder 中的 Reindex 层只在第 20 层构建的候选池里搜索。       |

<!-- BEGIN GENERATED: implemented-by-engines (synthesis.index) -->

## 实现此技术的引擎

由 [`data/extracted/engines/`](../../data/extracted/engines/) 中各引擎快照的 `technique_support[]` 自动生成，请勿手工编辑。上方表格记录采用该技术的模型，本表记录实现该技术的引擎。

| 引擎快照                                                                               | 角色                                  | 实现方式                                                                                                                                                                                                       | 参数                                                                                                                                                | 证据                                                                                                                                                                                                                                                                                                                                                                                               |
| -------------------------------------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`sglang-v0.5.19`](../../data/extracted/engines/sglang-v0.5.19.md)                     | inference                             | Cross-layer top-k reuse read from the model config (index_topk_freq / index_topk_pattern); the HiSparse guide calls it native in GLM-5.2 as IndexShare and prefetches skip layers' working sets automatically. | —                                                                                                                                                   | [model_config.py#L237](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L237), [model_config.py#L241](https://github.com/sgl-project/sglang/blob/0bcd822377da7b5718e674eaf9c870d349424dd1/python/sglang/srt/configs/model_config.py#L241)                                                                             |
| [`vllm-v0.29.0`](../../data/extracted/engines/vllm-v0.29.0.md)                         | inference                             | IndexCache: layers marked F compute and cache top-k indices, layers marked S reuse the previous layer's indices; configured per layer or by frequency.                                                         | `--hf-overrides '{"use_index_cache": true, "index_topk_freq": 4}'`<br>`--hf-overrides '{"use_index_cache": true, "index_topk_pattern": "FFSF..."}'` | [index_cache.md#L3](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/docs/features/index_cache.md#L3), [index_cache.md#L26](https://github.com/vllm-project/vllm/blob/98dff2a81d747d1dba01a47f939f48c3526d4206/docs/features/index_cache.md#L26)                                                                                                                 |
| [`megatron-bridge-v0.6.0`](../../data/extracted/engines/megatron-bridge-v0.6.0.md)     | training                              | GLM-5.2 IndexShare-style index reuse: index_topk_freq and index_skip_topk_offset are read from the HF config into the DSA provider.                                                                            | `dsa_indexer_topk_freq`<br>`dsa_indexer_skip_topk_offset`                                                                                           | [glm5_bridge.py#L136](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/src/megatron/bridge/models/glm_moe_dsa/glm5_bridge.py#L136), [glm5.md#L11](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/51885cf132b2814188b6855c25a8588254274c2a/docs/models/glm/glm5.md#L11)                                                                            |
| [`megatron-lm-core_v0.19.0`](../../data/extracted/engines/megatron-lm-core_v0.19.0.md) | training, rl_post_training, inference | DSA index sharing: with index_topk_freq > 1, layers without their own top-k reuse a previous indexer layer's selection; pipeline splits are validated so shared indices stay on one stage.                     | `dsa_indexer_topk_freq > 1`                                                                                                                         | [dsa.py#L1564](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/transformer/experimental_attention_variant/dsa.py#L1564), [experimental_attention_variant_module_specs.py#L339](https://github.com/NVIDIA/Megatron-LM/blob/5be9626709af2722333bf54797c954c09edeada3/megatron/core/models/gpt/experimental_attention_variant_module_specs.py#L339) |

<!-- END GENERATED: implemented-by-engines -->

## 相关技术

- [DeepSeek 稀疏注意力（DSA）](./dsa.zh.md) —— 本技术要解决的正是它的 indexer 开销。
- [Qwen 稀疏注意力（QSA）](./qsa.zh.md) —— 竞争性的另一个答案：在层内压缩 indexer 的输入，而不是跨层共享。
- [投机解码模块](./speculative-decoding.zh.md) —— `index_share_for_mtp_iteration` 在 draft 各步之间复用选择；Qwen3.8-Flash-Next 把这个技巧记在 GLM 名下。
