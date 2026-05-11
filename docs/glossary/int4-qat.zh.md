# Native INT4 量化感知训练（QAT）

> English: [int4-qat.md](./int4-qat.md)

**Slug:** `int4-qat`
**类别：** quantization
**一句话概括：** 在后训练阶段做的 QAT，仅对 MoE 路由专家权重做 INT4（按组量化，group_size=32，对称），保留注意力、共享专家、dense FFN、lm_head、以及视觉塔在高精度——长解码"思考"型工作负载下生成速度约 2×，质量号称无损。
**首次提出：** [Kimi K2-Thinking (Moonshot AI, 2025)](https://moonshotai.github.io/Kimi-K2/thinking.html) 提出此部署配方；[Kimi K2.5](https://arxiv.org/abs/2602.02276) 与 Kimi K2.6 直接沿用未改。

## 概述

万亿参数规模下"事后"INT4 权重量化通常会损失质量，"思考"模型每次解码上万 token 时这种损失还会沿思维链放大。Kimi 的配方从两个方向规避了这点：

1. **QAT 放在后训练阶段**（不是预训练）：模型训练时已经知晓最终的 INT4 表示，优化器把量化误差吸收进权重，而不是让它在推理时浮现。K2-Thinking README §4：「我们在后训练阶段引入 Quantization-Aware Training (QAT)，对 MoE 组件做 INT4 weight-only 量化」。
2. **只量化路由专家权重**。HF `config.quantization_config.ignore` 模式明确排除：`re:.*self_attn.*`、`re:.*shared_experts.*`、`re:.*mlp\\.(gate|up|gate_up|down)_proj.*`、`lm_head`，以及（在 K2.5/K2.6 上）`re:vision_tower.*` 和 `re:mm_projector.*`。所以注意力路径、共享专家、dense FFN gate/up/down 投影、LM 头、整条视觉管道都跑在高精度（BF16）；只有路由专家线性层——在 384 个专家的 1T MoE 中是绝对主体的参数——是 INT4。

压缩格式是 `compressed-tensors` 的 `pack-quantized`：`group_size=32`、`num_bits=4`、`type=int`、`symmetric=true`、`strategy=group`、`observer=minmax`。如果需要更高精度部署，INT4 权重可通过官方 `compressed-tensors` 仓库展开为 FP8/BF16。K2-Thinking README 声称所有 benchmark 数字都是在 INT4 精度下产出的。

与 DeepSeek-V4 的 [FP4 QAT (MXFP4)](./fp4-qat.zh.md) 形成对照：思路相同（后训练 QAT，仅 MoE 专家权重），但 V4 用 FP4（E2M1 + 32 元素 micro-block 缩放），Kimi 用 INT4（32 元素对称整数缩放）。

## 参考资料

- Kimi K2-Thinking 博客（配方原典）：<https://moonshotai.github.io/Kimi-K2/thinking.html>
- Kimi K2-Thinking README §4 "Native INT4 Quantization"：<https://huggingface.co/moonshotai/Kimi-K2-Thinking>
- compressed-tensors 仓库：<https://github.com/vllm-project/compressed-tensors>

## 使用此技术的模型

| 模型             | 变体 / 细节                                                                                                                                                                                                                                                                                                                                   |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K2-Thinking | 配方原典。`config.quantization_config`：`format='pack-quantized'`、`group_size=32`、`num_bits=4`、`type=int`、`symmetric=true`、`strategy=group`、`observer='minmax'`。Ignore：`lm_head`、`re:.*self_attn.*`、`re:.*shared_experts.*`、`re:.*mlp\\.(gate\|up\|gate_up\|down)_proj.*`。生成速度约 2× 提升；所有 benchmark 在 INT4 精度下完成。 |
| Kimi K2.5        | 直接沿用 K2-Thinking 的配方（README §4：「Kimi-K2.5 adopts the same native int4 quantization method as Kimi-K2-Thinking」）。`ignore` 多两条以保留视觉管道：`re:vision_tower.*` 和 `re:mm_projector.*`。                                                                                                                                      |
| Kimi K2.6        | 与 K2.5 完全相同（README §4：「Kimi-K2.6 adopts the same native int4 quantization method as Kimi-K2-Thinking」）。config.quantization_config 与 K2.5 字节级一致，只有无关的 eos_token_id 字段不同。                                                                                                                                           |

## 相关技术

- [FP4 QAT (MXFP4)](./fp4-qat.zh.md) — DeepSeek-V4 类似的后训练 MoE 专家权重 QAT，但用 FP4 + micro-block 缩放，而不是 INT4 + 按组对称整数缩放。
- [DeepSeekMoE](./deepseekmoe.zh.md) — INT4 QAT 实际作用的 MoE 拓扑（只量化路由专家线性层；共享专家被排除）。
