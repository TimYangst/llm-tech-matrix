# MiniMax-Speech-2.8

> English: [minimax-speech-2.8.md](./minimax-speech-2.8.md)

*媒体 schema 版本: 1*

## 发布信息与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | MiniMax-Speech-2.8 | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 系列 | MiniMax | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 组织 | MiniMax | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 发布日期 | 2026-01 | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 开放程度 | closed | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 许可证 | [Unknown/Not Disclosed] | — |
| 变体范围 | Hosted Speech 2.8 service announced January 23, 2026. Official announcement links the Open Platform and Audio product; no model checkpoint or self-hosted architecture is disclosed there. This record covers those public capabilities, not an open-weight release. | [source 1](https://www.minimax.io/news/minimax-speech-28) |

## 生成机制

| 字段 | 值 | 证据 |
|---|---|---|
| 输入模态 | text; audio | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 输出模态 | audio | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 任务 | text-to-speech; voice-cloned text-to-speech | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 生成目标 | [Unknown/Not Disclosed] | — |
| 调度器 | [Unknown/Not Disclosed] | — |
| 采样 | [Unknown/Not Disclosed] | — |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 主干网络 | [Unknown/Not Disclosed] | — |
| 参数量 | [Unknown/Not Disclosed] | — |
| 注意力 | [Unknown/Not Disclosed] | — |
| 条件输入 | Text includes native sound tags for fillers and nonverbal cues. Vendor describes voice cloning from a 10-second reference sample. Reference audio is conditioning for voice identity, not a claim of unrestricted audio-to-audio generation. | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| VAE | [Unknown/Not Disclosed] | — |
| 音频编解码器 | [Unknown/Not Disclosed] | — |
| 多模态耦合 | [Unknown/Not Disclosed] | — |
| 实现 | Hosted Open Platform API and MiniMax Audio are the access routes named in the announcement. | [source 1](https://www.minimax.io/news/minimax-speech-28) |

## 输出

| 字段 | 值 | 证据 |
|---|---|---|
| 分辨率 | [Unknown/Not Disclosed] | — |
| 帧率 | [Unknown/Not Disclosed] | — |
| 时长 | [Unknown/Not Disclosed] | — |
| 音频采样率 | [Unknown/Not Disclosed] | — |
| 音频声道 | [Unknown/Not Disclosed] | — |
| 格式 | — | — |

## 训练

| 字段 | 值 | 证据 |
|---|---|---|
| 训练数据 | [Unknown/Not Disclosed] | — |
| 预训练 | [Unknown/Not Disclosed] | — |
| 后训练 | [Unknown/Not Disclosed] | — |

## 精度

| 字段 | 值 | 证据 |
|---|---|---|
| 权重精度 | [Unknown/Not Disclosed] | — |
| 计算精度 | [Unknown/Not Disclosed] | — |
| 量化 | [Unknown/Not Disclosed] | — |

## 发布产物与限制

| 字段 | 值 | 证据 |
|---|---|---|
| 已发布产物 | — | — |
| 托管流程范围 | Speech 2.8 text-to-speech with native sound tags, voice cloning and cross-lingual improvements is offered through Open Platform and MiniMax Audio. | [source 1](https://www.minimax.io/news/minimax-speech-28) |
| 限制 | Announcement provides capabilities and demos rather than architecture, weights, training details or output-format specifications.; Voice similarity and noise-removal improvements are vendor claims; no runtime or listening evaluation was performed here. | [source 1](https://www.minimax.io/news/minimax-speech-28) |

## 开放问题

- Backbone, parameters, training objective/data/optimizer, codec and deployment precision are undisclosed in the registered announcement.
- Sample rate, channels, output formats and request limits need version-specific API evidence before they can be filled.
- Earlier Speech 02 /2.5 /2.6 services remain inventory items; the open Speech test dataset is not a release of model weights.

## 来源

- [Source 1](https://www.minimax.io/news/minimax-speech-28)
