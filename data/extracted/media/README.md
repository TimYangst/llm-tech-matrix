# Media generation model index

Generated from media extraction JSON. Each record distinguishes released weights, output limits and hosted pipeline components.

| Model | Family | Date | Openness | Input → output | Released artifacts |
|---|---|---|---|---|---|
| [MiniMax-H3](./minimax-h3.md) | MiniMax | 2026-08 | mixed | text, image, video, audio → video, audio | FL2VA base checkpoint: text or optional first/last image to audio-video; Ref2VA base checkpoint: text plus image/video/audio references to audio-video; Qwen3-VL-32B-derived encoder, tokenizer, visual and audio VAEs; configs and deployment examples |
| [MiniMax-Music3](./minimax-music3.md) | MiniMax | 2026-08 | open_weights | text → audio | Global and Local LLM components, condition encoder, flow-matching transformer and Flow-VAE/vocoder configs and weights; Pinned public card, license and end-to-end inference example |
| [MiniMax-Speech-2.8](./minimax-speech-2.8.md) | MiniMax | 2026-01 | closed | text, audio → audio | — |
