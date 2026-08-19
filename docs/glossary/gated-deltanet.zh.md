# Gated DeltaNet

> English: [gated-deltanet.md](./gated-deltanet.md)

**Slug:** `gated-deltanet`
**类别：** attention
**一句话概括：** 一种线性注意力变体，用 delta rule 维护一个递归的 KV state，再通过一个学习到的乘性门产出输出，在常数级单 token 成本下达到接近 softmax 注意力的检索质量。
**首次提出：** [Gated Delta Networks: Improving Mamba2 with Delta Rule (Yang et al., 2024)](https://arxiv.org/abs/2412.06464)

## 概述

线性注意力把 softmax 注意力的点积换成核化形式，从而允许一个常数大小的递归状态——把 N 位置处的单 token 成本从 O(N) 降到 O(1)。但朴素线性注意力在长上下文里检索能力下降，原因是 state 无法选择性地遗忘陈旧的 key。

Gated DeltaNet 结合了两个想法：

- **Delta rule**（DeltaNet, Yang et al. 2024）：每一步用一个*校正* `Δ = β·(v − Sₜ k) kᵀ` 来更新递归状态，而不是外积 `vkᵀ`。这相当于在线对 value 关于 key 做线性回归式拟合，使新的 key 能在同一"地址"上覆盖旧的 key，而不是不断累加噪声。
- **输出门控**：用 sigmoid（或 swish-gated）的逐通道门作用在注意力输出上，与现代 SSM（Mamba2）中的门控相呼应。门会压制那些 state 已经不再相关的通道，恢复选择性遗忘能力。

在 transformer 堆叠中，Gated DeltaNet 通常和少量 full softmax 注意力层（"全局正确"通道）交错使用——这样大多数步用接近 O(1) 的递归层，少量步用 softmax 提供长程检索。Qwen3.5 就采用这种布局：每 1 个 Gated Attention 层之间穿插 3 个 Gated DeltaNet 层，在 64 层堆叠中重复 16 次。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2412.06464>
- DeltaNet（delta rule 基线）：<https://arxiv.org/abs/2102.11174>

## 使用此技术的模型

| 模型                | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3.5-27B         | **每 4 层 3 层**采用（`config.layer_types` 列表为 `linear_attention` × 3 + `full_attention` × 1，重复 16 次——64 层中 48 层）。非对称头数：`linear_num_value_heads=48` × `linear_value_head_dim=128`（V state 宽度 6144），但 `linear_num_key_heads=16` × `linear_key_head_dim=128`（K state 宽度 2048）。DeltaNet 前接一个 1D 因果卷积，`linear_conv_kernel_dim=4`。State 用 `mamba_ssm_dtype=float32` 保证数值稳定。本 config 未暴露输出门激活函数（同家族中只有 Qwen3.6-27B config 显式设置 `output_gate_type=swish`）。无 RoPE——位置信息存在于递归状态更新中。 |
| Qwen3.5-35B-A3B     | 同样的混合模式，但 **V state 更窄**：`linear_num_value_heads=32` × `linear_value_head_dim=128`（V state 宽 4096），K state 仍是 `16 × 128 = 2048`。40 层中 30 层（10 个外层块，每块 3 个 DeltaNet + 1 个 GatedAttn）。配套的 MoE-FFN（256 个专家、8 路由 + 1 共享）让单 token 计算量与 27B 的 dense FFN 大致匹配，尽管线性注意力层的 V state 更小。                                                                                                                                                                                                               |
| Qwen3.6-27B         | Gated DeltaNet 形状与 Qwen3.5-27B 完全相同（V 48×128=6144，K 16×128=2048，conv kernel 4，swish 输出门控）——Qwen3.6-27B 整体继承骨干。3.6 仅是后训练刷新，线性注意力机制没有任何变化。                                                                                                                                                                                                                                                                                                                                                                             |
| Qwen3.6-35B-A3B     | Gated DeltaNet 形状与 Qwen3.5-35B-A3B 完全相同（V 32×128=4096，K 16×128=2048，conv kernel 4）——Qwen3.6-35B-A3B 整体继承骨干（config 仍报告 `architectures="Qwen3_5MoeForConditionalGeneration"` 和 `model_type="qwen3_5_moe"`）。                                                                                                                                                                                                                                                                                                                                 |
| Kimi K3（经由 KDA） | 严格说不是 Gated DeltaNet 本身，而是它在旗舰规模上的最近亲 —— [Kimi Delta Attention](./kda.zh.md) 是带**逐通道**遗忘门的 delta-rule 递推，而 Gated DeltaNet 用的是逐头标量门。跨厂商比较中值得记一笔：Kimi K3 与 Qwen3.5/3.6 各自独立地收敛到了**相同的 3:1 线性/全局层比例**。分歧在于混合搭档怎么做 —— Qwen 在其 Gated Attention 层保留 RoPE，K3 则在 Gated MLA 层跑 NoPE，把位置信息完全交给线性层承载。                                                                                                                                                       |
| Qwen3.8-27B         | Gated DeltaNet 模块与 Qwen3.6-27B 逐字节相同（V 48×128=6144，K 16×128=2048，conv kernel 4，swish 输出门控）。线性注意力骨干已连续三代冻结。                                                                                                                                                                                                                                                                                                                                                                                                                       |
| Qwen3.8-2.4T-A95B   | Gated DeltaNet 首次用到万亿规模——92 层里有 69 层。**V 头数随模型宽度扩张**（hidden 5120 时 48 → hidden 8192 时 **128**，V 状态 16384 维），而 **QK 头数固定在 16**（K 状态 2048 维），与所有小尺寸兄弟完全一致。conv kernel 4、swish 输出门控、3:1 配比均未变。                                                                                                                                                                                                                                                                                                   |

## 相关技术

- [GQA](./gqa.md) — Qwen3.5 混合堆叠中的 softmax 注意力配套（每 4 层 1 层）
