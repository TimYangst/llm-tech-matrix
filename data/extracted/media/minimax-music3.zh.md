# MiniMax-Music3

> English: [minimax-music3.md](./minimax-music3.md)

*媒体 schema 版本: 1*

## 发布信息与范围

| 字段 | 值 | 证据 |
|---|---|---|
| 名称 | MiniMax-Music3 | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 系列 | MiniMax | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 组织 | MiniMax | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 发布日期 | 2026-08 | [source 1](https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model) |
| 开放程度 | open_weights | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 许可证 | MiniMax-Music3 Community License; see pinned LICENSE. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/LICENSE) |
| 变体范围 | One released text-to-music pipeline: Global LLM + Local LLM + hidden-state fusion + Flow Matching + Flow-VAE decoder. Lyrics and music description are complementary text inputs; this record does not treat Music3 as a general chat LLM or a TTS voice-cloning model. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |

## 生成机制

| 字段 | 值 | 证据 |
|---|---|---|
| 输入模态 | text | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 输出模态 | audio | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 任务 | lyrics-and-description-to-music | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 生成目标 | Hierarchical autoregressive RVQ-codebook prediction plus continuous hidden-state synthesis using Flow Matching and Flow-VAE. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 调度器 | FlowMatchEulerDiscreteScheduler: shift=1.0, invert_sigmas=true, use_dynamic_shifting=false, stochastic_sampling=false; num_train_timesteps=1 is a config value and does not establish the training budget or universal inference-step count. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/scheduler/scheduler_config.json) |
| 采样 | Card example uses seed=7 and max_new_tokens=750 acoustic frames; each frame represents 1/25 second, with early termination at end-of-audio. A separate diffusers example requests audio_duration=60.0. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |

## 架构

| 字段 | 值 | 证据 |
|---|---|---|
| 主干网络 | Hierarchical Hybrid-LM: Qwen3-8B-initialized Global LLM predicts first RVQ codebook frame by frame; 0.6B Local LLM predicts remaining codebooks within a frame. Hidden-state fusion conditions a 2.4B flow-matching synthesis model and 123M Flow-VAE decoder. Global config: 36 layers, hidden=4096, FFN=12288, vocab=200000, max_position_embeddings=10240. Local config: 4 layers, hidden=4096, 8 codebooks. Synthesis transformer: 36 layers, 32 heads, head_dim=64, in_channels=128. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/language_model/config.json), [source 3](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/rvq_depth_decoder/config.json), [source 4](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/transformer/config.json) |
| 参数量 | Component counts from card: Global LLM 8B; Local LLM 0.6B; Flow Matching 2.4B; Flow-VAE decoder 123M. A complete unique-parameter accounting for the full pipeline is not supplied. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 注意力 | Global LLM: full attention in all 36 layers, 32 query heads /8 KV heads, head_dim=128, RoPE theta=1000000. Synthesis model: 32 attention heads, head_dim=64, rotary_dim=32. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/language_model/config.json), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/transformer/config.json) |
| 条件输入 | Lyrics with section tags define sung words and song structure; music description provides genre, emotion, vocal performance, instruments, arrangement and production. Fused final Global/Local hidden states condition the flow-matching path. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| VAE | Flow-VAE adapted from MiniMax Speech and retrained for music; card reports 123M decoder. Released vocoder config: latent_channels=128, decoder_hidden_dim=1536, upsampling_ratios=[8,8,4,2]. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/vocoder/config.json) |
| 音频编解码器 | Training uses 8-layer RVQ: first semantic codebook has 16384 entries, remaining 7 acoustic codebooks have 1024 each. Semantic codebook is trained first, then all codebooks jointly. Inference waveform synthesis uses fused continuous hidden states rather than the discrete tokenizer decoder. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 多模态耦合 | Text-conditioned music with expressive vocals and accompaniment in one audio output; no video generation or audio-reference conditioning is asserted by the registered card. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 实现 | MiniMaxMusic3ForConditionalGeneration architecture; card provides SGLang-Omni shared /v1/audio/speech endpoint and a diffusers modular pipeline. Endpoint naming alone does not establish general speech synthesis support. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/config.json) |

