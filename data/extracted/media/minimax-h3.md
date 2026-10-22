# MiniMax-H3

> 中文版：[minimax-h3.zh.md](./minimax-h3.zh.md)

*Media schema version: 1*

## Release identity and scope

| Field | Value | Evidence |
|---|---|---|
| Name | MiniMax-H3 | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Family | MiniMax | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Organization | MiniMax | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Release date | 2026-08 | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/LICENSE) |
| Openness | mixed | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| License | MiniMax H3 Community License Agreement; see pinned LICENSE for terms. The Qwen3-VL-32B encoder is separately Apache-2.0. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/LICENSE) |
| Variant policy | Released H3-Base has separate CFG-distilled BF16 FL2VA and Ref2VA checkpoints. Full hosted H3 additionally uses unreleased Context-IR preprocessing and Regenerate-2K. This record distinguishes that mixed system from its open-weight base. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |

## Generation

| Field | Value | Evidence |
|---|---|---|
| Input modalities | text; image; video; audio | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Output modalities | video; audio | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Tasks | text-to-audio-video; first/last-frame-to-audio-video; multimodal-reference-to-audio-video | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Objective | [Unknown/Not Disclosed] | — |
| Scheduler | Published MiniMaxH3Scheduler configs: video shift=12.0; audio shift=3.0. Training objective and solver details are not specified by these configs. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/scheduler/scheduler_config.json), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/audio_scheduler/scheduler_config.json) |
| Sampling | Released Omni-Transformer weights are CFG-distilled. No universal inference-step count is established by the registered card/config sources. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |

## Architecture

| Field | Value | Evidence |
|---|---|---|
| Backbone | Dense single-stream H3-Omni-Transformer (MiniMaxH3DiTModel): 50 layers, hidden_size=5376, num_attention_heads=56, attention_head_dim=128, FFN width=14336, token_refiner_num_layers=2. FL2VA and Ref2VA structural configs are identical. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/transformer/config.json), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/Ref2VA/transformer/config.json) |
| Parameters | 33B Omni-Transformer parameters, including approximately 13B AdaLN-branch parameters. The card says AdaLN outputs can be cached so these branch weights need not be loaded for inference-only deployment. This is not a full-pipeline parameter total: the Qwen3-VL-32B encoder and VAEs are separate. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Attention | Shared attention/FFN across modalities with modality-specific input/output and AdaLN branches; 3D MM-RoPE over time/height/width. Late-stage training uses native sparse attention, but the published initial inference implementation uses full attention; sparse kernels were promised separately. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Conditioning | H3-Encoder uses full pretrained Qwen3-VL-32B weights and layer-50 hidden states. Text uses this encoder; visual inputs use both H3-Encoder and VisualVAE; audio uses AudioVAE. Packed multimodal representations condition joint prediction. Ref2VA accepts up to 9 images, up to 3 video clips (2–15 s each, total <=15 s), up to 3 audio clips (same durations), with <=12 reference files in total. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| VAE | Temporally causal H3-VisualVAE: f16t4d24 (16x spatial, 4x temporal compression, 24 latent channels). Transformer patches are [1,2,2], giving effective 32x spatial /4x temporal token downsampling. A ViT-based decoder is additionally trained after the encoder. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/video_vae/config.json), [source 3](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/transformer/config.json) |
| Audio codec | H3-AudioVAE independently processes left/right channels with shared encoder/decoder, then recombines stereo; 32 kHz per-channel audio becomes 40 Hz latents. Released config: latent_channels=32, output_channel=2, sample_rate=32000. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/audio_vae/config.json) |
| Multimodal coupling | One packed sequence and one Omni-Transformer jointly predict video and audio latents; separate visual/audio VAEs decode synchronized video and stereo audio. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Implementation | Official checkpoint contains task-specific FL2VA/ and Ref2VA/ pipelines and component configs. The pinned card lists SGLang, vLLM, diffusers and ComfyUI integration guides; these are vendor deployment claims, not runtime validation in this repository. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/model_index.json) |

## Output

| Field | Value | Evidence |
|---|---|---|
| Resolution | Open H3-Base: 768p (default shorter side 768 pixels), multiple aspect ratios. 2K belongs to the separate hosted regeneration workflow. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Frame rate | 24 FPS | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Duration | 4–15 seconds (published system specification) | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Audio sample rate | 32 kHz | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Audio channels | Stereo (2 channels) | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Formats | — | — |

## Training

| Field | Value | Evidence |
|---|---|---|
| Training data | [Unknown/Not Disclosed] | — |
| Pretraining | The card reports task-generalization capabilities from pretraining and native sparse attention introduced at the final training stage. Dataset sizes/mix, optimizer and loss formulation are undisclosed. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Post-training | Released task-specific Omni-Transformer checkpoints are CFG-distilled; the distillation recipe is undisclosed. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |

## Precision

| Field | Value | Evidence |
|---|---|---|
| Weight precision | BF16 released FL2VA and Ref2VA checkpoints | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Compute precision | [Unknown/Not Disclosed] | — |
| Quantization | [Unknown/Not Disclosed] | — |

## Release artifacts and limitations

| Field | Value | Evidence |
|---|---|---|
| Released artifacts | FL2VA base checkpoint: text or optional first/last image to audio-video; Ref2VA base checkpoint: text plus image/video/audio references to audio-video; Qwen3-VL-32B-derived encoder, tokenizer, visual and audio VAEs; configs and deployment examples | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Hosted pipeline scope | Context-IR relies on multiple hosted models/services and is excluded from the weight release. Regenerate-2K is also unreleased and accessed via API; the full official 2K workflow combines these hosted modules with local H3-Base. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md) |
| Limitations | Initial released inference provides full attention; sparse attention implementation is not included.; Released base alone does not reproduce the complete hosted 2K workflow.; Custom community license; openness here describes availability, not an OSI license classification. | [source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md), [source 2](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/LICENSE) |

## Open questions

- The license explicitly dates release August 2, 2026; HF repository creation in July is not treated as the public release date.
- Exact pretraining objective, solver implementation, optimizer, data composition and training compute are not disclosed in the registered primary sources.
- 33B describes the Omni-Transformer including AdaLN branches, not the full encoder/VAEs pipeline; no full-system total or active-parameter count is asserted.
- Sparse-attention training support must not be counted as published sparse inference kernels.

## Sources

- [Source 1](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/README.md)
- [Source 2](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/LICENSE)
- [Source 3](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/model_index.json)
- [Source 4](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/transformer/config.json)
- [Source 5](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/Ref2VA/transformer/config.json)
- [Source 6](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/video_vae/config.json)
- [Source 7](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/audio_vae/config.json)
- [Source 8](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/scheduler/scheduler_config.json)
- [Source 9](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/audio_scheduler/scheduler_config.json)
- [Source 10](https://huggingface.co/MiniMaxAI/MiniMax-H3/raw/42ed227ee7df40d41602854ae760620d6eb651fe/FL2VA/text_encoder/config.json)
