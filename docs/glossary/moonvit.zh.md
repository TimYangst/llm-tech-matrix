# MoonViT — 原生分辨率 + 3D 时序视觉编码器

> English: [moonvit.md](./moonvit.md)

**Slug:** `moonvit`
**类别：** vision encoder
**一句话概括：** 一个由 SigLIP 初始化的原生分辨率视觉编码器，使用 NaViT 的 patch 打包策略支持可变分辨率训练；K2.5 把它扩展为 3D，把最多 4 个连续视频帧当作一个时空体打包成一条 1D 序列——图像和视频共享权重、共享嵌入空间、共用同一个注意力机制。
**首次提出：** [Kimi-VL Technical Report (Moonshot AI, 2025)](https://arxiv.org/abs/2504.07491) 提出 MoonViT；3D 扩展和联合预训练配方在 [Kimi K2.5: Visual Agentic Intelligence (Moonshot AI, 2026)](https://arxiv.org/abs/2602.02276) §4.2 落地。

## 概述

标准视觉编码器只支持固定的输入分辨率（如 224×224、336×336），高分辨率输入需要复杂的子图切分 + 拼接。MoonViT 跳过这种固定网格：图像在原生分辨率上切 patch，再把 patch 展平串联成一条 1D 序列——这就是 NaViT 的 "patch n' pack" 策略——所以一个 batch 可以容纳任意混合分辨率的图像，编码器在一次共享前向中全部跑完。

K2.5 把 MoonViT 扩展成 **MoonViT-3D**：把最多 4 个连续视频帧当作一个时空体，它们的 2D patch 联合展平后打包到一条 1D 序列中，让同一个注意力机制在空间和时间上无缝运作，而不需要单独的时序注意力模块。图像与视频 **共享全部权重** 和 **同一个嵌入空间**——架构上不分叉。projector 端轻量的时序池化把 4 帧压成 1 个 patch group，给出 4× 时序压缩——固定上下文窗口下能装 4 倍长的视频。

编码器从 **SigLIP-SO-400M**（约 4 亿参数）初始化，仅用 caption loss 持续预训练（与 Kimi-VL 不同，没有 contrastive loss）。两阶段对齐：阶段 1 让 MoonViT-3D 与小模型 Moonlight-16B-A3B 通过 caption loss 对齐（约 1T tokens，FLOPs 极低）；阶段 2 极短，只更新 MLP projector 把 MoonViT 桥接到 1T 的 K2 主干。

K2.5/K2.6 的 HF config 中，编码器以 `vision_config` 出现：depth=27、hidden=1152、intermediate=4304、num_heads=16、patch_size=14、projector_type='patchmerger'、merge_kernel_size=[2,2]、video_attn_type='spatial_temporal'、text_hidden_size=7168。

## 参考资料

- Kimi-VL 技术报告（提出 MoonViT 的 2D 版本）：<https://arxiv.org/abs/2504.07491>
- Kimi K2.5（提出 MoonViT-3D + 联合预训练配方）：<https://arxiv.org/abs/2602.02276>
- NaViT（patch n' pack）：<https://arxiv.org/abs/2307.06304>
- SigLIP（编码器初始化权重）：<https://arxiv.org/abs/2303.15343>

## 使用此技术的模型

| 模型      | 变体 / 细节                                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Kimi K2.5 | MoonViT-3D，27 层 / 1152 hidden / 4304 intermediate / 16 头 / patch_size=14 / 4 帧时空体 / merge_kernel_size=[2,2]（`sd2_tpool`）→ 经 `patchmerger` 投影到 LM hidden_size 7168。Preprocessor：image_mean/std=[0.5,0.5,0.5]，in_patch_limit=16384，in_patch_limit_each_frame=4096，sample_fps=2.0，temporal_merge_kernel_size=4，timestamp_mode='hh:mm:ss.fff'。与 K2 主干联合预训练 ~15T 混合视觉-文本 tokens（vision 占比恒定且较低）。 |
| Kimi K2.6 | MoonViT-3D + preprocessor 与 K2.5 完全一致（后训练-only 刷新；preprocessor_config.json 字节级相同）。                                                                                                                                                                                                                                                                                                                                    |

## 相关技术

- [YaRN RoPE scaling](./yarn-rope.zh.md) — K2.5 mid-training 通过 YaRN 把序列长度从 32K 扩到 256K，与 MoonViT-3D 的 4× 时序压缩叠加后给出更大的有效视频预算。
- [Native INT4 QAT](./int4-qat.zh.md) — MoonViT 和 MLP projector 在 K2.5/K2.6 的 INT4 量化中明确被排除（`config.quantization_config.ignore`）。
