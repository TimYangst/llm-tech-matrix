# Multimodal RoPE (mRoPE)

> 中文版：[mrope.zh.md](./mrope.zh.md)

**Slug:** `mrope`
**Category:** position-embedding
**One-line:** A RoPE variant that partitions the rotary head dimensions into bands assigned to different positional axes (temporal, height, width) so a single attention layer can encode 2D image and 3D video positions alongside 1D text positions in the same RoPE space.

**First introduced in:** [Qwen2-VL: Enhancing Vision-Language Model's Perception of the World at Any Resolution (Wang et al., 2024)](https://arxiv.org/abs/2409.12191) (as "M-RoPE")

## Description

Standard RoPE rotates each pair of consecutive head dimensions by an angle proportional
to a single scalar position. For multimodal sequences, "position" is no longer a scalar —
an image patch has (height, width); a video frame has (time, height, width). Encoding
them by flattening into a 1D index works but throws away spatial structure that the
attention layer could otherwise exploit.

mRoPE instead partitions the rotary head dimensions into named **sections**, one per
positional axis, and applies an axis-specific rotation to each section:

- **`mrope_section`** — list of section sizes, e.g. `[t, h, w]`. The first `t` rotary
  pairs encode temporal position, the next `h` encode height, the last `w` encode
  width. For a text-only token, all three axes share the 1D text position so the
  composition reduces to standard RoPE.
- **`mrope_interleaved`** — when `true`, the section indices are interleaved across
  the rotary dimension rather than placed in contiguous blocks, which empirically
  reduces frequency-band collisions.
- Often combined with **partial RoPE** (`partial_rotary_factor < 1.0`), where only a
  fraction of head dimensions are rotated and the remainder are NoPE — letting the
  model carry both relative-positional and content-only channels in the same head.

mRoPE composes naturally with YaRN: the YaRN factor stretches the within-axis
frequencies independently of the section partition.

## Reference materials

- Original paper (Qwen2-VL, §3): <https://arxiv.org/abs/2409.12191>
- HF Transformers reference: `transformers/models/qwen2_vl/modeling_qwen2_vl.py` `apply_multimodal_rotary_pos_emb`

## Used by

| Model           | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                              |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Qwen3.5-27B     | `rope_type="default"` in static config (mRoPE is the underlying form regardless of YaRN). `mrope_section=[11, 11, 10]` (temporal, height, width), `mrope_interleaved=true`. Combined with **partial RoPE** `partial_rotary_factor=0.25` — only 64 of the 256 attention head dims are rotated, the remaining 192 are NoPE. Applied only in the Gated Attention layers (1 of every 4); Gated DeltaNet layers use no RoPE. `rope_theta=10,000,000`. |
| Qwen3.5-35B-A3B | Identical mRoPE configuration to the 27B sibling: `mrope_section=[11, 11, 10]`, `mrope_interleaved=true`, `partial_rotary_factor=0.25`, `rope_theta=10,000,000`. Applied in 1 of every 4 layers (10 of 40 Gated Attention layers). The mRoPE setup is fixed at the family level across the dense-27B and MoE-35B-A3B variants.                                                                                                                   |
| Qwen3.6-27B     | Identical mRoPE configuration to Qwen3.5-27B — same section, interleaving, partial-rotary fraction, base. Inherited unchanged by the post-training-only 3.6 refresh.                                                                                                                                                                                                                                                                             |
| Qwen3.6-35B-A3B | Identical mRoPE configuration to Qwen3.5-35B-A3B (and to all four Qwen3.5/3.6 slugs); fixed at the family level.                                                                                                                                                                                                                                                                                                                                 |

## Related techniques

- [YaRN RoPE scaling](./yarn-rope.md) — orthogonal context-extension layer applied on top of mRoPE in Qwen3.5