## 输出

| 字段 | 值 | 证据 |
|---|---|---|
| 分辨率 | [Unknown/Not Disclosed] | — |
| 帧率 | 25 acoustic frames/second (not a video frame rate) | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 时长 | Up to five minutes per model card. The same card lists an implementation cap of 9000 acoustic frames; this cap and 25 frames/second must not be interpreted as a documented six-minute capability. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 音频采样率 | Card/API response: 32 kHz. Registered diffusers vocoder and condition-encoder configs specify 44100 Hz output; serving-path discrepancy is unresolved. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/vocoder/config.json), [source 3](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/condition_encoder/config.json) |
| 音频声道 | Stereo (2 channels) | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 格式 | 16-bit WAV (card/API example) | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |

## 训练

| 字段 | 值 | 证据 |
|---|---|---|
| 训练数据 | [Unknown/Not Disclosed] | — |
| 预训练 | Global LLM initializes from Qwen3-8B. Embedding and output layers are first adapted to semantic music tokens, then Global and Local LLMs are jointly trained on all RVQ codebooks. Flow-VAE is retrained for musical dynamics/spectral properties. Token/data totals, optimizer and training compute are undisclosed. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 后训练 | [Unknown/Not Disclosed] | — |

## 精度

| 字段 | 值 | 证据 |
|---|---|---|
| 权重精度 | Global LLM config dtype=bfloat16; card loads modular pipeline components with torch.bfloat16. No claim that every stored tensor has this dtype. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/language_model/config.json) |
| 计算精度 | [Unknown/Not Disclosed] | — |
| 量化 | [Unknown/Not Disclosed] | — |

## 发布产物与限制

| 字段 | 值 | 证据 |
|---|---|---|
| 已发布产物 | Global and Local LLM components, condition encoder, flow-matching transformer and Flow-VAE/vocoder configs and weights; Pinned public card, license and end-to-end inference example | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md) |
| 托管流程范围 | [Unknown/Not Disclosed] | — |
| 限制 | Card lists CUDA-only, non-streaming inference.; Card limits tokenized text prompt to 5000 tokens and generation to 9000 acoustic frames.; The card/API sample rate (32000 Hz) differs from released diffusers vocoder/condition-encoder output settings (44100 Hz); this repository has not run either serving path. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/vocoder/config.json), [source 3](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/condition_encoder/config.json) |

## 开放问题

- Official dated launch article is August 13, 2026; earlier HF repository creation is not treated as the launch date. The launch article says Global LLM initializes from Qwen3.5-8B, while the pinned checkpoint card says Qwen3-8B and its language-model config identifies Qwen3ForCausalLM. Checkpoint architecture follows config/card; initialization provenance conflict remains unresolved.
- Resolve 32 kHz card/API output versus 44.1 kHz diffusers vocoder/condition-encoder configuration at this exact revision.
- Card advertises five-minute songs but also lists 9000 acoustic frames and 25 frames/second; retain the capability statement and implementation cap separately.
- No model-weight downloads, inference runs, quality evaluation or GPU-memory measurements were performed. Vendor runtime/memory examples are not independently validated.

## 来源

- [Source 1](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/README.md)
- [Source 2](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/LICENSE)
- [Source 3](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/config.json)
- [Source 4](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/language_model/config.json)
- [Source 5](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/transformer/config.json)
- [Source 6](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/vocoder/config.json)
- [Source 7](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/rvq_depth_decoder/config.json)
- [Source 8](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/condition_encoder/config.json)
- [Source 9](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/scheduler/scheduler_config.json)
- [Source 10](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/qwen_7B/qwen_7B/config.json)
- [Source 11](https://huggingface.co/MiniMaxAI/MiniMax-Music3/raw/fbdf52fbaaca799592917417eb05f1899f1255ec/scripts/end_to_end/minimax_ttm_test.py)
- [Source 12](https://www.minimax.io/blog/minimax-music-3-0-next-generation-open-weights-production-ready-versatile-music-model)
