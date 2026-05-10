# Multimodal RoPE (mRoPE)

> English: [mrope.md](./mrope.md)

**Slug:** `mrope`
**类别：** position-embedding
**一句话概括：** RoPE 的一种变体——把 rotary 头维度划分成若干"段"，分别绑定到不同的位置轴（时间、高度、宽度），让单一注意力层在同一个 RoPE 空间里同时编码 1D 文本位置、2D 图像位置和 3D 视频位置。
**首次提出：** [Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution (Wang et al., 2024)](https://arxiv.org/abs/2409.12191)（论文中称 "M-RoPE"）

## 概述

标准 RoPE 把每对相邻头维度按一个标量位置成比例旋转。但多模态序列里"位置"不再是标量——一个图像 patch 有 (height, width)；一帧视频有 (time, height, width)。把它们扁平成 1D 索引虽然能用，但丢掉了注意力本可利用的空间结构。

mRoPE 的做法是把 rotary 头维度划分成命名的 **section**，每个 section 对应一个位置轴，并对该 section 应用轴特定的旋转：

- **`mrope_section`**——section 大小列表，例如 `[t, h, w]`。前 `t` 对 rotary pair 编码时间位置，下 `h` 对编码 height，最后 `w` 对编码 width。对纯文本 token，三个轴共享 1D 文本位置，组合后退化为标准 RoPE。
- **`mrope_interleaved`**——为 `true` 时 section 索引在 rotary 维度上交错排布，而非连续块；实证上能减少频段碰撞。
- 常常与 **partial RoPE**（`partial_rotary_factor < 1.0`）配合：只对一部分头维度做 rotary，剩下的是 NoPE，让模型同一头里同时承载相对位置通道和纯内容通道。

mRoPE 与 YaRN 自然组合：YaRN 因子在每个轴内独立伸缩频率，与 section 划分无冲突。

## 参考资料

- 原始论文（Qwen2-VL §3）：<https://arxiv.org/abs/2409.12191>
- HF Transformers 参考实现：`transformers/models/qwen2_vl/modeling_qwen2_vl.py` `apply_multimodal_rotary_pos_emb`

## 使用此技术的模型

| 模型            | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                     |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Qwen3.5-27B     | 静态 config 中 `rope_type="default"`（不论是否启用 YaRN，底层都是 mRoPE）。`mrope_section=[11, 11, 10]`（temporal、height、width），`mrope_interleaved=true`。配合 **partial RoPE** `partial_rotary_factor=0.25`——256 个注意力头维中只有 64 维做 rotary，剩下 192 维是 NoPE。仅在 Gated Attention 层（每 4 层 1 层）应用；Gated DeltaNet 层不用 RoPE。`rope_theta=10,000,000`。 |
| Qwen3.5-35B-A3B | mRoPE 配置与 27B 兄弟完全相同：`mrope_section=[11, 11, 10]`，`mrope_interleaved=true`，`partial_rotary_factor=0.25`，`rope_theta=10,000,000`。在每 4 层 1 层应用（40 层中 10 个 Gated Attention 层）。mRoPE 设置在 dense-27B 和 MoE-35B-A3B 间是家族级固定的。                                                                                                                  |
| Qwen3.6-27B     | mRoPE 配置与 Qwen3.5-27B 完全相同——同样的 section、interleaving、partial-rotary 比例、base。后训练-only 的 3.6 刷新原样继承。                                                                                                                                                                                                                                                   |
| Qwen3.6-35B-A3B | mRoPE 配置与 Qwen3.5-35B-A3B 完全相同（也与全部四个 Qwen3.5/3.6 slug 完全相同）；家族级固定。                                                                                                                                                                                                                                                                                   |

## 相关技术

- [YaRN RoPE scaling](./yarn-rope.md) — Qwen3.5 在 mRoPE 之上叠加的正交上下文扩展层
