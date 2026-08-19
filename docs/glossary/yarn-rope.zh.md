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

| 模型              | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3       | **只**作用在 MLA 中解耦的 RoPE key（`k_t^R`）上。两阶段扩展：4K→32K→128K，每阶段 1000 步。Config：`factor=40`（40 × 4096 原始 = 163840 max），`beta_fast=32`，`beta_slow=1`，`mscale=1.0`。烘焙进 HF `config.json` 的 `rope_scaling`。                                                                                                                                                                                                                                                    |
| Qwen3-32B         | 与 **Dual Chunk Attention** 组合，在部署阶段做 4× 扩展（训练 32K → 服务 128K）。预训练 Long-Context 阶段先把 RoPE base 通过 ABF 从 10K 提升到 1M、并在 32,768 上训练；YaRN+DCA 在推理时（vLLM/SGLang config）应用，且 *刻意* 不烘焙进 HF `config.json`（`rope_scaling=null`）。                                                                                                                                                                                                           |
| Qwen3-235B-A22B   | 与 Qwen3-32B 同样的 YaRN+DCA 食谱（部署期、factor 4，原始 32,768 → 131,072）。                                                                                                                                                                                                                                                                                                                                                                                                            |
| Qwen3.5-27B       | 纯 YaRN（无 DCA）。静态、需在部署侧通过 vLLM/SGLang flag 显式打开；静态 `config.json` 出厂时 `rope_type=default`，原生窗口 262K。README `factor=4.0`，`original_max_position_embeddings=262144`，把有效上下文 **262K → ~1010K**。与 **mRoPE**（`mrope_section=[11,11,10]`，`mrope_interleaved=true`）和 **partial RoPE**（`partial_rotary_factor=0.25`，256 维头中只 64 维 rotary）共存。README 提示实现是静态的（factor 与输入长度无关）；典型 524K 以下使用，`factor=2.0` 优于完整 4×。 |
| Qwen3.5-35B-A3B   | YaRN 食谱与 27B 兄弟完全相同——同样的 `factor=4.0`、同样的 `original_max_position_embeddings=262144`、同样的部署期 opt-in 激活。家族级配置，dense vs MoE 不影响长上下文扩展。                                                                                                                                                                                                                                                                                                              |
| Qwen3.6-27B       | 与 Qwen3.5-27B 完全相同——同样的 `factor=4.0`、同样的 `original_max_position_embeddings=262144`，通过推理框架 flag opt-in。3.6 整体继承 3.5 的长上下文食谱。                                                                                                                                                                                                                                                                                                                               |
| Qwen3.6-35B-A3B   | 与 Qwen3.5-35B-A3B 完全相同；家族级食谱在所有四个 Qwen3.5/3.6 slug 间共享。                                                                                                                                                                                                                                                                                                                                                                                                               |
| DeepSeek-V4-Pro   | YaRN scaling 静态配置在 `config.json`（`rope_scaling.type=yarn`，`factor=16`，`original_max_position_embeddings=65536`，`beta_fast=32`，`beta_slow=1`，`rope_theta=10,000`）。不同于 V3 在部署时把 4K 拉伸 40×，V4-Pro 在预训练阶段直接训到 1M（4K → 16K → 64K → 1M 课程化）；YaRN 在这里的作用是让 RoPE 基长度与压缩 KV 的位置锚点对齐，而不是在短的预训练窗口上做扩展。CSA/HCA 压缩 KV 分支额外使用 `compress_rope_theta=160,000`。                                                     |
| DeepSeek-V4-Flash | YaRN 配置与 V4-Pro 相同（`factor=16`，`original_max_position_embeddings=65536`，`compress_rope_theta=160,000`）。同样的课程化 1M 上下文训练。                                                                                                                                                                                                                                                                                                                                             |
| Kimi K2.5         | YaRN 烘焙进 HF `config.json`（`type='yarn'`，`factor=64`，`original_max_position_embeddings=4096`，`beta_fast=32`，`beta_slow=1`，`mscale=1.0`，`rope_theta=50000`）。联合预训练在 4K 跑，mid-training 通过 YaRN 插值序贯扩展到 32K 再到 256K（论文 §4.3 / Table 3：500B tokens at 32K，再 200B at 256K）。64× 扩展 = 4096 → 262144。                                                                                                                                                     |
| Kimi K2.6         | 与 K2.5 完全一致——`factor=64`，`beta_fast=32`，`beta_slow=1`，`original_max_position_embeddings=4096`，`rope_theta=50000`。K2.6 是后训练-only 刷新，长上下文配方继承自 K2.5。                                                                                                                                                                                                                                                                                                             |
| Kimi K2-Thinking  | 同样的家族级 YaRN（`factor=64`，`original_max_position_embeddings=4096`，`rope_theta=50000`），但 `beta_fast=1.0`（K2.5/K2.6 是 `beta_fast=32.0`）——K2 家族里 YaRN 配置上的唯一差异。效果：因为 `beta_fast == beta_slow == 1`，K2-Thinking 把 YaRN 的"快"区域校正应用到所有 RoPE 频率上；K2.5/K2.6 则按 YaRN 论文推荐在快慢区域之间做 split。                                                                                                                                             |
| DeepSeek-V3.2-Exp | `rope_scaling` 与 DeepSeek-V3 逐字节相同（type=yarn、factor=40、original_max_position_embeddings=4096、beta_fast=32、beta_slow=1、mscale=1.0、rope_theta=10000）。V3.1 一脉在挂上 DSA 之前就已扩展并训练到 128K，因此 V3.2-Exp 是继承这个窗口而非再做扩展 —— 它的贡献是让该窗口*更便宜*，而不是更长。                                                                                                                                                                                     |
| Kimi K3           | **刻意不使用 YaRN 或任何 RoPE 缩放** —— 作为反例列在此处。K3 采用 NoPE（`mla_use_nope=true`），通过 [KDA](./kda.zh.md) 的逐通道衰减递推隐式承载位置信息，论文指出这样「在扩展上下文长度时无需修改位置编码参数，例如重新调 RoPE 频率基或套用 YaRN」。1M 上下文由四阶段课程达成（预训练 8K → 64K，cooldown 256K → 1M），而不是从更短的训练窗口外推。与经 YaRN factor 64 达到 256K 的 K2 家族形成清晰对照。                                                                                  |
| Qwen3.8-27B       | 食谱与 Qwen3.5/3.6-27B 相同——在 `original_max_position_embeddings=262144` 之上 `factor=4.0`，服务时 opt-in。只有上限措辞变了（这里写 1,000,000，而 3.5/3.6 卡片和 2.4T 兄弟写 1,010,000）。**Qwen3.8-2.4T-A95B 的卡片声称 1,010,000 上限却完全没给 YaRN 配置块**，因此其扩展方法记为 UNKNOWN，不做推测。                                                                                                                                                                                  |

## 相关技术

- [MLA](./mla.md) — DeepSeek-V3 的 MLA 只在小的解耦 RoPE key 向量上承载 RoPE，所以 YaRN 是精准施加而非全 KV 施加
- [Dual Chunk Attention](./dual-chunk-attention.md) — Qwen3 把 DCA 叠加在 YaRN 之上以达到 4× 扩展并在长上下文保持精度
