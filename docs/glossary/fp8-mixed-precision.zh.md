# FP8 mixed precision（DeepSeek-V3 变体）

> English: [fp8-mixed-precision.md](./fp8-mixed-precision.md)

**Slug:** `fp8-mixed-precision`
**类别：** quantization
**一句话概括：** 一种训练精度食谱——在带细粒度 tile/block 缩放的 FP8（E4M3）下跑计算密集型 GEMM，同时把对精度敏感的算子（embedding、attention、normalization、optimizer state）保留在 BF16/FP32。
**首次提出（在此形态下）：** [DeepSeek-V3 Technical Report (DeepSeek-AI, 2024)](https://arxiv.org/abs/2412.19437)（§3.3）。建立在更早的 FP8 训练提议之上（如 NVIDIA Transformer Engine、Peng et al. 2023b）。

## 概述

DeepSeek-V3 的混合精度食谱是公开报告中第一个在前沿规模（671B 参数 MoE）预训练上成功应用 FP8 的案例。关键设计：

- **全 E4M3**，而非标准的 forward-E4M3 / backward-E5M2 混合。下面的细粒度缩放补偿了 E4M3 较小的动态范围。
- **细粒度量化缩放**——activation 按 `1×128` tile 缩放（每 token、每 128 通道）；weight 按 `128×128` block 缩放。这正是让全 E4M3 在大规模上可行的关键。
- **在线量化**——缩放因子每步重新计算，而不是用历史最大值跟踪。
- **CUDA core 提升累加精度**——Hopper Tensor Core 的 FP8 GEMM 内部累加只有约 14 比特；DeepSeek-V3 每 Nc=128 个元素就把部分和提升到 CUDA core 的 FP32 寄存器累加，恢复精度。
- **保留高精度**的部分：embedding、输出头、MoE 门控、normalization、attention。AdamW 一阶 / 二阶矩存为 BF16；master weight 和梯度累加器为 FP32。激活以 FP8 缓存供反向使用。

报告的相对损失误差（vs BF16）始终低于 0.25%。

## 参考资料

- DeepSeek-V3 论文 §3.3：<https://arxiv.org/abs/2412.19437>
- NVIDIA FP8 入门：<https://docs.nvidia.com/deeplearning/transformer-engine/user-guide/index.html>

## 使用此技术的模型

| 模型              | 变体 / 细节                                                                                                                                                                                                                                                                                                                                        |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3       | 食谱如上所述。在 V2-Lite 和 V2-scale baseline 上验证了约 1T tokens，再开始全量 V3 训练。                                                                                                                                                                                                                                                           |
| DeepSeek-V4-Pro   | 预训练沿用 V3 的 FP8 框架（E4M3，细粒度 1×128 / 128×128 缩放，每 Nc=128 个元素在 FP32 寄存器中累加）。后训练在其上叠加 FP4 QAT（MXFP4）：MoE 专家权重（config.expert_dtype='fp4'）和 CSA Lightning Indexer 的 QK 路径走 FP4，并能无损反量化回 FP8；KV cache 把 RoPE 维度存成 BF16，其余维度走 FP8（比纯 BF16 节省约一半）。推理使用原生 FP4 权重。 |
| DeepSeek-V4-Flash | 与 V4-Pro 相同的预训练 FP8 + 后训练 FP4 QAT 配方（同 config.quantization_config）。                                                                                                                                                                                                                                                                |

## 相关技术

- _Block-wise INT8 量化（LLM.int8、GPTQ）_ — 推理期的对应方法
