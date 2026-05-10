# FP4 量化感知训练 (MXFP4)

> English: [fp4-qat.md](./fp4-qat.md)

**Slug:** `fp4-qat`
**类别：** quantization
**一句话概括：** 在后训练阶段对 MoE 专家权重和 indexer 的 QK 路径做 MXFP4 量化感知训练；当 FP4 子块尺度的 max/min 比落入 FP8 指数范围内，FP4 → FP8 反量化无损，于是已有的 FP8 训练栈无须修改即可驱动 QAT。
**首次提出：** [Microscaling Data Formats for Deep Learning (Rouhani et al., 2023)](https://arxiv.org/abs/2310.10537) 定义 MXFP4；indexer-QK 与 MoE-expert 同时量化的具体配方是 DeepSeek-V4 的贡献（论文第 5.2.1 节）。

## 概述

FP4（4-bit 浮点，可为 E2M1 / MXFP4 / NVFP4 形式）相比 FP8 减半权重存储，相比 BF16 减为 1/4。万亿参数规模上直接做事后 PTQ 通常会掉点，因此 DeepSeek-V4 把 FP4 放到**后训练阶段以 QAT 形式**引入两个特定目标：

1. **MoE 专家权重** —— FP32 主权重先量化到 FP4，再无损反量化回 FP8 用于前向 GEMM。这里的"无损"非平凡：每个 FP4 子块（1×32 tile）有自己的 scale；一个 FP8（E4M3）量化块（128×128 tile）包含 16 个这样的子块。只要这 16 个子块 scale 的 max/min 比在 FP8 E4M3 的指数范围内，细粒度 FP4 scale 信息可被 FP8 表示完全吸收。V4 实测当前权重满足此条件。反向传播针对相同的 FP8 权重（Straight-Through Estimator），现有 FP8 训练框架原样跑 QAT 循环。
2. **CSA 中 Lightning Indexer 的 QK 路径** —— QK 激活全程以 FP4 缓存、加载、相乘。Index scores 额外从 FP32 量化到 BF16，让 top-k 选择器获得 2× 加速并保持 99.7% 召回。

在推理与 RL rollout（不需要反向传播）阶段，V4 直接使用原生 FP4 量化权重而非模拟量化，确保采样行为与上线部署完全一致。已发布的 checkpoint 标注为 `FP4 + FP8 Mixed`（MoE 专家参数 FP4；其余参数 FP8 / BF16）。

`config.quantization_config`: `fmt="e4m3"`, `scale_fmt="ue8m0"`, `weight_block_size=[128, 128]`, `activation_scheme="dynamic"`。

## 参考资料

- MXFP4 (Microscaling)：<https://arxiv.org/abs/2310.10537>
- DeepSeek-V4 技术报告第 5.2.1 节。
- README Model Downloads 表（FP4 + FP8 Mixed 部署）。

## 使用此技术的模型

| 模型              | 变体 / 细节                                                                                                                                                                                                        |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| DeepSeek-V4-Pro   | MoE 专家权重 FP4（config.expert_dtype="fp4"）。CSA indexer QK 路径 FP4。Index scores 从 FP32 量化到 BF16（top-k 选择器 2× 加速，99.7% 召回）。KV cache：RoPE 维度走 BF16 + 其余维度走 FP8（~纯 BF16 的一半大小）。 |
| DeepSeek-V4-Flash | FP4 QAT 配方与 V4-Pro 完全相同（同 config.quantization_config、同 expert_dtype="fp4"、同 indexer FP4、同 KV cache 混合精度）。                                                                                     |

## 相关技术

- [FP8 mixed precision（DeepSeek-V3 变体）](./fp8-mixed-precision.zh.md) — V4 继承的预训练框架；FP4 QAT 在其之上、在后训练阶段叠加。
