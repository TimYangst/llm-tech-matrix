# 投机解码模块（MTP-1 → EAGLE-3 / DSpark）

> English: [speculative-decoding.md](./speculative-decoding.md)

**Slug:** `speculative-decoding`
**类别：** infra
**一句话概括：** 由小草稿模型一次提出一整块候选 token，大模型用一次前向完成校验，接受与目标分布一致的最长前缀 —— 构造上无损；到 2026 年中期，它已经从"部署侧的后置优化"变成**随权重发布的模块**。
**首次提出：** 投机解码（Chen et al., 2023；Leviathan et al., 2023）。本条目跟踪的两个变体是 [EAGLE-3（Li et al., 2025）](https://arxiv.org/abs/2503.01840) 与 [DSpark（DeepSeek-AI, 2026）](https://arxiv.org/abs/2607.05147)。

## 概述

自回归解码每出一个 token 就要跑一次完整前向。投机解码把**起草**与**校验**解耦：轻量草稿先提出 γ 个候选 token，
目标模型用一次前向对整块做拒绝采样校验，接受与目标分布一致的最长前缀并追加一个 bonus token。
由于校验是并行的、接受规则精确保持目标分布，因此**没有质量损失** —— 只有延迟收益，其幅度由接受率决定。

设计上的张力在于起草延迟与接受率：

- **自回归草稿**让每个位置以上一个采样结果为条件，接受率高，但起草延迟随块大小线性增长，
  从而被迫使用短块和浅结构。
- **并行草稿**一次前向产出所有位置，延迟几乎与块大小无关，但无法建模块内 token 间依赖，
  会出现多模态碰撞、靠后位置接受率迅速衰减。

2026 年两个旗舰模型在数周之内不约而同地把草稿变成 checkpoint 的一等公民 —— 而且都是通过**改造或替换 MTP head**：

**EAGLE-3 路线（Kimi K3）。** EAGLE-3 草稿是一个结构与 backbone block 相同的单层 decoder ——
这恰好就是预训练 MTP 层的结构，于是 K3 冻结目标模型，把 MTP 层微调成草稿。
草稿输入融合目标模型的低/中/高层特征（K3 取第 1、第 4 与最后一个 [AttnRes](./attnres.zh.md) 块的输出），
拼接后由无 bias 的 `W_E3` 投影，其初始化为 `[0 0 I]`，因此起点恰好等于 MTP 层预训练时所依赖的高层特征。
训练时展开 7 步，优化基于似然的 LK loss —— 即接受率本身的负对数 —— 而不是 KL 代理，
因为对容量受限的草稿而言，最小化 KL 并不等价于最大化接受率。

**DSpark（DeepSeek-V4）。** 采用*半自回归*设计：昂贵的 backbone 保持并行，在其上叠一个廉价的顺序模块：

- **并行 backbone** —— 3 层 MoE，带 [mHC](./mhc.zh.md) 与窗口 128 的滑窗注意力，
  通过 DFlash 式 KV 注入以目标模型为条件：取目标若干层的隐状态拼接后投影，
  `H_ctx = RMSNorm(W_c[H^(l₁);…;H^(l_m)])`，再拼进草稿每一层的 key 与 value。
- **Markov head** —— 用一阶转移偏置 `B(x_{k−1}, ·) = W₁[x_{k−1}]W₂` 恢复块内依赖，
  以 r = 256 低秩分解，使顺序循环在约 10⁵ 词表下仍然便宜。
  （累积完整前缀状态的 RNN head 变体只带来边际增益，因此默认用 Markov。）
- **置信度调度校验** —— 由 `c_k = σ(wᵀ[h_k; W₁[x_{k−1}]])` 预测"在此前全部被接受的条件下，
  第 k 个草稿 token 能通过校验"的*条件*概率，用解析的逐步接受率
  `c*_k = 1 − ½‖p_draft − p_target‖` 监督。随后由硬件感知调度器决定：轻载时校验整块，
  重载时只校验置信前缀 —— 因为高并发下，校验高拒绝风险的 token 会占用本可服务其他请求的 batch 容量。

相对 DeepSeek 自家 MTP-1 生产基线的公布结果：在同等总吞吐下，V4-Flash 单用户生成速度提升 60–85%，V4-Pro 提升 57–78%。

## 参考资料

- DSpark 论文：<https://arxiv.org/abs/2607.05147> · 训练仓库：DeepSpec
- EAGLE-3 论文：<https://arxiv.org/abs/2503.01840>
- Kimi K3 技术报告 §4.1.4（草稿模型微调）：<https://arxiv.org/abs/2607.24653>
- Schema 说明：这些模块记录在 `architecture.auxiliary_modules[]`（v7+），与 `training.objectives.multi_token_prediction` 中的 MTP *目标*分开。

## 使用此技术的模型

| 模型                   | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V4-Flash-0731 | DSpark **随 checkpoint 一起发布** —— README 明确说该模型"与 DeepSeek-V4-Flash-DSpark 结构相同，即附带一个投机解码模块"，SGLang 文档也要求不要传 `--speculative-draft-model-path`。配置键：`dspark_block_size=5`（γ）、`dspark_markov_rank=256`（r）、`dspark_target_layer_ids=[40,41,42]`（KV 注入的来源层）、`dspark_noise_token_id=128799`。部署只需一个开关：vLLM `--speculative-config '{"method":"dspark",...}'`、SGLang `--speculative-algorithm DSPARK`。`config.compress_ratios` 从 44 项增至 46 项，与草稿的 3 层未压缩 SWA-128 相吻合。 |
| Kimi K3                | EAGLE-3 路线，由预训练 MTP 层微调而来，目标模型冻结，展开 7 步，用 LK（接受率）loss，并沿用与主模型相同的 MXFP4/MXFP8 QAT 配置。输入融合第 1 / 第 4 / 最后一个 AttnRes 块的特征。**未随权重发布**：`config.num_nextn_predict_layers=0`，HF 仓库中也没有草稿权重 —— 论文有记载，但开放权重中被保留。                                                                                                                                                                                                                                               |
| GLM-5                  | 不是独立草稿模块，但出于同样的生产考量：GLM-5 在 RL 中用 FP8 rollout 搭配 MTP 来降低尾延迟（论文 §3.6.2）。其 3 步 MTP 与 backbone 参数共享。                                                                                                                                                                                                                                                                                                                                                                                                     |
| Qwen3.8-Flash-Next     | MTP 模块兼作 draft 路径，并继承了 **GLM-5 的索引复用技巧**：QSA 的 top-k 索引算一次后在投机解码各步之间复用，draft 不必每步重跑 indexer 选择。实测无损——四步投机解码下平均接受长度 4.06 → 4.07。与 DeepSeek 的 DSpark、Kimi K3 的 EAGLE-3 改造不同，Qwen 把 MTP 就当 MTP 用，没有把它转成专用 draft 模块。                                                                                                                                                                                                                                        |

## 相关技术

- [Multi-Token Prediction (MTP)](./mtp.zh.md) —— 这些模块生长出来的训练目标。DSpark 之前，MTP-1 就是 DeepSeek 的生产投机解码基线；K3 的草稿更是直接由它的 MTP 层微调而来。
- [Manifold-Constrained Hyper-Connections (mHC)](./mhc.zh.md) —— DSpark 的草稿 backbone 同样使用它，因此目标与草稿共享残差拓扑。
- [Attention Residuals (AttnRes)](./attnres.zh.md) —— 为 Kimi K3 的草稿提供多层级特征。
