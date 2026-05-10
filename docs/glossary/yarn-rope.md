# YaRN RoPE scaling

> 中文版：[yarn-rope.zh.md](./yarn-rope.zh.md)

**Slug:** `yarn-rope`
**Category:** position-embedding
**One-line:** A RoPE position-encoding extension method that interpolates frequencies non-uniformly across head dimensions, enabling much longer context windows than the model was originally trained on with minimal fine-tuning.
**First introduced in:** [YaRN: Efficient Context Window Extension of Large Language Models (Peng et al., 2023)](https://arxiv.org/abs/2309.00071)

## Description

Standard RoPE encodes absolute position via per-dimension rotation frequencies. Naïve
context extension (linearly interpolating frequencies, "PI") works but degrades quality;
"NTK-aware" interpolation does better but still hits limits. YaRN observes that
different RoPE dimensions encode position at different scales, and applies different
interpolation strategies per dimension band:

- **High frequency** dimensions: extrapolate (do nothing) — they already average out.
- **Low frequency** dimensions: interpolate (PI-like) — they need to fit.
- **Middle frequencies**: a smooth ramp between the two regimes.

YaRN also rescales attention temperature (`mscale`) to compensate for the larger
effective sequence length. The extension typically requires only a short fine-tune
(thousands of steps) to recover quality.

## Reference materials

- Original paper: <https://arxiv.org/abs/2309.00071>

## Used by

| Model           | Variation / details                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DeepSeek-V3     | Applied **only** to the decoupled RoPE key in MLA (`k_t^R`). Two-phase extension: 4K→32K→128K, 1000 steps each. Config: `factor=40` (40 × 4096 original = 163840 max), `beta_fast=32`, `beta_slow=1`, `mscale=1.0`. Baked into HF `config.json` `rope_scaling`.                                                                                                                                                                                                                                                                                                                                             |
| Qwen3-32B       | Combined with **Dual Chunk Attention** for a 4× extension at deployment (32K trained → 128K served). Pre-train Long-Context Stage first lifts RoPE base 10K → 1M via ABF and trains at 32,768; YaRN+DCA is applied at inference time (vLLM/SGLang configs) and deliberately *not* baked into HF `config.json` (`rope_scaling=null`).                                                                                                                                                                                                                                                                        |
| Qwen3-235B-A22B | Same YaRN+DCA recipe as Qwen3-32B (deployment-time, factor 4, original 32,768 → 131,072).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| Qwen3.5-27B     | Pure YaRN (no DCA). Static, opt-in at deployment via vLLM/SGLang flags; the static `config.json` ships `rope_type=default` for the 262K native window. README `factor=4.0`, `original_max_position_embeddings=262144` to lift effective context **262K → ~1010K**. Co-exists with **mRoPE** (`mrope_section=[11,11,10]`, `mrope_interleaved=true`) and **partial RoPE** (`partial_rotary_factor=0.25`, only 64 of 256 head dims rotated). README warns the implementation is static (factor constant regardless of input length); for typical use under 524K, `factor=2.0` is recommended over the full 4×. |
| Qwen3.5-35B-A3B | Identical YaRN recipe to the 27B sibling — same `factor=4.0`, same `original_max_position_embeddings=262144`, same opt-in deployment-time activation. Family-level configuration; the dense vs MoE distinction does not affect long-context extension.                                                                                                                                                                                                                                                                                                                                                      |
| Qwen3.6-27B     | Identical to Qwen3.5-27B — same `factor=4.0`, same `original_max_position_embeddings=262144`, opt-in via inference-framework flags. The 3.6 release inherits 3.5's long-context recipe wholesale.                                                                                                                                                                                                                                                                                                                                                                                                           |
| Qwen3.6-35B-A3B | Identical to Qwen3.5-35B-A3B; family-level recipe shared across all four Qwen3.5/3.6 slugs.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |

## Related techniques

- [MLA](./mla.md) — DeepSeek-V3's MLA carries RoPE only on a small decoupled key vector, so YaRN is applied surgically rather than across all KV
- [Dual Chunk Attention](./dual-chunk-attention.md) — Qwen3 stacks DCA with YaRN to reach the 4× extension in a way that preserves accuracy at long context
