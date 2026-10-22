# 媒体生成模型索引

由媒体提取 JSON 自动生成。开放范围、输出限制和托管组件的区别见各模型记录。

| 模型 | 系列 | 日期 | 开放程度 | 输入 → 输出 | 已发布产物 |
|---|---|---|---|---|---|
| [MiniMax-H3](./minimax-h3.zh.md) | MiniMax | 2026-08 | mixed | text, image, video, audio → video, audio | FL2VA base checkpoint: text or optional first/last image to audio-video; Ref2VA base checkpoint: text plus image/video/audio references to audio-video; Qwen3-VL-32B-derived encoder, tokenizer, visual and audio VAEs; configs and deployment examples |
| [MiniMax-Music3](./minimax-music3.zh.md) | MiniMax | 2026-08 | open_weights | text → audio | Global and Local LLM components, condition encoder, flow-matching transformer and Flow-VAE/vocoder configs and weights; Pinned public card, license and end-to-end inference example |
| [MiniMax-Speech-2.8](./minimax-speech-2.8.zh.md) | MiniMax | 2026-01 | closed | text, audio → audio | — |
