# DeepSeek Sparse Attention (DSA)

> English: [dsa.md](./dsa.md)

**Slug:** `dsa`
**类别：** attention
**一句话概括：** 一种 token 级稀疏注意力——一个轻量的"Lightning Indexer"为每个 query 位置给所有前置 token 打分，core attention 只在分数最高的 top-k 个 token 上执行；和滑窗不同它是 content-dependent，按 GLM-5 论文的说法是 *lossless by construction*，在 128K 上下文下把注意力计算降低 ~1.5–2 倍。

**首次提出：** [DeepSeek-V3.2-Exp 技术报告 (DeepSeek-AI, 2025)](https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp)。两阶段"dense warm-up + sparse training adaptation"的 continual-pretraining 配方是 V3.2-Exp 的核心交付物；indexer 架构（每个 token 的 query × indexer-key 点积 → top-k 选择）是核心机制。

## 概述

128K+ 上下文下标准 `O(L^2)` 稠密注意力代价高昂；滑窗注意力虽然便宜但 content-blind——窗口外的相关 token 不论重要性都被丢弃。DSA 用 content-dependent 的稀疏化替代稠密注意力：

1. **Lightning Indexer。** 一个小辅助注意力路径，`index_n_heads` 个 head 每个 head_dim `index_head_dim`，对每个前置 token 计算相关度 `ReLU(q_indexer · k_indexer)`。indexer 的 query 复用主注意力 query 侧的低秩潜变量（indexer 便宜是因为它的 KV 路径独立于主 MLA / KV cache）。
2. **Top-k 选择。** 每个 query 位置取 indexer 打分前 `index_topk` 的 token，core attention 只在这个稀疏子集上计算（128K 下通常 `k=2048`，丢掉 ~98% 的注意力 entry）。
3. **Continued Pre-Training 适配。** DSA 不从头训练，而是装到 dense 基础模型上分两阶段做：先短暂 *warmup*（1000 步，base model 冻结只训 indexer），然后 *sparse adaptation* 阶段 indexer 与 base model 联合训练，用相对较少的 token 预算。DeepSeek-V3.2 用了 943.7B sparse-adaptation token；GLM-5 发现 20B token 已足够恢复 dense baseline 质量。

GLM-5 论文 §2.1.2 把 DSA 和 SWA、search-based pattern SWA、GDN、SimpleGDN 做了对比，结论是只有 DSA 在长上下文下是 *lossless by construction*——indexer 适应内容而不是承诺一个固定稀疏模式。SFT loss 曲线下，MLA-base 和 DSA-base 模型收敛到相同 loss（论文图 6）。

**RL 稳定性注意（GLM-5 §3.2）。** RL 期间 DSA indexer 的 top-k 算子必须是 deterministic 的。non-deterministic 的 CUDA top-k 实现在 RL 训练几步后就引发剧烈性能退化和 entropy 崩塌。GLM-5 用 `torch.topk`（略慢但 deterministic），并默认在 RL 时冻结 indexer 参数。

## 参考资料

- DeepSeek-V3.2-Exp 报告：<https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp>
- GLM-5 论文 §2.1.1 / §2.1.2 / §3.2 / §3.6（DSA continued-pretraining 配方、对 SWA / GDN 的消融、RL deterministic top-k 稳定性）：<https://arxiv.org/abs/2602.15763>
- GLM-5 cookbook（SGLang DSA Indexer 优化）：<https://cookbook.sglang.io/autoregressive/GLM/GLM-5>
- 紧密相关：DeepSeek-V4 的 [CSA + HCA 混合](./csa-hca.zh.md)——在 DSA 的 content-dependent 稀疏化基础上叠加了 token 级 KV 压缩。

## 使用此技术的模型

| 模型    | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GLM-5   | **首个非 DeepSeek 厂商落地 DSA**。Indexer 配置：`index_n_heads=32`，`index_head_dim=128`，`index_topk=2048`，`indexer_rope_interleave=true`。Continued Pre-Training 配方（论文 §2.1.1）：indexer-only warmup 1000 步 × 14 sequences × 202752 tokens，最大 LR 5e-3（约 2.84B tokens），然后 sparse adaptation 20B tokens（DSV3.2 用了 943.7B——更小的预算就够了）。长上下文几乎无损（论文表 3）：MQ-NIAH-128k 100.0 vs MLA 100.0，MV-NIAH-128k 97.0 vs 95.5，SQuAD-128k 86.0 vs 79.7，HotpotQA-128k 63.0 vs 66.3。论文 §2.1.2 对 SWA / search-based SWA / GDN / SimpleGDN 的消融结论：只有 DSA *lossless by construction*。RL 稳定性 §3.2：deterministic `torch.topk` 必须，CUDA top-k 引发 entropy 崩塌，RL 期间默认冻结 indexer。SGLang-Ascend 提供融合的 Lightning Indexer kernel。 |
| GLM-5.1 | DSA 架构与 GLM-5 完全一致（config 除 `transformers_version` 外字节相同）。同样的 indexer 配置、同样的 RL deterministic top-k 要求。Post-training-only refresh 继承了 GLM-5 的 indexer 权重和 RL 期间冻结 indexer 的训练纪律。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |

> 说明：DeepSeek-V3.2-Exp 和 DeepSeek-V4（把 DSA 拓展为 [CSA + HCA 混合](./csa-hca.zh.md)）目前在本 repo 中尚未作为独立 slug 提取——V3.2 时间上位于 V3 和 V4-Pro/Flash 之间，V4 的混合方案在自己的 glossary entry 中描述。上面的 DSA 机制是它们共享的契约。

## 相关技术

- [CSA + HCA 混合](./csa-hca.zh.md) — DeepSeek-V4 在 DSA 的 content-dependent 稀疏化之上加了 token 级 KV 压缩（CSA = 压缩后稀疏，HCA = 重压缩后 dense）。CSA 内部仍是同一套 Lightning Indexer 机制。
- [MLA (Multi-head Latent Attention)](./mla.zh.md) — DSA 在 GLM-5 / DeepSeek-V3.2 中是 *叠加* 在 MLA 之上：MLA 压缩 KV cache，DSA 决定 core attention 从压缩后 KV entry 中读哪些。
- [Muon 优化器](./muon.zh.md) — GLM-5 和 DSV4 都用 Muon 系列优化器训练 DSA；GLM-5 特别使用 Muon Split 在 MLA + DSA 组合下保持 logit 稳定，省去 QK-Clip。
