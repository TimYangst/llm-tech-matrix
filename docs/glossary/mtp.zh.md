# Multi-Token Prediction (MTP)

> English: [mtp.md](./mtp.md)

**Slug:** `mtp`
**类别：** training-objective
**一句话概括：** 一种预训练目标——通过若干个浅层附加模块同时预测下 D 个 token（不仅是下一个），在密化训练信号的同时（可选地）为推理提供 speculative decoding 的草稿头。
**首次提出：** [Better & Faster Large Language Models via Multi-token Prediction (Gloeckle et al., 2024)](https://arxiv.org/abs/2404.19737)

## 概述

标准自回归预训练中，每个 token 只贡献一次 next-token 预测损失。MTP 在主模型上挂 `D` 个额外的小头（每个对应未来位置偏移 1..D），把它们的交叉熵损失加权 λ 累入主损失。每 token 训练信号大致变成原来的 `1 + D · λ`，常常带来等算力下的指标提升。

不同变体在头的拓扑上有差异：

- **并行型（Gloeckle et al.）**——`D` 个独立头一次性预测位置 2..D+1。
- **串行型（DeepSeek-V3）**——头链式连接，第 `k` 个头基于第 `k-1` 个头的表示进行预测，保留因果链。实现上复用主模型的 embedding 和输出头以最小化参数开销。

推理时，MTP 模块可以丢弃（恢复基础模型），也可以转作 speculative decoding 的草稿头。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2404.19737>
- DeepSeek-V3 实现细节与消融：<https://arxiv.org/abs/2412.19437>（§2.2，Table 4）

## 使用此技术的模型

| 模型                   | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3            | 串行型，D=1（一个额外预测深度）。Embedding + 输出头与主模型共享。损失权重 λ=0.3 用于前 10T tokens，之后 0.1 用于剩余 4.8T。MTP 模块在推理时丢弃（或转作 speculative decoding 用）。                                                                                                                                                                                                                                                                                                               |
| Qwen3.5-27B            | HF model card 称 "trained with multi-steps"；具体步深 D 未披露。Config 暴露 `mtp_num_hidden_layers=1`（头深度）和 `mtp_use_dedicated_embeddings=false`（与主模型共享 input embedding）。服务侧把这个头用作 **speculative decoding**：vLLM `qwen3_next_mtp` 配 `num_speculative_tokens=2`；sglang NEXTN 配 `speculative-num-steps=3`、`speculative-num-draft-tokens=4`。提示有效推理草稿深度至少 2-4。                                                                                             |
| Qwen3.5-35B-A3B        | MTP 设置与 27B 兄弟相同：`mtp_num_hidden_layers=1`、`mtp_use_dedicated_embeddings=false`、README 称 "trained with multi-steps"。同样的 vLLM/sglang speculative decoding 食谱适用。MoE FFN 不影响 MTP 拓扑——头位于共享骨干之上。                                                                                                                                                                                                                                                                   |
| Qwen3.6-27B            | MTP 设置与 Qwen3.5-27B 完全相同——`mtp_num_hidden_layers=1`、`mtp_use_dedicated_embeddings=false`、README 称 "trained with multi-steps"，同样的 speculative decoding 服务食谱。3.6 没有披露任何 MTP 相关变更。                                                                                                                                                                                                                                                                                     |
| Qwen3.6-35B-A3B        | MTP 设置与 Qwen3.5-35B-A3B 完全相同——同样的头深度、embedding 共享、multi-step 训练声明、服务食谱。整个 Qwen3.5/3.6 家族在 MTP 拓扑上完全收敛。                                                                                                                                                                                                                                                                                                                                                    |
| DeepSeek-V4-Pro        | MTP 配置与 DeepSeek-V3 相同（论文第 2.1 节：DeepSeek-V4 系列保留 MTP 策略未作改动）。D=1，`config.num_nextn_predict_layers=1`。损失权重 λ=0.3 用于训练大部分时间，LR 衰减开始时下调到 0.1。Embedding + 输出头与主体共享；DualPipe 共址保留。                                                                                                                                                                                                                                                      |
| DeepSeek-V4-Flash      | MTP 设置与 V4-Pro 和 V3 完全相同——D=1，相同损失权重调度，相同共享模块。MTP head 是 43 层之外唯一的层（config.compress_ratios 数组长度 44，末尾的 0 对应 MTP head 的压缩槽位）。                                                                                                                                                                                                                                                                                                                   |
| GLM-4.7                | D=1，`config.num_nextn_predict_layers=1`。论文 §2.1 实现细节：MTP 层用 MoE FFN 拓扑，而非更小的 dense head。损失权重 λ=0.3 用于前 15T tokens，剩余为 0.1（论文 §2.4）。vLLM speculative decoding：`--speculative-config.method mtp --speculative-config.num_speculative_tokens 1`；SGLang：EAGLE 3 步。                                                                                                                                                                                           |
| GLM-5 / GLM-5.1        | 报告 D=3（论文 §2.1：在训练时把 3 个 MTP 层的参数共享）但物理上只有 1 个模块（`config.num_nextn_predict_layers=1`），通过参数共享在 3 个串行 speculative-step 预测之间复用。内存成本与 DeepSeek-V3 的单 MTP 设计一致，同时模型可预测 3 个额外 token。论文 Table 2：accept length 2.76 vs DeepSeek-V3.2 的 2.55（4 个 speculative step）。MTP 输出层与主输出头共置于最后一段 pipeline 上以实现参数共享；embedding + transformer 部分放在前一段以平衡内存（论文 §2.4.1 'Flexible MTP placement'）。 |
| Kimi K3                | 1 层 MTP，其结构对齐一个 backbone block（论文 Table 1 —— 与 K2 数量相同，这点值得注意，因为 K2-Thinking/K2.5/K2.6 的 `num_nextn_predict_layers=0`）。有意思的是它的「后续用途」：§4.1.4 把预训练好的 MTP 层微调成用于投机解码的 **EAGLE-3 式草稿模型**，因为 EAGLE-3 草稿正是一个结构相同的单层 decoder。**未包含在发布的 checkpoint 中** —— `config.num_nextn_predict_layers=0`，也没有草稿权重。见[投机解码](./speculative-decoding.zh.md)。                                                    |
| DeepSeek-V3.2-Exp      | `num_nextn_predict_layers=1`，与 DeepSeek-V3 一致，沿用 V3 的 head 设计。V3.2 论文完全没有讨论 MTP —— 它属于「为了让 DSA 成为唯一变量」而被刻意保持不变的众多要素之一。                                                                                                                                                                                                                                                                                                                           |
| DeepSeek-V4-Flash-0731 | 仍声明 `num_nextn_predict_layers=1`，但 MTP-1 现在被明确定位为 **DSpark 所取代的生产基线**：DSpark 论文在同等吞吐下测得单用户生成速度提升 60–85%。MTP head 是否仍能与随权重发布的 DSpark 模块并存，文档未说明。                                                                                                                                                                                                                                                                                   |
| Qwen3.8-27B            | 与 Qwen3.5/3.6 一致——`mtp_num_hidden_layers=1`、`mtp_use_dedicated_embeddings=false`、README 称 "trained with multi-steps"。步数 D 连续三代都没披露。                                                                                                                                                                                                                                                                                                                                             |
| Qwen3.8-2.4T-A95B      | 2.4T 规模下仍是单层 MTP 头——`mtp_num_hidden_layers=1`、`mtp_use_dedicated_embeddings=false`、"trained with multi-steps"。Qwen 把 MTP 保持为训练目标 + 投机解码辅助，**没有**跟随 DeepSeek / Kimi 把 MTP 层改造成专用 draft 模块（参见 [speculative-decoding](./speculative-decoding.zh.md)）。                                                                                                                                                                                                    |

## 相关技术

- _Speculative decoding（EAGLE、Medusa）_ — 一种相关但不同的 multi-future-token 头用法，目标是推理加速而非训练信号密化
