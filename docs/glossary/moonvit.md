# MoonViT — native-resolution + 3D temporal vision encoder

> 中文版：[moonvit.zh.md](./moonvit.zh.md)

**Slug:** `moonvit`
**Category:** vision encoder
**One-line:** A SigLIP-initialised native-resolution vision encoder using the NaViT patch-packing strategy for variable-resolution training, extended to 3D by treating up to 4 consecutive video frames as a spatiotemporal volume packed into a single 1D sequence — image and video share weights, embedding space, and the same attention mechanism.
**First introduced in:** [Kimi-VL Technical Report (Moonshot AI, 2025)](https://arxiv.org/abs/2504.07491) introduces MoonViT; the 3D extension and the joint-pretraining recipe land in [Kimi K2.5: Visual Agentic Intelligence (Moonshot AI, 2026)](https://arxiv.org/abs/2602.02276) §4.2.

## Description

Standard vision encoders fix a single input resolution (e.g. 224×224, 336×336) and require complex sub-image splitting + splicing for high-resolution inputs. MoonViT skips the fixed grid: images are divided into patches at their native resolution, flattened, and concatenated into a single 1D sequence — the NaViT "patch n' pack" strategy — so a batch can contain images of arbitrary, mixed resolutions and the encoder runs them all in one shared forward pass.

K2.5 extends MoonViT to **MoonViT-3D**: up to 4 consecutive video frames are treated as a spatiotemporal volume; their 2D patches are jointly flattened and packed into a single 1D sequence, letting the same attention mechanism operate over space and time without a separate temporal-attention block. Image and video use **fully shared weights** and a **single embedding space** — no architectural bifurcation. Lightweight temporal pooling at the projector compresses 4 frames → 1 patch group, giving 4× temporal compression that lets a fixed context window cover 4× more video.

The encoder is initialised from **SigLIP-SO-400M** (~400M params) and continually pre-trained against caption loss only (no contrastive loss, unlike Kimi-VL). Two-stage alignment: stage 1 trains MoonViT-3D against a small Moonlight-16B-A3B LLM via caption loss (~1T tokens, very low FLOPs); stage 2 (very short) updates only the MLP projector to bridge MoonViT to the 1T K2 backbone.

In K2.5/K2.6's HF config the encoder shows up as `vision_config` with depth=27, hidden=1152, intermediate=4304, num_heads=16, patch_size=14, projector_type='patchmerger', merge_kernel_size=[2,2], video_attn_type='spatial_temporal', text_hidden_size=7168.

## Reference materials

- Kimi-VL Technical Report (introduces MoonViT, the 2D version): <https://arxiv.org/abs/2504.07491>
- Kimi K2.5: Visual Agentic Intelligence (introduces MoonViT-3D + joint-pretraining recipe): <https://arxiv.org/abs/2602.02276>
- NaViT (patch n' pack): <https://arxiv.org/abs/2307.06304>
- SigLIP (initial weights for the encoder): <https://arxiv.org/abs/2303.15343>

## Used by

| Model     | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Kimi K2.5 | MoonViT-3D, 27 layers / 1152 hidden / 4304 intermediate / 16 heads / patch_size=14 / 4-frame temporal volume / merge_kernel_size=[2,2] (`sd2_tpool`) → projected via `patchmerger` to LM hidden_size 7168. Preprocessor: image_mean/std=[0.5,0.5,0.5], in_patch_limit=16384, in_patch_limit_each_frame=4096, sample_fps=2.0, temporal_merge_kernel_size=4, timestamp_mode='hh:mm:ss.fff'. Joint-pretrained with the K2 backbone over ~15T mixed vision-text tokens at constant low vision ratio. |
| Kimi K2.6 | Identical MoonViT-3D + preprocessor as K2.5 (post-training-only refresh; preprocessor_config.json is byte-identical between the two).                                                                                                                                                                                                                                                                                                                                                            |

## Related techniques

- [YaRN RoPE scaling](./yarn-rope.md) — K2.5 mid-training extends sequence length 32K → 256K via YaRN, which compounds with MoonViT-3D's 4× temporal compression to give a much larger effective video budget.
- [Native INT4 QAT](./int4-qat.md) — MoonViT and the MLP projector are explicitly excluded from K2.5/K2.6's INT4 quantization (`config.quantization_config.ignore` patterns).
