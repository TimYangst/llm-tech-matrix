# YaRN RoPE scaling

> English: [yarn-rope.md](./yarn-rope.md)

**Slug:** `yarn-rope`
**类别：** position-embedding
**一句话概括：** 一种 RoPE 位置编码扩展方法——按头维度跨频段做非均匀插值，使模型能以极小的微调代价支持远超原训练长度的上下文窗口。
**首次提出：** [YaRN: Efficient Context Window Extension of Large Language Models (Peng et al., 2023)](https://arxiv.org/abs/2309.00071)

## 概述

标准 RoPE 通过逐维旋转频率编码绝对位置。朴素的上下文扩展（线性插值频率，"PI"）能用但质量下降；"NTK-aware" 插值更好但仍然有上限。YaRN 观察到不同 RoPE 维度承载不同尺度的位置信息，于是按维度频段分别采用不同的插值策略：

- **高频维度**：外推（不做处理）——它们本来就被平均掉了。
- **低频维度**：插值（PI 风格）——它们需要被拟合到新长度。
- **中频段**：在两种策略之间做平滑过渡。

YaRN 还会重新缩放注意力温度（`mscale`）以补偿更长的等效序列长度。这种扩展通常只需要短微调（数千步）就能恢复质量。

## 参考资料

- 原始论文：<https://arxiv.org/abs/2309.00071>

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3     | **只**作用在 MLA 中解耦的 RoPE key（`k_t^R`）上。两阶段扩展：4K→32K→128K，每阶段 1000 步。Config：`factor=40`（40 × 4096 原始 = 163840 max），`beta_fast=32`，`beta_slow=1`，`mscale=1.0`。烘焙进 HF `config.json` 的 `rope_scaling`。                                                                                                                                                                                                                                                    |
| Qwen3-32B       | 与 **Dual Chunk Attention** 组合，在部署阶段做 4× 扩展（训练 32K → 服务 128K）。预训练 Long-Context 阶段先把 RoPE base 通过 ABF 从 10K 提升到 1M、并在 32,768 上训练；YaRN+DCA 在推理时（vLLM/SGLang config）应用，且 *刻意* 不烘焙进 HF `config.json`（`rope_scaling=null`）。                                                                                                                                                                                                           |
| Qwen3-235B-A22B | 与 Qwen3-32B 同样的 YaRN+DCA 食谱（部署期、factor 4，原始 32,768 → 131,072）。                                                                                                                                                                                                                                                                                                                                                                                                            |
| Qwen3.5-27B     | 纯 YaRN（无 DCA）。静态、需在部署侧通过 vLLM/SGLang flag 显式打开；静态 `config.json` 出厂时 `rope_type=default`，原生窗口 262K。README `factor=4.0`，`original_max_position_embeddings=262144`，把有效上下文 **262K → ~1010K**。与 **mRoPE**（`mrope_section=[11,11,10]`，`mrope_interleaved=true`）和 **partial RoPE**（`partial_rotary_factor=0.25`，256 维头中只 64 维 rotary）共存。README 提示实现是静态的（factor 与输入长度无关）；典型 524K 以下使用，`factor=2.0` 优于完整 4×。 |
| Qwen3.5-35B-A3B | YaRN 食谱与 27B 兄弟完全相同——同样的 `factor=4.0`、同样的 `original_max_position_embeddings=262144`、同样的部署期 opt-in 激活。家族级配置，dense vs MoE 不影响长上下文扩展。                                                                                                                                                                                                                                                                                                              |
| Qwen3.6-27B     | 与 Qwen3.5-27B 完全相同——同样的 `factor=4.0`、同样的 `original_max_position_embeddings=262144`，通过推理框架 flag opt-in。3.6 整体继承 3.5 的长上下文食谱。                                                                                                                                                                                                                                                                                                                               |
| Qwen3.6-35B-A3B | 与 Qwen3.5-35B-A3B 完全相同；家族级食谱在所有四个 Qwen3.5/3.6 slug 间共享。                                                                                                                                                                                                                                                                                                                                                                                                               |

## 相关技术

- [MLA](./mla.md) — DeepSeek-V3 的 MLA 只在小的解耦 RoPE key 向量上承载 RoPE，所以 YaRN 是精准施加而非全 KV 施加
- [Dual Chunk Attention](./dual-chunk-attention.md) — Qwen3 把 DCA 叠加在 YaRN 之上以达到 4× 扩展并在长上下文保持精度
